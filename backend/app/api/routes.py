from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = "default"
    language: Optional[str] = "en"
    history: Optional[List[dict]] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[str]
    disclaimer: bool
    session_id: str

class ClearMemoryRequest(BaseModel):
    session_id: str

class ClearMemoryResponse(BaseModel):
    success: bool
    session_id: str

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    try:
        result = chat_service.get_response(
            question=request.question,
            session_id=request.session_id,
            language=request.language,
            chat_history=request.history
        )
        return result
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear-memory", response_model=ClearMemoryResponse)
def clear_memory(request: ClearMemoryRequest):
    """Clear conversation memory for a session"""
    try:
        success = chat_service.clear_memory(request.session_id)
        return ClearMemoryResponse(success=success, session_id=request.session_id)
    except Exception as e:
        print(f"Clear memory error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
def health_check():
    return {"status": "healthy", "persona": "Dr. B.R. Ambedkar"}

@router.get("/sample-questions")
def get_sample_questions(language: str = "en"):
    return {"questions": chat_service.get_sample_questions(language)}

@router.get("/stats")
def get_stats():
    return {
        "persona": "Dr. B.R. Ambedkar", 
        "status": "active",
        "active_sessions": len(chat_service.conversation_memory)
    }
