#!/usr/bin/env python3
"""
Import the 1955 Constitution into ChromaDB for Dr. B.R. Ambedkar AI
Source: anoopdixith/TheConstitutionOfIndia - AMENDMENT_03_22021955.zip
"""

import os
import re
import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path

def load_all_txt_files(base_dir: str):
    """Load all .txt files from the constitution bundle"""
    all_content = []
    base_path = Path(base_dir)
    
    # Find all .txt files recursively
    txt_files = base_path.rglob("*.txt")
    
    for txt_file in sorted(txt_files):
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.strip():
                    # Get the section name from the parent folder and filename
                    section = txt_file.parent.name.replace('_', ' ').title()
                    file_name = txt_file.stem
                    
                    all_content.append({
                        'section': f"{section} - {file_name}",
                        'content': content,
                        'file': str(txt_file)
                    })
                    print(f"✅ Loaded: {section} - {file_name}")
        except Exception as e:
            print(f"⚠️ Could not read {txt_file}: {e}")
    
    return all_content

def chunk_constitution(content: str, section: str) -> list:
    """Split constitution text into manageable chunks"""
    chunks = []
    
    # Split by Article patterns or major sections
    article_pattern = r'(Article\s+\d+[A-Z]*\.|Preamble|PART\s+[IVX]+)'
    
    parts = re.split(article_pattern, content)
    
    current_header = ""
    for i, part in enumerate(parts):
        if re.match(article_pattern, part.strip()):
            current_header = part.strip()
        elif part.strip() and current_header:
            full_text = f"{current_header} {part.strip()}"
            
            # Limit chunk size
            if len(full_text) > 1500:
                # Split long sections
                sub_chunks = [full_text[j:j+1500] for j in range(0, len(full_text), 1500)]
                for idx, sub in enumerate(sub_chunks):
                    chunks.append({
                        'text': sub.strip(),
                        'metadata': {
                            'section': section,
                            'article': current_header[:100],
                            'part': idx + 1
                        }
                    })
            else:
                chunks.append({
                    'text': full_text.strip(),
                    'metadata': {
                        'section': section,
                        'article': current_header[:100]
                    }
                })
            current_header = ""
    
    # If no articles found, add the whole content as one chunk
    if not chunks and content.strip():
        chunks.append({
            'text': content.strip(),
            'metadata': {'section': section, 'article': 'Full Section'}
        })
    
    return chunks

def main():
    print("=" * 70)
    print("📚 Importing Constitution of India (1955) into ChromaDB")
    print("=" * 70)
    
    # Path to extracted constitution files
    constitution_dir = "/home/ubuntu/ambedkar-ai/backend/data/constitution_1955"
    
    if not os.path.exists(constitution_dir):
        print(f"❌ Directory not found: {constitution_dir}")
        return
    
    # Load all text files
    print("\n📖 Loading constitution files...")
    constitution_parts = load_all_txt_files(constitution_dir)
    
    if not constitution_parts:
        print("❌ No text files found.")
        return
    
    print(f"\n📄 Total sections found: {len(constitution_parts)}")
    
    # Chunk the content
    print("\n✂️ Chunking content...")
    all_chunks = []
    
    for part in constitution_parts:
        chunks = chunk_constitution(part['content'], part['section'])
        for chunk in chunks:
            all_chunks.append(chunk)
    
    print(f"✅ Created {len(all_chunks)} chunks")
    
    # Connect to ChromaDB
    print("\n💾 Connecting to ChromaDB...")
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    # Create a new collection for the 1955 Constitution
    collection_name = "constitution_1955"
    try:
        chroma_client.delete_collection(collection_name)
        print("✅ Removed existing collection")
    except:
        pass
    
    collection = chroma_client.create_collection(
        name=collection_name,
        embedding_function=embedding_fn
    )
    
    # Add chunks in batches
    batch_size = 100
    total_added = 0
    
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i+batch_size]
        batch_ids = [f"const_1955_{i+j}" for j in range(len(batch))]
        batch_texts = [chunk['text'] for chunk in batch]
        batch_metadatas = [chunk['metadata'] for chunk in batch]
        
        collection.add(
            ids=batch_ids,
            documents=batch_texts,
            metadatas=batch_metadatas
        )
        
        total_added += len(batch)
        print(f"   Added {total_added}/{len(all_chunks)} chunks")
    
    print(f"\n🎉 SUCCESS! Added {total_added} chunks from Constitution of India (1955)")
    print(f"   Collection name: {collection_name}")
    
    # Test queries
    print("\n" + "=" * 70)
    print("🔍 Testing with sample queries:")
    print("=" * 70)
    
    test_queries = [
        "What does the Preamble say?",
        "What are the Fundamental Rights?",
        "What is Article 9 about?",
        "How is the President elected?"
    ]
    
    for query in test_queries:
        results = collection.query(query_texts=[query], n_results=1)
        print(f"\n📝 Query: {query}")
        if results['documents'] and results['documents'][0]:
            preview = results['documents'][0][0][:250].replace('\n', ' ')
            print(f"   Found: {preview}...")
        else:
            print("   No results found")
    
    print("\n✅ Constitution of India (1955) is now searchable!")
    print("   You can now ask constitutional questions in the chat interface.")

if __name__ == "__main__":
    main()
