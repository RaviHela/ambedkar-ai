import os
from dotenv import load_dotenv

# Load .env file from current directory
load_dotenv()

class Config:
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    USE_LOCAL_EMBEDDINGS = os.getenv("USE_LOCAL_EMBEDDINGS", "true").lower() == "true"
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    @classmethod
    def validate(cls):
        if not cls.ANTHROPIC_API_KEY:
            print("⚠️  WARNING: ANTHROPIC_API_KEY is not set in .env file")
            print("   The app will run in fallback mode without Claude AI")
            return False
        return True

# Print status
if Config.ANTHROPIC_API_KEY:
    print(f"✅ Claude API key loaded (starts with: {Config.ANTHROPIC_API_KEY[:15]}...)")
else:
    print("⚠️  No Claude API key found. Please add ANTHROPIC_API_KEY to .env file")
