# Dhruva Observability - Quick Setup Guide

This is a condensed quick-start guide for setting up the Dhruva Observability Package. For detailed information, refer to `OBSERVABILITY_TECHNICAL_DOCUMENTATION.md`.

---

## Prerequisites (Must Complete First!)

### ⚠️ CRITICAL: Organization Identification

**You MUST implement organization extraction before using this package.**

#### Option A: JWT Token with Organization Claims

Add organization to your JWT tokens:

```python
payload = {
    "sub": "user@example.com",
    "organization": "irctc",  # Required!
    "name": "IRCTC",
    "exp": 1234567890
}
```

#### Option B: Database Mapping

Store organization with API keys in your database and modify the middleware.

#### ⚠️ Current Mock Implementation

The system currently uses **mock organization extraction** (lines 126-135 in `middleware.py`):
```python
def _get_organization_from_api_key(api_key: str) -> str:
    organizations = ["irctc", "kisanmitra", "bashadaan", "beml"]
    # Hash-based random mapping
```

**→ Replace this with your actual implementation!**

---

## Installation

### Option 1: pip Package (Quick)
```bash
pip install dhruva-observability
```

### Option 2: Source Code (Customizable)
Copy the `observability` folder from `observability__module` branch into your `server/` directory.

---

## Configuration

### 1. Set Environment Variables

```bash
# Enable plugin
export DHRUVA_ENTERPRISE_ENABLED=true

# Organizations (comma-separated)
export DHRUVA_ENTERPRISE_CUSTOMERS=irctc,kisanmitra,bashadaan,beml

# Apps
export DHRUVA_ENTERPRISE_APPS=app1,app2,app3

# Grafana credentials
export GRAFANA_ADMIN_USER=admin
export GRAFANA_ADMIN_PASSWORD=YourSecurePassword123
```

### 2. Integrate with FastAPI

```python
from fastapi import FastAPI
from dhruva_observability import ObservabilityPlugin

app = FastAPI()

# Add observability (3 lines!)
enterprise = ObservabilityPlugin()
enterprise.register_plugin(app)
```

---

## Start Monitoring Stack

```bash
# Start Prometheus + Grafana
docker-compose -f docker-compose-monitoring.yml up -d

# Verify metrics endpoint
curl http://localhost:8000/enterprise/metrics

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets
```

---

## Grafana Setup (Manual Steps Required)

### Step 1: Login to Grafana
- URL: `http://localhost:3000`
- Username: `admin`
- Password: `YourSecurePassword123`

### Step 2: Create Organization (For Each Client)

1. **Server Admin → Organizations → New Organization**
2. Name: `IRCTC`
3. Click **Create**
4. **Switch to IRCTC organization**

### Step 3: Create Prometheus Data Source

1. **Configuration → Data Sources → Add data source**
2. Select **Prometheus**
3. Name: `Prometheus-IRCTC`
4. URL: `http://dhruva-platform-prometheus:9090`
5. Click **Save & Test**
6. **📝 COPY THE UID** from the URL:
   ```
   http://localhost:3000/datasources/edit/P1809F7CD0C75ACF3
                                          ↑ This is the UID
   ```

### Step 4: Update Dashboard JSON with UID

**⚠️ CRITICAL STEP - Do this BEFORE importing!**

```bash
# Edit the dashboard JSON file
cd grafana/provisioning/dashboards

# Find and replace the data source UID
# Replace "OLD_UID" with your actual UID (e.g., P1809F7CD0C75ACF3)
```

**Using VS Code or text editor:**
- Find: `"uid": "OLD_UID_HERE"`
- Replace: `"uid": "P1809F7CD0C75ACF3"`
- Save file

**Using command line (Linux/Mac):**
```bash
sed -i 's/"uid": "OLD_UID_HERE"/"uid": "P1809F7CD0C75ACF3"/g' \
  "Dhruva DevOps Operations Dashboard-v3-1760288510339.json"
```

**Using PowerShell (Windows):**
```powershell
(Get-Content "Dhruva DevOps Operations Dashboard-v3-1760288510339.json") `
  -replace '"uid": "OLD_UID_HERE"', '"uid": "P1809F7CD0C75ACF3"' | `
  Set-Content "Dhruva DevOps Operations Dashboard-v3-1760288510339.json"
```

### Step 5: Import Dashboard

1. **Dashboards → Import**
2. **Upload JSON file** (the one you just edited)
3. Click **Import**
4. Dashboard should now show metrics!

---

## Repeat for Each Organization

For each new client (KisanMitra, BashaDaan, BEML, etc.):

1. ✅ Create new Grafana Organization
2. ✅ Create new Prometheus Data Source in that org
3. ✅ Copy the Data Source UID
4. ✅ **Make a copy of dashboard JSON** and update UID
5. ✅ Import the modified JSON into the organization

---

## Verification Checklist

```bash
# ✅ Dhruva server running
curl http://localhost:8000/health

# ✅ Metrics endpoint working
curl http://localhost:8000/enterprise/metrics

# ✅ Prometheus scraping
curl http://localhost:9090/api/v1/targets

# ✅ Grafana accessible
curl http://localhost:3000/api/health
```

In Grafana:
- ✅ Organization created
- ✅ Data source connected (green checkmark)
- ✅ Dashboard showing data (not "No data")
- ✅ Organization filter showing correct org

---

## Troubleshooting Quick Fixes

### "No data" in Grafana
```bash
# Check if metrics are being generated
curl http://localhost:8000/enterprise/metrics | grep dhruva_enterprise

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | grep dhruva-enterprise
```

**Fix:** Verify data source UID in dashboard matches your Prometheus data source.

### Wrong organization data showing
```bash
# Enable debug mode
export DHRUVA_ENTERPRISE_DEBUG=true

# Restart server
docker-compose restart dhruva-platform-server

# Check logs
docker logs dhruva-platform-server | grep "organization"
```

**Fix:** Implement proper organization extraction from JWT tokens.

### Metrics endpoint returns 404
```bash
# Check if plugin enabled
echo $DHRUVA_ENTERPRISE_ENABLED  # Should be "true"

# Verify plugin registration in code
grep "ObservabilityPlugin" server/main.py
```

**Fix:** Set `DHRUVA_ENTERPRISE_ENABLED=true` and restart.

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `docker-compose-monitoring.yml` | Starts Prometheus + Grafana |
| `prometheus/prometheus.yml` | Configures metric scraping |
| `grafana/provisioning/dashboards/*.json` | Dashboard definitions |
| `server/observability/middleware.py` | **Organization extraction (MODIFY THIS!)** |
| `server/observability/metrics.py` | Metrics definitions |

---

## Important Notes

1. **Organization extraction is REQUIRED** - Replace the mock implementation!
2. **Data source UID must be updated** in dashboard JSON before importing
3. **Each organization needs its own data source** in Grafana
4. **Only Grafana Server Admin** can create organizations
5. **Dashboard JSON cannot auto-detect** data sources - must be manually configured

---

## Next Steps

1. ✅ Implement proper organization extraction
2. ✅ Create Grafana organizations for all clients
3. ✅ Set up data sources for each organization
4. ✅ Import customized dashboards
5. ✅ Configure alerts (optional)
6. ✅ Set up backup procedures

---

## Support

**Having issues?**

1. Enable debug mode: `export DHRUVA_ENTERPRISE_DEBUG=true`
2. Check logs: `docker logs dhruva-platform-server`
3. Refer to full documentation: `OBSERVABILITY_TECHNICAL_DOCUMENTATION.md`

**Common Commands:**
```bash
# View all metrics
curl http://localhost:8000/enterprise/metrics

# Restart monitoring stack
docker-compose -f docker-compose-monitoring.yml restart

# View Prometheus targets
open http://localhost:9090/targets

# Access Grafana
open http://localhost:3000
```

---

**Quick Setup Guide v1.0** | Last updated: October 2025

