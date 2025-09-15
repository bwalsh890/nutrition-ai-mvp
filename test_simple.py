#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json

# Test with a simple approach
base_url = "http://localhost:8000"

def test_post(url, data):
    try:
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            data = response.read()
            print(f"POST {url}")
            print(f"Status: {response.status}")
            print(f"Response: {data.decode()}")
            print("-" * 50)
            return response.status == 200
    except Exception as e:
        print(f"POST {url}")
        print(f"Exception: {e}")
        print("-" * 50)
        return False

# Test creating a new user first
print("Creating a new user...")
new_user = {
    "email": "test2@example.com",
    "username": "testuser2",
    "full_name": "Test User 2",
    "password": "test123"
}
test_post(f"{base_url}/users/", new_user)

# Test questionnaire for user 2
print("Creating questionnaire for user 2...")
questionnaire_data = {
    "sleep_hours": 8.0,
    "water_goal_ml": 2000,
    "meal_frequency": 3,
    "exercise_frequency": 4,
    "exercise_duration": 30,
    "stress_level": "moderate",
    "energy_level": "high",
    "mood_tracking": True,
    "weight_goal": "maintain",
    "target_weight_kg": 70.0
}
test_post(f"{base_url}/users/2/questionnaire", questionnaire_data)

# Test habit target for user 2
print("Creating habit target for user 2...")
water_target = {
    "habit_type": "water",
    "target_value": 2000,
    "target_unit": "ml"
}
test_post(f"{base_url}/users/2/habit-targets", water_target)
