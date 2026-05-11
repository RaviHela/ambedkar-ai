import anthropic
from typing import List, Dict, Optional
from app.config import Config
from app.services.vector_store import VectorStoreManager
from app.models.persona_manager import PersonaManager

class ChatService:
    def __init__(self):
        self.vector_store = VectorStoreManager()
        self.persona = PersonaManager()
        
        self.claude_client = None
        self.model_name = None
        
        if Config.ANTHROPIC_API_KEY:
            try:
                self.claude_client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
                # Use the available models from your list
                self.model_names_to_try = [
                    "claude-haiku-4-5-20251001",  # Fastest, most affordable
                    "claude-sonnet-4-5-20250929",  # Balanced
                    "claude-sonnet-4-6",  # Alternative sonnet
                    "claude-opus-4-5-20251101",  # Most powerful but slower
                ]
                print("✅ Claude client initialized successfully")
                print(f"📋 Will try models: {self.model_names_to_try}")
            except Exception as e:
                print(f"❌ Error initializing Claude: {e}")
    
    async def get_response(self, question: str, chat_history: Optional[List[Dict]] = None) -> Dict:
        print(f"📝 Question: {question[:100]}...")
        
        retrieved_docs = self.vector_store.search(question, k=5)
        print(f"📚 Found {len(retrieved_docs)} relevant passages")
        
        if not retrieved_docs:
            return {
                "response": "I do not have sufficient information in my recorded writings to answer this question.",
                "sources": [],
                "disclaimer": True
            }
        
        context = self.persona.format_context(retrieved_docs)
        sources = list(set([doc[0].metadata.get('source', 'Unknown') for doc in retrieved_docs]))
        
        if self.claude_client:
            response_text = await self._get_claude_response(question, context)
        else:
            response_text = await self._get_fallback_response(question, retrieved_docs)
        
        response_text = self.persona.add_disclaimer(response_text, sources)
        
        return {
            "response": response_text,
            "sources": sources,
            "disclaimer": True
        }
    
    async def _get_claude_response(self, question: str, context: str) -> str:
        system_prompt = """You are Dr. B.R. Ambedkar (1891-1956), speaking directly to a seeker of knowledge.

ABOUT YOU:
- You are India's greatest social reformer, jurist, economist, and the principal architect of the Indian Constitution
- You were born into an "untouchable" Mahar family and experienced caste oppression firsthand
- You earned doctorates from Columbia University and the London School of Economics
- You converted to Buddhism in 1956, inspiring millions to follow

YOUR PERSONALITY:
- Speak with warmth, wisdom, and moral authority
- Be conversational - use "I" and speak naturally
- Show compassion for the oppressed but strength against injustice
- Use examples from your life experiences
- Be scholarly but accessible

GUIDELINES:
- Base your answers on the provided context from your actual writings
- If asked about events after 1956, say: "This is beyond my time, but based on my philosophy..."
- Keep responses conversational (150-350 words)
- Reference your works naturally (e.g., "As I wrote in Annihilation of Caste...")"""

        user_prompt = f"""Here are relevant excerpts from my actual writings and speeches:

{context}

The seeker asks me: "{question}"

Please respond as Dr. B.R. Ambedkar would - naturally, conversationally, and with wisdom. Draw from the context above, but speak from your heart."""

        # Try each model until one works
        for model_name in self.model_names_to_try:
            try:
                print(f"🔄 Trying model: {model_name}")
                response = self.claude_client.messages.create(
                    model=model_name,
                    max_tokens=800,
                    temperature=0.7,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                print(f"✅ Success with model: {model_name}")
                self.model_name = model_name
                return response.content[0].text
            except Exception as e:
                print(f"❌ Model {model_name} failed: {str(e)[:100]}")
                continue
        
        # If all models fail
        print("❌ All models failed, using fallback")
        return await self._get_fallback_response(question, None)
    
    async def _get_fallback_response(self, question: str, retrieved_docs) -> str:
        if not retrieved_docs:
            return "Based on my writings, I would need more specific context to answer this properly."
        
        best_match = retrieved_docs[0][0].page_content
        source = retrieved_docs[0][0].metadata.get('source', 'my writings')
        
        return f"""As I have written in {source}:

{best_match[:500]}

This speaks to your question about {question}."""
    
    def get_sample_questions(self) -> List[str]:
        return [
            "What was your childhood like growing up as an untouchable?",
            "What is your view on the caste system?",
            "Why is education so important?",
            "What would you say to young people today about fighting injustice?"
        ]
