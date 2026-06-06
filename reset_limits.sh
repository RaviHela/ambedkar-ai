#!/bin/bash
cd /home/ubuntu/ambedkar-ai/backend
python3 -c "
from app.services.rate_limiter import rate_limiter
from app.services.otp_service import OTPService
otp = OTPService()
user = otp.get_user_by_identifier('ravi801227@gmail.com')
if user:
    rate_limiter.user_daily[user['user_id']] = 0
    rate_limiter.user_daily_date[user['user_id']] = '2000-01-01'
    print('✅ Rate limits reset for ravi801227@gmail.com')
else:
    print('❌ User not found')
"
