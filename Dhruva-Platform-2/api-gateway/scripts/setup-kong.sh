#!/bin/bash

# Kong API Gateway Setup Script
# This script sets up Kong with AI model services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
KONG_ADMIN_URL="http://localhost:8001"
AI_MODEL_IP="172.31.31.208"
PUBLIC_IP=$(curl -s ifconfig.me || echo "YOUR_PUBLIC_IP")

echo -e "${GREEN}🚀 Setting up Kong API Gateway for AI Models${NC}"
echo -e "${YELLOW}AI Model IP: ${AI_MODEL_IP}${NC}"
echo -e "${YELLOW}Public IP: ${PUBLIC_IP}${NC}"

# Wait for Kong to be ready
echo -e "${YELLOW}⏳ Waiting for Kong to be ready...${NC}"
until curl -s $KONG_ADMIN_URL/status | grep -q "database"; do
    echo "Waiting for Kong..."
    sleep 5
done

echo -e "${GREEN}✅ Kong is ready!${NC}"

# Function to create service and route
create_service_route() {
    local service_name=$1
    local service_url=$2
    local route_path=$3
    local rate_limit=$4
    
    echo -e "${YELLOW}📝 Creating service: ${service_name}${NC}"
    
    # Create service
    curl -s -X POST $KONG_ADMIN_URL/services/ \
        --data "name=${service_name}" \
        --data "url=${service_url}" \
        --data "connect_timeout=60000" \
        --data "read_timeout=60000" \
        --data "write_timeout=60000"
    
    # Create route
    curl -s -X POST $KONG_ADMIN_URL/services/${service_name}/routes \
        --data "name=${service_name}-route" \
        --data "paths[]=/${route_path}" \
        --data "strip_path=true"
    
    # Add key-auth plugin
    curl -s -X POST $KONG_ADMIN_URL/services/${service_name}/plugins \
        --data "name=key-auth" \
        --data "config.key_names=X-API-Key" \
        --data "config.hide_credentials=false"
    
    # Add rate limiting
    curl -s -X POST $KONG_ADMIN_URL/services/${service_name}/plugins \
        --data "name=rate-limiting" \
        --data "config.minute=${rate_limit}" \
        --data "config.hour=$(($rate_limit * 60))" \
        --data "config.policy=local"
    
    # Add CORS plugin
    curl -s -X POST $KONG_ADMIN_URL/services/${service_name}/plugins \
        --data "name=cors" \
        --data "config.origins=*" \
        --data "config.methods=GET,HEAD,PUT,PATCH,POST,DELETE,OPTIONS" \
        --data "config.headers=Accept,Accept-Version,Content-Length,Content-MD5,Content-Type,Date,X-Auth-Token,Authorization,X-API-Key" \
        --data "config.exposed_headers=X-Auth-Token,Authorization,X-API-Key" \
        --data "config.credentials=true" \
        --data "config.max_age=3600"
    
    echo -e "${GREEN}✅ Service ${service_name} created successfully${NC}"
}

# Create AI Model Services
echo -e "${YELLOW}🤖 Creating AI Model Services...${NC}"

# ASR Service
create_service_route "asr-service" "http://${AI_MODEL_IP}:5000" "asr" 100

# TTS Service  
create_service_route "tts-service" "http://${AI_MODEL_IP}:9000" "tts" 50

# Translation Service
create_service_route "translation-service" "http://${AI_MODEL_IP}:8000" "translation" 200

# Backend Service (for existing API)
create_service_route "backend-service" "http://dhruva-platform-server:8000" "api" 1000

echo -e "${GREEN}🎉 All services created successfully!${NC}"

# Create sample consumers and API keys
echo -e "${YELLOW}🔑 Creating sample consumers and API keys...${NC}"

# Create consumers for each service
create_consumer() {
    local consumer_name=$1
    local api_key=$2
    
    # Create consumer
    curl -s -X POST $KONG_ADMIN_URL/consumers/ \
        --data "username=${consumer_name}"
    
    # Create API key for consumer
    curl -s -X POST $KONG_ADMIN_URL/consumers/${consumer_name}/key-auth \
        --data "key=${api_key}"
    
    echo -e "${GREEN}✅ Consumer ${consumer_name} created with API key: ${api_key}${NC}"
}

# Create sample consumers
create_consumer "asr-user" "asr_1234567890abcdef"
create_consumer "tts-user" "tts_1234567890abcdef" 
create_consumer "translation-user" "trans_1234567890abcdef"
create_consumer "admin-user" "admin_1234567890abcdef"

echo -e "${GREEN}🎯 Kong setup completed!${NC}"
echo -e "${YELLOW}📋 Summary:${NC}"
echo -e "  • Kong Admin API: http://localhost:8001"
echo -e "  • Kong Manager: http://localhost:8002"
echo -e "  • API Gateway: http://localhost:8000"
echo -e "  • HTTPS Gateway: https://${PUBLIC_IP}"
echo -e ""
echo -e "${YELLOW}🔗 API Endpoints:${NC}"
echo -e "  • ASR: https://${PUBLIC_IP}/asr"
echo -e "  • TTS: https://${PUBLIC_IP}/tts"
echo -e "  • Translation: https://${PUBLIC_IP}/translation"
echo -e "  • Backend API: https://${PUBLIC_IP}/api"
echo -e ""
echo -e "${YELLOW}🔑 Sample API Keys:${NC}"
echo -e "  • ASR: asr_1234567890abcdef"
echo -e "  • TTS: tts_1234567890abcdef"
echo -e "  • Translation: trans_1234567890abcdef"
echo -e "  • Admin: admin_1234567890abcdef"
echo -e ""
echo -e "${GREEN}✨ Setup complete! Your API gateway is ready to use.${NC}"
