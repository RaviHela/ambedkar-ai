#!/usr/bin/env python3
"""
Process ALL pages of the Draft Constitution using OCR
"""

import os
import sys
from pdf2image import convert_from_path
import pytesseract
import chromadb
from chromadb.utils import embedding_functions

print("=" * 70)
print("📚 OCR Processing COMPLETE Draft Constitution (All 238 Pages)")
print("=" * 70)

pdf_path = "data/constitution/original_draft-constitution_goi.pdf"

if not os.path.exists(pdf_path):
    print(f"❌ PDF not found: {pdf_path}")
    sys.exit(1)

print(f"📖 Processing: {pdf_path}")

# Convert entire PDF to images
print("\n🖼️ Converting PDF to images (this will take 5-10 minutes)...")
print("   Processing 238 pages with OCR...")

try:
    # Convert all pages with lower DPI for speed
    images = convert_from_path(pdf_path, dpi=150, first_page=1, last_page=238)
    print(f"✅ Converted {len(images)} pages")
except Exception as e:
    print(f"❌ Conversion failed: {e}")
    sys.exit(1)

# Extract text using OCR
print("\n🔍 Running OCR on all pages...")
full_text = ""
page_count = 0

for i, image in enumerate(images):
    page_num = i + 1
    print(f"   Processing page {page_num}/238...", end="\r")
    text = pytesseract.image_to_string(image)
    if text.strip():
        full_text += f"\n\n--- PAGE {page_num} ---\n\n"
        full_text += text
        page_count += 1

print(f"\n✅ Processed {page_count} pages with text")
print(f"📝 Total characters extracted: {len(full_text):,}")

# Save extracted text
output_file = "data/constitution/constitution_full_ocr.txt"
with open(output_file, "w", encoding='utf-8') as f:
    f.write(full_text)
print(f"✅ Saved full text to: {output_file}")

# Split into chunks
print("\n✂️ Splitting into chunks...")
chunks = []
pages = full_text.split("--- PAGE")

for page in pages:
    if page.strip():
        # Get page number and content
        lines = page.strip().split('\n', 1)
        page_header = lines[0] if lines else "Unknown"
        content = lines[1] if len(lines) > 1 else page
        
        # Further split large chunks
        if len(content) > 1000:
            # Split by paragraphs
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                if para.strip() and len(para) > 50:
                    chunks.append(f"[{page_header}] {para.strip()[:800]}")
        else:
            if content.strip() and len(content) > 50:
                chunks.append(f"[{page_header}] {content.strip()[:800]}")

print(f"✅ Created {len(chunks)} chunks")

# Add to ChromaDB
print("\n💾 Adding to ChromaDB...")
chroma_client = chromadb.PersistentClient(path="./chroma_db")
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Delete old collection if exists
collection_name = "constitution_full_ocr"
try:
    chroma_client.delete_collection(collection_name)
    print("✅ Removed existing collection")
except:
    pass

# Create new collection
collection = chroma_client.create_collection(
    name=collection_name,
    embedding_function=embedding_fn
)

# Add chunks in batches
batch_size = 100
total_added = 0

for i in range(0, len(chunks), batch_size):
    batch = chunks[i:i+batch_size]
    batch_ids = [f"const_ocr_{i+j}" for j in range(len(batch))]
    
    collection.add(
        ids=batch_ids,
        documents=batch,
        metadatas=[{"source": "draft_constitution_ocr", "type": "ambedkar_draft"} for _ in batch]
    )
    
    total_added += len(batch)
    print(f"   Added {total_added}/{len(chunks)} chunks")

print(f"\n🎉 SUCCESS! Added {total_added} chunks to ChromaDB!")

# Test queries
print("\n" + "=" * 70)
print("🔍 TESTING WITH SAMPLE QUERIES")
print("=" * 70)

test_queries = [
    "What is the Preamble of the Constitution?",
    "What are Fundamental Rights?",
    "What does Article 9 say about discrimination?",
    "What is the role of the President?",
    "How can the Constitution be amended?",
]

for query in test_queries:
    results = collection.query(query_texts=[query], n_results=1)
    print(f"\n📝 Q: {query}")
    if results['documents'] and results['documents'][0]:
        answer = results['documents'][0][0][:250].replace('\n', ' ')
        print(f"   A: {answer}...")
    else:
        print("   No results found")

print("\n" + "=" * 70)
print("✅ Complete! The full Draft Constitution is now searchable!")
print("   Users can ask questions about Dr. Ambedkar's Draft Constitution")
print("=" * 70)
