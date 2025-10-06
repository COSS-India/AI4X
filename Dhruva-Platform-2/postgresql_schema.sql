-- PostgreSQL Schema for Dhruva Platform 2
-- Migration from MongoDB to PostgreSQL

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables if they exist (for clean migration)
DROP TABLE IF EXISTS feedback CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS api_keys CASCADE;
DROP TABLE IF EXISTS services CASCADE;
DROP TABLE IF EXISTS models CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Users table (from MongoDB 'user' collection)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('ADMIN', 'USER', 'DEVELOPER', 'CONSUMER')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Models table (from MongoDB 'model' collection)
CREATE TABLE models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id VARCHAR(255) UNIQUE NOT NULL,
    version VARCHAR(100) NOT NULL,
    submitted_on BIGINT NOT NULL,
    updated_on BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    ref_url VARCHAR(500),
    task JSONB NOT NULL,
    languages JSONB NOT NULL DEFAULT '[]',
    license VARCHAR(255),
    domain JSONB NOT NULL DEFAULT '[]',
    inference_endpoint JSONB NOT NULL,
    benchmarks JSONB DEFAULT NULL,
    submitter JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Services table (from MongoDB 'service' collection)
CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    service_description TEXT,
    hardware_description TEXT,
    published_on BIGINT NOT NULL,
    model_id VARCHAR(255),
    endpoint VARCHAR(500) NOT NULL,
    api_key VARCHAR(255),
    health_status JSONB DEFAULT NULL,
    benchmarks JSONB DEFAULT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(model_id) ON DELETE SET NULL
);

-- API Keys table (from MongoDB 'api_key' collection)
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    masked_key VARCHAR(255) NOT NULL,
    active BOOLEAN DEFAULT true,
    user_id UUID NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'INFERENCE',
    created_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    usage INTEGER DEFAULT 0,
    hits INTEGER DEFAULT 0,
    data_tracking BOOLEAN DEFAULT false,
    services JSONB DEFAULT '[]',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Sessions table (from MongoDB 'session' collection)
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    type VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Feedback table (from MongoDB 'feedback' collection)
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    api_key_name VARCHAR(255),
    pipeline_input JSONB DEFAULT NULL,
    pipeline_output JSONB DEFAULT NULL,
    suggested_pipeline_output JSONB DEFAULT NULL,
    pipeline_feedback JSONB DEFAULT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

CREATE INDEX idx_models_model_id ON models(model_id);
CREATE INDEX idx_models_name ON models(name);
CREATE INDEX idx_models_task ON models USING GIN(task);

CREATE INDEX idx_services_service_id ON services(service_id);
CREATE INDEX idx_services_model_id ON services(model_id);
CREATE INDEX idx_services_name ON services(name);

CREATE INDEX idx_api_keys_api_key ON api_keys(api_key);
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_name ON api_keys(name);
CREATE INDEX idx_api_keys_active ON api_keys(active);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_type ON sessions(type);
CREATE INDEX idx_sessions_timestamp ON sessions(timestamp);

CREATE INDEX idx_feedback_user_id ON feedback(user_id);
CREATE INDEX idx_feedback_api_key_name ON feedback(api_key_name);
CREATE INDEX idx_feedback_created_at ON feedback(created_at);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_models_updated_at BEFORE UPDATE ON models FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_services_updated_at BEFORE UPDATE ON services FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_api_keys_updated_at BEFORE UPDATE ON api_keys FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_feedback_updated_at BEFORE UPDATE ON feedback FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
