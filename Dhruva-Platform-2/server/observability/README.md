# Dhruva Observability Package

> **Enterprise-grade monitoring and metrics collection for Dhruva Platform deployments**

---

## 🎯 What Is This?

The Dhruva Observability Package provides comprehensive monitoring, metrics tracking, and real-time analytics for Dhruva platform deployments. It enables multi-tenant metrics collection, SLA tracking, and business analytics through Prometheus and Grafana.

## ✨ Key Features

- **Multi-tenant metrics collection** with organization-level isolation
- **Automatic service detection** (Translation, TTS, ASR, LLM, NER, etc.)
- **Real-time monitoring** via Prometheus and Grafana
- **Pre-built dashboards** for DevOps and business analytics
- **SLA compliance tracking** and alerting
- **Business metrics** - tokens, characters, audio seconds processed
- **Resource monitoring** - CPU, memory, throughput
- **Easy integration** - 3 lines of code to get started

---

## 📋 Prerequisites

### ⚠️ CRITICAL: Organization Identification Required

**Before using this package, you MUST implement organization extraction.** The system needs to identify which organization/tenant each request belongs to.

#### Option 1: JWT Token with Organization Claims (Recommended)

Add organization information to your JWT tokens:

```python
payload = {
    "sub": "user@example.com",
    "organization": "your-organization-name",  # Required!
    "name": "Organization Display Name",
    "exp": 1234567890
}
```

The middleware checks for these fields in order: `organization`, `org`, `name`, `company`

#### Option 2: Database Mapping

Store organization with API keys in your database and modify the middleware's organization extraction logic.

#### ⚠️ Current Mock Implementation

The package includes a **mock organization extractor** that randomly maps API keys to organizations. **You MUST replace this** in production:

```python
# In middleware.py - REPLACE THIS!
def _get_organization_from_api_key(api_key: str) -> str:
    organizations = ["irctc", "kisanmitra", "bashadaan", "beml"]
    # Hash-based random mapping - NOT FOR PRODUCTION!
```

### System Requirements

- **FastAPI** application (native support)
- **Python 3.8+**
- **Docker** (for Prometheus + Grafana)
- **Prometheus** for metrics storage
- **Grafana** for visualization

---

## 🚀 Quick Start

### 1. Installation

**Option A: Use as Local Module (Current Setup)**
```bash
# Package is already in server/observability/
# No installation needed!
```

**Option B: Install from PyPI (Future)**
```bash
pip install dhruva-observability
```

### 2. Configure Environment Variables

**Option A: Add to `.env` file** (Recommended)
```bash
# Required - Observability Plugin
DHRUVA_ENTERPRISE_ENABLED=true
DHRUVA_ENTERPRISE_CUSTOMERS=org1,org2,org3

# Required - Grafana Admin Credentials
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=YourSecurePassword123

# Optional - Apps and Paths
DHRUVA_ENTERPRISE_APPS=app1,app2,default
DHRUVA_ENTERPRISE_METRICS_PATH=/enterprise/metrics
DHRUVA_ENTERPRISE_HEALTH_PATH=/enterprise/health

# Optional - Debug and Metrics Collection
DHRUVA_ENTERPRISE_DEBUG=true
DHRUVA_ENTERPRISE_COLLECT_SYSTEM_METRICS=true
DHRUVA_ENTERPRISE_COLLECT_GPU_METRICS=true
DHRUVA_ENTERPRISE_COLLECT_DB_METRICS=true
```

**Option B: Set in docker-compose-app.yml**

These variables are already configured in `docker-compose-app.yml`. Update the values as needed for your deployment.

**Option C: Export in shell**
```bash
export DHRUVA_ENTERPRISE_ENABLED=true
export DHRUVA_ENTERPRISE_CUSTOMERS=org1,org2,org3
export GRAFANA_ADMIN_USER=admin
export GRAFANA_ADMIN_PASSWORD=YourSecurePassword123
# ... (add other variables as needed)
```

### 3. Integrate with FastAPI (3 Lines!)

```python
from fastapi import FastAPI
from observability import ObservabilityPlugin

app = FastAPI()

# Initialize and register observability
enterprise = ObservabilityPlugin()
enterprise.register_plugin(app)

# That's it! Middleware and endpoints are auto-registered
```

### 4. Start All Services

```bash
# Start Database, Metering, Monitoring, and Application services
docker-compose -f docker-compose-db.yml -f docker-compose-metering.yml -f docker-compose-monitoring.yml -f docker-compose-app.yml up -d

# Verify metrics endpoint
curl http://localhost:8000/enterprise/metrics

# Check Prometheus is scraping
curl http://localhost:9090/api/v1/targets
```

---

## 🔧 Configuration

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DHRUVA_ENTERPRISE_ENABLED` | Yes | `false` | Enable/disable the plugin |
| `DHRUVA_ENTERPRISE_CUSTOMERS` | Yes | - | Comma-separated list of organizations |
| `GRAFANA_ADMIN_USER` | Yes | - | Grafana admin username |
| `GRAFANA_ADMIN_PASSWORD` | Yes | - | Grafana admin password |
| `DHRUVA_ENTERPRISE_APPS` | No | `default` | Comma-separated list of apps |
| `DHRUVA_ENTERPRISE_DEBUG` | No | `false` | Enable debug logging |
| `DHRUVA_ENTERPRISE_METRICS_PATH` | No | `/enterprise/metrics` | Metrics endpoint path |
| `DHRUVA_ENTERPRISE_HEALTH_PATH` | No | `/enterprise/health` | Health check endpoint |
| `DHRUVA_ENTERPRISE_COLLECT_SYSTEM_METRICS` | No | `true` | Collect system metrics (CPU, memory) |
| `DHRUVA_ENTERPRISE_COLLECT_GPU_METRICS` | No | `true` | Collect GPU usage metrics |
| `DHRUVA_ENTERPRISE_COLLECT_DB_METRICS` | No | `true` | Collect database connection metrics |
| `DHRUVA_ENTERPRISE_DEFAULT_CUSTOMER` | No | `default` | Default organization name |
| `DHRUVA_ENTERPRISE_DEFAULT_APP` | No | `default` | Default app name |

---

## 📡 Available Endpoints

Once registered, the plugin automatically creates these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/enterprise/metrics` | GET | Prometheus metrics (scraped by Prometheus) |
| `/enterprise/health` | GET | Health check and plugin status |
| `/enterprise/config` | GET | Current plugin configuration |

---

## 🔍 Grafana Dashboard Setup

### Manual Steps Required (Per Organization)

1. **Login to Grafana**: `http://localhost:3000`
2. **Create Organization**: Server Admin → Organizations → New Organization
3. **Create Prometheus Data Source**:
   - Configuration → Data Sources → Add data source
   - Type: Prometheus
   - URL: `http://dhruva-platform-prometheus:9090`
   - Click "Save & Test"
   - **Note the UID** from URL
4. **Update Dashboard JSON**:
   - Edit `grafana/provisioning/dashboards/*.json`
   - Replace `"uid": "OLD_UID"` with your actual data source UID
5. **Import Dashboard**: Dashboards → Import → Upload modified JSON

**Repeat for each client organization!**

---

## ✅ Verification Checklist

```bash
# Check server is running
curl http://localhost:8000/health

# Check metrics endpoint
curl http://localhost:8000/enterprise/metrics

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check Grafana
curl http://localhost:3000/api/health
```

**In Grafana:**
- ✅ Organization created
- ✅ Data source connected (green checkmark)
- ✅ Dashboard shows data (not "No data")
- ✅ Metrics filtered for correct organization

---

## 📚 Documentation

### Available Documentation Files

| Document | Purpose |
|----------|---------|
| `OBSERVABILITY_COMPLETE_GUIDE.md` | Comprehensive guide (all docs combined) |
| `OBSERVABILITY_QUICK_SETUP_GUIDE.md` | Fast setup steps |
| `OBSERVABILITY_TECHNICAL_DOCUMENTATION.md` | Detailed technical reference |
| `OBSERVABILITY_ARCHITECTURE_DIAGRAM.md` | Visual architecture diagrams |
| `LOCAL_OBSERVABILITY_SETUP.md` | Local development setup |
| `ORGANIZATION_EXTRACTION_IMPLEMENTATION_GUIDE.md` | How to implement organization extraction |

---

## 🎓 Quick Example

### Complete Integration Example

```python
# main.py
from fastapi import FastAPI
from observability import ObservabilityPlugin

app = FastAPI()

# Initialize observability
enterprise = ObservabilityPlugin()
enterprise.register_plugin(app)

# Your existing routes work unchanged
@app.get("/")
def read_root():
    return {"message": "Hello World"}

# Metrics are automatically tracked for all requests!
```

### What Happens Automatically

1. **Middleware intercepts** all requests
2. **Extracts organization** from JWT token or headers
3. **Detects service type** from URL path
4. **Tracks metrics**: request count, duration, errors
5. **Extracts business metrics**: characters, tokens, audio length
6. **Updates Prometheus metrics** in real-time
7. **Grafana visualizes** data via dashboards

---

## 🔐 Security Considerations

### Production Requirements

1. ✅ **JWT Signature Verification**: Implement proper token verification
2. ✅ **Change Grafana Admin Password**: Don't use default credentials
3. ✅ **Use HTTPS**: Enable TLS for Grafana in production
4. ✅ **Restrict Prometheus Access**: Internal network only
5. ✅ **Organization Isolation**: Verify metrics don't leak between orgs

---

## 📦 Package Structure

```
server/observability/
├── __init__.py              # Package initialization
├── plugin.py                # Main ObservabilityPlugin class
├── middleware.py            # FastAPI middleware (request tracking)
├── metrics.py               # MetricsCollector (50+ metrics)
├── config.py                # PluginConfig (environment variables)
├── adapters/                # Framework adapters (Flask, Django, etc.)
│   ├── __init__.py
│   ├── flask_adapter.py     # Flask integration (optional)
│   ├── django_adapter.py    # Django integration (optional)
│   ├── generic_adapter.py   # Generic framework support
│   └── manual_adapter.py    # Manual metrics tracking
└── README.md                # This file
```

---

## 🚨 Important Notes

### Before Deploying to Production

1. **MUST IMPLEMENT** organization extraction from JWT tokens
2. **MUST UPDATE** Grafana admin password
3. **MUST CONFIGURE** proper JWT secret and verification
4. **MUST CREATE** Grafana organizations for each client
5. **MUST UPDATE** dashboard JSON files with correct data source UIDs

### Known Limitations

- **Manual Grafana setup required** for each organization
- **Dashboard JSON must be updated** with data source UIDs before import
- **Mock organization extractor** must be replaced with real implementation

---

## 📞 Support

### Getting Help

1. **Enable debug mode**: `export DHRUVA_ENTERPRISE_DEBUG=true`
2. **Check logs**: `docker logs dhruva-platform-server`
3. **Refer to documentation**: See `OBSERVABILITY_COMPLETE_GUIDE.md`

### Common Commands

```bash
# View all metrics
curl http://localhost:8000/enterprise/metrics

# Restart all services
docker-compose -f docker-compose-db.yml -f docker-compose-metering.yml -f docker-compose-monitoring.yml -f docker-compose-app.yml restart

# Restart only the application server
docker-compose -f docker-compose-app.yml restart dhruva-platform-server

# View Prometheus UI
open http://localhost:9090

# View Grafana UI
open http://localhost:3000

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets
```

---

## 📄 License

Part of the Dhruva Platform

---

## 🔄 Version Information

- **Package Version**: 1.0.3
- **Last Updated**: October 2025
- **Framework**: FastAPI (native support)
- **Python**: 3.8+

---

## 🎯 Next Steps

1. ✅ **Implement organization extraction** (JWT tokens recommended)
2. ✅ **Set environment variables** 
3. ✅ **Integrate with FastAPI** (3 lines of code)
4. ✅ **Start monitoring stack** (Prometheus + Grafana)
5. ✅ **Create Grafana organizations** for each client
6. ✅ **Import dashboards** (update UIDs first!)
7. ✅ **Verify metrics display** correctly
8. ✅ **Configure alerts** (optional)

---

**Ready to get started?** 

See `OBSERVABILITY_QUICK_SETUP_GUIDE.md` for step-by-step instructions!

---

**Maintained by**: Dhruva Platform Team  
**Questions?** Check the troubleshooting section or enable debug mode for detailed logs.

