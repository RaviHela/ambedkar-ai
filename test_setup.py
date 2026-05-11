import sys
import os

# Add the current directory to Python's path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Also add the backend directory if needed
backend_dir = os.path.join(current_dir, 'backend')
if os.path.exists(backend_dir):
    sys.path.insert(0, backend_dir)

print(f"Python path includes: {current_dir}")
print(f"Looking for app folder in: {current_dir}")
print(f"app folder exists: {os.path.exists(os.path.join(current_dir, 'app'))}")

try:
    from app.services.document_processor import DocumentProcessor
    print("✅ DocumentProcessor imported successfully!")
    print("Your document processor is ready to process PDF files.")
    print("\nNext step: Add PDF files to the 'data/raw/' folder")
except Exception as e:
    print(f"Error: {e}")
    print("\nCurrent directory contents:")
    for item in os.listdir(current_dir):
        print(f"  - {item}")