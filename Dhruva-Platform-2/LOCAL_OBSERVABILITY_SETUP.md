# Local Observability Package Setup

## Overview
This document describes how we configured the Dhruva Platform to use the **local observability package** instead of installing from TestPyPI.

## Changes Made

### 1. Copied Local Package to Server Directory
```bash
cp -r dhruva_observability_package/dhruva_observability server/
```

This copies the latest observability code directly into the server directory so it gets included in the Docker build.

### 2. Requirements.txt Configuration
The `server/requirements.txt` already has the TestPyPI package commented out:
```
# dhruva-observability==1.0.9
```

### 3. Server Code (main.py)
The server imports the observability plugin locally:
```python
from dhruva_observability import ObservabilityPlugin
```

Since we copied the package to `server/dhruva_observability/`, Python will find it locally first before looking for installed packages.

## Key Features of the Latest Middleware

### Customer Name Extraction from JWT
The middleware now extracts customer names from JWT tokens in the Authorization header:

```python
def _extract_customer_from_token(self, request: Request) -> str:
    """Extract customer name from JWT token in authorization header."""
    auth_header = request.headers.get("authorization", "")
    
    if auth_header:
        decoded_token = self._decode_jwt_token(auth_header)
        if decoded_token:
            # Extract customer name from 'name' field in token
            customer_name = decoded_token.get("name")
            if customer_name:
                return customer_name
            
            # Fallback: try to extract from 'sub' field if 'name' is not available
            sub = decoded_token.get("sub")
            if sub:
                return sub
    
    return self.config.default_customer
```

### Debug Logging
When `DHRUVA_ENTERPRISE_DEBUG=true`, the middleware logs detailed request information:
```python
print(f"🔍 Request: {method} {path} -> Service: {service_type}, Customer: {customer}, App: {app}")
print(f"🔑 Extracted customer from JWT: {customer_name}")
```

## Deployment Steps

### 1. Stop All Containers
```bash
sudo docker compose -f docker-compose-db.yml -f docker-compose-metering.yml -f docker-compose-monitoring.yml -f docker-compose-app.yml down
```

### 2. Clear Prometheus Data (Optional)
```bash
sudo rm -rf prometheus/data
```

### 3. Clear Docker Build Cache (Optional)
```bash
sudo docker builder prune -af
```

### 4. Copy Local Package
```bash
cp -r dhruva_observability_package/dhruva_observability server/
```

### 5. Rebuild Server and Worker Images
```bash
sudo docker compose -f docker-compose-db.yml -f docker-compose-metering.yml -f docker-compose-monitoring.yml -f docker-compose-app.yml build server worker
```

### 6. Start All Services
```bash
sudo docker compose -f docker-compose-db.yml -f docker-compose-metering.yml -f docker-compose-monitoring.yml -f docker-compose-app.yml up -d
```

## Testing Customer Name Extraction

### 1. Generate a Test JWT Token
```bash
python3 -c "
import jwt
import datetime

payload = {
    'name': 'TestCustomer123',
    'sub': 'user@example.com',
    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
}

token = jwt.encode(payload, 'secret', algorithm='HS256')
print(f'Bearer {token}')
"
```

### 2. Make a Request with the Token
```bash
TOKEN="<your-generated-token>"
curl -X GET "http://localhost:8000/enterprise/health" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Check the Logs
```bash
sudo docker logs dhruva-platform-server --tail 20 | grep "🔍\|🔑"
```

You should see output like:
```
🔍 Request: GET /enterprise/health -> Service: enterprise, Customer: TestCustomer123, App: default
🔑 Extracted customer from JWT: TestCustomer123
```

## Environment Variables (docker-compose-app.yml)

The observability plugin is configured with these environment variables:

```yaml
environment:
  - DHRUVA_ENTERPRISE_ENABLED=true
  - DHRUVA_ENTERPRISE_DEBUG=true
  - DHRUVA_ENTERPRISE_CUSTOMERS=cust1,cust2,default
  - DHRUVA_ENTERPRISE_APPS=app1,app2,default
  - DHRUVA_ENTERPRISE_METRICS_PATH=/enterprise/metrics
  - DHRUVA_ENTERPRISE_HEALTH_PATH=/enterprise/health
```

## Prometheus Metrics

The middleware tracks metrics by customer and app:
- `dhruva_enterprise_requests_total{customer="TestCustomer123", app="default"}`
- `dhruva_enterprise_request_duration_seconds{customer="TestCustomer123", app="default"}`

Access metrics at: http://localhost:8000/enterprise/metrics

## Troubleshooting

### Check if Local Package is Being Used
```bash
sudo docker exec dhruva-platform-server ls -la /app/dhruva_observability/
```

### Check Installed Package Version vs Local Code
```bash
sudo docker exec dhruva-platform-server cat /app/dhruva_observability/middleware.py | grep "# Debug logging" -A 2
```

Should show:
```python
# Debug logging
if self.config.debug:
    print(f"🔍 Request: {method} {path} -> Service: {service_type}, Customer: {customer}, App: {app}")
```

### View Real-time Logs
```bash
sudo docker logs -f dhruva-platform-server
```

## Benefits of Local Package Approach

1. **No TestPyPI Dependency**: No need to publish to TestPyPI for every change
2. **Instant Updates**: Changes to local code are immediately available after rebuild
3. **Development Speed**: Faster iteration during development
4. **Version Control**: The exact code version is in the repository

## Future Migration to Published Package

When ready to use a published package:

1. Uncomment in `server/requirements.txt`:
   ```
   dhruva-observability==1.0.10
   ```

2. Remove the local copy:
   ```bash
   rm -rf server/dhruva_observability/
   ```

3. Rebuild containers
