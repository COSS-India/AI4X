#!/usr/bin/env python3
import requests
import json

def test_signup_api():
    url = "http://localhost:8000/auth/signup"
    data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "testpass123"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 201:
            response_data = response.json()
            print("\n=== SIGNUP SUCCESS ===")
            print(f"User ID: {response_data.get('id')}")
            print(f"Name: {response_data.get('name')}")
            print(f"Email: {response_data.get('email')}")
            print(f"Role: {response_data.get('role')}")
            print(f"API Key: {response_data.get('api_key')}")
            print(f"Message: {response_data.get('message')}")
        else:
            print(f"\n=== SIGNUP FAILED ===")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error making request: {e}")

def test_root_endpoint():
    url = "http://localhost:8000/"
    try:
        response = requests.get(url)
        print(f"Root endpoint status: {response.status_code}")
        print(f"Root endpoint response: {response.text}")
    except Exception as e:
        print(f"Error accessing root: {e}")

if __name__ == "__main__":
    print("Testing Dhruva API...")
    test_root_endpoint()
    print("\n" + "="*50)
    test_signup_api()
