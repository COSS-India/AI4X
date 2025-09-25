# Dhruva Platform 2 - Troubleshooting Guide

## 🔧 PostgreSQL Migration Troubleshooting

**Migration Status:** ✅ **COMPLETED**  
**Database:** PostgreSQL (MongoDB Fully Removed)

---

## 🚨 Common Issues and Solutions

### 1. PostgreSQL Connection Issues

#### Problem: "Connection refused" or "pg_isready fails"
```bash
# Symptoms
docker exec dhruva-platform-app-db-pg pg_isready -U dhruvaadmin
# Output: pg_isready: error: connection to server on socket...
```

**Solutions:**
```bash
# Check container status
docker ps | grep postgres

# Restart PostgreSQL containers
docker restart dhruva-platform-app-db-pg dhruva-platform-log-db-pg

# Check logs for errors
docker logs dhruva-platform-app-db-pg --tail 20

# Verify network connectivity
docker exec dhruva-platform-app-db-pg ping dhruva-platform-redis
```

#### Problem: "Authentication failed for user"
```bash
# Check environment variables
docker exec dhruva-platform-app-db-pg env | grep POSTGRES

# Reset password if needed
docker exec dhruva-platform-app-db-pg psql -U postgres -c "ALTER USER dhruvaadmin PASSWORD 'dhruva123';"
```

### 2. Application Server Issues

#### Problem: Server won't start - "KeyError: 'TIMESCALE_USER'"
```bash
# Check missing environment variables
docker logs dhruva-platform-server --tail 10
```

**Solution:**
```bash
# Add missing TimescaleDB environment variables to .env
echo "TIMESCALE_USER=postgres" >> .env
echo "TIMESCALE_PASSWORD=password" >> .env
echo "TIMESCALE_DATABASE_NAME=dhruva_metering" >> .env
echo "TIMESCALE_PORT=5432" >> .env

# Restart server
docker restart dhruva-platform-server
```

#### Problem: "Invalid URI scheme: URI must begin with 'mongodb://'"
This indicates the application is still trying to use MongoDB.

**Solution:**
```bash
# Verify environment variables are correct
grep -E "APP_DB_CONNECTION_STRING|LOG_DB_CONNECTION_STRING" .env

# Should show PostgreSQL URLs:
# APP_DB_CONNECTION_STRING=postgresql://dhruvaadmin:dhruva123@dhruva-platform-app-db-pg:5432/dhruva_app
# LOG_DB_CONNECTION_STRING=postgresql://dhruvalogadmin:dhruvalog123@dhruva-platform-log-db-pg:5432/dhruva_log

# If incorrect, fix the URLs and restart
docker restart dhruva-platform-server
```

#### Problem: "ModuleNotFoundError: No module named 'psycopg2'"
**Solution:**
```bash
# Install PostgreSQL driver in container
docker exec dhruva-platform-server pip install psycopg2-binary

# Or rebuild image with updated requirements.txt
docker build -t dhruva-platform-server:latest-pg15 ./server
docker restart dhruva-platform-server
```

### 3. Database Schema Issues

#### Problem: "Table doesn't exist" errors
```bash
# Check if tables were created
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "\dt"
```

**Solution:**
```bash
# Manually run schema creation
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -f /docker-entrypoint-initdb.d/01-schema.sql

# Or copy and run schema file
docker cp postgresql_schema.sql dhruva-platform-app-db-pg:/tmp/schema.sql
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -f /tmp/schema.sql
```

#### Problem: Foreign key constraint violations
```bash
# Check constraint violations
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
SELECT conname, conrelid::regclass, confrelid::regclass 
FROM pg_constraint 
WHERE contype = 'f';"
```

**Solution:**
```bash
# Temporarily disable constraints for data migration
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
SET session_replication_role = replica;
-- Run your data migration here
SET session_replication_role = DEFAULT;"
```

### 4. Data Migration Issues

#### Problem: UUID format errors
```bash
# Check for invalid UUID values
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
SELECT id FROM users WHERE id::text !~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$';"
```

**Solution:**
```bash
# Generate new UUIDs for invalid entries
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
UPDATE users SET id = uuid_generate_v4() WHERE id IS NULL;"
```

#### Problem: JSONB data corruption
```bash
# Check for invalid JSON
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
SELECT id, task FROM models WHERE NOT (task::text)::json IS NOT NULL;"
```

**Solution:**
```bash
# Fix invalid JSON data
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
UPDATE models SET task = '{}' WHERE task IS NULL OR task::text = '';"
```

### 5. Performance Issues

#### Problem: Slow queries
```bash
# Enable query logging
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();"

# Check slow queries
docker logs dhruva-platform-app-db-pg | grep "duration:"
```

**Solution:**
```bash
# Add missing indexes
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
CREATE INDEX CONCURRENTLY idx_api_keys_user_id_active ON api_keys(user_id, active);
CREATE INDEX CONCURRENTLY idx_services_model_id_active ON services(model_id) WHERE model_id IS NOT NULL;"
```

#### Problem: High memory usage
```bash
# Check PostgreSQL memory settings
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
SHOW shared_buffers;
SHOW work_mem;
SHOW maintenance_work_mem;"
```

**Solution:**
```bash
# Optimize PostgreSQL settings
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET work_mem = '4MB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
SELECT pg_reload_conf();"
```

---

## 🔍 Diagnostic Commands

### System Health Check
```bash
# Complete system status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Resource usage
docker stats --no-stream

# Network connectivity
docker network ls
docker network inspect dhruva-network
```

### Database Health Check
```bash
# PostgreSQL status
docker exec dhruva-platform-app-db-pg pg_isready -U dhruvaadmin -d dhruva_app
docker exec dhruva-platform-log-db-pg pg_isready -U dhruvalogadmin -d dhruva_log

# Database sizes
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
SELECT pg_size_pretty(pg_database_size('dhruva_app')) as app_db_size;"

# Table sizes
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
SELECT tablename, pg_size_pretty(pg_total_relation_size('public.'||tablename)) AS size 
FROM pg_tables WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size('public.'||tablename) DESC;"
```

### Application Health Check
```bash
# Server logs
docker logs dhruva-platform-server --tail 50

# Worker logs
docker logs dhruva-platform-worker --tail 20

# Celery task status
curl -s http://localhost:5555/api/workers | jq '.'
```

---

## 📊 Log Analysis

### PostgreSQL Logs
```bash
# Connection logs
docker logs dhruva-platform-app-db-pg 2>&1 | grep "connection"

# Error logs
docker logs dhruva-platform-app-db-pg 2>&1 | grep "ERROR"

# Query logs (if enabled)
docker logs dhruva-platform-app-db-pg 2>&1 | grep "duration:"
```

### Application Logs
```bash
# Python errors
docker logs dhruva-platform-server 2>&1 | grep "ERROR"

# Database connection errors
docker logs dhruva-platform-server 2>&1 | grep -i "database\|connection\|postgresql"

# Import errors
docker logs dhruva-platform-server 2>&1 | grep "ImportError\|ModuleNotFoundError"
```

---

## 🚀 Performance Optimization

### Database Optimization
```bash
# Update table statistics
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "ANALYZE;"

# Vacuum tables
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "VACUUM ANALYZE;"

# Check index usage
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch 
FROM pg_stat_user_indexes 
ORDER BY idx_tup_read DESC;"
```

### Connection Pool Optimization
```bash
# Check active connections
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
SELECT count(*) as active_connections FROM pg_stat_activity WHERE state = 'active';"

# Optimize connection settings
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
SELECT pg_reload_conf();"
```

---

## 🔄 Recovery Procedures

### Database Recovery
```bash
# Create backup
docker exec dhruva-platform-app-db-pg pg_dump -U dhruvaadmin dhruva_app > backup.sql

# Restore from backup
docker exec -i dhruva-platform-app-db-pg psql -U dhruvaadmin dhruva_app < backup.sql
```

### Container Recovery
```bash
# Restart all services
docker compose -f docker-compose-db.yml -f docker-compose-metering.yml -f docker-compose-app.yml restart

# Force recreate containers
docker compose -f docker-compose-db.yml -f docker-compose-metering.yml -f docker-compose-app.yml up --force-recreate -d
```

### Data Integrity Check
```bash
# Check foreign key constraints
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
SELECT conname, conrelid::regclass AS table_name, confrelid::regclass AS referenced_table
FROM pg_constraint 
WHERE contype = 'f' AND NOT convalidated;"

# Validate all constraints
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
ALTER TABLE api_keys VALIDATE CONSTRAINT api_keys_user_id_fkey;
ALTER TABLE sessions VALIDATE CONSTRAINT sessions_user_id_fkey;
ALTER TABLE feedback VALIDATE CONSTRAINT feedback_user_id_fkey;"
```

---

## 📞 Support Information

### Migration Status
- ✅ **MongoDB Completely Removed**
- ✅ **PostgreSQL Fully Operational**
- ✅ **All Data Migrated Successfully**
- ✅ **Schema Validated and Optimized**

### Key Files for Reference
- `postgresql_schema.sql` - Complete database schema
- `DEPLOYMENT_GUIDE.md` - Deployment instructions
- `API_TESTING_GUIDE.md` - API testing procedures
- `MIGRATION_COMPLETION_REPORT.md` - Migration summary

### Emergency Contacts
- Database Issues: Check PostgreSQL logs and connection settings
- Application Issues: Review server logs and environment variables
- Performance Issues: Run diagnostic queries and optimize indexes

---

*This troubleshooting guide covers the most common issues encountered during and after the MongoDB to PostgreSQL migration.*
