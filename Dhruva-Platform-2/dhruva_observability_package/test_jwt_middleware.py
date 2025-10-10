#!/usr/bin/env python3
"""
Unit tests for JWT token extraction in ObservabilityMiddleware
"""
import sys
import os

# Add the current directory to Python path to import the middleware
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unittest.mock import Mock, MagicMock

# Simple mock for testing
class MockRequest:
    def __init__(self, headers=None):
        self.headers = headers or {}

# Import our middleware components
try:
    from dhruva_observability.middleware import ObservabilityMiddleware
    from dhruva_observability.config import PluginConfig
    from dhruva_observability.metrics import MetricsCollector
except ImportError:
    print("❌ Could not import dhruva_observability modules")
    print("📝 Make sure to run: pip install -e .")
    sys.exit(1)


class TestJWTExtraction:
    """Test JWT token extraction functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = PluginConfig(
            enabled=True,
            debug=True,
            default_customer="default_customer",
            default_app="default_app"
        )
        self.metrics_collector = Mock(spec=MetricsCollector)
        self.middleware = ObservabilityMiddleware(
            app=Mock(), 
            metrics_collector=self.metrics_collector,
            config=self.config
        )
    
    def test_decode_jwt_token_valid(self):
        """Test decoding a valid JWT token."""
        # Valid JWT token with customer name "Admin2"
        valid_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODI3MjhkODU4OTQzZTZkM2JhZDIwZDciLCJuYW1lIjoiQWRtaW4yIiwiZXhwIjoxNzYxNjQyODQ0LCJpYXQiOjE3NTkwNTA4NDQsInNlc3NfaWQiOiI2OGQ4ZmM1YzhiNDUzZjVkYjY1YWJjZGEifQ.fake_signature"
        
        decoded = self.middleware._decode_jwt_token(valid_token)
        
        assert decoded is not None
        assert decoded["name"] == "Admin2"
        assert decoded["sub"] == "682728d858943e6d3bad20d7"
    
    def test_decode_jwt_token_invalid_format(self):
        """Test handling invalid token format."""
        invalid_token = "InvalidTokenFormat"
        
        decoded = self.middleware._decode_jwt_token(invalid_token)
        
        assert decoded is None
    
    def test_decode_jwt_token_malformed(self):
        """Test handling malformed JWT token."""
        malformed_token = "Bearer invalid.jwt.token"
        
        decoded = self.middleware._decode_jwt_token(malformed_token)
        
        assert decoded is None
    
    def test_extract_customer_from_token_with_name(self):
        """Test extracting customer from token with 'name' field."""
        request = MockRequest({
            "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiQWRtaW4yIiwic3ViIjoiNjgyNzI4ZDg1ODk0M2U2ZDNiYWQyMGQ3In0.fake"
        })
        
        customer = self.middleware._extract_customer_from_token(request)
        
        assert customer == "Admin2"
    
    def test_extract_customer_from_token_fallback_to_sub(self):
        """Test falling back to 'sub' field when 'name' is not available."""
        request = MockRequest({
            "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODI3MjhkODU4OTQzZTZkM2JhZDIwZDcifQ.fake"
        })
        
        customer = self.middleware._extract_customer_from_token(request)
        
        assert customer == "682728d858943e6d3bad20d7"
    
    def test_extract_customer_from_token_no_auth_header(self):
        """Test handling missing authorization header."""
        request = MockRequest({})
        
        customer = self.middleware._extract_customer_from_token(request)
        
        assert customer == self.config.default_customer
    
    def test_extract_customer_app_jwt_priority(self):
        """Test that JWT token takes priority over headers."""
        request = MockRequest({
            "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiSldUQ3VzdG9tZXIifQ.fake",
            "X-Customer-ID": "HeaderCustomer",
            "X-App-ID": "TestApp"
        })
        
        customer, app = self.middleware._extract_customer_app(request)
        
        assert customer == "JWTCustomer"  # JWT takes priority
        assert app == "TestApp"
    
    def test_extract_customer_app_header_fallback(self):
        """Test fallback to headers when JWT extraction fails."""
        request = MockRequest({
            "authorization": "Bearer invalid.token",
            "X-Customer-ID": "HeaderCustomer",
            "X-App-ID": "TestApp"
        })
        
        customer, app = self.middleware._extract_customer_app(request)
        
        assert customer == "HeaderCustomer"
        assert app == "TestApp"
    
    def test_real_token_from_curl_example(self):
        """Test with the actual token from the curl example."""
        real_token = "Bearer eyJhbGciOiJIUzI1NiIsInRvayI6ImFjY2VzcyIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODI3MjhkODU4OTQzZTZkM2JhZDIwZDciLCJuYW1lIjoiQWRtaW4yIiwiZXhwIjoxNzYxNjQyODQ0LjE1Njg2NTQsImlhdCI6MTc1OTA1MDg0NC4xNTY4NjU4LCJzZXNzX2lkIjoiNjhkOGZjNWM4YjQ1M2Y1ZGI2NWFiY2RhIn0.nrG79cfIIQPR8nO9yFy9ifkNxD-_2F56A8RgGu5qoH0"
        
        request = MockRequest({"authorization": real_token})
        
        customer = self.middleware._extract_customer_from_token(request)
        
        assert customer == "Admin2"


if __name__ == "__main__":
    # Run tests
    test_instance = TestJWTExtraction()
    test_instance.setup_method()
    
    print("🧪 Running JWT extraction tests...")
    
    try:
        test_instance.test_decode_jwt_token_valid()
        print("✅ Valid JWT token decoding test passed")
        
        test_instance.test_extract_customer_from_token_with_name()
        print("✅ Customer extraction from name field test passed")
        
        test_instance.test_extract_customer_from_token_fallback_to_sub()
        print("✅ Fallback to sub field test passed")
        
        test_instance.test_extract_customer_from_token_no_auth_header()
        print("✅ Missing auth header test passed")
        
        test_instance.test_extract_customer_app_jwt_priority()
        print("✅ JWT priority over headers test passed")
        
        test_instance.test_extract_customer_app_header_fallback()
        print("✅ Header fallback test passed")
        
        test_instance.test_real_token_from_curl_example()
        print("✅ Real curl token test passed")
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
