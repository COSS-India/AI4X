#!/bin/bash

# Let's Encrypt SSL Certificate Setup Script
# For production use with a domain name

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN=${1:-""}
EMAIL=${2:-"admin@yourdomain.com"}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_GATEWAY_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🔐 Let's Encrypt SSL Certificate Setup${NC}"

# Function to display help
show_help() {
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "  $0 <domain> [email]"
    echo -e ""
    echo -e "${YELLOW}Examples:${NC}"
    echo -e "  $0 api.yourdomain.com admin@yourdomain.com"
    echo -e "  $0 yourdomain.com"
    echo -e ""
    echo -e "${YELLOW}Note:${NC}"
    echo -e "  • Domain must point to this server's public IP"
    echo -e "  • Email is optional (defaults to admin@yourdomain.com)"
    echo -e "  • This script requires root privileges"
}

# Check if domain is provided
if [ -z "$DOMAIN" ]; then
    echo -e "${RED}❌ Domain is required${NC}"
    show_help
    exit 1
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ This script must be run as root${NC}"
    echo -e "${YELLOW}Please run: sudo $0 $DOMAIN $EMAIL${NC}"
    exit 1
fi

echo -e "${YELLOW}Domain: $DOMAIN${NC}"
echo -e "${YELLOW}Email: $EMAIL${NC}"

# Check if domain resolves to this server
echo -e "${YELLOW}🔍 Checking domain resolution...${NC}"
PUBLIC_IP=$(curl -s ifconfig.me)
DOMAIN_IP=$(dig +short $DOMAIN | tail -n1)

if [ "$DOMAIN_IP" != "$PUBLIC_IP" ]; then
    echo -e "${RED}❌ Domain $DOMAIN does not resolve to this server's IP ($PUBLIC_IP)${NC}"
    echo -e "${YELLOW}Domain resolves to: $DOMAIN_IP${NC}"
    echo -e "${YELLOW}Please update your DNS records and try again${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Domain resolves correctly${NC}"

# Install certbot if not installed
if ! command -v certbot >/dev/null 2>&1; then
    echo -e "${YELLOW}📦 Installing certbot...${NC}"
    
    # Detect OS and install certbot
    if [ -f /etc/debian_version ]; then
        apt-get update
        apt-get install -y certbot
    elif [ -f /etc/redhat-release ]; then
        yum install -y certbot
    else
        echo -e "${RED}❌ Unsupported OS. Please install certbot manually${NC}"
        exit 1
    fi
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating directories...${NC}"
mkdir -p "$API_GATEWAY_DIR/certbot/conf"
mkdir -p "$API_GATEWAY_DIR/certbot/www"

# Stop nginx temporarily
echo -e "${YELLOW}🛑 Stopping nginx temporarily...${NC}"
docker-compose -f "$API_GATEWAY_DIR/docker-compose.kong.yml" stop nginx || true

# Obtain SSL certificate
echo -e "${YELLOW}🔐 Obtaining SSL certificate from Let's Encrypt...${NC}"
certbot certonly \
    --webroot \
    --webroot-path="$API_GATEWAY_DIR/certbot/www" \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --domains "$DOMAIN" \
    --non-interactive

# Check if certificate was obtained
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo -e "${GREEN}✅ SSL certificate obtained successfully${NC}"
    
    # Copy certificates to api-gateway directory
    echo -e "${YELLOW}📋 Copying certificates...${NC}"
    cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$API_GATEWAY_DIR/ssl/cert.pem"
    cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$API_GATEWAY_DIR/ssl/key.pem"
    
    # Set proper permissions
    chmod 644 "$API_GATEWAY_DIR/ssl/cert.pem"
    chmod 600 "$API_GATEWAY_DIR/ssl/key.pem"
    
    # Update nginx configuration
    echo -e "${YELLOW}⚙️  Updating nginx configuration...${NC}"
    sed -i "s/YOUR_PUBLIC_IP/$DOMAIN/g" "$API_GATEWAY_DIR/nginx/nginx.conf"
    
    # Create certificate renewal script
    echo -e "${YELLOW}📝 Creating certificate renewal script...${NC}"
    cat > "$API_GATEWAY_DIR/scripts/renew-ssl.sh" << EOF
#!/bin/bash
# SSL Certificate Renewal Script

set -e

DOMAIN="$DOMAIN"
API_GATEWAY_DIR="$API_GATEWAY_DIR"

echo "🔄 Renewing SSL certificate for $DOMAIN..."

# Renew certificate
certbot renew --quiet

# Copy renewed certificates
cp "/etc/letsencrypt/live/\$DOMAIN/fullchain.pem" "\$API_GATEWAY_DIR/ssl/cert.pem"
cp "/etc/letsencrypt/live/\$DOMAIN/privkey.pem" "\$API_GATEWAY_DIR/ssl/key.pem"

# Reload nginx
docker-compose -f "\$API_GATEWAY_DIR/docker-compose.kong.yml" restart nginx

echo "✅ SSL certificate renewed successfully"
EOF

    chmod +x "$API_GATEWAY_DIR/scripts/renew-ssl.sh"
    
    # Add cron job for automatic renewal
    echo -e "${YELLOW}⏰ Setting up automatic renewal...${NC}"
    (crontab -l 2>/dev/null; echo "0 12 * * * $API_GATEWAY_DIR/scripts/renew-ssl.sh >> /var/log/ssl-renewal.log 2>&1") | crontab -
    
    # Start nginx with new certificates
    echo -e "${YELLOW}🚀 Starting nginx with new certificates...${NC}"
    docker-compose -f "$API_GATEWAY_DIR/docker-compose.kong.yml" up -d nginx
    
    echo -e "${GREEN}🎉 SSL certificate setup completed successfully!${NC}"
    echo -e ""
    echo -e "${BLUE}📋 Certificate Details:${NC}"
    echo -e "  • Domain: $DOMAIN"
    echo -e "  • Certificate: $API_GATEWAY_DIR/ssl/cert.pem"
    echo -e "  • Private Key: $API_GATEWAY_DIR/ssl/key.pem"
    echo -e "  • Expires: $(openssl x509 -in "$API_GATEWAY_DIR/ssl/cert.pem" -noout -dates | grep notAfter | cut -d= -f2)"
    echo -e ""
    echo -e "${BLUE}🔗 Your API gateway is now available at:${NC}"
    echo -e "  • HTTPS: https://$DOMAIN"
    echo -e "  • Kong Admin: http://$DOMAIN:8001"
    echo -e "  • Kong Manager: http://$DOMAIN:8002"
    echo -e ""
    echo -e "${YELLOW}💡 Certificate will auto-renew via cron job${NC}"
    echo -e "${YELLOW}💡 Manual renewal: $API_GATEWAY_DIR/scripts/renew-ssl.sh${NC}"
    
else
    echo -e "${RED}❌ Failed to obtain SSL certificate${NC}"
    echo -e "${YELLOW}Please check the error messages above and try again${NC}"
    exit 1
fi
