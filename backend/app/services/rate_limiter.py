"""
Rate Limiter Service for Dr. B.R. Ambedkar AI
Prevents abuse and excessive API usage
"""

from datetime import datetime, timedelta
from collections import defaultdict
import threading

class RateLimiter:
    def __init__(self):
        self.user_requests = defaultdict(list)
        self.ip_requests = defaultdict(list)
        self.user_daily = defaultdict(int)
        self.user_daily_date = defaultdict(str)
        self.lock = threading.Lock()
        
        # Default limits - FREE TIER
        self.USER_PER_MINUTE = 2      # Max 2 requests per user per minute
        self.USER_PER_DAY = 5         # Max 5 requests per user per day (FREE)
        self.IP_PER_MINUTE = 10       # Max 10 requests per IP per minute
        self.MIN_QUESTION_LEN = 3
        self.MAX_QUESTION_LEN = 500
        
    def can_make_request(self, user_id: str) -> tuple:
        """Check if user can make a request (checks both daily and minute limits)"""
        with self.lock:
            today = datetime.now().date().isoformat()
            
            # Reset daily counter for new day
            if self.user_daily_date.get(user_id) != today:
                self.user_daily[user_id] = 0
                self.user_daily_date[user_id] = today
                print(f"📊 Reset daily counter for user {user_id[:8]}...")
            
            # Check daily limit
            if self.user_daily[user_id] >= self.USER_PER_DAY:
                return False, f"Daily limit of {self.USER_PER_DAY} questions reached. Please try again tomorrow."
            
            # Check minute limit
            now = datetime.now()
            cutoff = now - timedelta(minutes=1)
            self.user_requests[user_id] = [t for t in self.user_requests[user_id] if t > cutoff]
            
            if len(self.user_requests[user_id]) >= self.USER_PER_MINUTE:
                return False, f"Rate limit exceeded. Please wait a moment."
            
            # All checks passed - increment counters
            self.user_requests[user_id].append(now)
            self.user_daily[user_id] += 1
            
            remaining = self.USER_PER_DAY - self.user_daily[user_id]
            print(f"📊 User {user_id[:8]}... used {self.user_daily[user_id]}/{self.USER_PER_DAY}. Remaining: {remaining}")
            
            return True, f"OK (Remaining today: {remaining})"
    
    def check_ip_limit(self, ip: str) -> tuple:
        """Check if IP has exceeded per-minute limit"""
        with self.lock:
            now = datetime.now()
            cutoff = now - timedelta(minutes=1)
            
            self.ip_requests[ip] = [t for t in self.ip_requests[ip] if t > cutoff]
            
            if len(self.ip_requests[ip]) >= self.IP_PER_MINUTE:
                return False, f"Too many requests from this IP. Please wait a moment."
            
            self.ip_requests[ip].append(now)
            return True, "OK"
    
    def validate_question(self, question: str) -> tuple:
        """Validate question length and content"""
        if not question or len(question.strip()) < self.MIN_QUESTION_LEN:
            return False, f"Question too short (minimum {self.MIN_QUESTION_LEN} characters)"
        
        if len(question) > self.MAX_QUESTION_LEN:
            return False, f"Question too long (maximum {self.MAX_QUESTION_LEN} characters)"
        
        import re
        if re.search(r'(.)\1{15,}', question):
            return False, "Question contains repetitive characters"
        
        return True, "OK"
    
    def get_remaining_limits(self, user_id: str) -> dict:
        """Get remaining limits for user"""
        today = datetime.now().date().isoformat()
        
        if self.user_daily_date.get(user_id) != today:
            used = 0
            remaining = self.USER_PER_DAY
        else:
            used = self.user_daily.get(user_id, 0)
            remaining = max(0, self.USER_PER_DAY - used)
        
        return {
            "daily_limit": self.USER_PER_DAY,
            "daily_used": used,
            "daily_remaining": remaining,
            "per_minute_limit": self.USER_PER_MINUTE,
            "is_premium": False
        }

# Singleton instance
rate_limiter = RateLimiter()
