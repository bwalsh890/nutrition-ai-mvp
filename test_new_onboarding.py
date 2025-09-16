#!/usr/bin/env python3
import requests
import time

BASE_URL = "http://localhost:8000"

def test_new_onboarding():
    print("Testing new onboarding flow...")
    
    # Step 1: Start onboarding
    print("\n1. Starting onboarding...")
    response = requests.post(f"{BASE_URL}/start-onboarding/1")
    print(f"Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return
    
    data = response.json()
    print(f"Message: {data['message']}")
    print(f"Question: {data['question']}")
    
    session_data = data['session_data']
    
    # Step 2: Answer first question
    print("\n2. Answering first question...")
    response = requests.post(f"{BASE_URL}/onboarding-chat", json={
        "user_id": 1,
        "message": "I'm feeling tired all the time and want to get my energy back",
        "session_data": session_data
    })
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"AI Response: {data['response']}")
        print(f"Progress: {data['progress']}")
        print(f"Is Complete: {data['is_complete']}")
        session_data = data['session_data']
    else:
        print(f"Error: {response.text}")
        return
    
    # Step 3: Answer follow-up question
    print("\n3. Answering follow-up question...")
    response = requests.post(f"{BASE_URL}/onboarding-chat", json={
        "user_id": 1,
        "message": "8",
        "session_data": session_data
    })
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"AI Response: {data['response']}")
        print(f"Progress: {data['progress']}")
        print(f"Is Complete: {data['is_complete']}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_new_onboarding()
