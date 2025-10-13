# Organization Extraction Implementation Guide

## Overview

This guide explains how to implement **organization identification** for the Dhruva Observability Package. Organization extraction is **REQUIRED** for multi-tenant metrics tracking.

---

## Why Organization Extraction is Critical

The observability system uses organization names to:
- **Isolate metrics** between different clients/tenants
- **Track usage** per organization in Grafana dashboards
- **Calculate quotas** and billing information
- **Monitor SLA compliance** for each organization separately

Without proper organization extraction, all metrics will be mixed together, making multi-tenant monitoring impossible.

---

## Current Mock Implementation (⚠️ MUST REPLACE)

### Location
File: `server/observability/middleware.py` (or `dhruva_observability/middleware.py`)

### Current Code (Lines 126-135)
```python
@staticmethod
def _get_organization_from_api_key(api_key: str) -> str:
    """Map API key to organization name using consistent hashing."""
    # Organization names
    organizations = ["irctc", "kisanmitra", "bashadaan", "beml"]
    
    # Use hash of API key to consistently map to same organization
    hash_value = int(hashlib.md5(api_key.encode()).hexdigest(), 16)
    org_index = hash_value % len(organizations)
    
    return organizations[org_index]
```

### Why This is a Mock
- Uses **random hash-based mapping** instead of real organization data
- **Not suitable for production** - organizations will be randomly assigned
- No persistence or accuracy

---

## Implementation Options

You have **three options** for implementing organization extraction:

### Option 1: JWT Token with Organization Claims (Recommended)

**Best for:** Systems already using JWT authentication

#### Step 1: Update JWT Token Generation

Modify your authentication system to include organization in the JWT token:

```python
import jwt
from datetime import datetime, timedelta

def create_access_token(
    user_id: str, 
    organization: str,  # Add organization parameter
    user_email: str = None
):
    """Create JWT token with organization information."""
    payload = {
        "sub": user_id,
        "email": user_email,
        "organization": organization,  # Primary field
        "name": organization,           # Fallback field
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    
    # Use your secret key
    token = jwt.encode(payload, "your_secret_key", algorithm="HS256")
    return token

# Usage example
token = create_access_token(
    user_id="user123",
    organization="irctc",
    user_email="admin@irctc.com"
)
```

#### Step 2: Verify Middleware Can Extract

The middleware already supports JWT extraction (lines 106-158 in middleware.py):

```python
def _decode_jwt_token(self, authorization_header: str) -> Optional[Dict[str, Any]]:
    """Decode JWT token from authorization header."""
    try:
        if not authorization_header.startswith("Bearer "):
            return None
        
        token = authorization_header[7:]  # Remove "Bearer " prefix
        
        # Decode with verification (update with your secret)
        decoded_token = jwt.decode(
            token, 
            "your_secret_key",  # 🔧 UPDATE THIS
            algorithms=["HS256"]
        )
        
        return decoded_token
    except Exception as e:
        if self.config.debug:
            print(f"⚠️ JWT decoding failed: {e}")
        return None
```

**⚠️ UPDATE REQUIRED:** Replace `options={"verify_signature": False}` with proper signature verification using your secret key.

#### Step 3: Enable JWT Verification

Update the `_decode_jwt_token` method in middleware.py:

```python
def _decode_jwt_token(self, authorization_header: str) -> Optional[Dict[str, Any]]:
    """Decode JWT token from authorization header."""
    try:
        if not authorization_header.startswith("Bearer "):
            return None
        
        token = authorization_header[7:]
        
        # Get secret from environment or config
        jwt_secret = os.getenv("JWT_SECRET_KEY", "your_default_secret")
        
        # Decode WITH verification
        decoded_token = jwt.decode(
            token, 
            jwt_secret,
            algorithms=["HS256"]
        )
        
        return decoded_token
    except jwt.ExpiredSignatureError:
        if self.config.debug:
            print("⚠️ JWT token expired")
        return None
    except jwt.InvalidTokenError as e:
        if self.config.debug:
            print(f"⚠️ JWT validation failed: {e}")
        return None
```

#### Step 4: Test JWT Extraction

```bash
# Enable debug mode
export DHRUVA_ENTERPRISE_DEBUG=true

# Make a request with JWT token
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/translation/v1

# Check logs for organization extraction
docker logs dhruva-platform-server | grep "Extracted customer from JWT"
```

Expected log output:
```
🔑 Extracted customer from JWT: irctc
```

---

### Option 2: Database Mapping

**Best for:** Systems with API key to organization mapping in database

#### Step 1: Create Database Query Function

```python
# In your database layer (e.g., db/repositories.py)
from typing import Optional

async def get_organization_by_api_key(api_key: str) -> Optional[str]:
    """Get organization name from API key."""
    # Example with MongoDB
    from db.database import get_database
    
    db = get_database()
    api_key_doc = await db.api_keys.find_one({"api_key": api_key})
    
    if api_key_doc and "organization" in api_key_doc:
        return api_key_doc["organization"]
    
    return None

# Example with SQL
async def get_organization_by_api_key_sql(api_key: str) -> Optional[str]:
    """Get organization from SQL database."""
    from db.database import get_db_session
    
    async with get_db_session() as session:
        result = await session.execute(
            "SELECT organization FROM api_keys WHERE api_key = :api_key",
            {"api_key": api_key}
        )
        row = result.fetchone()
        return row[0] if row else None
```

#### Step 2: Modify Middleware to Use Database

Update `_get_organization_from_api_key` in middleware.py:

```python
async def _get_organization_from_api_key(self, api_key: str) -> str:
    """Get organization from database using API key."""
    from db.repositories import get_organization_by_api_key
    
    try:
        organization = await get_organization_by_api_key(api_key)
        
        if organization:
            if self.config.debug:
                print(f"🏢 Found organization for API key: {organization}")
            return organization
        else:
            if self.config.debug:
                print(f"⚠️ No organization found for API key, using default")
            return self.config.default_customer
            
    except Exception as e:
        if self.config.debug:
            print(f"❌ Database lookup failed: {e}")
        return self.config.default_customer
```

#### Step 3: Update `_extract_customer_app` Method

Since database lookup is async, update the method signature:

```python
async def _extract_customer_app(self, request: Request) -> tuple:
    """Extract organization and app from request headers and JWT token."""
    # First try to get customer from JWT token
    organization = self._extract_customer_from_token(request)
    
    # If not found in token, fallback to header
    if organization == self.config.default_customer:
        organization = request.headers.get("X-Customer-ID", organization)
    
    # Extract organization from API key (now async)
    auth_header = request.headers.get("authorization", "")
    
    if auth_header:
        api_key = auth_header
        if auth_header.startswith("Bearer "):
            api_key = auth_header[7:]
        
        # Async database lookup
        org_from_db = await self._get_organization_from_api_key(api_key)
        if org_from_db:
            organization = org_from_db
    
    app = request.headers.get("X-App-ID", self.config.default_app)
    
    if not self.config.is_app_allowed(app):
        app = self.config.default_app
        
    return organization, app
```

#### Step 4: Update Middleware Dispatch

Make sure the dispatch method handles async properly:

```python
async def dispatch(self, request: Request, call_next):
    """Process request through middleware."""
    if not self.config.enabled:
        return await call_next(request)
    
    start_time = time.time()
    
    # Extract metadata from request
    path = request.url.path
    method = request.method
    
    # Extract organization and app (now async)
    organization, app = await self._extract_customer_app(request)
    
    # ... rest of the code ...
```

---

### Option 3: Static Configuration File

**Best for:** Small deployments with fixed client list

#### Step 1: Create API Key Mapping File

Create `config/api_key_mapping.json`:

```json
{
  "api_keys": {
    "sk-irctc-prod-abc123": "irctc",
    "sk-kisanmitra-prod-xyz789": "kisanmitra",
    "sk-bashadaan-dev-def456": "bashadaan",
    "sk-beml-prod-ghi789": "beml"
  }
}
```

#### Step 2: Load Configuration

Update middleware.py:

```python
import json
from pathlib import Path

class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Middleware for tracking requests and collecting metrics."""
    
    def __init__(self, app, metrics_collector=None, config=None):
        super().__init__(app)
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.config = config or PluginConfig()
        
        # Load API key mapping
        self.api_key_mapping = self._load_api_key_mapping()
    
    def _load_api_key_mapping(self) -> dict:
        """Load API key to organization mapping from file."""
        try:
            mapping_file = Path("config/api_key_mapping.json")
            if mapping_file.exists():
                with open(mapping_file, 'r') as f:
                    data = json.load(f)
                    return data.get("api_keys", {})
            else:
                if self.config.debug:
                    print("⚠️ API key mapping file not found")
                return {}
        except Exception as e:
            if self.config.debug:
                print(f"❌ Failed to load API key mapping: {e}")
            return {}
    
    def _get_organization_from_api_key(self, api_key: str) -> str:
        """Get organization from API key mapping."""
        # Remove "Bearer " prefix if present
        clean_key = api_key.replace("Bearer ", "")
        
        # Lookup in mapping
        organization = self.api_key_mapping.get(clean_key)
        
        if organization:
            if self.config.debug:
                print(f"🏢 Mapped API key to organization: {organization}")
            return organization
        else:
            if self.config.debug:
                print(f"⚠️ API key not in mapping, using default")
            return self.config.default_customer
```

---

## Testing Your Implementation

### Test Script

Create `test_organization_extraction.py`:

```python
import requests
import jwt
from datetime import datetime, timedelta

# Test configuration
BASE_URL = "http://localhost:8000"
JWT_SECRET = "your_secret_key"

def create_test_token(organization: str):
    """Create a test JWT token."""
    payload = {
        "sub": "test_user",
        "organization": organization,
        "name": organization,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def test_organization_extraction():
    """Test organization extraction."""
    organizations = ["irctc", "kisanmitra", "bashadaan", "beml"]
    
    for org in organizations:
        print(f"\n🧪 Testing organization: {org}")
        
        # Create token
        token = create_test_token(org)
        
        # Make request
        response = requests.get(
            f"{BASE_URL}/enterprise/metrics",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Check if metrics contain the organization
        if org in response.text:
            print(f"  ✅ Organization '{org}' found in metrics")
        else:
            print(f"  ❌ Organization '{org}' NOT found in metrics")
        
        # Print sample metric line
        for line in response.text.split('\n'):
            if f'organization="{org}"' in line and "dhruva_enterprise_requests_total" in line:
                print(f"  📊 Sample: {line[:100]}...")
                break

if __name__ == "__main__":
    test_organization_extraction()
```

Run the test:
```bash
python test_organization_extraction.py
```

### Expected Output

```
🧪 Testing organization: irctc
  ✅ Organization 'irctc' found in metrics
  📊 Sample: dhruva_enterprise_requests_total{organization="irctc",app="app1",method="POST",endpoint="/trans...

🧪 Testing organization: kisanmitra
  ✅ Organization 'kisanmitra' found in metrics
  📊 Sample: dhruva_enterprise_requests_total{organization="kisanmitra",app="app1",method="GET",endpoin...
```

---

## Verification Checklist

After implementing organization extraction:

- [ ] **JWT tokens include organization claim** (if using Option 1)
- [ ] **Database has organization mapping** (if using Option 2)
- [ ] **Configuration file exists** (if using Option 3)
- [ ] **Debug mode enabled** for testing: `export DHRUVA_ENTERPRISE_DEBUG=true`
- [ ] **Logs show correct organization**: `docker logs dhruva-platform-server | grep organization`
- [ ] **Metrics contain organization labels**: `curl localhost:8000/enterprise/metrics | grep organization`
- [ ] **Different API keys map to different organizations**
- [ ] **Grafana dashboards filter by organization correctly**

---

## Common Issues

### Issue: All requests show "default" organization

**Cause:** Organization extraction is not working

**Solutions:**
1. Check JWT token includes organization claim
2. Verify JWT secret is correct
3. Enable debug mode and check logs
4. Test JWT decoding separately

### Issue: JWT decoding fails

**Cause:** Token signature verification failing

**Solutions:**
1. Ensure JWT_SECRET_KEY matches token generation secret
2. Check token hasn't expired
3. Verify algorithm matches (HS256, RS256, etc.)

### Issue: Database lookup returns None

**Cause:** API key not in database or wrong field name

**Solutions:**
1. Verify API key exists in database
2. Check field name is "organization" (not "org" or other variant)
3. Add logging to database query
4. Test database query separately

---

## Best Practices

### 1. Organization Naming Convention

Use consistent, lowercase identifiers:
- ✅ `irctc`, `kisanmitra`, `bashadaan`
- ❌ `IRCTC`, `Kisan Mitra`, `Basha-Daan`

### 2. JWT Token Structure

Always include:
```json
{
  "sub": "user_id",
  "organization": "irctc",  // Primary field
  "name": "IRCTC",           // Human-readable fallback
  "email": "user@irctc.com",
  "exp": 1234567890
}
```

### 3. Error Handling

Always have a fallback:
```python
organization = extract_from_jwt(token) or \
               extract_from_header(request) or \
               extract_from_database(api_key) or \
               "default"
```

### 4. Security

- ✅ **DO** verify JWT signatures
- ✅ **DO** check token expiration
- ✅ **DO** sanitize organization names
- ❌ **DON'T** use `verify_signature=False` in production
- ❌ **DON'T** expose JWT secrets in logs

---

## Example: Complete Implementation (Option 1 - JWT)

Here's a complete working example using JWT tokens:

```python
# auth/token_provider.py
import jwt
import os
from datetime import datetime, timedelta
from typing import Dict, Any

JWT_SECRET = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

def create_access_token(user_id: str, organization: str, **extra_claims) -> str:
    """Create JWT access token with organization."""
    payload = {
        "sub": user_id,
        "organization": organization,
        "name": organization,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        **extra_claims
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and verify JWT token."""
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
```

```python
# observability/middleware.py (update)
import os
import jwt

class ObservabilityMiddleware(BaseHTTPMiddleware):
    
    def _decode_jwt_token(self, authorization_header: str):
        """Decode JWT token with verification."""
        try:
            if not authorization_header.startswith("Bearer "):
                return None
            
            token = authorization_header[7:]
            jwt_secret = os.getenv("JWT_SECRET_KEY", "your-secret-key")
            
            decoded = jwt.decode(
                token,
                jwt_secret,
                algorithms=["HS256"]
            )
            
            return decoded
            
        except jwt.ExpiredSignatureError:
            if self.config.debug:
                print("⚠️ JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            if self.config.debug:
                print(f"⚠️ JWT invalid: {e}")
            return None
    
    def _extract_customer_from_token(self, request: Request) -> str:
        """Extract organization from JWT token."""
        auth_header = request.headers.get("authorization", "")
        
        if auth_header:
            decoded = self._decode_jwt_token(auth_header)
            if decoded:
                # Try multiple fields
                org = (decoded.get("organization") or 
                       decoded.get("org") or 
                       decoded.get("name") or 
                       decoded.get("company"))
                
                if org:
                    if self.config.debug:
                        print(f"🔑 Extracted organization: {org}")
                    return org
        
        return self.config.default_customer
```

---

## Summary

1. **Choose an implementation option** (JWT recommended)
2. **Remove the mock implementation** from middleware.py
3. **Implement your chosen method** following the examples above
4. **Test thoroughly** using the test script
5. **Verify in Grafana** that metrics are properly separated by organization

**Remember:** Organization extraction is **mandatory** for the observability package to work correctly in a multi-tenant environment!

---

**Document Version:** 1.0  
**Last Updated:** October 2025

