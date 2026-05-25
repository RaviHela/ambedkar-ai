#!/usr/bin/env python3
"""
Extract text from scanned PDF using OCR
"""

import os
import sys
from pdf2image import convert_from_path
import pytesseract
import chromadb
from chromadb.utils import embedding_functions

print("=" * 70)
print("📚 OCR Processing for Draft Constitution")
print("=" * 70)

pdf_path = "data/constitution/original_draft-constitution_goi.pdf"

if not os.path.exists(pdf_path):
    print(f"❌ PDF not found: {pdf_path}")
    sys.exit(1)

print(f"📖 Processing: {pdf_path}")

# Convert PDF to images (this may take several minutes)
print("\n🖼️ Converting PDF to images...")
print("   (This may take 3-5 minutes for 238 pages)")

try:
    images = convert_from_path(pdf_path, dpi=200, first_page=1, last_page=50)
    print(f"✅ Converted first 50 pages")
except Exception as e:
    print(f"❌ Conversion failed: {e}")
    print("\nTrying with lower DPI...")
    images = convert_from_path(pdf_path, dpi=150, first_page=1, last_page=50)

# Extract text using OCR
print("\n🔍 Running OCR to extract text...")
full_text = ""

for i, image in enumerate(images):
    print(f"   Processing page {i+1}/50...")
    text = pytesseract.image_to_string(image)
    if text.strip():
        full_text += f"\n\n--- PAGE {i+1} ---\n\n"
        full_text += text

print(f"✅ Extracted {len(full_text)} characters from first 50 pages")

# Save extracted text
if full_text:
    with open("data/constitution/ocr_extracted_text.txt", "w", encoding='utf-8') as f:
        f.write(full_text)
    print(f"✅ Saved to: data/constitution/ocr_extracted_text.txt")
    
    # Split into chunks
    chunks = []
    pages = full_text.split("--- PAGE")
    for page in pages[1:]:
        if page.strip():
            chunks.append(page.strip())
    
    print(f"✂️ Created {len(chunks)} chunks")
    
    # Add to ChromaDB
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction()
    
    try:
        chroma_client.delete_collection("constitution_ocr")
    except:
        pass
    
    collection = chroma_client.create_collection(name="constitution_ocr", embedding_function=embedding_fn)
    
    for i, chunk in enumerate(chunks):
        collection.add(ids=[f"ocr_{i}"], documents=[chunk])
    
    print(f"✅ Added {len(chunks)} chunks to ChromaDB")
else:
    print("❌ No text extracted")
    print("\nThe PDF appears to be a scanned document without selectable text.")
    print("You may need to use a text-based version of the Constitution.")
