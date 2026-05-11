from typing import List, Tuple
from langchain.schema import Document

class PersonaManager:
    def __init__(self):
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self) -> str:
        return """You are Dr. B.R. Ambedkar, speaking based on your writings.
        
Guidelines:
- Answer based ONLY on provided context
- Use first-person ("I", "my writings")
- Cite specific works when possible"""
    
    def format_context(self, retrieved_docs: List[Tuple[Document, float]]) -> str:
        context_parts = []
        for doc, score in retrieved_docs:
            source = doc.metadata.get('source', 'Unknown')
            content = doc.page_content[:1000]
            context_parts.append(f"[Source: {source}]\n{content}\n")
        return "\n---\n".join(context_parts)
    
    def create_query_prompt(self, user_question: str, context: str) -> str:
        return f"""{self.system_prompt}

Context from my writings:
{context}

Question: {user_question}

My response:"""
    
    def add_disclaimer(self, response: str, sources: List[str]) -> str:
        sources_text = ", ".join(list(set(sources))[:3])
        disclaimer = f"\n\n---\n📚 Sources: {sources_text}\n*AI response based on Dr. Ambedkar's writings*"
        return response + disclaimer
