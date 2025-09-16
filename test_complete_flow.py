#!/usr/bin/env python3
"""
Test script to automatically complete the onboarding flow with made-up answers
"""

import requests
import json
import time

# Test data - realistic answers for all 8 questions
test_answers = [
    "I found this app through a friend who recommended it",
    "I decided to try it because I want to get healthier and lose some weight",
    "• Lose 15 pounds\n• Have more energy throughout the day\n• Build better eating habits\n• Feel more confident in my body",
    "I think my main obstacles are lack of time to meal prep and not knowing what foods are actually good for me",
    "I currently do light exercise 2-3 times per week - mostly walking and some basic home workouts",
    "I'm 5'10\" tall, weigh 180 pounds, and my energy levels are pretty low especially in the afternoons",
    "In an ideal world, I'd be 165 pounds, have tons of energy, feel strong and confident, and be able to run a 5K without getting winded",
    "My current diet is pretty inconsistent - lots of takeout, processed foods, and I skip breakfast most days. I drink too much coffee and not enough water"
]

def test_onboarding_flow():
    base_url = "http://localhost:8000"
    user_id = 6  # Brendon2
    
    print("🚀 Starting automated onboarding test...")
    
    # Step 1: Start onboarding
    print("\n1. Starting onboarding...")
    response = requests.post(f"{base_url}/start-onboarding/{user_id}")
    if response.status_code != 200:
        print(f"❌ Failed to start onboarding: {response.status_code}")
        return
    
    data = response.json()
    print(f"✅ Started onboarding: {data['message'][:50]}...")
    
    session_data = data['session_data']
    
    # Step 2: Answer all 8 questions
    for i, answer in enumerate(test_answers, 1):
        print(f"\n{i}. Answering question {i}: {answer[:50]}...")
        
        response = requests.post(f"{base_url}/onboarding-chat", json={
            "user_id": user_id,
            "message": answer,
            "session_data": session_data
        })
        
        if response.status_code != 200:
            print(f"❌ Failed to answer question {i}: {response.status_code}")
            return
        
        data = response.json()
        session_data = data['session_data']
        
        print(f"✅ Question {i} answered. Progress: {data['progress']['percentage']:.1f}%")
        
        # Check if complete
        if data.get('is_complete'):
            print(f"\n🎉 Onboarding completed!")
            print(f"📊 Final progress: {data['progress']['percentage']:.1f}%")
            print(f"🤖 AI Response: {data['response'][:100]}...")
            break
        
        time.sleep(0.5)  # Small delay between questions
    
    # Step 3: Test dashboard access
    print(f"\n3. Testing dashboard access...")
    
    # Simulate what the frontend does - set user in localStorage equivalent
    user_data = {
        "id": user_id,
        "username": "Brendon2", 
        "email": "brendon2@example.com"
    }
    
    # Test if we can load user data (what dashboard does)
    try:
        profile_response = requests.get(f"{base_url}/users/{user_id}/health-profile")
        if profile_response.status_code == 200:
            profile = profile_response.json()
            print(f"✅ Health profile loaded: {profile}")
        else:
            print(f"⚠️  No health profile found (status: {profile_response.status_code})")
    except Exception as e:
        print(f"⚠️  Error loading profile: {e}")
    
    print(f"\n✅ Test completed! User {user_id} should now be able to access the dashboard.")
    print(f"🔗 Open: frontend/dashboard.html")

if __name__ == "__main__":
    test_onboarding_flow()