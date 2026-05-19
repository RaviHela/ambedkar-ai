import boto3
import os
from typing import Optional

class EmailService:
    def __init__(self):
        # Use SES in sandbox mode (for testing)
        # You'll need to verify your email address first
        self.ses = boto3.client('ses', region_name='ap-south-1')
        self.source_email = "noreply@ambedkar-ai.com"  # Update this after verification
    
    def send_otp(self, email: str, otp: str) -> bool:
        """Send OTP via email using AWS SES"""
        try:
            subject = "Dr. B.R. Ambedkar AI - Email Verification"
            body = f"""
            <html>
            <body>
                <h2>Dr. B.R. Ambedkar AI - Email Verification</h2>
                <p>Your verification code is: <strong>{otp}</strong></p>
                <p>This code is valid for 10 minutes.</p>
                <p>If you did not request this, please ignore this email.</p>
                <br>
                <p>Thank you,<br>Dr. B.R. Ambedkar AI Team</p>
            </body>
            </html>
            """
            
            # For sandbox mode, you need to verify both sender and recipient emails
            # For now, just print the OTP (SES will work after verification)
            print(f"📧 Would send email to {email} with OTP: {otp}")
            
            # Uncomment when SES is configured:
            # response = self.ses.send_email(
            #     Source=self.source_email,
            #     Destination={'ToAddresses': [email]},
            #     Message={
            #         'Subject': {'Data': subject},
            #         'Body': {'Html': {'Data': body}}
            #     }
            # )
            # return True
            
            return True
        except Exception as e:
            print(f"❌ Email error: {e}")
            return False
