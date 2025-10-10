#!/usr/bin/env python3
"""
Test script to verify JWT token decoding functionality
"""
import jwt
import json

def test_jwt_decoding():
    # Example token from the curl request
    token = "eyJhbGciOiJIUzI1NiIsInRvayI6ImFjY2VzcyIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODI3MjhkODU4OTQzZTZkM2JhZDIwZDciLCJuYW1lIjoiQWRtaW4yIiwiZXhwIjoxNzYxNjQyODQ0LjE1Njg2NTQsImlhdCI6MTc1OTA1MDg0NC4xNTY4NjU4LCJzZXNzX2lkIjoiNjhkOGZjNWM4YjQ1M2Y1ZGI2NWFiY2RhIn0.nrG79cfIIQPR8nO9yFy9ifkNxD-_2F56A8RgGu5qoH0"
    
    try:
        # Decode without signature verification (for testing purposes)
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        
        print("🔍 Decoded JWT Token:")
        print(json.dumps(decoded_token, indent=2))
        
        # Extract customer name
        customer_name = decoded_token.get("name", "default")
        print(f"\n✅ Customer Name: {customer_name}")
        
        # Show other useful fields
        print(f"📧 User ID (sub): {decoded_token.get('sub', 'N/A')}")
        print(f"🔑 Session ID: {decoded_token.get('sess_id', 'N/A')}")
        
        return customer_name
        
    except Exception as e:
        print(f"❌ Error decoding JWT: {e}")
        return None

if __name__ == "__main__":
    test_jwt_decoding()
