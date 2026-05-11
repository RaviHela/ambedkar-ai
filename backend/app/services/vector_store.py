from typing import List, Tuple
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
from app.config import Config

class VectorStoreManager:
    def __init__(self):
        self.embeddings = self._get_embeddings()
        self.vector_store = None
        
    def _get_embeddings(self):
        """Initialize embeddings using local model"""
        print("Loading embedding model...")
        return HuggingFaceEmbeddings(
            model_name=Config.MODEL_NAME,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    
    def create_vector_store(self, documents: List[Document]):
        """Create vector store from documents"""
        print(f"Creating vector store with {len(documents)} documents...")
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=Config.CHROMA_PERSIST_DIR
        )
        self.vector_store.persist()
        print(f"✅ Vector store created and saved to {Config.CHROMA_PERSIST_DIR}")
    
    def load_vector_store(self):
        """Load existing vector store"""
        print("Loading existing vector store...")
        self.vector_store = Chroma(
            persist_directory=Config.CHROMA_PERSIST_DIR,
            embedding_function=self.embeddings
        )
        print("✅ Vector store loaded")
    
    def search(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Search for similar documents"""
        if not self.vector_store:
            self.load_vector_store()
        
        results = self.vector_store.similarity_search_with_score(query, k=k)
        return results