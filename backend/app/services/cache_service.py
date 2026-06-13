"""
Response Caching Service for Dr. B.R. Ambedkar AI
Stores common Q&A pairs to reduce Claude API calls and improve response time
"""

import hashlib
import json
from datetime import datetime, timedelta
from collections import OrderedDict

class ResponseCache:
    def __init__(self, max_size=1000, ttl_hours=24):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)
    
    def _generate_key(self, question: str, language: str) -> str:
        """Generate a unique cache key from question and language"""
        content = f"{question.lower().strip()}:{language}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, question: str, language: str) -> dict:
        """Get cached response if exists and not expired"""
        key = self._generate_key(question, language)
        
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() - entry['timestamp'] < self.ttl:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                print(f"✅ Cache HIT for: {question[:50]}...")
                return entry['response']
            else:
                # Remove expired entry
                del self.cache[key]
                print(f"⏰ Cache expired for: {question[:50]}...")
        
        print(f"📝 Cache MISS for: {question[:50]}...")
        return None
    
    def set(self, question: str, language: str, response: dict):
        """Store response in cache"""
        key = self._generate_key(question, language)
        
        # Remove oldest if at capacity
        if len(self.cache) >= self.max_size:
            oldest = next(iter(self.cache))
            del self.cache[oldest]
            print(f"🗑️ Removed oldest cache entry")
        
        self.cache[key] = {
            'response': response,
            'timestamp': datetime.now()
        }
        print(f"💾 Cached response for: {question[:50]}...")
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        print("🧹 Cache cleared")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'ttl_hours': self.ttl.total_seconds() / 3600
        }

# Singleton instance
response_cache = ResponseCache()
