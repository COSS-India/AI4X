#!/bin/bash

# SSL Certificate Generation Script for Public IP
# This script generates self-signed certificates for development/testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PUBLIC_IP=$(curl -s ifconfig.me || echo "YOUR_PUBLIC_IP")
SSL_DIR="./ssl"
CERT_FILE="$SSL_DIR/cert.pem"
KEY_FILE="$SSL_DIR/key.pem"

echo -e "${GREEN}🔐 Generating SSL certificates for IP: ${PUBLIC_IP}${NC}"

# Create SSL directory
mkdir -p $SSL_DIR

# Generate private key
echo -e "${YELLOW}📝 Generating private key...${NC}"
openssl genrsa -out $KEY_FILE 2048

# Generate certificate signing request
echo -e "${YELLOW}📝 Generating certificate signing request...${NC}"
openssl req -new -key $KEY_FILE -out $SSL_DIR/cert.csr -subj "/C=US/ST=State/L=City/O=Organization/CN=$PUBLIC_IP"

# Generate self-signed certificate
echo -e "${YELLOW}📝 Generating self-signed certificate...${NC}"
openssl x509 -req -days 365 -in $SSL_DIR/cert.csr -signkey $KEY_FILE -out $CERT_FILE \
    -extensions v3_req -extfile <(
        echo "[req]"
        echo "distinguished_name = req_distinguished_name"
        echo "req_extensions = v3_req"
        echo "prompt = no"
        echo ""
        echo "[req_distinguished_name]"
        echo "C = US"
        echo "ST = State"
        echo "L = City"
        echo "O = Organization"
        echo "CN = $PUBLIC_IP"
        echo ""
        echo "[v3_req]"
        echo "keyUsage = keyEncipherment, dataEncipherment"
        echo "extendedKeyUsage = serverAuth"
        echo "subjectAltName = @alt_names"
        echo ""
        echo "[alt_names]"
        echo "IP.1 = $PUBLIC_IP"
        echo "IP.2 = 127.0.0.1"
        echo "DNS.1 = localhost"
    )

# Set proper permissions
chmod 600 $KEY_FILE
chmod 644 $CERT_FILE

# Clean up CSR file
rm $SSL_DIR/cert.csr

echo -e "${GREEN}✅ SSL certificates generated successfully!${NC}"
echo -e "${YELLOW}📁 Certificate files:${NC}"
echo -e "  • Certificate: $CERT_FILE"
echo -e "  • Private Key: $KEY_FILE"
echo -e ""
echo -e "${YELLOW}⚠️  Note: These are self-signed certificates for development/testing.${NC}"
echo -e "${YELLOW}   For production, use Let's Encrypt or a trusted CA.${NC}"
echo -e ""
echo -e "${GREEN}🔗 Your API gateway will be available at: https://${PUBLIC_IP}${NC}"
