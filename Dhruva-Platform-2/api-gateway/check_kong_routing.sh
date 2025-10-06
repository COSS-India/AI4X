#!/bin/bash

echo "🔍 Kong API Gateway Routing Status Check"
echo "========================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "\n${BLUE}📋 1. Kong Services Configuration${NC}"
echo "----------------------------------------"
curl -s http://localhost:8001/services | jq -r '.data[] | "• \(.name): \(.host):\(.port) (\(.protocol))"'

echo -e "\n${BLUE}🛣️  2. Kong Routes Configuration${NC}"
echo "----------------------------------------"
curl -s http://localhost:8001/routes | jq -r '.data[] | "• \(.name): \(.paths[0]) -> Service ID: \(.service.id)"'

echo -e "\n${BLUE}🔑 3. Authentication & Rate Limiting${NC}"
echo "----------------------------------------"
echo "Services with Key Authentication:"
curl -s http://localhost:8001/plugins | jq -r '.data[] | select(.name == "key-auth") | "• Service ID: \(.service.id)"'

echo -e "\nServices with Rate Limiting:"
curl -s http://localhost:8001/plugins | jq -r '.data[] | select(.name == "rate-limiting") | "• Service ID: \(.service.id) - \(.config.minute) req/min"'

echo -e "\n${BLUE}👥 4. Consumers & API Keys${NC}"
echo "----------------------------------------"
curl -s http://localhost:8001/consumers | jq -r '.data[] | "• Consumer: \(.username) (ID: \(.id))"'

echo -e "\nAPI Keys:"
curl -s http://localhost:8001/key-auths | jq -r '.data[] | "• Key: \(.key) -> Consumer ID: \(.consumer.id)"'

echo -e "\n${BLUE}🧪 5. Endpoint Testing${NC}"
echo "----------------------------------------"

# Test each endpoint
test_endpoint() {
    local name=$1
    local endpoint=$2
    local api_key=$3
    
    echo -n "Testing $name ($endpoint): "
    response=$(curl -s -w "%{http_code}" -H "X-API-Key: $api_key" "http://localhost:8000$endpoint" -o /dev/null)
    
    case $response in
        200) echo -e "${GREEN}✅ OK (200)${NC}" ;;
        400) echo -e "${YELLOW}⚠️  Bad Request (400) - Service responding but needs proper payload${NC}" ;;
        404) echo -e "${YELLOW}⚠️  Not Found (404) - Route exists but backend not responding${NC}" ;;
        503) echo -e "${RED}❌ Service Unavailable (503) - Backend service not reachable${NC}" ;;
        401) echo -e "${RED}❌ Unauthorized (401) - API key issue${NC}" ;;
        *) echo -e "${RED}❌ Error ($response)${NC}" ;;
    esac
}

test_endpoint "ASR Service" "/asr" "asr_1234567890abcdef"
test_endpoint "TTS Service" "/tts" "tts_1234567890abcdef"
test_endpoint "Translation Service" "/translation" "trans_1234567890abcdef"
test_endpoint "Backend API" "/api" "admin_1234567890abcdef"

echo -e "\n${BLUE}🌐 6. Accessible URLs${NC}"
echo "----------------------------------------"
echo "• Kong Admin API: http://localhost:8001"
echo "• Kong Manager: http://localhost:8002"
echo "• API Gateway: http://localhost:8000"
echo "• HTTPS Gateway: https://3.110.67.135"

echo -e "\n${BLUE}📊 7. Kong Status${NC}"
echo "----------------------------------------"
curl -s http://localhost:8001/status | jq -r '"• Database: " + (.database.reachable | if . then "✅ Connected" else "❌ Disconnected" end)'
curl -s http://localhost:8001/status | jq -r '"• Total Requests: " + (.server.total_requests | tostring)'

echo -e "\n${GREEN}✨ Kong routing check completed!${NC}"
