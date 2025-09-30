# Kong API Gateway for AI Models

A comprehensive, plug-and-play API gateway solution using Kong and Nginx to provide secure access to AI models hosted on EC2 instances.

## 🏗️ Architecture Overview

```
Internet → Nginx (SSL/TLS) → Kong Gateway → AI Models (EC2)
                ↓
         Kong Admin API
                ↓
         API Key Manager (MongoDB Sync)
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenSSL (for SSL certificate generation)
- jq (for JSON processing in scripts)
- curl (for API testing)

### One-Command Deployment

```bash
cd api-gateway
./scripts/deploy.sh
```

This script will:
1. ✅ Check prerequisites
2. 🔐 Generate SSL certificates
3. 🏗️ Build and start all services
4. ⚙️ Configure Kong services and routes
5. 🧪 Test the setup
6. 📋 Display usage information

## 📁 Project Structure

```
api-gateway/
├── docker-compose.kong.yml    # Main Docker Compose file
├── nginx/
│   └── nginx.conf            # Nginx configuration
├── kong-config/
│   └── kong.conf             # Kong configuration
├── api-manager/              # API key sync service
│   ├── Dockerfile
│   ├── requirements.txt
│   └── api_manager.py
├── scripts/
│   ├── deploy.sh             # Main deployment script
│   ├── setup-kong.sh         # Kong configuration script
│   ├── generate-ssl.sh       # SSL certificate generation
│   └── manage-api-keys.sh    # API key management
└── README.md
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `api-gateway` directory:

```env
PUBLIC_IP=your_public_ip
AI_MODEL_IP=172.31.31.208
MONGODB_URI=mongodb://dhruva-platform-app-db:27017
KONG_ADMIN_URL=http://kong:8001
SYNC_INTERVAL=30
```

### AI Model Endpoints

The gateway is pre-configured for these AI models:

| Service | Port | Endpoint | Rate Limit |
|---------|------|----------|------------|
| ASR | 5000-5002 | `/asr` | 100/min |
| TTS | 9000-9002 | `/tts` | 50/min |
| Translation | 8000-8002 | `/translation` | 200/min |
| Backend API | 8000 | `/api` | 1000/min |

## 🔑 API Key Management

### Using the Management Script

```bash
# List all consumers
./scripts/manage-api-keys.sh list-consumers

# Create a new consumer
./scripts/manage-api-keys.sh create-consumer myuser

# Create API key for consumer
./scripts/manage-api-keys.sh create-api-key myuser mykey123

# Test an API key
./scripts/manage-api-keys.sh test-api-key mykey123

# Sync from MongoDB
./scripts/manage-api-keys.sh sync-from-db
```

### Sample API Keys

For testing, these sample API keys are created:

- **ASR**: `asr_1234567890abcdef`
- **TTS**: `tts_1234567890abcdef`
- **Translation**: `trans_1234567890abcdef`
- **Admin**: `admin_1234567890abcdef`

## 🌐 API Usage

### Base URLs

- **HTTP**: `http://your-public-ip:8000`
- **HTTPS**: `https://your-public-ip`

### Authentication

All requests must include the API key in the header:

```bash
curl -H "X-API-Key: your_api_key" \
     -H "Content-Type: application/json" \
     https://your-public-ip/asr
```

### Example Requests

#### ASR (Automatic Speech Recognition)

```bash
curl -X POST https://your-public-ip/asr \
  -H "X-API-Key: asr_1234567890abcdef" \
  -H "Content-Type: application/json" \
  -d '{
    "audio": "base64_encoded_audio_data",
    "language": "hi",
    "format": "wav"
  }'
```

#### TTS (Text-to-Speech)

```bash
curl -X POST https://your-public-ip/tts \
  -H "X-API-Key: tts_1234567890abcdef" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, world!",
    "language": "hi",
    "voice": "female"
  }'
```

#### Translation

```bash
curl -X POST https://your-public-ip/translation \
  -H "X-API-Key: trans_1234567890abcdef" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, world!",
    "source_language": "en",
    "target_language": "hi"
  }'
```

## 🔒 Security Features

### SSL/TLS
- Self-signed certificates for development
- Let's Encrypt support for production
- TLS 1.2+ with secure cipher suites

### Authentication
- API key-based authentication
- Kong key-auth plugin
- Automatic API key validation

### Rate Limiting
- Per-service rate limits
- Configurable limits per minute/hour
- Local rate limiting policy

### CORS
- Configurable CORS policies
- Support for all HTTP methods
- Custom headers support

## 🛠️ Management

### Service Management

```bash
# Start services
docker-compose -f docker-compose.kong.yml up -d

# Stop services
docker-compose -f docker-compose.kong.yml down

# View logs
docker-compose -f docker-compose.kong.yml logs -f

# Restart specific service
docker-compose -f docker-compose.kong.yml restart kong
```

### Kong Admin Interface

Access Kong's admin interface at:
- **Admin API**: `http://localhost:8001`
- **Kong Manager**: `http://localhost:8002`

### Health Checks

```bash
# Kong health
curl http://localhost:8001/status

# Nginx health
curl http://localhost/health

# API Manager health
curl http://localhost:8080/health
```

## 🔄 Database Integration

The API Manager automatically syncs:

1. **API Keys** from MongoDB `api_key` collection
2. **Services** from MongoDB `service` collection
3. **Consumers** based on user IDs
4. **Routes** for each service

### Sync Process

- Runs every 30 seconds (configurable)
- Creates Kong consumers for active API keys
- Creates Kong services for MongoDB services
- Maintains route mappings

## 🚨 Troubleshooting

### Common Issues

#### Kong not starting
```bash
# Check Kong logs
docker-compose -f docker-compose.kong.yml logs kong

# Check database connection
docker-compose -f docker-compose.kong.yml logs kong-database
```

#### SSL certificate issues
```bash
# Regenerate certificates
./scripts/generate-ssl.sh

# Check certificate validity
openssl x509 -in ssl/cert.pem -text -noout
```

#### API key not working
```bash
# Test API key
./scripts/manage-api-keys.sh test-api-key your_key

# Check consumer status
./scripts/manage-api-keys.sh list-consumers
```

### Log Locations

- **Kong**: `docker-compose -f docker-compose.kong.yml logs kong`
- **Nginx**: `docker-compose -f docker-compose.kong.yml logs nginx`
- **API Manager**: `docker-compose -f docker-compose.kong.yml logs kong-api-manager`

## 🔧 Customization

### Adding New Services

1. Update the `setup-kong.sh` script
2. Add service configuration
3. Restart Kong services

### Modifying Rate Limits

Edit the rate limiting configuration in `setup-kong.sh`:

```bash
# Add rate limiting plugin
curl -s -X POST $KONG_ADMIN_URL/services/${service_name}/plugins \
    --data "name=rate-limiting" \
    --data "config.minute=100" \
    --data "config.hour=6000"
```

### Custom SSL Certificates

Replace the generated certificates in the `ssl/` directory:

```bash
# Copy your certificates
cp your-cert.pem ssl/cert.pem
cp your-key.pem ssl/key.pem

# Restart nginx
docker-compose -f docker-compose.kong.yml restart nginx
```

## 📊 Monitoring

### Metrics

Kong provides built-in metrics:
- Request count
- Response time
- Error rates
- Rate limiting stats

### Logs

All services log to stdout/stderr for easy monitoring with Docker.

## 🤝 Integration with Existing Backend

The gateway integrates seamlessly with your existing backend:

1. **No code changes required** - uses existing API key structure
2. **Automatic sync** - API keys from MongoDB are automatically available
3. **Service discovery** - services from MongoDB are automatically routed
4. **Backward compatible** - existing API calls continue to work

## 📝 Production Considerations

### Security
- Use Let's Encrypt for production SSL certificates
- Implement proper firewall rules
- Regular security updates
- Monitor API key usage

### Performance
- Configure appropriate rate limits
- Monitor resource usage
- Scale Kong instances as needed
- Use Redis for distributed rate limiting

### Backup
- Regular database backups
- Configuration backups
- SSL certificate backups

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review service logs
3. Verify configuration
4. Test individual components

## 📄 License

This project is part of the AI4X platform and follows the same licensing terms.
