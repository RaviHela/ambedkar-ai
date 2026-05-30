#!/usr/bin/env python3
"""
Properly import Constitution of India (1955) with article-level chunking
"""

import os
import re
import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path

def extract_articles(text: str) -> list:
    """Extract individual articles from constitution text"""
    articles = []
    
    # Pattern to match Article numbers
    article_pattern = r'(Article\s+(\d+[A-Z]*\.?))\s*(.*?)(?=Article\s+\d+|$)'
    
    matches = re.findall(article_pattern, text, re.DOTALL)
    
    for match in matches:
        article_header = match[0]
        article_num = match[1]
        article_content = match[2].strip()
        
        if article_content:
            articles.append({
                'article_num': article_num,
                'header': article_header,
                'content': article_content,
                'full_text': f"{article_header} {article_content}"
            })
    
    return articles

def main():
    print("=" * 60)
    print("📚 Importing Constitution with Article-level chunking")
    print("=" * 60)
    
    base_dir = "/home/ubuntu/ambedkar-ai/backend/data/constitution_1955"
    
    # Find all text files
    txt_files = list(Path(base_dir).rglob("*.txt"))
    print(f"Found {len(txt_files)} text files")
    
    all_articles = []
    
    for txt_file in txt_files:
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Extract articles
            articles = extract_articles(content)
            for article in articles:
                article['source_file'] = str(txt_file)
                all_articles.append(article)
                
            print(f"  {txt_file.parent.name}/{txt_file.stem}: {len(articles)} articles")
    
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
        doc_text = f"Article {article['article_num']}: {article['content']}"
        
        collection.add(
            ids=[f"art_{article['article_num']}_{i}"],
            documents=[doc_text],
            metadatas=[{
                'article': article['article_num'],
                'source': 'Constitution of India (1955)',
                'type': 'article'
            }]
        )
        
        if (i + 1) % 50 == 0:
            print(f"  Added {i+1}/{len(all_articles)} articles")
    
    print(f"\n🎉 SUCCESS! Added {len(all_articles)} articles to ChromaDB")
    
    # Test Article 15
    print("\n🔍 Testing Article 15...")
    results = collection.query(query_texts=["Article 15"], n_results=1)
    if results['documents'] and results['documents'][0]:
        print(f"✅ Found: {results['documents'][0][0][:300]}...")
    else:
        print("❌ Article 15 not found")
    
    # Test Article 14
    print("\n🔍 Testing Article 14...")
    results = collection.query(query_texts=["Article 14"], n_results=1)
    if results['documents'] and results['documents'][0]:
        print(f"✅ Found: {results['documents'][0][0][:300]}...")
    else:
        print("❌ Article 14 not found")

if __name__ == "__main__":
    main()
