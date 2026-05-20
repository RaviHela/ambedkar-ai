from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class SendOTPRequest(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    pincode: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$')
    date_of_birth: str = Field(..., min_length=10, max_length=10)

class VerifyOTPOnlyRequest(BaseModel):
    email: str
    otp: str

class CompleteRegistrationRequest(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone_number: str
    pincode: str = Field(..., min_length=6, max_length=6)
    date_of_birth: str = Field(..., min_length=10, max_length=10)
    password: str = Field(..., min_length=6, max_length=100)

class LoginRequest(BaseModel):
    identifier: str
    password: str

class ResendOTPRequest(BaseModel):
    email: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    first_name: str
    last_name: str
    email: str
    phone_number: str

class UserInfo(BaseModel):
    user_id: str
    email: str
    phone_number: str
    first_name: str
    last_name: str
    pincode: str
    date_of_birth: str
    created_at: datetime
    total_questions: int = 0
