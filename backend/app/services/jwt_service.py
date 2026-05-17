import os
from datetime import datetime, timedelta
from jose import jwt

class JWTService:
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this')
        self.algorithm = os.getenv('JWT_ALGORITHM', 'HS256')
        self.expiry_minutes = int(os.getenv('JWT_EXPIRY_MINUTES', '1440'))
    
    def create_token(self, user_id: str, phone_number: str) -> str:
        payload = {
            'sub': user_id,
            'phone': phone_number,
            'exp': datetime.utcnow() + timedelta(minutes=self.expiry_minutes),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.JWTError:
            return None
