from app.services.cache_service import response_cache
import anthropic
import boto3
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Optional
from app.config import Config
import chromadb
import re

class ChatService:
    def __init__(self):
        self.conversation_memory = defaultdict(list)
        self.max_memory_length = 10
        self.claude_client = None
        self.chroma_client = None
        self.baws_collection = None
        self.constitution_collection = None
        
        # Initialize ChromaDB
        try:
            self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
            self.baws_collection = self.chroma_client.get_collection("langchain")
            self.constitution_collection = self.chroma_client.get_collection("constitution_1955")
            print(f"✅ BAWS: {self.baws_collection.count()} documents")
            print(f"✅ Constitution 1955: {self.constitution_collection.count()} documents")
        except Exception as e:
            print(f"⚠️ ChromaDB error: {e}")
        
        # Initialize Claude
        if Config.ANTHROPIC_API_KEY:
            try:
                self.claude_client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
                print("✅ Claude client initialized")
            except Exception as e:
                print(f"Error: {e}")
    
    def extract_volume_name(self, source_file: str) -> str:
        """Extract readable volume name from source file"""
        volume_names = {
            "1": "BAWS Volume 1 - Castes in India",
            "2": "BAWS Volume 2 - Annihilation of Caste",
            "3": "BAWS Volume 3 - What Congress and Gandhi Have Done",
            "5": "BAWS Volume 5 - Essays on Untouchables",
            "9": "BAWS Volume 9 - The Buddha and His Dhamma",
            "13": "BAWS Volume 13 - Draft Constitution",
            "16": "BAWS Volume 16 - Pali Dictionary"
        }
        
        match = re.search(r'BAWS[_\-]*Volume[_\-]*(\d+)', source_file, re.IGNORECASE)
        if match:
            vol_num = match.group(1)
            return volume_names.get(vol_num, f"BAWS Volume {vol_num}")
        return "BAWS - Dr. B.R. Ambedkar's Writings"
    
    def extract_article_info(self, doc: str) -> str:
        """Extract article information from constitution text"""
        match = re.search(r'(\d+)\.\s+([A-Z][^.\n]{0,80})', doc)
        if match:
            article_num = match.group(1)
            article_title = match.group(2).strip()
            return f"Constitution of India (1955) - Article {article_num}: {article_title}"
        return "Constitution of India (1955)"
    
    def search_all_sources(self, question: str, n_results: int = 3) -> tuple:
        """Search both BAWS and Constitution collections"""
        all_context = []
        all_sources = []
        
        # Search BAWS
        if self.baws_collection:
            try:
                baws_results = self.baws_collection.query(query_texts=[question], n_results=n_results)
                if baws_results['documents'] and baws_results['documents'][0]:
                    for i, doc in enumerate(baws_results['documents'][0]):
                        # Extract volume name from metadata
                        volume_name = "BAWS - Dr. B.R. Ambedkar's Writings"
                        if baws_results['metadatas'] and baws_results['metadatas'][0]:
                            metadata = baws_results['metadatas'][0][i] if i < len(baws_results['metadatas'][0]) else {}
                            source_file = metadata.get('source', '')
                            if source_file:
                                volume_name = self.extract_volume_name(source_file)
                        all_context.append(f"[{volume_name}]\n{doc[:600]}")
                        all_sources.append(volume_name)
            except Exception as e:
                print(f"BAWS search error: {e}")
        
        # Search Constitution
        if self.constitution_collection:
            try:
                const_results = self.constitution_collection.query(query_texts=[question], n_results=n_results)
                if const_results['documents'] and const_results['documents'][0]:
                    for i, doc in enumerate(const_results['documents'][0]):
                        article_info = self.extract_article_info(doc)
                        all_context.append(f"[{article_info}]\n{doc[:600]}")
                        all_sources.append(article_info)
            except Exception as e:
                print(f"Constitution search error: {e}")
        
        combined_context = "\n\n---\n\n".join(all_context)
        unique_sources = list(set(all_sources))
        
        return combined_context, unique_sources
    
    async def get_response(self, question: str, user_id: str = "anonymous", 
                          session_id: str = "default", 
                          language: str = "en", 
                          chat_history: Optional[List[Dict]] = None) -> Dict:
        
        # Check cache first
        cached_response = response_cache.get(question, language)
        if cached_response:
            return cached_response
        
        # Search both sources
        context, sources = self.search_all_sources(question)
        
        if not context:
            return {
                "response": "I do not have sufficient information in my recorded writings to answer this question.",
                "sources": [],
                "disclaimer": True,
                "session_id": session_id
            }
        
        if self.claude_client:
            response_text = self._get_claude_response(question, context, sources, language)
        else:
            response_text = "Claude API not available. Please check your API key."
        
        # Add source footnote
        footnote = self._get_footnote(sources, language)
        
        # Store in cache
        result = {
            "response": response_text + footnote,
            "sources": sources,
            "disclaimer": True,
            "session_id": session_id
        }
        response_cache.set(question, language, result)
        
        return result
    
    def _get_footnote(self, sources: list, language: str) -> str:
        if not sources:
            sources = ["Dr. B.R. Ambedkar's Writings and Constitution of India"]
        
        if language == "hi":
            return "\n\n---\n📚 **स्रोत:**\n" + "\n".join([f"- {v}" for v in sources]) + "\n\n*AI प्रतिक्रिया डॉ. अम्बेडकर के लेखन और भारत के संविधान पर आधारित है.*"
        elif language == "bn":
            return "\n\n---\n📚 **উৎস:**\n" + "\n".join([f"- {v}" for v in sources]) + "\n\n*AI প্রতিক্রিয়া ডঃ আম্বেদকরের রচনা এবং ভারতের সংবিধানের উপর ভিত্তি করে তৈরি.*"
        else:
            return "\n\n---\n📚 **Sources:**\n" + "\n".join([f"- {v}" for v in sources]) + "\n\n*AI response based on Dr. Ambedkar's writings and the Constitution of India.*"
    
    def _get_claude_response(self, question: str, context: str, sources: list, language: str) -> str:
        try:
            lang_instruction = "Respond in English."
            if language == "hi":
                lang_instruction = "CRITICAL: Respond ONLY in HINDI language. Use Devanagari script."
            elif language == "bn":
                lang_instruction = "CRITICAL: Respond ONLY in BENGALI language. Use Bengali script."
            
            system_prompt = f"""You are Dr. B.R. Ambedkar. Answer as if you are him. Use first person 'I' and 'my'.
{lang_instruction}
Base your answers on the provided context from my writings and the Constitution of India.
When referencing the Constitution, say "In the Constitution I helped draft, Article X states..."
Be direct, authoritative, and conversational."""
            
            user_prompt = f"""Context from my writings and the Constitution:
{context}

Question: {question}

Answer directly as Dr. B.R. Ambedkar:"""
            
            response = self.claude_client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=800,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Claude API error: {e}")
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
                "যুবকদের জন্য আপনার বার্তা কী?"
            ]
        return [
            "What is your view on the caste system?",
            "Why is education important?",
            "What is your message to young people?"
        ]

chat_service = ChatService()
