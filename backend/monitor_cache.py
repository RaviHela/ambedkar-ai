#!/usr/bin/env python3
"""
Cache Monitoring Script for Dr. B.R. Ambedkar AI
Shows cache hit rate and statistics
"""

import sys
import time
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, '/home/ubuntu/ambedkar-ai/backend')

from app.services.cache_service import response_cache

def show_stats():
    stats = response_cache.get_stats()
    print("\n" + "=" * 40)
    print("📊 CACHE STATISTICS")
    print("=" * 40)
    print(f"  Cache size:     {stats['size']}/{stats['max_size']}")
    print(f"  TTL:            {stats['ttl_hours']} hours")
    print("=" * 40)

def monitor_cache():
    print("Cache Monitor - Press Ctrl+C to exit")
    print("=" * 40)
    
    while True:
        show_stats()
        time.sleep(30)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        show_stats()
    else:
        monitor_cache()
