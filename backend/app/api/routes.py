from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from app.services.chat_service import ChatService
from app.services.jwt_service import JWTService
from app.services.rate_limiter import rate_limiter
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
    user: dict = Depends(get_current_user),
    req: Request = None
):
    user_id = user.get('sub')
    client_ip = req.client.host if req else "unknown"
    
    # 1. Validate question
    is_valid, error_msg = rate_limiter.validate_question(request.question)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # 2. Check IP rate limit
    ip_allowed, ip_msg = rate_limiter.check_ip_limit(client_ip)
    if not ip_allowed:
        raise HTTPException(status_code=429, detail=ip_msg)
    
    # 3. Check user limits (this also increments counters)
    user_allowed, user_msg = rate_limiter.can_make_request(user_id)
    if not user_allowed:
        raise HTTPException(status_code=429, detail=user_msg)
    
    # 4. Get answer from chat service
    result = await chat_service.get_response(
        question=request.question,
        user_id=user_id,
        session_id=request.session_id,
        language=request.language,
        chat_history=request.history
    )
    
    # 5. Add rate limit info to response
    limits = rate_limiter.get_remaining_limits(user_id)
    result['rate_limits'] = limits
    
    return result

@router.get("/health")
def health_check():
    return {"status": "healthy", "persona": "Dr. B.R. Ambedkar"}

@router.get("/sample-questions")
def get_sample_questions(language: str = "en"):
    return {"questions": chat_service.get_sample_questions(language)}

@router.get("/rate-limits")
async def get_rate_limits(user: dict = Depends(get_current_user)):
    user_id = user.get('sub')
    limits = rate_limiter.get_remaining_limits(user_id)
    return limits
