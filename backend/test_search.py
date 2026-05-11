#!/usr/bin/env python3
"""
Test search functionality after ingestion
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.services.vector_store import VectorStoreManager

def main():
    print("Testing Vector Store Search")
    print("=" * 40)
    
    try:
        # Load vector store
        vector_manager = VectorStoreManager()
        vector_manager.load_vector_store()
        
        # Test queries
        test_queries = [
            "What is the caste system?",
            "What did you say about education?",
            "What are your views on equality?"
        ]
        
        for query in test_queries:
            print(f"\n📝 Question: {query}")
            print("-" * 40)
            
            results = vector_manager.search(query, k=2)
            
            for i, (doc, score) in enumerate(results, 1):
                source = doc.metadata.get('source', 'Unknown')
                content_preview = doc.page_content[:200].replace('\n', ' ')
                print(f"\nResult {i} (Score: {score:.4f})")
                print(f"Source: {source}")
                print(f"Preview: {content_preview}...")
        
        print("\n" + "=" * 40)
        print("✅ Search test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you've run ingest.py first to create the vector store.")

if __name__ == "__main__":
    main()