import boto3
from botocore.exceptions import ClientError

class EmailService:
    def __init__(self):
        self.ses_client = boto3.client('ses', region_name='ap-south-1')
        self.sender_email = 'admin@ambedkar-ai.com'
        self.sender_name = 'Dr. B.R. Ambedkar AI'
        self.image_url = 'https://ambedkar-ai.com/static/ambedkar-profile.jpg'
        
    def send_otp(self, to_email: str, otp: str) -> bool:
        """Send OTP via AWS SES with Dr. Ambedkar's image"""
        subject = "Your OTP for Dr. B.R. Ambedkar AI"
        
        formatted_from = f"{self.sender_name} <{self.sender_email}>"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: #ffffff;
                }}
                .header {{
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .profile-image {{
                    width: 80px;
                    height: 80px;
                    border-radius: 50%;
                    border: 3px solid #ffd700;
                    margin-bottom: 15px;
                }}
                .content {{
                    padding: 30px;
                    background: #f9f9f9;
                }}
                .otp-code {{
                    font-size: 48px;
                    font-weight: bold;
                    color: #2a5298;
                    text-align: center;
                    padding: 30px;
                    background: white;
                    border-radius: 10px;
                    margin: 20px 0;
                    letter-spacing: 5px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    font-size: 12px;
                    color: #666;
                    background: #f0f0f0;
                    border-top: 1px solid #ddd;
                }}
                .jai-bhim {{
                    color: #2a5298;
                    font-weight: bold;
                    font-size: 18px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="{self.image_url}" alt="Dr. B.R. Ambedkar" class="profile-image">
                    <h1>Dr. B.R. Ambedkar AI</h1>
                    <p>Based on his writings, speeches, and parliamentary debates</p>
                </div>
                <div class="content">
                    <h2>Your One-Time Password (OTP)</h2>
                    <p>Hello,</p>
                    <p>You requested to verify your email address for Dr. B.R. Ambedkar AI platform.</p>
                    <div class="otp-code">{otp}</div>
                    <p>This OTP is valid for <strong>10 minutes</strong>.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                    <div class="jai-bhim">Jai Bhim! 🙏</div>
                </div>
                <div class="footer">
                    <p>Dr. B.R. Ambedkar AI Platform</p>
                    <p>Preserving and promoting the thoughts of Babasaheb</p>
                    <p><small>This is an automated message, please do not reply.</small></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Dr. B.R. Ambedkar AI - OTP Verification
        
        Your OTP is: {otp}
        
        This OTP is valid for 10 minutes.
        
        If you didn't request this, please ignore this email.
        
        Jai Bhim!
        """
        
        try:
            response = self.ses_client.send_email(
                Source=formatted_from,
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {
                        'Text': {'Data': text_body, 'Charset': 'UTF-8'},
                        'Html': {'Data': html_body, 'Charset': 'UTF-8'}
                    }
                }
            )
            print(f"✅ OTP email sent from {self.sender_email} to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Failed to send OTP email: {e}")
            return False
    
    def send_welcome_email(self, to_email: str, first_name: str) -> bool:
        """Send welcome email with Dr. Ambedkar's image"""
        subject = f"Welcome to Dr. B.R. Ambedkar AI, {first_name}!"
        
        formatted_from = f"{self.sender_name} <{self.sender_email}>"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: #ffffff;
                }}
                .header {{
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .profile-image {{
                    width: 80px;
                    height: 80px;
                    border-radius: 50%;
                    border: 3px solid #ffd700;
                    margin-bottom: 15px;
                }}
                .content {{
                    padding: 30px;
                    background: #f9f9f9;
                }}
                .button {{
                    display: inline-block;
                    background: #2a5298;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 25px;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .quote {{
                    font-style: italic;
                    color: #555;
                    padding: 20px;
                    background: #fff3cd;
                    border-left: 4px solid #ffd700;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    font-size: 12px;
                    color: #666;
                    background: #f0f0f0;
                    border-top: 1px solid #ddd;
                }}
                .jai-bhim {{
                    color: #2a5298;
                    font-weight: bold;
                    font-size: 18px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="{self.image_url}" alt="Dr. B.R. Ambedkar" class="profile-image">
                    <h1>Dr. B.R. Ambedkar AI</h1>
                    <p>Based on his writings, speeches, and parliamentary debates</p>
                </div>
                <div class="content">
                    <h2>Welcome, {first_name}! 🎉</h2>
                    <p>Thank you for joining the Dr. B.R. Ambedkar AI platform.</p>
                    <div class="quote">
                        "Cultivation of mind should be the ultimate aim of human existence."<br>
                        - Dr. B.R. Ambedkar
                    </div>
                    <p>You can now:</p>
                    <ul>
                        <li>Ask questions based on Dr. Ambedkar's writings</li>
                        <li>Get AI-powered responses in multiple languages</li>
                        <li>Learn about social justice, equality, and democracy</li>
                        <li>Explore his parliamentary debates and speeches</li>
                    </ul>
                    <div style="text-align: center;">
                        <a href="https://ambedkar-ai.com" class="button">Start Exploring</a>
                    </div>
                    <div class="jai-bhim">Jai Bhim! 🙏</div>
                </div>
                <div class="footer">
                    <p>Dr. B.R. Ambedkar AI Platform</p>
                    <p>"I measure the progress of a community by the degree of progress which women have achieved."</p>
                    <p><small>Questions? Visit our website or contact support.</small></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        try:
            response = self.ses_client.send_email(
                Source=formatted_from,
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {'Html': {'Data': html_body, 'Charset': 'UTF-8'}}
                }
            )
            print(f"✅ Welcome email sent to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Failed to send welcome email: {e}")
            return False
    
    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """Send password reset email with Dr. Ambedkar's image"""
        reset_link = f"https://ambedkar-ai.com/reset-password?token={reset_token}"
        
        formatted_from = f"{self.sender_name} <{self.sender_email}>"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: #ffffff;
                }}
                .header {{
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .profile-image {{
                    width: 80px;
                    height: 80px;
                    border-radius: 50%;
                    border: 3px solid #ffd700;
                    margin-bottom: 15px;
                }}
                .content {{
                    padding: 30px;
                    background: #f9f9f9;
                }}
                .button {{
                    display: inline-block;
                    background: #2a5298;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 25px;
                    margin: 20px 0;
                }}
                .warning {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    font-size: 12px;
                    color: #666;
                    background: #f0f0f0;
                    border-top: 1px solid #ddd;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="{self.image_url}" alt="Dr. B.R. Ambedkar" class="profile-image">
                    <h1>Dr. B.R. Ambedkar AI</h1>
                </div>
                <div class="content">
                    <h2>Password Reset Request</h2>
                    <p>We received a request to reset your password for Dr. B.R. Ambedkar AI.</p>
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </div>
                    <div class="warning">
                        <p>⚠️ This link will expire in <strong>1 hour</strong>.</p>
                        <p>If you didn't request this, please ignore this email.</p>
                    </div>
                    <p>For security, do not share this link with anyone.</p>
                </div>
                <div class="footer">
                    <p>Dr. B.R. Ambedkar AI Platform</p>
                    <p>Jai Bhim! 🙏</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        try:
            response = self.ses_client.send_email(
                Source=formatted_from,
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {'Html': {'Data': html_body, 'Charset': 'UTF-8'}}
                }
            )
            print(f"✅ Password reset email sent to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Failed to send password reset email: {e}")
            return False
