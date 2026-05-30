#!/usr/bin/env python3
"""
Test script for Dr. B.R. Ambedkar AI - Constitution + BAWS Integration
Run this to test the Q&A system with sample questions
"""

import requests
import json
import sys
import time

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "ravi801227@gmail.com"
TEST_PASSWORD = "132@test132"

def login():
    """Login and get auth token"""
    print("🔐 Logging in...")
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"identifier": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return None
    
    token = response.json().get('access_token')
    print(f"✅ Login successful")
    return token

def ask_question(token, question, language="en"):
    """Ask a question to the AI"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/chat",
        json={"question": question, "language": language},
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        return None
    
    return response.json()

def print_response(response, question):
    """Pretty print the response"""
    print("\n" + "=" * 70)
    print(f"📝 Q: {question}")
    print("=" * 70)
    
    if response and 'response' in response:
        # Print the response (first 800 chars for readability)
        answer = response['response']
        print(f"\n💬 A: {answer[:800]}")
        if len(answer) > 800:
            print("\n... (response truncated, full answer in console)")
        
        # Print sources if available
        if 'sources' in response and response['sources']:
            print("\n📚 Sources:")
            for source in response['sources'][:5]:
                print(f"   - {source}")
    else:
        print("❌ No response received")
    
    print("\n" + "-" * 70)

def main():
    print("=" * 70)
    print("🧪 Dr. B.R. Ambedkar AI - Test Suite")
    print("=" * 70)
    
    # Login
    token = login()
    if not token:
        print("❌ Cannot proceed without login")
        return
    
    # ============================================================
    # SECTION 1: Constitutional Questions
    # ============================================================
    print("\n" + "=" * 70)
    print("📜 SECTION 1: Constitutional Questions")
    print("=" * 70)
    
    constitutional_questions = [
        # Fundamental Rights
        "What does Article 14 of the Constitution say about equality?",
        "What does Article 15 say about discrimination?",
        "What does Article 16 say about equality in employment?",
        "What does Article 19 say about freedom of speech?",
        "What does Article 21 say about protection of life and liberty?",
        "What does Article 32 say about constitutional remedies?",
        
        # Other important articles
        "What does Article 25 say about freedom of religion?",
        "What does Article 29 say about protection of minorities?",
        "What does Article 44 say about uniform civil code?",
        
        # General constitutional topics
        "What is the Preamble of the Constitution?",
        "What are the Directive Principles of State Policy?",
        "What is the structure of the Judiciary under the Constitution?",
        "How is the President of India elected?",
    ]
    
    print("\n📖 Testing Constitutional Questions...\n")
    
    for i, question in enumerate(constitutional_questions[:5], 1):  # Test first 5 to save time
        print(f"\n[{i}/{len(constitutional_questions[:5])}]")
        response = ask_question(token, question, "en")
        if response:
            print_response(response, question)
        time.sleep(1)  # Small delay to avoid rate limiting
    
    # ============================================================
    # SECTION 2: General Questions (BAWS)
    # ============================================================
    print("\n" + "=" * 70)
    print("📚 SECTION 2: General Questions (BAWS Content)")
    print("=" * 70)
    
    general_questions = [
        "What is your view on the caste system?",
        "Why is education important?",
        "What is your message to young people?",
        "What is social justice according to you?",
        "What do you think about women's rights?",
        "What is your opinion on democracy?",
        "Why did you convert to Buddhism?",
    ]
    
    print("\n📖 Testing General Questions...\n")
    
    for i, question in enumerate(general_questions[:4], 1):  # Test first 4
        print(f"\n[{i}/{len(general_questions[:4])}]")
        response = ask_question(token, question, "en")
        if response:
            print_response(response, question)
        time.sleep(1)
    
    # ============================================================
    # SECTION 3: Multi-Language Test
    # ============================================================
    print("\n" + "=" * 70)
    print("🌐 SECTION 3: Multi-Language Support")
    print("=" * 70)
    
    language_questions = [
        {"question": "जाति व्यवस्था पर आपके क्या विचार हैं?", "language": "hi", "name": "Hindi"},
        {"question": "শিক্ষা কেন গুরুত্বপূর্ণ?", "language": "bn", "name": "Bengali"},
        {"question": "What is your view on the caste system?", "language": "en", "name": "English"},
    ]
    
    print("\n📖 Testing Multi-Language Responses...\n")
    
    for test in language_questions:
        print(f"\n--- {test['name']} ({test['language']}) ---")
        response = ask_question(token, test['question'], test['language'])
        if response:
            answer = response['response'][:300]
            print(f"\n💬 Response: {answer}...")
        time.sleep(1)
    
    # ============================================================
    # SUMMARY
    # ============================================================
    print("\n" + "=" * 70)
    print("✅ TEST SUMMARY")
    print("=" * 70)
    print("""
    If you saw responses with:
    - ✅ Constitution article references (Article 14, 15, etc.)
    - ✅ Source citations (BAWS Volume X, Constitution of India)
    - ✅ Dr. Ambedkar's speaking style (first person "I")
    - ✅ Proper multi-language responses
    
    Then the integration is WORKING CORRECTLY!
    
    Issues to look for:
    - ⚠️ "Based on my writings" - should not appear
    - ⚠️ Generic responses without sources
    - ⚠️ Wrong language responses
    """)
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    main()
