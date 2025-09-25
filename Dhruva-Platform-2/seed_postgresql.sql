-- Seed PostgreSQL database with initial data
-- This script creates sample data for testing the migration

-- Insert a default admin user
INSERT INTO users (id, name, email, password, role) VALUES 
(
    '550e8400-e29b-41d4-a716-446655440000',
    'Default Admin',
    'admin@dhruva.co',
    '$argon2id$v=19$m=65536,t=3,p=4$hashed_password_here',
    'ADMIN'
) ON CONFLICT (email) DO NOTHING;

-- Insert a sample model
INSERT INTO models (
    id, model_id, version, submitted_on, updated_on, name, description, 
    ref_url, task, languages, license, domain, inference_endpoint, 
    benchmarks, submitter
) VALUES (
    '550e8400-e29b-41d4-a716-446655440001',
    'sample-model-001',
    '1.0',
    1640995200,
    1640995200,
    'Sample Translation Model',
    'A sample model for testing',
    'https://example.com/model',
    '{"type": "translation", "source": "en", "target": "hi"}',
    '[{"sourceLanguage": "en", "targetLanguage": "hi"}]',
    'MIT',
    '["general"]',
    '{"schema": {"request": {"input": "string"}, "response": {"output": "string"}}}',
    NULL,
    '{"name": "Test Submitter", "aboutMe": "Test submission", "team": []}'
) ON CONFLICT (model_id) DO NOTHING;

-- Insert a sample service
INSERT INTO services (
    id, service_id, name, service_description, hardware_description,
    published_on, model_id, endpoint, api_key, health_status, benchmarks
) VALUES (
    '550e8400-e29b-41d4-a716-446655440002',
    'sample-service-001',
    'Sample Translation Service',
    'A sample service for testing',
    'CPU-based inference',
    1640995200,
    'sample-model-001',
    'http://localhost:8080/translate',
    'sample-api-key',
    '{"status": "healthy", "lastUpdated": "2024-01-01T00:00:00Z"}',
    NULL
) ON CONFLICT (service_id) DO NOTHING;

-- Insert a sample API key
INSERT INTO api_keys (
    id, name, api_key, masked_key, active, user_id, type,
    created_timestamp, usage, hits, data_tracking, services
) VALUES (
    '550e8400-e29b-41d4-a716-446655440003',
    'test-api-key',
    'dhruva_test_key_12345678901234567890',
    'dhru****************************7890',
    true,
    '550e8400-e29b-41d4-a716-446655440000',
    'INFERENCE',
    CURRENT_TIMESTAMP,
    0,
    0,
    false,
    '[]'
) ON CONFLICT (api_key) DO NOTHING;

-- Insert a sample session
INSERT INTO sessions (
    id, user_id, type, timestamp
) VALUES (
    '550e8400-e29b-41d4-a716-446655440004',
    '550e8400-e29b-41d4-a716-446655440000',
    'login',
    CURRENT_TIMESTAMP
);

-- Verify the data was inserted
SELECT 'Users:' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'Models:', COUNT(*) FROM models
UNION ALL
SELECT 'Services:', COUNT(*) FROM services
UNION ALL
SELECT 'API Keys:', COUNT(*) FROM api_keys
UNION ALL
SELECT 'Sessions:', COUNT(*) FROM sessions
UNION ALL
SELECT 'Feedback:', COUNT(*) FROM feedback;
