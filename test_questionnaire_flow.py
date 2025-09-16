#!/usr/bin/env python3
"""
Test script to verify the questionnaire flow works properly
"""

import requests
import json
import time

def test_questionnaire_flow():
    """Test the complete questionnaire flow"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Questionnaire Flow")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("\n1. Testing server connection...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Server is running (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return False
    
    # Test 2: Test AI chat endpoint
    print("\n2. Testing AI chat endpoint...")
    try:
        chat_data = {
            "message": "Test message for Dr. Grey",
            "conversation_history": [],
            "health_profile": {}
        }
        response = requests.post(f"{base_url}/chat", json=chat_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI chat working: {data.get('response', 'No response')[:100]}...")
        else:
            print(f"❌ AI chat failed: {response.status_code}")
    except Exception as e:
        print(f"❌ AI chat error: {e}")
    
    # Test 3: Test user creation
    print("\n3. Testing user creation...")
    try:
        user_data = {
            "username": f"testuser_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "full_name": "Test User",
            "password": "testpass123"
        }
        response = requests.post(f"{base_url}/users/", json=user_data)
        if response.status_code == 200:
            user = response.json()
            print(f"✅ User created: {user['username']}")
            return user['id']
        else:
            print(f"❌ User creation failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ User creation error: {e}")
        return None

def test_question_flow():
    """Test the question flow logic"""
    print("\n4. Testing question flow logic...")
    
    # Simulate the question flow
    questions = [
        {"id": 1, "question": "How did you find this app?", "followUp": "What drew you to it?"},
        {"id": 2, "question": "Why did you want to use it?", "followUp": "What are you hoping for?"},
        {"id": 3, "question": "What needs to change?", "followUp": "What's really bothering you?"}
    ]
    
    current_question = 0
    responses = ["instagram", "I want to lose weight", "I need more energy"]
    
    for i, response in enumerate(responses):
        print(f"  Question {current_question + 1}: {questions[current_question]['question']}")
        print(f"  User response: {response}")
        print(f"  Follow-up: {questions[current_question]['followUp']}")
        current_question += 1
        print(f"  Moving to question {current_question + 1}")
        print()
    
    print("✅ Question flow logic test completed")

if __name__ == "__main__":
    print("🚀 Starting comprehensive questionnaire testing...")
    
    # Test server and basic functionality
    user_id = test_questionnaire_flow()
    
    # Test question flow logic
    test_question_flow()
    
    print("\n" + "=" * 50)
    print("✅ Testing completed!")
    print("\nTo test the full questionnaire:")
    print("1. Open http://localhost:8000 in your browser")
    print("2. Or open frontend/onboarding.html")
    print("3. Check browser console for debug logs")
