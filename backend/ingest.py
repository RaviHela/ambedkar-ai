#!/usr/bin/env python3
"""
Document Ingestion Script for Dr. B.R. Ambedkar AI
Run this script to process PDFs and create the vector database
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.document_processor import DocumentProcessor
from app.services.vector_store import VectorStoreManager

def main():
    print("=" * 50)
    print("Dr. B.R. Ambedkar AI - Document Ingestion")
    print("=" * 50)
    
    # Check if data/raw folder exists
    data_dir = "./data/raw"
    if not os.path.exists(data_dir):
        print(f"❌ Error: {data_dir} folder not found!")
        print("Please create the folder and add PDF files.")
        return
    
    # Check if there are PDF files
    pdf_files = [f for f in os.listdir(data_dir) if f.endswith('.pdf')]
    if not pdf_files:
        print(f"❌ No PDF files found in {data_dir}")
        print("Please add Dr. Ambedkar's PDF files to this folder.")
        return
    
    print(f"\n📁 Found {len(pdf_files)} PDF files:")
    for pdf in pdf_files:
        print(f"   - {pdf}")
    
    print("\n🔄 Processing documents...")
    processor = DocumentProcessor()
    documents = processor.process_documents(data_dir)
    
    if not documents:
        print("❌ No documents were processed. Check your PDF files.")
        return
    
    print(f"\n📄 Created {len(documents)} text chunks")
    
    print("\n💾 Creating vector store...")
    vector_manager = VectorStoreManager()
    vector_manager.create_vector_store(documents)
    
    print("\n" + "=" * 50)
    print("✅ Ingestion complete!")
    print("You can now start the API server.")
    print("=" * 50)

if __name__ == "__main__":
    main()