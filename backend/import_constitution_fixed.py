#!/usr/bin/env python3
"""
Import Constitution with proper article extraction (handles both "Article" and numbered format)
"""

import os
import re
import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path

def extract_articles_from_text(text: str, part_name: str) -> list:
    """Extract articles from constitution text (handles numbered format like 14., 15., etc.)"""
    articles = []
    
    # Pattern for numbered articles (14. 15. 16. etc.)
    numbered_pattern = r'(\d+\.\s+[A-Z][^\n]+)\n(.*?)(?=\n\d+\.\s+[A-Z]|\n\nPART|\Z)'
    
    matches = re.findall(numbered_pattern, text, re.DOTALL)
    
    for match in matches:
        article_title = match[0].strip()
        article_content = match[1].strip()
        
        if article_content:
            articles.append({
                'title': article_title,
                'content': article_content,
                'full_text': f"{article_title}\n{article_content}",
                'part': part_name
            })
    
    return articles

def main():
    print("=" * 60)
    print("📚 Importing Constitution with proper article extraction")
    print("=" * 60)
    
    base_dir = "/home/ubuntu/ambedkar-ai/backend/data/constitution_1955"
    
    # Find all text files
    txt_files = list(Path(base_dir).rglob("*.txt"))
    print(f"Found {len(txt_files)} text files")
    
    all_articles = []
    
    for txt_file in txt_files:
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            part_name = f"{txt_file.parent.name}/{txt_file.stem}"
            
            # Extract articles
            articles = extract_articles_from_text(content, part_name)
            for article in articles:
                all_articles.append(article)
            
            if articles:
                print(f"  {part_name}: {len(articles)} articles")
    
    print(f"\n📄 Total articles extracted: {len(all_articles)}")
    
    # Connect to ChromaDB
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction()
    
    # Delete old collection
    collection_name = "constitution_1955"
    try:
        chroma_client.delete_collection(collection_name)
        print("✅ Removed old collection")
    except:
        pass
    
    collection = chroma_client.create_collection(
        name=collection_name,
        embedding_function=embedding_fn
    )
    
    # Add articles as individual documents
    for i, article in enumerate(all_articles):
        doc_text = f"{article['title']}\n{article['content']}"
        
        collection.add(
            ids=[f"art_{i}"],
            documents=[doc_text],
            metadatas=[{
                'title': article['title'][:100],
                'part': article['part'],
                'source': 'Constitution of India (1955)'
            }]
        )
        
        if (i + 1) % 50 == 0:
            print(f"  Added {i+1}/{len(all_articles)} articles")
    
    print(f"\n🎉 SUCCESS! Added {len(all_articles)} articles to ChromaDB")
    
    # Test Article 15
    print("\n🔍 Testing Article 15...")
    results = collection.query(query_texts=["15. Prohibition of discrimination"], n_results=1)
    if results['documents'] and results['documents'][0]:
        print(f"✅ Found: {results['documents'][0][0][:400]}...")
    else:
        print("❌ Article 15 not found")

if __name__ == "__main__":
    main()
