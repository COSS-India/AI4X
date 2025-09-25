#!/usr/bin/env python3
import requests
import json

def check_available_endpoints():
    url = "http://localhost:8000/openapi.json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            openapi_spec = response.json()
            paths = openapi_spec.get('paths', {})
            
            print("Available endpoints:")
            for path, methods in paths.items():
                for method, details in methods.items():
                    print(f"  {method.upper()} {path}")
                    if 'summary' in details:
                        print(f"    Summary: {details['summary']}")
                    print()
            
            # Check specifically for auth endpoints
            auth_endpoints = [path for path in paths.keys() if '/auth' in path]
            print(f"\nAuth endpoints found: {len(auth_endpoints)}")
            for endpoint in auth_endpoints:
                print(f"  {endpoint}")
                
        else:
            print(f"Failed to get OpenAPI spec: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_available_endpoints()
