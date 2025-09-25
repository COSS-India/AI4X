# Dhruva Platform 2 - PostgreSQL Deployment Guide

## 🚀 Complete MongoDB to PostgreSQL Migration Deployment

**Status:** ✅ **MIGRATION SUCCESSFULLY COMPLETED**  
**Date:** January 25, 2025  
**Database:** MongoDB → PostgreSQL (Fully Migrated)

---

## 📋 Prerequisites

### System Requirements
- **Docker**: Version 20.10+ 
- **Docker Compose**: Version 2.0+
- **Operating System**: Windows with WSL2, Linux, or macOS
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Storage**: Minimum 20GB free space

### Required Ports
- `5432`: TimescaleDB (analytics)
- `5433`: PostgreSQL App Database
- `5434`: PostgreSQL Log Database  
- `6379`: Redis
- `8000`: API Server
- `8082`: PgAdmin (Database Management)
- `5555`: Celery Flower (Task Monitoring)
- `5672`: RabbitMQ
- `15672`: RabbitMQ Management

---

## 🗄️ Database Architecture (Post-Migration)

### PostgreSQL Databases
```
dhruva-platform-app-db-pg (Port 5433)
├── users (UUID primary keys)
├── api_keys (Foreign keys to users)
├── models (JSONB for complex data)
├── services (Foreign keys to models)
├── sessions (Foreign keys to users)
└── feedback (JSONB for ULCA structures)

dhruva-platform-log-db-pg (Port 5434)
└── log_entries (Application logging)
```

### Key Features
- **ACID Compliance**: Full transactional integrity
- **UUID Primary Keys**: Consistent across all tables
- **JSONB Columns**: Flexible document storage where needed
- **Foreign Key Constraints**: Enforced data relationships
- **Automatic Timestamps**: Created/updated tracking

---

## 🚀 Step-by-Step Deployment

### Step 1: Environment Setup
```bash
# Navigate to project directory
cd Dhruva-Platform-2

# Verify environment file exists and is configured
cat .env | grep -E "APP_DB_CONNECTION_STRING|LOG_DB_CONNECTION_STRING"
```

**Expected Output:**
```
APP_DB_CONNECTION_STRING=postgresql://dhruvaadmin:dhruva123@dhruva-platform-app-db-pg:5432/dhruva_app
LOG_DB_CONNECTION_STRING=postgresql://dhruvalogadmin:dhruvalog123@dhruva-platform-log-db-pg:5432/dhruva_log
```

### Step 2: Start PostgreSQL Infrastructure
```bash
# Start PostgreSQL databases and supporting services
docker compose -f docker-compose-db.yml up -d

# Wait for health checks (2-3 minutes)
docker ps --format "table {{.Names}}\t{{.Status}}"
```

**Expected Services:**
- ✅ `dhruva-platform-app-db-pg` (healthy)
- ✅ `dhruva-platform-log-db-pg` (healthy)
- ✅ `dhruva-platform-redis` (healthy)
- ✅ `timescaledb` (healthy)
- ✅ `dhruva-platform-pgadmin` (running)

### Step 3: Verify PostgreSQL Health
```bash
# Test app database connectivity
docker exec dhruva-platform-app-db-pg pg_isready -U dhruvaadmin -d dhruva_app

# Verify schema and data
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "SELECT COUNT(*) FROM users;"
```

**Expected Output:**
```
/var/run/postgresql:5432 - accepting connections
 count 
-------
     1
```

### Step 4: Start Metering Services
```bash
# Start Celery and RabbitMQ services
docker compose -f docker-compose-metering.yml up -d

# Verify RabbitMQ is healthy
docker exec dhruva-platform-rabbitmq rabbitmq-diagnostics check_port_connectivity
```

### Step 5: Start Application Services
```bash
# Start main application services
docker compose -f docker-compose-app.yml up -d

# Monitor startup logs
docker logs -f dhruva-platform-server
```

### Step 6: Health Check Verification
```bash
# Verify all services are running
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Test API endpoint (once server is ready)
curl -s http://localhost:8000/ || echo "Server starting up..."
```

---

## 🔧 Configuration Reference

### Environment Variables

#### PostgreSQL Configuration
```bash
# App Database
POSTGRES_APP_DB_USERNAME=dhruvaadmin
POSTGRES_APP_DB_PASSWORD=dhruva123
POSTGRES_APP_DB_NAME=dhruva_app
POSTGRES_APP_DB_HOST=dhruva-platform-app-db-pg
POSTGRES_APP_DB_PORT=5432

# Log Database  
POSTGRES_LOG_DB_USERNAME=dhruvalogadmin
POSTGRES_LOG_DB_PASSWORD=dhruvalog123
POSTGRES_LOG_DB_NAME=dhruva_log
POSTGRES_LOG_DB_HOST=dhruva-platform-log-db-pg
POSTGRES_LOG_DB_PORT=5432

# Connection Strings
APP_DB_CONNECTION_STRING=postgresql://dhruvaadmin:dhruva123@dhruva-platform-app-db-pg:5432/dhruva_app
LOG_DB_CONNECTION_STRING=postgresql://dhruvalogadmin:dhruvalog123@dhruva-platform-log-db-pg:5432/dhruva_log
```

#### TimescaleDB Configuration
```bash
TIMESCALE_USER=postgres
TIMESCALE_PASSWORD=password
TIMESCALE_DATABASE_NAME=dhruva_metering
TIMESCALE_PORT=5432
```

#### Redis Configuration
```bash
REDIS_HOST=dhruva-platform-redis
REDIS_PORT=6379
REDIS_PASSWORD=dhruva123
REDIS_DB=0
```

---

## 🗃️ Database Initialization

### Automatic Schema Creation
The PostgreSQL schema is automatically created on first startup via:
- `postgresql_schema.sql` - Complete table definitions
- `seed_postgresql.sql` - Sample data insertion
- `populate_postgresql.py` - Python-based seeding

### Manual Schema Verification
```bash
# Connect to database
docker exec -it dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app

# List all tables
\dt

# Describe table structure
\d users
\d api_keys
\d models
\d services
```

---

## 🔍 Health Check Commands

### PostgreSQL Health
```bash
# App database
docker exec dhruva-platform-app-db-pg pg_isready -U dhruvaadmin -d dhruva_app

# Log database
docker exec dhruva-platform-log-db-pg pg_isready -U dhruvalogadmin -d dhruva_log

# Check table counts
docker exec dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app -c "
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL SELECT 'api_keys', COUNT(*) FROM api_keys
UNION ALL SELECT 'models', COUNT(*) FROM models
UNION ALL SELECT 'services', COUNT(*) FROM services;"
```

### Service Health
```bash
# All containers status
docker ps --format "table {{.Names}}\t{{.Status}}"

# Application logs
docker logs dhruva-platform-server --tail 20

# Database logs
docker logs dhruva-platform-app-db-pg --tail 10
```

---

## 🌐 Access Points

### Database Management
- **PgAdmin**: http://localhost:8082
  - Email: `admin@dhruva.co`
  - Password: `admin`

### Application Services
- **API Server**: http://localhost:8000 (when running)
- **API Documentation**: http://localhost:8000/docs (when running)
- **Celery Flower**: http://localhost:5555
- **RabbitMQ Management**: http://localhost:15672

### Direct Database Access
```bash
# App database
docker exec -it dhruva-platform-app-db-pg psql -U dhruvaadmin -d dhruva_app

# Log database  
docker exec -it dhruva-platform-log-db-pg psql -U dhruvalogadmin -d dhruva_log
```

---

## ✅ Success Criteria

### Deployment Successful When:
- [ ] All PostgreSQL containers show "healthy" status
- [ ] Database connectivity tests pass
- [ ] Schema contains all 6 tables with proper structure
- [ ] Sample data exists in all tables
- [ ] Foreign key relationships are enforced
- [ ] No MongoDB containers are running
- [ ] Application services start without PostgreSQL connection errors

### Validation Commands
```bash
# Run comprehensive validation
python3 validate_migration.py

# Quick health check
./complete_migration.sh
```

---

## 🚨 Important Notes

### Migration Status
- ✅ **MongoDB Completely Removed**: All MongoDB containers and volumes deleted
- ✅ **PostgreSQL Fully Operational**: All data migrated and verified
- ✅ **Schema Validated**: All tables, relationships, and constraints working
- ✅ **Data Integrity Confirmed**: Foreign keys and JSONB data validated

### Rollback Information
- **No Rollback Available**: MongoDB infrastructure has been completely removed
- **Data Backup**: Original MongoDB data was preserved during migration
- **Fresh Deployment**: This is now a PostgreSQL-native deployment

---

*For troubleshooting and advanced configuration, see `TROUBLESHOOTING_GUIDE.md`*
