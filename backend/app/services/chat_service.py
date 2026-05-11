import anthropic
from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict
from app.config import Config
from app.services.vector_store import VectorStoreManager
from app.models.persona_manager import PersonaManager

class ChatService:
    def __init__(self):
        self.vector_store = VectorStoreManager()
        self.persona = PersonaManager()
        self.claude_client = None
        self.conversation_memory = defaultdict(list)
        self.max_memory_length = 10
        
        if Config.ANTHROPIC_API_KEY:
            try:
                self.claude_client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
                print("Claude AI ready")
            except Exception as e:
                print(f"Claude init error: {e}")
    
    def get_response(self, question: str, session_id: str = "default", 
                    language: str = "en", chat_history: Optional[List[Dict]] = None) -> Dict:
        
        try:
            retrieved_docs = self.vector_store.search(question, k=5)
        except Exception as e:
            print(f"Search error: {e}")
            retrieved_docs = []
        
        if not retrieved_docs:
            return {
                "response": "I cannot find specific information in my writings about this. Please ask about social justice, caste, education, or the Constitution.",
                "sources": [],
                "disclaimer": True,
                "session_id": session_id
            }
        
        context = self.persona.format_context(retrieved_docs)
        sources = list(set([doc[0].metadata.get('source', 'Unknown') for doc in retrieved_docs]))
        conversation_history = self._get_conversation_history(session_id)
        
        if self.claude_client:
            try:
                response_text = self._get_claude_response(question, context, conversation_history, language)
            except Exception as e:
                print(f"Claude error: {e}")
                response_text = f"Based on my writings in {sources[0]}: {context[:300]}"
        else:
            response_text = f"Based on my writings in {sources[0]}: {context[:400]}"
        
        self._add_to_memory(session_id, question, response_text)
        response_text = self.persona.add_disclaimer(response_text, sources)
        
        return {
            "response": response_text,
            "sources": sources,
            "disclaimer": True,
            "session_id": session_id
        }
    
    def _get_conversation_history(self, session_id: str) -> str:
        memory = self.conversation_memory.get(session_id, [])
        if not memory:
            return ""
        history = "Previous conversation:\n"
        for item in memory[-self.max_memory_length:]:
            history += f"User: {item['question'][:200]}\n"
            history += f"Dr. Ambedkar: {item['response'][:200]}\n\n"
        return history
    
    def _add_to_memory(self, session_id: str, question: str, response: str):
        self.conversation_memory[session_id].append({
            "question": question,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
        if len(self.conversation_memory[session_id]) > self.max_memory_length:
            self.conversation_memory[session_id] = self.conversation_memory[session_id][-self.max_memory_length:]
    
    def clear_memory(self, session_id: str) -> bool:
        if session_id in self.conversation_memory:
            self.conversation_memory[session_id] = []
            return True
        return False
    
    def _get_claude_response(self, question: str, context: str, conversation_history: str, language: str) -> str:
        if language == "hi":
            prompt = f"मेरे लेखन से:\n{context[:1200]}\n\n{conversation_history}\nप्रश्न: {question}\n\nडॉ. अंबेडकर के रूप में हिंदी में उत्तर दें:"
        else:
            prompt = f"From my writings:\n{context[:1200]}\n\n{conversation_history}\nQuestion: {question}\n\nRespond as Dr. Ambedkar naturally:"
        
        response = self.claude_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    def get_sample_questions(self, language: str = "en") -> List[str]:
        if language == "hi":
            return ["जाति व्यवस्था पर विचार?", "शिक्षा का महत्व?", "युवाओं के लिए संदेश?"]
        return ["What is your view on caste?", "Why is education important?", "Message for youth?"]
