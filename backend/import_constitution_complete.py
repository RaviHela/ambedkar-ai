#!/usr/bin/env python3
"""
Complete import of Constitution of India (1955) - Properly extracts ALL articles
"""

import os
import re
import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path

def extract_all_articles(text: str, part_name: str) -> list:
    """Extract all numbered articles from constitution text"""
    articles = []
    
    # Pattern for numbered articles (14., 15., 16., 14A., etc.)
    # Matches: "15. Prohibition of discrimination..." followed by content until next number
    pattern = r'(\d+[A-Z]*\.\s+[A-Z][^\n]+)\n(.*?)(?=\n\d+[A-Z]*\.\s+[A-Z]|\n\nPART|\Z)'
    
    matches = re.findall(pattern, text, re.DOTALL)
    
    for match in matches:
        title = match[0].strip()
        content = match[1].strip()
        
        # Extract article number
        num_match = re.match(r'(\d+[A-Z]*)\.', title)
        article_num = num_match.group(1) if num_match else "Unknown"
        
        articles.append({
            'article_num': article_num,
            'title': title,
            'content': content,
            'full_text': f"{title}\n{content}",
            'part': part_name
        })
    
    return articles

def main():
    print("=" * 60)
    print("📚 Importing ALL Articles from Constitution of India (1955)")
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
            
            articles = extract_all_articles(content, part_name)
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
    
    # Add ALL articles
    for i, article in enumerate(all_articles):
        doc_text = f"Article {article['article_num']}: {article['title']}\n{article['content']}"
        
        collection.add(
            ids=[f"art_{article['article_num']}_{i}"],
            documents=[doc_text],
            metadatas=[{
                'article': article['article_num'],
                'title': article['title'][:100],
                'part': article['part'],
                'source': f"Constitution of India (1955) - Article {article['article_num']}"
            }]
        )
        
        if (i + 1) % 50 == 0:
            print(f"  Added {i+1}/{len(all_articles)} articles")
    
    print(f"\n🎉 SUCCESS! Added {len(all_articles)} articles to ChromaDB")
    
    # Test multiple articles
    print("\n🔍 Testing article search:")
    test_articles = ["15", "14", "21", "32"]
    for art_num in test_articles:
        results = collection.query(query_texts=[f"Article {art_num}"], n_results=1)
        if results['documents'] and results['documents'][0]:
            doc = results['documents'][0][0]
            if f"Article {art_num}" in doc[:50]:
                print(f"  ✅ Article {art_num}: Found")
            else:
                print(f"  ⚠️ Article {art_num}: Found but not exact")
        else:
            print(f"  ❌ Article {art_num}: Not found")

if __name__ == "__main__":
    main()
