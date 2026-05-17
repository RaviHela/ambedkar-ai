import random
import boto3
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

class OTPService:
    def __init__(self):
        self.otp_store = {}
        self.otp_expiry_minutes = 10
        
        self.dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'ap-south-1'))
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
    
    def generate_otp(self) -> str:
        return f"{random.randint(100000, 999999)}"
    
    def send_otp(self, phone_number: str) -> bool:
        otp = self.generate_otp()
        self.otp_store[phone_number] = {
            'otp': otp,
            'expires_at': datetime.now() + timedelta(minutes=self.otp_expiry_minutes)
        }
        
        # For development, print OTP to console
        print(f"📱 OTP for {phone_number}: {otp}")
        
        # TODO: Integrate Twilio or AWS SNS for actual SMS
        return True
    
    def verify_otp(self, phone_number: str, otp: str) -> bool:
        stored = self.otp_store.get(phone_number)
        if not stored:
            return False
        if stored['otp'] != otp:
            return False
        if datetime.now() > stored['expires_at']:
            return False
        # Clean up used OTP
        del self.otp_store[phone_number]
        return True
    
    def get_or_create_user(self, phone_number: str) -> Dict:
        # Check if user exists
        response = self.users_table.scan(
            FilterExpression='phone_number = :phone',
            ExpressionAttributeValues={':phone': phone_number}
        )
        
        if response['Items']:
            return response['Items'][0]
        
        # Create new user
        user_id = f"user_{int(datetime.now().timestamp())}"
        user = {
            'user_id': user_id,
            'phone_number': phone_number,
            'created_at': datetime.now().isoformat(),
            'total_questions': 0
        }
        self.users_table.put_item(Item=user)
        print(f"✅ New user created: {user_id}")
        return user
