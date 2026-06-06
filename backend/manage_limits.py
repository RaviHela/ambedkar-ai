#!/usr/bin/env python3
"""
Rate Limit Management Script for Development & Testing
Usage: python3 manage_limits.py [command] [user_email]

Commands:
  status      - Show current limits for a user
  reset       - Reset daily counter for a user
  lift        - Temporarily lift all limits for a user
  restore     - Restore normal limits
  set         - Set custom daily limit
  help        - Show this help
  test        - Simulate reaching limit
  clear       - Clear all user data

Examples:
  python3 manage_limits.py status ravi801227@gmail.com
  python3 manage_limits.py reset ravi801227@gmail.com
  python3 manage_limits.py lift ravi801227@gmail.com
  python3 manage_limits.py set ravi801227@gmail.com 20
  python3 manage_limits.py test ravi801227@gmail.com
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, '/home/ubuntu/ambedkar-ai/backend')

from app.services.rate_limiter import rate_limiter
from app.services.otp_service import OTPService

otp = OTPService()

def get_user_id(email):
    """Get user_id from email"""
    user = otp.get_user_by_identifier(email)
    if user:
        return user['user_id']
    return None

def show_status(user_id, email):
    """Show current rate limit status"""
    limits = rate_limiter.get_remaining_limits(user_id)
    print("\n" + "=" * 50)
    print(f"📊 Rate Limit Status for: {email}")
    print("=" * 50)
    print(f"  Daily Limit:     {limits['daily_limit']} questions/day")
    print(f"  Used Today:      {limits['daily_used']}")
    print(f"  Remaining Today: {limits['daily_remaining']}")
    print(f"  Per-minute Limit: {limits['per_minute_limit']} questions/minute")
    print(f"  Premium User:    {limits['is_premium']}")
    print("=" * 50)

def reset_counter(user_id, email):
    """Reset daily counter"""
    rate_limiter.user_daily[user_id] = 0
    rate_limiter.user_daily_date[user_id] = "2000-01-01"
    print(f"✅ Daily counter reset for {email}")
    show_status(user_id, email)

def lift_limits(user_id, email):
    """Temporarily lift all limits (set to very high)"""
    rate_limiter.USER_PER_DAY = 1000
    rate_limiter.USER_PER_MINUTE = 100
    rate_limiter.user_daily[user_id] = 0
    rate_limiter.user_daily_date[user_id] = "2000-01-01"
    print(f"🚀 LIMITS LIFTED for {email}")
    print(f"   Daily limit: {rate_limiter.USER_PER_DAY} questions")
    print(f"   Per-minute: {rate_limiter.USER_PER_MINUTE} questions")
    print("\n⚠️ Remember to restore limits after testing:")
    print("   python3 manage_limits.py restore")

def restore_limits(user_id, email):
    """Restore normal limits"""
    rate_limiter.USER_PER_DAY = 5
    rate_limiter.USER_PER_MINUTE = 2
    rate_limiter.user_daily[user_id] = 0
    rate_limiter.user_daily_date[user_id] = "2000-01-01"
    print(f"✅ Normal limits restored for {email}")
    print(f"   Daily limit: {rate_limiter.USER_PER_DAY} questions")
    print(f"   Per-minute: {rate_limiter.USER_PER_MINUTE} questions")
    show_status(user_id, email)

def set_custom_limit(user_id, email, limit):
    """Set custom daily limit"""
    rate_limiter.USER_PER_DAY = limit
    rate_limiter.user_daily[user_id] = 0
    rate_limiter.user_daily_date[user_id] = "2000-01-01"
    print(f"✅ Daily limit set to {limit} questions for {email}")
    show_status(user_id, email)

def simulate_limit(user_id, email):
    """Simulate reaching the daily limit"""
    limit = rate_limiter.USER_PER_DAY
    rate_limiter.user_daily[user_id] = limit
    rate_limiter.user_daily_date[user_id] = "2026-06-06"
    print(f"⚠️ Simulated: User has reached daily limit of {limit}")
    show_status(user_id, email)

def clear_all_data():
    """Clear all rate limit data (use with caution)"""
    confirm = input("⚠️ This will clear ALL rate limit data for ALL users. Continue? (yes/no): ")
    if confirm.lower() == 'yes':
        rate_limiter.user_daily.clear()
        rate_limiter.user_daily_date.clear()
        rate_limiter.user_requests.clear()
        rate_limiter.ip_requests.clear()
        print("✅ All rate limit data cleared")
    else:
        print("❌ Operation cancelled")

def print_help():
    print(__doc__)

def main():
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'help':
        print_help()
        return
    
    if command == 'clear':
        clear_all_data()
        return
    
    if len(sys.argv) < 3 and command not in ['restore', 'clear']:
        print("❌ Please provide email address")
        print(f"Usage: python3 manage_limits.py {command} user@example.com")
        return
    
    email = sys.argv[2] if len(sys.argv) > 2 else None
    
    if command != 'clear' and command != 'restore':
        user_id = get_user_id(email)
        if not user_id:
            print(f"❌ User not found: {email}")
            return
    
    if command == 'status':
        show_status(user_id, email)
    elif command == 'reset':
        reset_counter(user_id, email)
    elif command == 'lift':
        lift_limits(user_id, email)
    elif command == 'restore':
        restore_limits(None, "all users")
    elif command == 'set':
        if len(sys.argv) < 4:
            print("❌ Please provide limit value")
            print("Usage: python3 manage_limits.py set user@example.com 20")
            return
        limit = int(sys.argv[3])
        set_custom_limit(user_id, email, limit)
    elif command == 'test':
        simulate_limit(user_id, email)
    else:
        print(f"❌ Unknown command: {command}")
        print_help()

if __name__ == "__main__":
    main()
