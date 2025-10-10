# JWT Token Customer Extraction

## Overview

The `ObservabilityMiddleware` has been enhanced to extract customer names from JWT tokens in the `authorization` header. This allows for automatic customer identification without requiring additional headers.

## How it Works

### 1. Token Extraction Process

The middleware follows this priority order for customer identification:

1. **JWT Token (Primary)**: Extracts customer name from the `name` field in the JWT token
2. **Fallback to `sub`**: If `name` is not available, uses the `sub` field
3. **Header Fallback**: Falls back to `X-Customer-ID` header
4. **Default**: Uses configured default customer

### 2. JWT Token Structure

Your JWT token contains:
```json
{
  "sub": "682728d858943e6d3bad20d7",
  "name": "Admin2",
  "exp": 1761642844.1568654,
  "iat": 1759050844.1568658,
  "sess_id": "68d8fc5c8b453f5db65abcda"
}
```

The middleware extracts `"Admin2"` from the `name` field as the customer identifier.

### 3. Updated Middleware Features

#### New Methods Added:

- `_decode_jwt_token()`: Safely decodes JWT tokens without signature verification
- `_extract_customer_from_token()`: Extracts customer name from decoded token
- Enhanced `_extract_customer_app()`: Uses JWT token as primary source

#### Security Considerations:

- Token decoding is done **without signature verification** for customer name extraction
- This is safe for metrics collection as we only extract the `name` field
- For security-critical operations, proper token verification should be implemented

### 4. Debug Logging

When `config.debug = True`, the middleware logs:
- JWT decoding success/failure
- Extracted customer name
- Request details including customer and app

Example debug output:
```
🔑 Extracted customer from JWT: Admin2
🔍 Request: POST /services/inference/translation -> Service: translation, Customer: Admin2, App: default_app
```

## Usage Example

```python
from dhruva_observability import ObservabilityMiddleware, PluginConfig

# Enable debug logging to see JWT extraction
config = PluginConfig(
    enabled=True,
    debug=True,
    default_customer="unknown",
    default_app="default_app"
)

app.add_middleware(ObservabilityMiddleware, config=config)
```

## Testing

Use the provided test script to verify JWT decoding:

```bash
python3 test_jwt_decoding.py
```

This will decode your example token and show the extracted customer name.

## Authorization Header Format

The middleware expects the authorization header in the format:
```
authorization: Bearer <jwt_token>
```

Example from your curl request:
```bash
-H 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInRvayI6ImFjY2VzcyIsInR5cCI6IkpXVCJ9...'
```

## Dependencies

Added `PyJWT>=2.0.0` to requirements.txt for JWT token decoding functionality.

## Error Handling

- If JWT decoding fails, the middleware gracefully falls back to header-based extraction
- Malformed tokens or missing authorization headers don't break the request flow
- Debug logging shows JWT decoding errors when enabled

## Benefits

1. **Automatic Customer Detection**: No need for additional `X-Customer-ID` headers
2. **Backward Compatibility**: Still supports header-based customer identification
3. **Secure**: Only extracts customer name, doesn't validate token signature
4. **Robust**: Graceful fallback handling for invalid tokens
