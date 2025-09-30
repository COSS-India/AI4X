#!/bin/bash

# Kong API Key Management Script
# Manage API keys, consumers, and services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
KONG_ADMIN_URL="http://localhost:8001"

# Function to display help
show_help() {
    echo -e "${BLUE}Kong API Key Management Script${NC}"
    echo -e ""
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "  $0 [COMMAND] [OPTIONS]"
    echo -e ""
    echo -e "${YELLOW}Commands:${NC}"
    echo -e "  list-consumers          List all consumers"
    echo -e "  list-services           List all services"
    echo -e "  list-routes             List all routes"
    echo -e "  create-consumer         Create a new consumer"
    echo -e "  create-api-key          Create API key for consumer"
    echo -e "  delete-consumer         Delete a consumer"
    echo -e "  delete-api-key          Delete an API key"
    echo -e "  test-api-key            Test an API key"
    echo -e "  sync-from-db            Sync API keys from MongoDB"
    echo -e "  help                    Show this help message"
    echo -e ""
    echo -e "${YELLOW}Examples:${NC}"
    echo -e "  $0 list-consumers"
    echo -e "  $0 create-consumer myuser"
    echo -e "  $0 create-api-key myuser mykey123"
    echo -e "  $0 test-api-key mykey123"
}

# Function to check if Kong is running
check_kong() {
    if ! curl -s $KONG_ADMIN_URL/status > /dev/null; then
        echo -e "${RED}❌ Kong is not running or not accessible at $KONG_ADMIN_URL${NC}"
        exit 1
    fi
}

# Function to list consumers
list_consumers() {
    echo -e "${YELLOW}📋 Listing all consumers...${NC}"
    curl -s $KONG_ADMIN_URL/consumers | jq -r '.data[] | "\(.username) (\(.id))"'
}

# Function to list services
list_services() {
    echo -e "${YELLOW}📋 Listing all services...${NC}"
    curl -s $KONG_ADMIN_URL/services | jq -r '.data[] | "\(.name) -> \(.url)"'
}

# Function to list routes
list_routes() {
    echo -e "${YELLOW}📋 Listing all routes...${NC}"
    curl -s $KONG_ADMIN_URL/routes | jq -r '.data[] | "\(.name) -> \(.paths[])"'
}

# Function to create consumer
create_consumer() {
    local username=$1
    if [ -z "$username" ]; then
        echo -e "${RED}❌ Username is required${NC}"
        echo -e "${YELLOW}Usage: $0 create-consumer <username>${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}👤 Creating consumer: $username${NC}"
    response=$(curl -s -X POST $KONG_ADMIN_URL/consumers \
        --data "username=$username")
    
    if echo "$response" | jq -e '.id' > /dev/null; then
        echo -e "${GREEN}✅ Consumer created successfully${NC}"
        echo "$response" | jq -r '"ID: " + .id'
    else
        echo -e "${RED}❌ Failed to create consumer${NC}"
        echo "$response" | jq -r '.message // .'
    fi
}

# Function to create API key
create_api_key() {
    local username=$1
    local api_key=$2
    
    if [ -z "$username" ] || [ -z "$api_key" ]; then
        echo -e "${RED}❌ Username and API key are required${NC}"
        echo -e "${YELLOW}Usage: $0 create-api-key <username> <api_key>${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}🔑 Creating API key for consumer: $username${NC}"
    response=$(curl -s -X POST $KONG_ADMIN_URL/consumers/$username/key-auth \
        --data "key=$api_key")
    
    if echo "$response" | jq -e '.id' > /dev/null; then
        echo -e "${GREEN}✅ API key created successfully${NC}"
        echo -e "${BLUE}API Key: $api_key${NC}"
    else
        echo -e "${RED}❌ Failed to create API key${NC}"
        echo "$response" | jq -r '.message // .'
    fi
}

# Function to delete consumer
delete_consumer() {
    local username=$1
    if [ -z "$username" ]; then
        echo -e "${RED}❌ Username is required${NC}"
        echo -e "${YELLOW}Usage: $0 delete-consumer <username>${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}🗑️  Deleting consumer: $username${NC}"
    response=$(curl -s -X DELETE $KONG_ADMIN_URL/consumers/$username)
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Consumer deleted successfully${NC}"
    else
        echo -e "${RED}❌ Failed to delete consumer${NC}"
    fi
}

# Function to delete API key
delete_api_key() {
    local api_key=$1
    if [ -z "$api_key" ]; then
        echo -e "${RED}❌ API key is required${NC}"
        echo -e "${YELLOW}Usage: $0 delete-api-key <api_key>${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}🗑️  Deleting API key: $api_key${NC}"
    
    # Find the consumer for this API key
    consumer_id=$(curl -s $KONG_ADMIN_URL/key-auths | jq -r ".data[] | select(.key == \"$api_key\") | .consumer.id")
    
    if [ -z "$consumer_id" ]; then
        echo -e "${RED}❌ API key not found${NC}"
        exit 1
    fi
    
    # Get consumer username
    username=$(curl -s $KONG_ADMIN_URL/consumers/$consumer_id | jq -r '.username')
    
    # Delete the API key
    response=$(curl -s -X DELETE $KONG_ADMIN_URL/consumers/$username/key-auth/$api_key)
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ API key deleted successfully${NC}"
    else
        echo -e "${RED}❌ Failed to delete API key${NC}"
    fi
}

# Function to test API key
test_api_key() {
    local api_key=$1
    if [ -z "$api_key" ]; then
        echo -e "${RED}❌ API key is required${NC}"
        echo -e "${YELLOW}Usage: $0 test-api-key <api_key>${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}🧪 Testing API key: $api_key${NC}"
    
    # Test with a simple request
    response=$(curl -s -w "%{http_code}" -H "X-API-Key: $api_key" http://localhost:8000/health)
    http_code="${response: -3}"
    body="${response%???}"
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✅ API key is valid${NC}"
        echo -e "${BLUE}Response: $body${NC}"
    else
        echo -e "${RED}❌ API key is invalid or request failed${NC}"
        echo -e "${BLUE}HTTP Code: $http_code${NC}"
        echo -e "${BLUE}Response: $body${NC}"
    fi
}

# Function to sync from database
sync_from_db() {
    echo -e "${YELLOW}🔄 Syncing API keys from MongoDB...${NC}"
    
    # Check if API manager is running
    if curl -s http://localhost:8080/health > /dev/null; then
        response=$(curl -s -X POST http://localhost:8080/sync)
        echo -e "${GREEN}✅ Sync completed${NC}"
        echo "$response" | jq -r '.message // .'
    else
        echo -e "${RED}❌ API Manager is not running${NC}"
        echo -e "${YELLOW}Make sure the API Manager container is running${NC}"
    fi
}

# Main script logic
check_kong

case "${1:-help}" in
    "list-consumers")
        list_consumers
        ;;
    "list-services")
        list_services
        ;;
    "list-routes")
        list_routes
        ;;
    "create-consumer")
        create_consumer "$2"
        ;;
    "create-api-key")
        create_api_key "$2" "$3"
        ;;
    "delete-consumer")
        delete_consumer "$2"
        ;;
    "delete-api-key")
        delete_api_key "$2"
        ;;
    "test-api-key")
        test_api_key "$2"
        ;;
    "sync-from-db")
        sync_from_db
        ;;
    "help"|*)
        show_help
        ;;
esac
