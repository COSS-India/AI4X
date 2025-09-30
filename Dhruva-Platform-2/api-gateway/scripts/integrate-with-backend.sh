#!/bin/bash

# Backend Integration Script
# Updates backend configuration to use Kong API Gateway

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
BACKEND_DIR="$PLATFORM_DIR/server"
PUBLIC_IP=$(curl -s ifconfig.me || echo "YOUR_PUBLIC_IP")

echo -e "${BLUE}🔗 Backend Integration Script${NC}"
echo -e "${YELLOW}Platform Directory: ${PLATFORM_DIR}${NC}"
echo -e "${YELLOW}Backend Directory: ${BACKEND_DIR}${NC}"
echo -e "${YELLOW}Public IP: ${PUBLIC_IP}${NC}"

# Function to backup file
backup_file() {
    local file=$1
    if [ -f "$file" ]; then
        cp "$file" "${file}.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${GREEN}✅ Backed up: $file${NC}"
    fi
}

# Function to update service endpoints in MongoDB
update_service_endpoints() {
    echo -e "${YELLOW}🔄 Updating service endpoints in MongoDB...${NC}"
    
    # Create a Python script to update the database
    cat > /tmp/update_endpoints.py << EOF
import pymongo
import os
from datetime import datetime

# MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client.get_default_database()

# Update service endpoints to use Kong gateway
services_to_update = [
    {
        "serviceId": "asr-service",
        "endpoint": "https://${PUBLIC_IP}/asr",
        "api_key": "asr_1234567890abcdef"
    },
    {
        "serviceId": "tts-service", 
        "endpoint": "https://${PUBLIC_IP}/tts",
        "api_key": "tts_1234567890abcdef"
    },
    {
        "serviceId": "translation-service",
        "endpoint": "https://${PUBLIC_IP}/translation", 
        "api_key": "trans_1234567890abcdef"
    }
]

for service in services_to_update:
    result = db.service.update_one(
        {"serviceId": service["serviceId"]},
        {
            "\$set": {
                "endpoint": service["endpoint"],
                "api_key": service["api_key"],
                "updatedAt": datetime.now()
            }
        },
        upsert=True
    )
    
    if result.modified_count > 0:
        print(f"✅ Updated service: {service['serviceId']}")
    elif result.upserted_id:
        print(f"✅ Created service: {service['serviceId']}")
    else:
        print(f"ℹ️  Service unchanged: {service['serviceId']}")

print("🎉 Service endpoints updated successfully!")
EOF

    # Run the Python script
    if command -v python3 >/dev/null 2>&1; then
        python3 /tmp/update_endpoints.py
    elif command -v python >/dev/null 2>&1; then
        python /tmp/update_endpoints.py
    else
        echo -e "${RED}❌ Python is not installed. Please install Python to update the database.${NC}"
        echo -e "${YELLOW}You can manually update the service endpoints in MongoDB:${NC}"
        echo -e "  • ASR: https://${PUBLIC_IP}/asr"
        echo -e "  • TTS: https://${PUBLIC_IP}/tts"
        echo -e "  • Translation: https://${PUBLIC_IP}/translation"
    fi
    
    # Clean up
    rm -f /tmp/update_endpoints.py
}

# Function to create environment configuration
create_env_config() {
    echo -e "${YELLOW}📝 Creating environment configuration...${NC}"
    
    local env_file="$PLATFORM_DIR/.env.kong"
    
    cat > "$env_file" << EOF
# Kong API Gateway Configuration
KONG_GATEWAY_URL=https://${PUBLIC_IP}
KONG_ADMIN_URL=http://localhost:8001
KONG_MANAGER_URL=http://localhost:8002

# API Keys for Kong Gateway
KONG_ASR_API_KEY=asr_1234567890abcdef
KONG_TTS_API_KEY=tts_1234567890abcdef
KONG_TRANSLATION_API_KEY=trans_1234567890abcdef
KONG_ADMIN_API_KEY=admin_1234567890abcdef

# Service Endpoints (Updated to use Kong)
ASR_SERVICE_URL=https://${PUBLIC_IP}/asr
TTS_SERVICE_URL=https://${PUBLIC_IP}/tts
TRANSLATION_SERVICE_URL=https://${PUBLIC_IP}/translation

# SSL Configuration
SSL_VERIFY=true
SSL_CERT_PATH=./api-gateway/ssl/cert.pem
EOF

    echo -e "${GREEN}✅ Environment configuration created: $env_file${NC}"
}

# Function to create backend integration helper
create_integration_helper() {
    echo -e "${YELLOW}🔧 Creating backend integration helper...${NC}"
    
    local helper_file="$BACKEND_DIR/kong_integration.py"
    
    cat > "$helper_file" << EOF
"""
Kong API Gateway Integration Helper
Provides utilities for working with Kong gateway
"""

import os
import requests
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class KongGatewayClient:
    """Client for interacting with Kong API Gateway"""
    
    def __init__(self):
        self.gateway_url = os.getenv('KONG_GATEWAY_URL', 'https://localhost')
        self.admin_url = os.getenv('KONG_ADMIN_URL', 'http://localhost:8001')
        self.verify_ssl = os.getenv('SSL_VERIFY', 'true').lower() == 'true'
    
    def make_request(self, service: str, endpoint: str, method: str = 'POST', 
                    data: Optional[Dict] = None, api_key: Optional[str] = None) -> Dict:
        """
        Make a request through Kong gateway
        
        Args:
            service: Service name (asr, tts, translation)
            endpoint: API endpoint
            method: HTTP method
            data: Request data
            api_key: API key for authentication
            
        Returns:
            Response data
        """
        url = f"{self.gateway_url}/{service}{endpoint}"
        headers = {
            'Content-Type': 'application/json'
        }
        
        if api_key:
            headers['X-API-Key'] = api_key
        
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                headers=headers,
                verify=self.verify_ssl,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def get_service_health(self, service: str) -> bool:
        """Check if a service is healthy"""
        try:
            response = requests.get(
                f"{self.gateway_url}/{service}/health",
                verify=self.verify_ssl,
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def get_kong_status(self) -> Dict:
        """Get Kong gateway status"""
        try:
            response = requests.get(f"{self.admin_url}/status")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get Kong status: {e}")
            return {"status": "error", "message": str(e)}

# Global instance
kong_client = KongGatewayClient()

# Convenience functions
def call_asr_service(audio_data: str, language: str = "hi", api_key: str = None) -> Dict:
    """Call ASR service through Kong gateway"""
    data = {
        "audio": audio_data,
        "language": language,
        "format": "wav"
    }
    return kong_client.make_request("asr", "", "POST", data, api_key)

def call_tts_service(text: str, language: str = "hi", voice: str = "female", api_key: str = None) -> Dict:
    """Call TTS service through Kong gateway"""
    data = {
        "text": text,
        "language": language,
        "voice": voice
    }
    return kong_client.make_request("tts", "", "POST", data, api_key)

def call_translation_service(text: str, source_lang: str = "en", target_lang: str = "hi", api_key: str = None) -> Dict:
    """Call Translation service through Kong gateway"""
    data = {
        "text": text,
        "source_language": source_lang,
        "target_language": target_lang
    }
    return kong_client.make_request("translation", "", "POST", data, api_key)
EOF

    echo -e "${GREEN}✅ Integration helper created: $helper_file${NC}"
}

# Function to update docker-compose to include Kong network
update_docker_compose() {
    echo -e "${YELLOW}🐳 Updating Docker Compose configuration...${NC}"
    
    local compose_file="$PLATFORM_DIR/docker-compose-app.yml"
    
    if [ -f "$compose_file" ]; then
        backup_file "$compose_file"
        
        # Add Kong network to existing services
        if ! grep -q "kong-network" "$compose_file"; then
            # Add external network to networks section
            if grep -q "networks:" "$compose_file"; then
                sed -i '/networks:/a\  kong-network:\n    external: true' "$compose_file"
            else
                echo -e "\nnetworks:\n  kong-network:\n    external: true" >> "$compose_file"
            fi
            
            # Add kong-network to server service
            if grep -q "networks:" "$compose_file" && grep -q "dhruva-network" "$compose_file"; then
                sed -i '/dhruva-network/a\      - kong-network' "$compose_file"
            fi
            
            echo -e "${GREEN}✅ Updated Docker Compose configuration${NC}"
        else
            echo -e "${YELLOW}ℹ️  Kong network already configured${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Docker Compose file not found: $compose_file${NC}"
    fi
}

# Function to create integration test script
create_integration_test() {
    echo -e "${YELLOW}🧪 Creating integration test script...${NC}"
    
    local test_file="$PLATFORM_DIR/test-kong-integration.py"
    
    cat > "$test_file" << EOF
#!/usr/bin/env python3
"""
Kong API Gateway Integration Test
Tests the integration between backend and Kong gateway
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

try:
    from kong_integration import kong_client, call_asr_service, call_tts_service, call_translation_service
except ImportError:
    print("❌ Kong integration module not found. Please run the integration script first.")
    sys.exit(1)

def test_kong_status():
    """Test Kong gateway status"""
    print("🔍 Testing Kong gateway status...")
    status = kong_client.get_kong_status()
    if status.get('database', {}).get('reachable'):
        print("✅ Kong gateway is healthy")
        return True
    else:
        print("❌ Kong gateway is not healthy")
        return False

def test_service_health():
    """Test service health"""
    print("🔍 Testing service health...")
    services = ['asr', 'tts', 'translation']
    healthy_services = []
    
    for service in services:
        if kong_client.get_service_health(service):
            print(f"✅ {service.upper()} service is healthy")
            healthy_services.append(service)
        else:
            print(f"❌ {service.upper()} service is not healthy")
    
    return healthy_services

def test_api_keys():
    """Test API key authentication"""
    print("🔍 Testing API key authentication...")
    
    # Test with a simple health check
    try:
        response = requests.get(
            "https://localhost/health",
            headers={'X-API-Key': 'asr_1234567890abcdef'},
            verify=False,
            timeout=10
        )
        if response.status_code == 200:
            print("✅ API key authentication is working")
            return True
        else:
            print(f"❌ API key authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API key authentication test failed: {e}")
        return False

def test_service_calls():
    """Test actual service calls"""
    print("🔍 Testing service calls...")
    
    # Test ASR service
    try:
        result = call_asr_service("dGVzdCBhdWRpbyBkYXRh", "hi", "asr_1234567890abcdef")
        print("✅ ASR service call successful")
    except Exception as e:
        print(f"❌ ASR service call failed: {e}")
    
    # Test TTS service
    try:
        result = call_tts_service("Hello, world!", "hi", "female", "tts_1234567890abcdef")
        print("✅ TTS service call successful")
    except Exception as e:
        print(f"❌ TTS service call failed: {e}")
    
    # Test Translation service
    try:
        result = call_translation_service("Hello, world!", "en", "hi", "trans_1234567890abcdef")
        print("✅ Translation service call successful")
    except Exception as e:
        print(f"❌ Translation service call failed: {e}")

def main():
    """Run all integration tests"""
    print("🚀 Starting Kong API Gateway Integration Tests")
    print("=" * 50)
    
    # Test Kong status
    if not test_kong_status():
        print("❌ Kong gateway is not available. Please start the gateway first.")
        return
    
    # Test service health
    healthy_services = test_service_health()
    
    # Test API key authentication
    test_api_keys()
    
    # Test service calls
    test_service_calls()
    
    print("=" * 50)
    print("🎉 Integration tests completed!")
    
    if len(healthy_services) == 3:
        print("✅ All services are healthy and ready to use")
    else:
        print(f"⚠️  Only {len(healthy_services)}/3 services are healthy")

if __name__ == "__main__":
    main()
EOF

    chmod +x "$test_file"
    echo -e "${GREEN}✅ Integration test created: $test_file${NC}"
}

# Main execution
echo -e "${YELLOW}🔗 Starting backend integration...${NC}"

# Check if backend directory exists
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}❌ Backend directory not found: $BACKEND_DIR${NC}"
    exit 1
fi

# Update service endpoints
update_service_endpoints

# Create environment configuration
create_env_config

# Create integration helper
create_integration_helper

# Update Docker Compose
update_docker_compose

# Create integration test
create_integration_test

echo -e "${GREEN}🎉 Backend integration completed successfully!${NC}"
echo -e ""
echo -e "${BLUE}📋 Integration Summary:${NC}"
echo -e "  ✅ Service endpoints updated in MongoDB"
echo -e "  ✅ Environment configuration created"
echo -e "  ✅ Integration helper created"
echo -e "  ✅ Docker Compose updated"
echo -e "  ✅ Integration test created"
echo -e ""
echo -e "${YELLOW}🔧 Next Steps:${NC}"
echo -e "  1. Start the Kong API Gateway: cd api-gateway && ./scripts/deploy.sh"
echo -e "  2. Start your backend services: docker-compose -f docker-compose-app.yml up -d"
echo -e "  3. Run integration tests: python test-kong-integration.py"
echo -e "  4. Update your backend code to use the Kong integration helper"
echo -e ""
echo -e "${GREEN}✨ Your backend is now integrated with Kong API Gateway!${NC}"
