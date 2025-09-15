#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json

# Test the API endpoints
base_url = "http://localhost:8000"

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

# Test health endpoint
print("Testing Health Endpoint")
test_get(f"{base_url}/health")

# Test users endpoint
print("Testing Users Endpoint")
test_get(f"{base_url}/users/")

# Test habit targets endpoint
print("Testing Habit Targets Endpoint")
test_get(f"{base_url}/users/1/habit-targets")

# Test habit logs endpoint
print("Testing Habit Logs Endpoint")
test_get(f"{base_url}/users/1/habit-logs")
