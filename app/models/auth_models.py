from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SendOTPRequest(BaseModel):
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')

class VerifyOTPRequest(BaseModel):
    phone_number: str
    otp: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserInfo(BaseModel):
    user_id: str
    phone_number: str
    username: Optional[str] = None
    created_at: datetime
    total_questions: int = 0
