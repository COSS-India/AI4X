#!/usr/bin/env python3
import requests
import json

def test_create_user_api():
    url = "http://localhost:8000/auth/user"
    data = {
        "name": "Test User",
        "email": "testuser2@example.com",
        "password": "testpass123",
        "role": "CONSUMER"
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
            print("\n=== USER CREATE SUCCESS ===")
            print(f"User ID: {response_data.get('id')}")
            print(f"Name: {response_data.get('name')}")
            print(f"Email: {response_data.get('email')}")
            print(f"Role: {response_data.get('role')}")
        else:
            print(f"\n=== USER CREATE FAILED ===")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error making request: {e}")

def get_openapi_user_endpoint():
    url = "http://localhost:8000/openapi.json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            openapi_spec = response.json()
            user_endpoint = openapi_spec.get('paths', {}).get('/auth/user', {}).get('post', {})
            print("=== /auth/user POST endpoint details ===")
            print(f"Summary: {user_endpoint.get('summary', 'N/A')}")
            print(f"Request Body Schema:")
            request_body = user_endpoint.get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema', {})
            print(json.dumps(request_body, indent=2))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_openapi_user_endpoint()
    print("\n" + "="*50)
    test_create_user_api()
