# Dhruva Observability Package - Documentation Index

Welcome to the Dhruva Observability Package documentation. This enterprise-grade monitoring solution provides comprehensive observability, multi-tenant metrics tracking, and real-time analytics for Dhruva platform deployments.

---

## 📚 Documentation Structure

This package includes multiple documentation files designed for different use cases:

### 1. **Quick Setup Guide** (Start Here!)
**File:** `OBSERVABILITY_QUICK_SETUP_GUIDE.md`

**For:** DevOps engineers who want to get up and running quickly

**Contents:**
- Fast installation steps
- Essential configuration
- Grafana setup checklist
- Quick troubleshooting

**Read this if:** You want a condensed, step-by-step guide to deploy the observability stack.

---

### 2. **Complete Technical Documentation** (Reference)
**File:** `OBSERVABILITY_TECHNICAL_DOCUMENTATION.md`

**For:** System architects, platform engineers, and technical decision-makers

**Contents:**
- Detailed architecture overview
- Complete installation options
- Comprehensive prerequisites
- Monitoring infrastructure deep-dive
- Full Grafana dashboard configuration
- Complete metrics reference
- Advanced troubleshooting
- Best practices and security considerations

**Read this if:** You need complete technical details, architecture information, or troubleshooting guidance.

---

### 3. **Organization Extraction Implementation Guide** (Critical!)
**File:** `ORGANIZATION_EXTRACTION_IMPLEMENTATION_GUIDE.md`

**For:** Backend developers implementing the observability package

**Contents:**
- Detailed explanation of organization identification
- Current mock implementation (must be replaced!)
- Three implementation options:
  - JWT token-based (recommended)
  - Database mapping
  - Static configuration
- Complete code examples
- Testing procedures
- Verification checklist

**Read this if:** You're implementing the observability package and need to set up organization extraction (REQUIRED for multi-tenant metrics).

---

## 🚀 Quick Start Path

Follow this path for fastest deployment:

```
1. Read: ORGANIZATION_EXTRACTION_IMPLEMENTATION_GUIDE.md
   └─> Implement organization extraction in your code
   
2. Read: OBSERVABILITY_QUICK_SETUP_GUIDE.md  
   └─> Install and configure the observability stack
   
3. Reference: OBSERVABILITY_TECHNICAL_DOCUMENTATION.md
   └─> For detailed information and troubleshooting
```

---

## ⚠️ Critical Prerequisites (READ FIRST!)

Before deploying the observability package, you **MUST** complete these requirements:

### 1. **Organization Identification Implementation**

The observability system requires organization/tenant identification to work properly. You must implement one of:

- ✅ **JWT tokens with organization claims** (recommended)
- ✅ **Database mapping of API keys to organizations**
- ✅ **Static configuration file with API key mappings**

**Current Status:** The package includes a **mock implementation** that randomly assigns organizations. This **MUST be replaced** with your actual implementation.

**→ See:** `ORGANIZATION_EXTRACTION_IMPLEMENTATION_GUIDE.md`

### 2. **Environment Variables**

```bash
export DHRUVA_ENTERPRISE_ENABLED=true
export DHRUVA_ENTERPRISE_CUSTOMERS=irctc,kisanmitra,bashadaan,beml
export GRAFANA_ADMIN_USER=admin
export GRAFANA_ADMIN_PASSWORD=YourSecurePassword
```

### 3. **Grafana Manual Configuration**

- Create organizations for each client (manual)
- Create Prometheus data source for each organization (manual)
- Update dashboard JSON with data source UID (manual)
- Import dashboard for each organization (manual)

**→ See:** `OBSERVABILITY_QUICK_SETUP_GUIDE.md` - Grafana Setup section

---

## 🎯 Key Features

- **Multi-tenant metrics collection** with organization-level isolation
- **Automatic service detection** (Translation, TTS, ASR, LLM, etc.)
- **Real-time monitoring** via Prometheus and Grafana
- **Pre-built dashboards** for DevOps and business analytics
- **SLA tracking and compliance** monitoring
- **Resource usage monitoring** (CPU, memory, requests, errors)
- **Character/token/audio tracking** for billing and quota management

---

## 📦 Installation Options

### Option 1: pip Package (Quick)
```bash
pip install dhruva-observability
```

**Pros:** Fast, easy updates  
**Cons:** Less control over code

### Option 2: Source Code Import (Flexible)
Copy the `observability` folder from `observability__module` branch into your project.

**Pros:** Full control, customizable  
**Cons:** Manual updates

**→ See:** `OBSERVABILITY_TECHNICAL_DOCUMENTATION.md` - Installation Options section

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Dhruva Platform Server                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Observability Middleware                       │  │
│  │  - Intercepts all requests                               │  │
│  │  - Extracts organization from JWT/headers                │  │
│  │  - Tracks metrics (requests, latency, errors)            │  │
│  │  - Monitors service usage (NMT, TTS, ASR, LLM)          │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Metrics Collector (metrics.py)                 │  │
│  │  - 50+ Prometheus metrics                                │  │
│  │  - System metrics (CPU, memory)                          │  │
│  │  - Business metrics (tokens, characters, audio)          │  │
│  │  - SLA compliance tracking                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Endpoint: /enterprise/metrics (Prometheus format)             │
└─────────────────────────────────────────────────────────────────┘
                              ▼
                    (Metrics Scraping)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Prometheus                              │
│  - Scrapes /enterprise/metrics every 5 seconds                 │
│  - Stores time-series data                                      │
│  - Provides query interface (PromQL)                            │
│  - Port: 9090                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ▼
                       (Data Query)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          Grafana                                │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Organization: IRCTC                                      │ │
│  │  - Prometheus Data Source (UID: abc123)                   │ │
│  │  - DevOps Dashboard (filtered for IRCTC)                  │ │
│  └───────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Organization: KisanMitra                                 │ │
│  │  - Prometheus Data Source (UID: xyz789)                   │ │
│  │  - DevOps Dashboard (filtered for KisanMitra)             │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  - Multi-tenant dashboards                                      │
│  - Real-time visualization                                      │
│  - Alerting (optional)                                          │
│  - Port: 3000                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Metrics Categories

### Request Metrics
- Total requests by organization/app/endpoint
- Request duration histograms
- Error counts and rates
- Status code distribution

### Service Metrics
- Service-specific request counts (NMT, TTS, ASR, LLM)
- Component latency tracking
- Service availability

### Business Metrics
- LLM tokens processed
- TTS characters synthesized
- NMT characters translated
- ASR audio seconds processed

### System Metrics
- CPU usage
- Memory usage
- Peak throughput
- Active connections

### SLA Metrics
- Availability percentage
- Response time targets
- Compliance tracking

**→ See:** `OBSERVABILITY_TECHNICAL_DOCUMENTATION.md` - Metrics Reference section

---

## 🔧 Configuration

### Minimal Configuration

```bash
# .env file
DHRUVA_ENTERPRISE_ENABLED=true
DHRUVA_ENTERPRISE_CUSTOMERS=irctc,kisanmitra,bashadaan,beml
DHRUVA_ENTERPRISE_APPS=app1,app2,app3
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=SecurePassword123
```

### Application Integration

```python
from fastapi import FastAPI
from dhruva_observability import ObservabilityPlugin

app = FastAPI()

# Initialize observability (3 lines!)
enterprise = ObservabilityPlugin()
enterprise.register_plugin(app)

# Your existing Dhruva endpoints work unchanged
```

**→ See:** `OBSERVABILITY_QUICK_SETUP_GUIDE.md` for complete configuration

---

## 🎛️ Grafana Setup (Manual Steps)

The Grafana setup requires manual configuration for each client organization:

### For Each Client Organization:

1. ✅ **Create Grafana Organization** (Admin only)
2. ✅ **Create Prometheus Data Source** in the organization
3. ✅ **Copy the Data Source UID** from the URL
4. ✅ **Edit Dashboard JSON** - replace UID with your data source UID
5. ✅ **Import Dashboard** into the organization
6. ✅ **Verify metrics display** correctly

**Why Manual?**
- Grafana doesn't support automatic data source creation via API without admin credentials
- Dashboard JSON cannot auto-detect data sources - UID must be explicitly configured
- Multi-tenancy requires organization isolation

**→ See:** `OBSERVABILITY_QUICK_SETUP_GUIDE.md` - Grafana Setup section

---

## 🐛 Troubleshooting Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| "No data" in Grafana | Verify data source UID matches dashboard JSON |
| Wrong organization data | Implement organization extraction properly |
| Metrics endpoint 404 | Set `DHRUVA_ENTERPRISE_ENABLED=true` |
| Prometheus not scraping | Check `docker-compose-monitoring.yml` network |
| JWT decoding fails | Verify JWT secret and algorithm match |

**→ See:** `OBSERVABILITY_TECHNICAL_DOCUMENTATION.md` - Troubleshooting section

---

## 📁 File Locations

| Component | File Path |
|-----------|-----------|
| **Documentation** | |
| Quick Setup Guide | `OBSERVABILITY_QUICK_SETUP_GUIDE.md` |
| Technical Docs | `OBSERVABILITY_TECHNICAL_DOCUMENTATION.md` |
| Org Extraction Guide | `ORGANIZATION_EXTRACTION_IMPLEMENTATION_GUIDE.md` |
| **Source Code** | |
| Metrics Collector | `server/observability/metrics.py` |
| Middleware | `server/observability/middleware.py` |
| Configuration | `server/observability/config.py` |
| **Infrastructure** | |
| Docker Compose | `docker-compose-monitoring.yml` |
| Prometheus Config | `prometheus/prometheus.yml` |
| Dashboard JSONs | `grafana/provisioning/dashboards/*.json` |

---

## 🚦 Deployment Checklist

### Pre-Deployment
- [ ] Read all documentation files
- [ ] Implement organization extraction
- [ ] Test organization extraction with debug mode
- [ ] Set environment variables
- [ ] Configure Grafana admin credentials

### Deployment
- [ ] Start monitoring stack: `docker-compose -f docker-compose-monitoring.yml up -d`
- [ ] Verify metrics endpoint: `curl localhost:8000/enterprise/metrics`
- [ ] Check Prometheus targets: `curl localhost:9090/api/v1/targets`
- [ ] Access Grafana: `http://localhost:3000`

### Grafana Configuration (Per Organization)
- [ ] Create Grafana organization
- [ ] Add organization admin/members
- [ ] Create Prometheus data source
- [ ] Note data source UID
- [ ] Update dashboard JSON with UID
- [ ] Import dashboard
- [ ] Verify metrics display
- [ ] Set up alerts (optional)

### Post-Deployment
- [ ] Verify organization isolation
- [ ] Test with multiple organizations
- [ ] Configure backup procedures
- [ ] Document organization-specific configurations
- [ ] Train team on dashboard usage

---

## 🔐 Security Considerations

1. **JWT Signature Verification**
   - ✅ DO verify JWT signatures in production
   - ❌ DON'T use `verify_signature=False`

2. **Grafana Security**
   - ✅ Change default admin password
   - ✅ Use HTTPS in production
   - ✅ Configure proper RBAC

3. **Prometheus Security**
   - ✅ Restrict access to internal network
   - ✅ Use authentication in production

4. **Organization Isolation**
   - ✅ Verify organization extraction works correctly
   - ✅ Test cross-organization data isolation
   - ✅ Audit dashboard access regularly

---

## 📞 Support

### Getting Help

1. **Check documentation** in this order:
   - Quick Setup Guide for common tasks
   - Technical Documentation for detailed info
   - Organization Extraction Guide for implementation

2. **Enable debug mode** for troubleshooting:
   ```bash
   export DHRUVA_ENTERPRISE_DEBUG=true
   docker-compose restart dhruva-platform-server
   ```

3. **Check logs**:
   ```bash
   docker logs dhruva-platform-server
   docker logs dhruva-platform-prometheus
   docker logs dhruva-platform-grafana
   ```

### Common Commands

```bash
# View all metrics
curl http://localhost:8000/enterprise/metrics

# Restart monitoring stack
docker-compose -f docker-compose-monitoring.yml restart

# Access Prometheus UI
open http://localhost:9090

# Access Grafana UI
open http://localhost:3000

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets
```

---

## 🎓 Learning Path

### For DevOps Engineers
1. Read: Quick Setup Guide
2. Deploy: Monitoring stack
3. Configure: Grafana organizations and dashboards
4. Monitor: Dashboard usage and alerts

### For Backend Developers
1. Read: Organization Extraction Guide
2. Implement: JWT tokens or database mapping
3. Test: Organization extraction with debug mode
4. Verify: Metrics in Grafana

### For System Architects
1. Read: Technical Documentation
2. Review: Architecture and security considerations
3. Plan: Multi-tenant deployment strategy
4. Document: Organization-specific configurations

---

## 📈 Monitoring Best Practices

1. **Start Small**: Deploy for one organization first, verify, then scale
2. **Test Organization Isolation**: Ensure metrics don't leak between organizations
3. **Monitor the Monitors**: Set up alerts for Prometheus/Grafana health
4. **Regular Backups**: Backup Grafana dashboards and Prometheus data
5. **Document Customizations**: Keep track of dashboard modifications per organization
6. **Review Access**: Regularly audit who has access to which organization's metrics

---

## 📝 Version Information

- **Package Version:** 1.0
- **Documentation Version:** 1.0
- **Last Updated:** October 2025
- **Compatible Dhruva Versions:** All FastAPI-based implementations

---

## 🗺️ Next Steps

1. **→ Start with:** `OBSERVABILITY_QUICK_SETUP_GUIDE.md`
2. **→ Implement:** Organization extraction using `ORGANIZATION_EXTRACTION_IMPLEMENTATION_GUIDE.md`
3. **→ Reference:** `OBSERVABILITY_TECHNICAL_DOCUMENTATION.md` for details

**Ready to begin?** Open `OBSERVABILITY_QUICK_SETUP_GUIDE.md` and follow the steps!

---

**Document maintained by:** Dhruva Platform Team  
**Questions or issues?** Refer to the troubleshooting sections in the technical documentation.

