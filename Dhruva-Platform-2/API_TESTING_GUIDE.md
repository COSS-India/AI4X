# Dhruva Platform 2 - API Testing Guide

## 🧪 Complete API Testing Reference (PostgreSQL)

**Database:** PostgreSQL (Migrated from MongoDB)  
**Status:** Ready for Testing  
**Base URL:** `http://localhost:8000`

---

## 📋 API Endpoint Reference

### Authentication Endpoints

#### 1. User Registration
```bash
# POST /auth/register
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com", 
    "password": "securepassword123",
    "role": "USER"
  }'
```

**Expected Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Test User",
  "email": "test@example.com",
  "role": "USER",
  "created_at": "2025-01-25T10:00:00Z"
}
```

#### 2. User Login
```bash
# POST /auth/login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

**Expected Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Test User",
    "email": "test@example.com",
    "role": "USER"
  }
}
```

#### 3. Session Validation
```bash
# GET /auth/session
curl -X GET "http://localhost:8000/auth/session" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### API Key Management

#### 4. Create API Key
```bash
# POST /api-keys
curl -X POST "http://localhost:8000/api-keys" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Test API Key",
    "type": "INFERENCE",
    "data_tracking": true
  }'
```

**Expected Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "My Test API Key",
  "api_key": "dhruva_test_key_abcdef123456789",
  "masked_key": "dhru****************************789",
  "active": true,
  "type": "INFERENCE",
  "usage": 0,
  "hits": 0,
  "data_tracking": true,
  "created_timestamp": "2025-01-25T10:00:00Z"
}
```

#### 5. List API Keys
```bash
# GET /api-keys
curl -X GET "http://localhost:8000/api-keys" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 6. Update API Key
```bash
# PUT /api-keys/{api_key_id}
curl -X PUT "http://localhost:8000/api-keys/550e8400-e29b-41d4-a716-446655440001" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated API Key Name",
    "active": false
  }'
```

### Model Management

#### 7. List Models
```bash
# GET /models
curl -X GET "http://localhost:8000/models" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response (200):**
```json
{
  "models": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "model_id": "sample-model-001",
      "name": "Sample Translation Model",
      "version": "1.0",
      "description": "A sample model for testing",
      "task": {
        "type": "translation",
        "source": "en",
        "target": "hi"
      },
      "languages": [
        {
          "sourceLanguage": "en",
          "targetLanguage": "hi"
        }
      ],
      "license": "MIT",
      "domain": ["general"],
      "inference_endpoint": {
        "schema": {
          "request": {"input": "string"},
          "response": {"output": "string"}
        }
      }
    }
  ]
}
```

#### 8. Get Model by ID
```bash
# GET /models/{model_id}
curl -X GET "http://localhost:8000/models/sample-model-001" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 9. Create Model
```bash
# POST /models
curl -X POST "http://localhost:8000/models" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "new-model-001",
    "name": "New Test Model",
    "version": "1.0",
    "description": "A new model for testing",
    "task": {
      "type": "translation",
      "source": "en",
      "target": "fr"
    },
    "languages": [
      {
        "sourceLanguage": "en",
        "targetLanguage": "fr"
      }
    ],
    "license": "Apache-2.0",
    "domain": ["general"],
    "inference_endpoint": {
      "schema": {
        "request": {"text": "string"},
        "response": {"translation": "string"}
      }
    },
    "submitter": {
      "name": "Test Submitter",
      "aboutMe": "Testing submission",
      "team": []
    }
  }'
```

### Service Management

#### 10. List Services
```bash
# GET /services
curl -X GET "http://localhost:8000/services" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 11. Get Service by ID
```bash
# GET /services/{service_id}
curl -X GET "http://localhost:8000/services/sample-service-001" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 12. Create Service
```bash
# POST /services
curl -X POST "http://localhost:8000/services" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": "new-service-001",
    "name": "New Test Service",
    "service_description": "A new service for testing",
    "hardware_description": "CPU-based inference",
    "model_id": "sample-model-001",
    "endpoint": "http://localhost:8080/translate",
    "api_key": "service-api-key-123"
  }'
```

### Feedback Management

#### 13. Submit Feedback
```bash
# POST /feedback
curl -X POST "http://localhost:8000/feedback" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key_name": "My Test API Key",
    "pipeline_input": {
      "input": [
        {
          "source": "Hello world"
        }
      ]
    },
    "pipeline_output": {
      "output": [
        {
          "target": "Bonjour le monde"
        }
      ]
    },
    "pipeline_feedback": {
      "rating": 5,
      "comments": "Excellent translation"
    }
  }'
```

#### 14. Get User Feedback
```bash
# GET /feedback
curl -X GET "http://localhost:8000/feedback" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🔧 Database Verification Commands

### Verify Data Persistence
After each API call, verify data was written to PostgreSQL:

```bash
# Check users table
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC LIMIT 5;"

# Check API keys table
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
SELECT id, name, masked_key, active, user_id, created_timestamp FROM api_keys ORDER BY created_timestamp DESC LIMIT 5;"

# Check models table
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
SELECT id, model_id, name, version, task FROM models ORDER BY created_at DESC LIMIT 5;"

# Check services table
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
SELECT id, service_id, name, model_id, endpoint FROM services ORDER BY created_at DESC LIMIT 5;"

# Check feedback table
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
SELECT id, user_id, api_key_name, created_at FROM feedback ORDER BY created_at DESC LIMIT 5;"
```

### Verify Relationships
```bash
# Check foreign key relationships
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
SELECT u.name, u.email, COUNT(ak.id) as api_key_count 
FROM users u 
LEFT JOIN api_keys ak ON u.id = ak.user_id 
GROUP BY u.id, u.name, u.email;"

# Check services-models relationship
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
SELECT s.name as service_name, m.name as model_name 
FROM services s 
LEFT JOIN models m ON s.model_id = m.model_id;"
```

---

## 🚨 Error Scenarios Testing

### Authentication Errors
```bash
# Invalid credentials (401)
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "wrong@email.com", "password": "wrongpassword"}'

# Missing authorization (401)
curl -X GET "http://localhost:8000/api-keys"

# Invalid token (401)
curl -X GET "http://localhost:8000/api-keys" \
  -H "Authorization: Bearer invalid_token"
```

### Validation Errors
```bash
# Invalid email format (400)
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "email": "invalid-email", "password": "pass"}'

# Duplicate email (409)
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "email": "admin@dhruva.co", "password": "pass"}'
```

### Resource Not Found
```bash
# Non-existent model (404)
curl -X GET "http://localhost:8000/models/non-existent-model" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Non-existent service (404)
curl -X GET "http://localhost:8000/services/non-existent-service" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 📊 Expected Response Codes

| Scenario | HTTP Code | Description |
|----------|-----------|-------------|
| Successful GET | 200 | Resource found and returned |
| Successful POST | 201 | Resource created successfully |
| Successful PUT | 200 | Resource updated successfully |
| Successful DELETE | 204 | Resource deleted successfully |
| Bad Request | 400 | Invalid request data |
| Unauthorized | 401 | Missing or invalid authentication |
| Forbidden | 403 | Insufficient permissions |
| Not Found | 404 | Resource does not exist |
| Conflict | 409 | Resource already exists |
| Server Error | 500 | Internal server error |

---

## 🔍 Testing Checklist

### Pre-Testing Setup
- [ ] PostgreSQL databases are healthy
- [ ] Application server is running on port 8000
- [ ] Sample data exists in database
- [ ] API documentation accessible at `/docs`

### Authentication Flow
- [ ] User registration works
- [ ] User login returns valid JWT token
- [ ] Session validation with token works
- [ ] Invalid credentials return 401

### API Key Management
- [ ] API key creation works
- [ ] API keys list correctly
- [ ] API key updates work
- [ ] API key deletion works

### Model Operations
- [ ] Models list correctly
- [ ] Individual model retrieval works
- [ ] Model creation works
- [ ] Model updates work

### Service Operations
- [ ] Services list correctly
- [ ] Individual service retrieval works
- [ ] Service creation works
- [ ] Service updates work

### Feedback System
- [ ] Feedback submission works
- [ ] Feedback retrieval works
- [ ] Feedback data persists in PostgreSQL

### Database Verification
- [ ] All operations write to PostgreSQL
- [ ] Foreign key relationships maintained
- [ ] JSONB data properly stored
- [ ] Timestamps automatically set

---

*For deployment instructions, see `DEPLOYMENT_GUIDE.md`*  
*For troubleshooting, see `TROUBLESHOOTING_GUIDE.md`*
