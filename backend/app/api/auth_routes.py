from fastapi import APIRouter, HTTPException, Request
from datetime import datetime
from app.models.auth_models import SendOTPRequest, VerifyOTPRequest, TokenResponse, UserInfo
from app.services.otp_service import OTPService
from app.services.jwt_service import JWTService

router = APIRouter(prefix="/auth", tags=["Authentication"])
otp_service = OTPService()
jwt_service = JWTService()

@router.post("/send-otp")
async def send_otp(request: SendOTPRequest):
    """Send OTP to phone number"""
    success = otp_service.send_otp(request.phone_number)
    if success:
        return {"message": "OTP sent successfully", "phone": request.phone_number}
    raise HTTPException(status_code=500, detail="Failed to send OTP")

@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(request: VerifyOTPRequest):
    """Verify OTP and return JWT token"""
    is_valid = otp_service.verify_otp(request.phone_number, request.otp)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    user = otp_service.get_or_create_user(request.phone_number)
    token = jwt_service.create_token(user['user_id'], request.phone_number)
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=jwt_service.expiry_minutes * 60
    )

@router.get("/me", response_model=UserInfo)
async def get_current_user(request: Request):
    """Get current authenticated user info"""
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
    
    # Get total questions from questions table
    questions_table = otp_service.dynamodb.Table('ambedkar_questions')
    questions = questions_table.query(
        KeyConditionExpression='user_id = :uid',
        ExpressionAttributeValues={':uid': user['user_id']}
    ).get('Items', [])
    
    return UserInfo(
        user_id=user['user_id'],
        phone_number=user['phone_number'],
        created_at=datetime.fromisoformat(user['created_at']),
        total_questions=len(questions)
    )
