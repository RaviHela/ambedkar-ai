import anthropic
import boto3
import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from collections import defaultdict
from app.config import Config
from app.services.vector_store import VectorStoreManager
from app.models.persona_manager import PersonaManager

class ChatService:
    def __init__(self):
        self.vector_store = VectorStoreManager()
        self.persona = PersonaManager()
        self.conversation_memory = defaultdict(list)
        self.max_memory_length = 10
        self.claude_client = None
        
        # Initialize DynamoDB for tracking
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=Config.AWS_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
        )
        self.questions_table = None
        self._init_tables()
        
        if Config.ANTHROPIC_API_KEY:
            try:
                self.claude_client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
                print("✅ Claude client initialized")
            except Exception as e:
                print(f"Error: {e}")
    
    def _init_tables(self):
        """Create DynamoDB tables if they don't exist"""
        try:
            self.questions_table = self.dynamodb.create_table(
                TableName='ambedkar_questions',
                KeySchema=[
                    {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'user_id', 'AttributeType': 'S'},
                    {'AttributeName': 'timestamp', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            print("✅ Created questions table")
        except self.dynamodb.meta.client.exceptions.ResourceInUseException:
            self.questions_table = self.dynamodb.Table('ambedkar_questions')
            print("📋 Questions table already exists")
    
    def track_user_question(self, user_id: str, question: str, response: str, session_id: str):
        """Track user questions and responses in DynamoDB"""
        if not self.questions_table:
            return
        
        try:
            self.questions_table.put_item(
                Item={
                    'user_id': user_id,
                    'timestamp': datetime.now().isoformat(),
                    'question': question[:1000],
                    'response': response[:1000],
                    'session_id': session_id,
                    'question_length': len(question),
                    'response_length': len(response)
                }
            )
            # Update user's total question count
            users_table = self.dynamodb.Table('ambedkar_users')
            users_table.update_item(
                Key={'user_id': user_id},
                UpdateExpression='ADD total_questions :inc',
                ExpressionAttributeValues={':inc': 1}
            )
            print(f"📝 Tracked question from user: {user_id[:8]}...")
        except Exception as e:
            print(f"⚠️ Failed to track question: {e}")
    
    async def get_response(self, question: str, user_id: str = "anonymous", 
                          session_id: str = "default", 
                          language: str = "en", 
                          chat_history: Optional[List[Dict]] = None) -> Dict:
        
        print(f"👤 User {user_id[:8]}... asked: {question[:100]}...")
        
        retrieved_docs = self.vector_store.search(question, k=5)
        
        if not retrieved_docs:
            return {
                "response": "I do not have sufficient information in my recorded writings to answer this question.",
                "sources": [],
                "disclaimer": True,
                "session_id": session_id
            }
        
        context = self.persona.format_context(retrieved_docs)
        sources = list(set([doc[0].metadata.get('source', 'Unknown') for doc in retrieved_docs]))
        conversation_context = self._get_conversation_context(session_id)
        
        if self.claude_client:
            response_text = self._get_claude_response(question, context, conversation_context, language)
        else:
            response_text = "Claude API not available. Please check your API key."
        
        self._add_to_memory(session_id, question, response_text)
        
        # Track the question and response (only for authenticated users)
        if user_id != "anonymous":
            self.track_user_question(user_id, question, response_text, session_id)
        
        response_text = self.persona.add_disclaimer(response_text, sources)
        
        return {
            "response": response_text,
            "sources": sources,
            "disclaimer": True,
            "session_id": session_id
        }
    
    def _get_conversation_context(self, session_id: str) -> str:
        memory = self.conversation_memory[session_id]
        if not memory:
            return ""
        context = "Previous conversation:\n"
        for item in memory[-self.max_memory_length:]:
            context += f"User: {item['question'][:200]}\n"
            context += f"Dr. Ambedkar: {item['response'][:200]}\n\n"
        return context
    
    def _add_to_memory(self, session_id: str, question: str, response: str):
        self.conversation_memory[session_id].append({
            "question": question,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
        if len(self.conversation_memory[session_id]) > self.max_memory_length:
            self.conversation_memory[session_id] = self.conversation_memory[session_id][-self.max_memory_length:]
    
    def _get_claude_response(self, question: str, context: str, conversation_context: str, language: str) -> str:
        prompt = f"Context: {context}\n\n{conversation_context}\n\nQuestion: {question}\n\nRespond as Dr. Ambedkar:"
        
        if language == "hi":
            prompt = f"हिंदी में उत्तर दें। संदर्भ: {context}\n\n{conversation_context}\n\nप्रश्न: {question}\n\nडॉ. अंबेडकर के रूप में उत्तर दें:"
        elif language == "bn":
            prompt = f"বাংলায় উত্তর দিন। প্রসঙ্গ: {context}\n\n{conversation_context}\n\nপ্রশ্ন: {question}\n\nডঃ আম্বেদকর হিসাবে উত্তর দিন:"
        
        try:
            response = self.claude_client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=500,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"❌ Claude error: {e}")
            return f"Based on my writings: {context[:300]}"
    
    def get_sample_questions(self, language: str = "en") -> List[str]:
        if language == "hi":
            return [
                "जाति व्यवस्था पर आपके क्या विचार हैं?",
                "शिक्षा क्यों महत्वपूर्ण है?",
                "युवाओं के लिए आपका क्या संदेश है?"
            ]
        elif language == "bn":
            return [
                "জাত ব্যবস্থা সম্পর্কে আপনার দৃষ্টিভঙ্গি কী?",
                "শিক্ষা কেন গুরুত্বপূর্ণ?",
                "যুবকদের জন্য您的 বার্তা কী?"
            ]
        return [
            "What is your view on the caste system?",
            "Why is education important?",
            "What is your message to young people?"
        ]
