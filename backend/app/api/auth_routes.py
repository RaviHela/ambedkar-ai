from fastapi import APIRouter, HTTPException, Request
from datetime import datetime
from app.models.auth_models import (
    SendOTPRequest, VerifyOTPOnlyRequest, CompleteRegistrationRequest, 
    LoginRequest, ResendOTPRequest, TokenResponse, UserInfo
)
from app.services.otp_service import OTPService
from app.services.jwt_service import JWTService
from app.services.geolocation_service import GeolocationService

router = APIRouter(prefix="/auth", tags=["Authentication"])
otp_service = OTPService()
jwt_service = JWTService()
geo_service = GeolocationService()

@router.post("/send-otp")
async def send_otp(request: SendOTPRequest, req: Request):
    existing_user = otp_service.get_user_by_identifier(request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    client_ip = geo_service.get_client_ip(req)
    location = await geo_service.get_location_from_ip(client_ip)
    detected_pincode = location.get('pincode', '') if location else ''
    final_pincode = request.pincode or detected_pincode
    
    success = otp_service.send_otp(
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        phone_number=request.phone_number,
        pincode=final_pincode
    )
    
    if success:
        return {
            "message": "OTP sent successfully",
            "email": request.email
        }
    raise HTTPException(status_code=500, detail="Failed to send OTP")

@router.post("/resend-otp")
async def resend_otp(request: ResendOTPRequest):
    success = otp_service.resend_otp(request.email)
    if success:
        return {"message": "OTP resent successfully"}
    raise HTTPException(status_code=429, detail="Please wait before requesting another OTP")

@router.post("/verify-otp-only")
async def verify_otp_only(request: VerifyOTPOnlyRequest):
    is_valid = otp_service.verify_otp(request.email, request.otp)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    # Mark OTP as verified but don't delete registration data
    otp_service.mark_otp_verified(request.email)
    
    return {"message": "OTP verified successfully"}

@router.post("/complete-registration")
async def complete_registration(request: CompleteRegistrationRequest):
    # Check if OTP was verified
    if not otp_service.is_otp_verified(request.email):
        raise HTTPException(status_code=400, detail="OTP not verified. Please verify OTP first.")
    
    # Complete registration with password
    user = otp_service.complete_registration(
        email=request.email,
        password=request.password,
        first_name=request.first_name,
        last_name=request.last_name,
        phone_number=request.phone_number,
        pincode=request.pincode or ''
    )
    
    if not user:
        raise HTTPException(status_code=400, detail="Registration failed")
    
    token = jwt_service.create_token(user['user_id'], request.email)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": jwt_service.expiry_minutes * 60,
        "user_id": user['user_id'],
        "first_name": user['first_name'],
        "last_name": user['last_name'],
        "email": user['email'],
        "phone_number": user['phone_number']
    }

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    user = otp_service.authenticate_user(request.identifier, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email/phone or password")
    
    token = jwt_service.create_token(user['user_id'], user['email'])
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": jwt_service.expiry_minutes * 60,
        "user_id": user['user_id'],
        "first_name": user.get('first_name', ''),
        "last_name": user.get('last_name', ''),
        "email": user['email'],
        "phone_number": user.get('phone_number', '')
    }

@router.get("/me")
async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = auth_header.split(" ")[1]
    payload = jwt_service.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = otp_service.users_table.get_item(Key={'user_id': payload['sub']}).get('Item')
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user['user_id'],
        "email": user.get('email', ''),
        "phone_number": user.get('phone_number', ''),
        "first_name": user.get('first_name', ''),
        "last_name": user.get('last_name', ''),
        "pincode": user.get('pincode', ''),
        "created_at": datetime.fromisoformat(user['created_at']),
        "total_questions": 0
    }
