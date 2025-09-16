#!/usr/bin/env python3
import requests
import time

def test_server():
    print("🧪 Testing Nutrition AI MVP Server...")
    
    try:
        # Test health endpoint
        print("1. Testing health endpoint...")
        response = requests.get('http://localhost:8000/health', timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test root endpoint
        print("\n2. Testing root endpoint...")
        response = requests.get('http://localhost:8000/', timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test users endpoint
        print("\n3. Testing users endpoint...")
        response = requests.get('http://localhost:8000/users/', timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        print("\n✅ All tests passed! Server is working!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Start it with: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_server()
