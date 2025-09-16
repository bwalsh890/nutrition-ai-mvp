import requests
import json

# Test user creation
url = "http://localhost:8000/users/"
data = {
    "username": "testuser",
    "email": "test@example.com", 
    "full_name": "Test User",
    "password": "password123"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
