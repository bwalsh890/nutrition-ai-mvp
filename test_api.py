#!/usr/bin/env python3
import requests
import json

# Test the API endpoints
base_url = "http://localhost:8000"

def test_endpoint(method, url, data=None):
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        print(f"{method} {url}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
        print("-" * 50)
        return response
    except Exception as e:
        print(f"Exception: {e}")
        print("-" * 50)
        return None

# Test health endpoint
print("Testing Health Endpoint")
test_endpoint("GET", f"{base_url}/health")

# Test users endpoint
print("Testing Users Endpoint")
test_endpoint("GET", f"{base_url}/users/")

# Test questionnaire endpoint
print("Testing Questionnaire Endpoint")
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
test_endpoint("POST", f"{base_url}/users/1/questionnaire", questionnaire_data)

# Test habit targets endpoint
print("Testing Habit Targets Endpoint")
test_endpoint("GET", f"{base_url}/users/1/habit-targets")

# Test habit logs endpoint
print("Testing Habit Logs Endpoint")
test_endpoint("GET", f"{base_url}/users/1/habit-logs")

# Test creating a habit log
print("Testing Create Habit Log")
habit_log_data = {
    "log_date": "2025-09-15",
    "habit_type": "water",
    "logged_value": 1500,
    "unit": "ml",
    "notes": "Morning hydration"
}
test_endpoint("POST", f"{base_url}/users/1/habit-logs", habit_log_data)
