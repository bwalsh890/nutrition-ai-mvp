import requests
import json
import time

# Test user creation with unique username
url = "http://localhost:8000/users/"
data = {
    "username": f"testuser_{int(time.time())}",  # Unique username
    "email": f"test_{int(time.time())}@example.com",  # Unique email
    "full_name": "Test User",
    "password": "password123"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
