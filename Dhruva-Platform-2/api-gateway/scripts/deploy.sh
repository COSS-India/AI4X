#!/bin/bash

# Kong API Gateway Deployment Script
# Complete plug-and-play deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_GATEWAY_DIR="$(dirname "$SCRIPT_DIR")"
PUBLIC_IP=$(curl -s ifconfig.me || echo "YOUR_PUBLIC_IP")

echo -e "${BLUE}🚀 Kong API Gateway Deployment Script${NC}"
echo -e "${YELLOW}Public IP: ${PUBLIC_IP}${NC}"
echo -e "${YELLOW}Deployment Directory: ${API_GATEWAY_DIR}${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

if ! command_exists docker; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command_exists docker-compose; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

if ! command_exists openssl; then
    echo -e "${RED}❌ OpenSSL is not installed. Please install OpenSSL first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites are installed${NC}"

# Create necessary directories
echo -e "${YELLOW}📁 Creating directories...${NC}"
mkdir -p "$API_GATEWAY_DIR/ssl"
mkdir -p "$API_GATEWAY_DIR/certbot/conf"
mkdir -p "$API_GATEWAY_DIR/certbot/www"
mkdir -p "$API_GATEWAY_DIR/nginx/conf.d"

# Generate SSL certificates
echo -e "${YELLOW}🔐 Generating SSL certificates...${NC}"
cd "$API_GATEWAY_DIR"
./scripts/generate-ssl.sh

# Update nginx configuration with public IP
echo -e "${YELLOW}⚙️  Updating configuration with public IP...${NC}"
sed -i "s/YOUR_PUBLIC_IP/${PUBLIC_IP}/g" nginx/nginx.conf

# Create environment file
echo -e "${YELLOW}📝 Creating environment file...${NC}"
cat > .env << EOF
# Kong API Gateway Environment
PUBLIC_IP=${PUBLIC_IP}
AI_MODEL_IP=172.31.31.208
MONGODB_URI=mongodb://dhruva-platform-app-db:27017
KONG_ADMIN_URL=http://kong:8001
SYNC_INTERVAL=30
EOF

# Stop existing containers if running
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose -f docker-compose.kong.yml down --remove-orphans || true

# Build and start services
echo -e "${YELLOW}🏗️  Building and starting services...${NC}"
docker-compose -f docker-compose.kong.yml up -d --build

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 30

# Check if Kong is ready
echo -e "${YELLOW}🔍 Checking Kong status...${NC}"
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -s http://localhost:8001/status | grep -q "database"; then
        echo -e "${GREEN}✅ Kong is ready!${NC}"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        echo -e "${RED}❌ Kong failed to start after ${max_attempts} attempts${NC}"
        echo -e "${YELLOW}📋 Checking logs...${NC}"
        docker-compose -f docker-compose.kong.yml logs kong
        exit 1
    fi
    
    echo "Attempt $attempt/$max_attempts: Waiting for Kong..."
    sleep 10
    ((attempt++))
done

# Setup Kong services and routes
echo -e "${YELLOW}⚙️  Setting up Kong services and routes...${NC}"
./scripts/setup-kong.sh

# Test the setup
echo -e "${YELLOW}🧪 Testing the setup...${NC}"

# Test Kong Admin API
if curl -s http://localhost:8001/status > /dev/null; then
    echo -e "${GREEN}✅ Kong Admin API is accessible${NC}"
else
    echo -e "${RED}❌ Kong Admin API is not accessible${NC}"
fi

# Test Kong Proxy
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ Kong Proxy is accessible${NC}"
else
    echo -e "${RED}❌ Kong Proxy is not accessible${NC}"
fi

# Test HTTPS
if curl -s -k https://localhost/health > /dev/null; then
    echo -e "${GREEN}✅ HTTPS is working${NC}"
else
    echo -e "${RED}❌ HTTPS is not working${NC}"
fi

# Display summary
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e ""
echo -e "${BLUE}📋 Service URLs:${NC}"
echo -e "  • Kong Admin API: http://localhost:8001"
echo -e "  • Kong Manager: http://localhost:8002"
echo -e "  • Kong Proxy: http://localhost:8000"
echo -e "  • HTTPS Gateway: https://${PUBLIC_IP}"
echo -e ""
echo -e "${BLUE}🔗 API Endpoints:${NC}"
echo -e "  • ASR: https://${PUBLIC_IP}/asr"
echo -e "  • TTS: https://${PUBLIC_IP}/tts"
echo -e "  • Translation: https://${PUBLIC_IP}/translation"
echo -e "  • Backend API: https://${PUBLIC_IP}/api"
echo -e ""
echo -e "${BLUE}🔑 Sample API Keys:${NC}"
echo -e "  • ASR: asr_1234567890abcdef"
echo -e "  • TTS: tts_1234567890abcdef"
echo -e "  • Translation: trans_1234567890abcdef"
echo -e "  • Admin: admin_1234567890abcdef"
echo -e ""
echo -e "${YELLOW}📖 Usage Example:${NC}"
echo -e "  curl -H 'X-API-Key: asr_1234567890abcdef' \\"
echo -e "       -H 'Content-Type: application/json' \\"
echo -e "       -d '{\"audio\": \"base64_encoded_audio\"}' \\"
echo -e "       https://${PUBLIC_IP}/asr"
echo -e ""
echo -e "${GREEN}✨ Your API gateway is ready to use!${NC}"
echo -e "${YELLOW}💡 To stop the services: docker-compose -f docker-compose.kong.yml down${NC}"
echo -e "${YELLOW}💡 To view logs: docker-compose -f docker-compose.kong.yml logs -f${NC}"
