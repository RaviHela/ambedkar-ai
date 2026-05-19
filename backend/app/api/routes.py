from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from app.services.chat_service import ChatService
from app.services.jwt_service import JWTService
from app.api.auth_routes import router as auth_router

router = APIRouter()
chat_service = ChatService()
jwt_service = JWTService()
security = HTTPBearer()

router.include_router(auth_router)

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

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = jwt_service.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    user: dict = Depends(get_current_user)
):
    user_id = user.get('sub')
    result = await chat_service.get_response(
        question=request.question,
        user_id=user_id,
        session_id=request.session_id,
        language=request.language,
        chat_history=request.history
    )
    return result

@router.get("/health")
def health_check():
    return {"status": "healthy", "persona": "Dr. B.R. Ambedkar"}

@router.get("/sample-questions")
def get_sample_questions(language: str = "en"):
    return {"questions": chat_service.get_sample_questions(language)}
