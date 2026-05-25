#!/usr/bin/env python3
"""
Simple script to add Dr. Ambedkar's Draft Constitution to ChromaDB
"""

import os
import sys
import chromadb
from chromadb.utils import embedding_functions

def main():
    print("=" * 60)
    print("📚 Adding Draft Constitution to ChromaDB")
    print("=" * 60)
    
    # Initialize ChromaDB client
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    
    # Use sentence transformer embeddings
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    # Get or create collection
    collection_name = "constitution"
    try:
        collection = chroma_client.get_collection(name=collection_name)
        print(f"✅ Existing collection '{collection_name}' found")
    except:
        collection = chroma_client.create_collection(
            name=collection_name,
            embedding_function=embedding_fn
        )
        print(f"✅ Created new collection '{collection_name}'")
    
    # Path to constitution file
    constitution_path = "data/constitution/draft_constitution_ambedkar.txt"
    
    if not os.path.exists(constitution_path):
        print(f"❌ File not found: {constitution_path}")
        return
    
    # Read the file
    with open(constitution_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into sections based on article headings
    sections = []
    current_section = ""
    lines = content.split('\n')
    
    for line in lines:
        if line.strip().startswith('Article') or line.strip().startswith('##') or line.strip().startswith('PART'):
            if current_section.strip():
                sections.append(current_section.strip())
            current_section = line + "\n"
        else:
            current_section += line + "\n"
    
    if current_section.strip():
        sections.append(current_section.strip())
    
    print(f"📄 Split into {len(sections)} sections")
    
    # Add sections to ChromaDB
    ids = []
    documents = []
    metadatas = []
    
    for i, section in enumerate(sections):
        if len(section) > 50:  # Only add substantial sections
            ids.append(f"constitution_section_{i}")
            documents.append(section)
            metadatas.append({"source": "draft_constitution", "index": i, "title": section[:50]})
    
    # Add in batches
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch_ids = ids[i:i+batch_size]
        batch_docs = documents[i:i+batch_size]
        batch_meta = metadatas[i:i+batch_size]
        
        collection.add(
            ids=batch_ids,
            documents=batch_docs,
            metadatas=batch_meta
        )
        print(f"✅ Added {len(batch_ids)} documents (total: {i+len(batch_ids)}/{len(documents)})")
    
    print(f"\n✅ Successfully added {len(documents)} sections to ChromaDB!")
    
    # Test query
    print("\n" + "=" * 60)
    print("🔍 Testing with sample queries:")
    print("=" * 60)
    
    test_queries = [
        "What is the preamble of the constitution?",
        "What are fundamental rights?",
        "What is Article 9 about?"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        results = collection.query(query_texts=[query], n_results=2)
        if results['documents'] and results['documents'][0]:
            print(f"   Found: {results['documents'][0][0][:200]}...")
        else:
            print("   No results found")
    
    print("\n✅ Done! The Constitution is now available for queries.")

if __name__ == "__main__":
    main()
