import random
import boto3
import hashlib
import binascii
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from app.services.email_service import EmailService

class OTPService:
    def __init__(self):
        self.otp_store = {}
        self.temp_registration_store = {}
        self.otp_expiry_minutes = 10
        self.resend_cooldown_seconds = 30
        
        self.email_service = EmailService()
        self.dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        self.users_table = None
        self._init_tables()
    
    def _init_tables(self):
        try:
            self.users_table = self.dynamodb.create_table(
                TableName='ambedkar_users',
                KeySchema=[{'AttributeName': 'user_id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'user_id', 'AttributeType': 'S'}],
                BillingMode='PAY_PER_REQUEST'
            )
            print("✅ Created users table")
        except self.dynamodb.meta.client.exceptions.ResourceInUseException:
            self.users_table = self.dynamodb.Table('ambedkar_users')
            print("📋 Users table already exists")
    
    def hash_password(self, password: str) -> str:
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return binascii.hexlify(salt).decode() + ':' + binascii.hexlify(key).decode()
    
    def verify_password(self, stored_password: str, provided_password: str) -> bool:
        try:
            salt_hex, key_hex = stored_password.split(':')
            salt = binascii.unhexlify(salt_hex)
            key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
            return binascii.hexlify(key).decode() == key_hex
        except:
            return False
    
    def generate_otp(self) -> str:
        return f"{random.randint(100000, 999999)}"
    
    def send_otp(self, email: str, first_name: str, last_name: str, phone_number: str, pincode: str = "", date_of_birth: str = "") -> bool:
        otp = self.generate_otp()
        now = datetime.now()
        
        self.otp_store[email] = {
            'otp': otp,
            'expires_at': now + timedelta(minutes=self.otp_expiry_minutes),
            'last_sent': now,
            'attempts': 0,
            'verified': False
        }
        
        self.temp_registration_store[email] = {
            'first_name': first_name,
            'last_name': last_name,
            'phone_number': phone_number,
            'pincode': pincode,
            'date_of_birth': date_of_birth
        }
        
        sent = self.email_service.send_otp(email, otp)
        print(f"📧 OTP for {email}: {otp}")
        print(f"📝 Registration data: {first_name} {last_name}, Phone: {phone_number}")
        
        return sent
    
    def resend_otp(self, email: str) -> bool:
        stored = self.otp_store.get(email)
        if not stored:
            return False
        
        now = datetime.now()
        last_sent = stored.get('last_sent')
        
        if last_sent and (now - last_sent).total_seconds() < self.resend_cooldown_seconds:
            return False
        
        new_otp = self.generate_otp()
        self.otp_store[email] = {
            'otp': new_otp,
            'expires_at': now + timedelta(minutes=self.otp_expiry_minutes),
            'last_sent': now,
            'attempts': stored.get('attempts', 0),
            'verified': False
        }
        
        self.email_service.send_otp(email, new_otp)
        print(f"📧 Resent email OTP for {email}: {new_otp}")
        return True
    
    def verify_otp(self, email: str, otp: str) -> bool:
        stored = self.otp_store.get(email)
        if not stored:
            return False
        
        stored['attempts'] = stored.get('attempts', 0) + 1
        
        if stored['otp'] != otp:
            return False
        if datetime.now() > stored['expires_at']:
            return False
        
        return True
    
    def mark_otp_verified(self, email: str):
        if email in self.otp_store:
            self.otp_store[email]['verified'] = True
    
    def is_otp_verified(self, email: str) -> bool:
        stored = self.otp_store.get(email)
        return stored.get('verified', False) if stored else False
    
    def complete_registration(self, email: str, password: str, first_name: str, last_name: str, phone_number: str, pincode: str = "", date_of_birth: str = "") -> Optional[Dict]:
        temp_data = self.temp_registration_store.get(email)
        if not temp_data:
            return None
        
        user_id = f"user_{int(datetime.now().timestamp())}"
        hashed_password = self.hash_password(password)
        
        user = {
            'user_id': user_id,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'phone_number': phone_number,
            'password_hash': hashed_password,
            'pincode': pincode,
            'date_of_birth': date_of_birth,
            'created_at': datetime.now().isoformat(),
            'total_questions': 0
        }
        
        self.users_table.put_item(Item=user)
        print(f"✅ User created: {user_id} ({first_name} {last_name})")
        
        self.email_service.send_welcome_email(email, first_name)
        
        if email in self.temp_registration_store:
            del self.temp_registration_store[email]
        if email in self.otp_store:
            del self.otp_store[email]
        
        return user
    
    def get_user_by_identifier(self, identifier: str) -> Optional[Dict]:
        response = self.users_table.scan(
            FilterExpression='email = :id or phone_number = :id',
            ExpressionAttributeValues={':id': identifier}
        )
        return response['Items'][0] if response['Items'] else None
    
    def authenticate_user(self, identifier: str, password: str) -> Optional[Dict]:
        user = self.get_user_by_identifier(identifier)
        if not user:
            return None
        if self.verify_password(user.get('password_hash', ''), password):
            return user
        return None
