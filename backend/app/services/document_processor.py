import os
from typing import List, Dict
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF file"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            print(f"Error reading {pdf_path}: {e}")
            return ""
    
    def process_documents(self, data_dir: str) -> List[Document]:
        """Process all PDFs in a directory and return LangChain Documents"""
        documents = []
        
        for filename in os.listdir(data_dir):
            if filename.endswith('.pdf'):
                file_path = os.path.join(data_dir, filename)
                print(f"Processing: {filename}")
                
                text = self.extract_text_from_pdf(file_path)
                if text:
                    metadata = {
                        "source": filename,
                        "author": "Dr. B.R. Ambedkar",
                        "type": "book" if "volume" in filename.lower() else "speech"
                    }
                    
                    chunks = self.text_splitter.split_text(text)
                    
                    for i, chunk in enumerate(chunks):
                        doc = Document(
                            page_content=chunk,
                            metadata={**metadata, "chunk_id": i}
                        )
                        documents.append(doc)
                    print(f"  -> Created {len(chunks)} chunks from {filename}")
        
        print(f"\n✅ Total: {len(documents)} document chunks created")
        return documents