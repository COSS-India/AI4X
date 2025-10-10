#!/usr/bin/env python3
"""
Simple test for JWT token customer extraction functionality
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import jwt

def test_jwt_extraction_simple():
    """Simple test of JWT extraction logic."""
    print("🧪 Testing JWT customer extraction...")
    
    # Test token from the curl example
    token = "eyJhbGciOiJIUzI1NiIsInRvayI6ImFjY2VzcyIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODI3MjhkODU4OTQzZTZkM2JhZDIwZDciLCJuYW1lIjoiQWRtaW4yIiwiZXhwIjoxNzYxNjQyODQ0LjE1Njg2NTQsImlhdCI6MTc1OTA1MDg0NC4xNTY4NjU4LCJzZXNzX2lkIjoiNjhkOGZjNWM4YjQ1M2Y1ZGI2NWFiY2RhIn0.nrG79cfIIQPR8nO9yFy9ifkNxD-_2F56A8RgGu5qoH0"
    
    # Test 1: Decode JWT token without verification
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        print(f"✅ Token decoded successfully")
        print(f"   Customer name: {decoded.get('name', 'NOT_FOUND')}")
        print(f"   User ID: {decoded.get('sub', 'NOT_FOUND')}")
        assert decoded["name"] == "Admin2", f"Expected 'Admin2', got {decoded.get('name')}"
    except Exception as e:
        print(f"❌ Token decoding failed: {e}")
        return False
    
    # Test 2: Test authorization header parsing
    auth_header = f"Bearer {token}"
    
    def extract_token_from_header(header):
        if not header.startswith("Bearer "):
            return None
        return header[7:]  # Remove "Bearer " prefix
    
    extracted_token = extract_token_from_header(auth_header)
    assert extracted_token == token, "Token extraction from header failed"
    print("✅ Authorization header parsing works")
    
    # Test 3: Test customer extraction logic
    def extract_customer_name(auth_header, default="default"):
        try:
            if not auth_header.startswith("Bearer "):
                return default
            
            token = auth_header[7:]
            decoded = jwt.decode(token, options={"verify_signature": False})
            
            # Priority: name field first, then sub field
            if "name" in decoded:
                return decoded["name"]
            elif "sub" in decoded:
                return decoded["sub"]
            else:
                return default
        except:
            return default
    
    customer = extract_customer_name(auth_header)
    assert customer == "Admin2", f"Expected 'Admin2', got {customer}"
    print("✅ Customer extraction logic works")
    
    # Test 4: Test fallback scenarios
    invalid_header = "Bearer invalid.token.here"
    fallback_customer = extract_customer_name(invalid_header, "fallback_user")
    assert fallback_customer == "fallback_user", "Fallback logic failed"
    print("✅ Fallback logic works")
    
    print("\n🎉 All JWT extraction tests passed!")
    return True

def test_middleware_integration():
    """Test integration with the actual middleware if available."""
    try:
        from dhruva_observability.middleware import ObservabilityMiddleware
        from dhruva_observability.config import PluginConfig
        from dhruva_observability.metrics import MetricsCollector
        
        print("\n📦 Testing middleware integration...")
        
        # Create middleware instance
        config = PluginConfig(enabled=True, debug=False)
        metrics = MetricsCollector()
        middleware = ObservabilityMiddleware(app=None, metrics_collector=metrics, config=config)
        
        # Test JWT decoding method
        auth_header = "Bearer eyJhbGciOiJIUzI1NiIsInRvayI6ImFjY2VzcyIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODI3MjhkODU4OTQzZTZkM2JhZDIwZDciLCJuYW1lIjoiQWRtaW4yIiwiZXhwIjoxNzYxNjQyODQ0LjE1Njg2NTQsImlhdCI6MTc1OTA1MDg0NC4xNTY4NjU4LCJzZXNzX2lkIjoiNjhkOGZjNWM4YjQ1M2Y1ZGI2NWFiY2RhIn0.nrG79cfIIQPR8nO9yFy9ifkNxD-_2F56A8RgGu5qoH0"
        
        decoded = middleware._decode_jwt_token(auth_header)
        assert decoded is not None, "Middleware JWT decoding failed"
        assert decoded["name"] == "Admin2", f"Expected 'Admin2', got {decoded.get('name')}"
        print("✅ Middleware JWT decoding works")
        
        # Test customer extraction
        class MockRequest:
            def __init__(self, headers):
                self.headers = headers
        
        request = MockRequest({"authorization": auth_header})
        customer = middleware._extract_customer_from_token(request)
        assert customer == "Admin2", f"Expected 'Admin2', got {customer}"
        print("✅ Middleware customer extraction works")
        
        print("🎉 Middleware integration tests passed!")
        return True
        
    except ImportError as e:
        print(f"⚠️ Middleware not available for testing: {e}")
        print("   This is expected if the package isn't installed yet.")
        return True
    except Exception as e:
        print(f"❌ Middleware integration test failed: {e}")
        return False

if __name__ == "__main__":
    success = True
    
    success &= test_jwt_extraction_simple()
    success &= test_middleware_integration()
    
    if success:
        print("\n🏆 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)
