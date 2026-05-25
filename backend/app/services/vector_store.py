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
    def search_with_sources(self, query: str, n_results: int = 5) -> list:
        """Search and return results with source information"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            documents = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    doc_info = {
                        'content': doc,
                        'source': 'BAWS - Annihilation of Caste' if 'Annihilation' in doc else 'BAWS - Dr. B.R. Ambedkar Writings'
                    }
                    
                    # Add metadata if available
                    if results['metadatas'] and results['metadatas'][0]:
                        metadata = results['metadatas'][0][i] if i < len(results['metadatas'][0]) else {}
                        if metadata.get('source'):
                            doc_info['source'] = metadata['source']
                        elif metadata.get('title'):
                            doc_info['source'] = metadata['title']
                    
                    documents.append(doc_info)
            
            return documents
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def search_with_volumes(self, query: str, n_results: int = 5) -> list:
        """Search and return results with volume information"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            documents = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    # Extract volume from metadata if available
                    volume = "BAWS"
                    if results['metadatas'] and results['metadatas'][0]:
                        metadata = results['metadatas'][0][i] if i < len(results['metadatas'][0]) else {}
                        volume = metadata.get('volume', metadata.get('source', metadata.get('title', 'BAWS')))
                    
                    # Try to extract volume from content if not in metadata
                    if volume == "BAWS":
                        if "Volume" in doc[:200]:
                            import re
                            vol_match = re.search(r'(Volume\s+[\d]+|Vol\.\s*[\d]+)', doc[:200])
                            if vol_match:
                                volume = vol_match.group(0)
                    
                    documents.append({
                        'content': doc,
                        'volume': volume,
                        'source': f"BAWS - {volume}"
                    })
            
            return documents
        except Exception as e:
            print(f"Search error: {e}")
            return []
