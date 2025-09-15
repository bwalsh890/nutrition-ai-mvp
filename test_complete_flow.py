#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json

# Test the complete habit tracking flow
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

def test_get(url):
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            print(f"GET {url}")
            print(f"Status: {response.status}")
            print(f"Response: {data.decode()}")
            print("-" * 50)
            return response.status == 200
    except Exception as e:
        print(f"GET {url}")
        print(f"Exception: {e}")
        print("-" * 50)
        return False

print("=== TESTING COMPLETE HABIT TRACKING FLOW ===\n")

# 1. Create questionnaire
print("1. Creating Questionnaire")
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
test_post(f"{base_url}/users/1/questionnaire", questionnaire_data)

# 2. Create habit targets
print("2. Creating Habit Targets")
water_target = {
    "habit_type": "water",
    "target_value": 2000,
    "target_unit": "ml"
}
test_post(f"{base_url}/users/1/habit-targets", water_target)

meals_target = {
    "habit_type": "meals",
    "target_value": 3,
    "target_unit": "count"
}
test_post(f"{base_url}/users/1/habit-targets", meals_target)

exercise_target = {
    "habit_type": "exercise",
    "target_value": 120,
    "target_unit": "minutes"
}
test_post(f"{base_url}/users/1/habit-targets", exercise_target)

# 3. Check habit targets
print("3. Checking Habit Targets")
test_get(f"{base_url}/users/1/habit-targets")

# 4. Create habit logs
print("4. Creating Habit Logs")
water_log = {
    "log_date": "2025-09-15",
    "habit_type": "water",
    "logged_value": 1500,
    "unit": "ml",
    "notes": "Morning hydration"
}
test_post(f"{base_url}/users/1/habit-logs", water_log)

meals_log = {
    "log_date": "2025-09-15",
    "habit_type": "meals",
    "logged_value": 2,
    "unit": "count",
    "notes": "Breakfast and lunch"
}
test_post(f"{base_url}/users/1/habit-logs", meals_log)

# 5. Check habit logs
print("5. Checking Habit Logs")
test_get(f"{base_url}/users/1/habit-logs")

# 6. Test progress calculation
print("6. Testing Progress Calculation")
test_get(f"{base_url}/users/1/progress/daily/2025-09-15/water")

# 7. Test feedback
print("7. Testing Feedback")
test_get(f"{base_url}/users/1/feedback/water")

print("\n=== TEST COMPLETE ===")
