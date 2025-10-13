# Dhruva Observability Package - Technical Documentation

## Table of Contents
1. [Overview](#overview)
2. [Installation Options](#installation-options)
3. [Prerequisites and Requirements](#prerequisites-and-requirements)
4. [Organization Identification Setup](#organization-identification-setup)
5. [Monitoring Infrastructure Setup](#monitoring-infrastructure-setup)
6. [Grafana Dashboard Configuration](#grafana-dashboard-configuration)
7. [Metrics Reference](#metrics-reference)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The Dhruva Observability Package is an enterprise-grade monitoring and metrics collection system designed to provide comprehensive observability for Dhruva platform deployments. It enables multi-tenant monitoring, SLA tracking, business analytics, and real-time performance insights.

### Key Features
- **Multi-tenant metrics collection** with organization-level isolation
- **Automatic service detection** (NMT, TTS, ASR, LLM, etc.)
- **Real-time monitoring** via Prometheus and Grafana
- **Pre-built dashboards** for DevOps and business analytics
- **SLA compliance tracking** and alerting
- **Resource usage monitoring** (CPU, memory, requests, errors)

---

## Installation Options

The observability package can be integrated into your Dhruva application in two ways:

### Option 1: Install via pip Package (Recommended for Quick Setup)

Install the pre-packaged observability plugin from PyPI:

```bash
pip install dhruva-observability
```

**Advantages:**
- Quick and easy installation
- Minimal setup required
- Automatic updates via pip

**Usage:**
```python
from fastapi import FastAPI
from dhruva_observability import ObservabilityPlugin

app = FastAPI()

# Initialize and register the plugin
enterprise = ObservabilityPlugin()
enterprise.register_plugin(app)
```

### Option 2: Import from Source Code (Recommended for Customization)

For clients who need more control over the observability code, import the observability module directly from the source:

1. **Access the observability module** from the `observability__module` branch
2. **Copy the `observability` folder** into your Dhruva server directory
3. **Import directly** from your local code:

```python
from observability.plugin import ObservabilityPlugin
from observability.middleware import ObservabilityMiddleware
from observability.metrics import MetricsCollector

app = FastAPI()

# Initialize with custom configuration
enterprise = ObservabilityPlugin()
enterprise.register_plugin(app)
```

**Advantages:**
- Full control over the code
- Ability to customize metrics collection
- Can modify middleware behavior
- Direct access to source for debugging

**Note:** When using the source code option, ensure all dependencies are installed:
```bash
pip install prometheus-client psutil pyjwt
```

---

## Prerequisites and Requirements

### Critical Requirements

Before deploying the Dhruva Observability Package, ensure the following prerequisites are met:

#### 1. **Organization Name in API User Creation**

The observability system requires organization identification to enable multi-tenant metrics tracking. You **MUST** implement one of the following:

**Option A: Add Organization Name During API User Creation**
- When creating API users in your system, include an `organization` or `organization_name` field
- Store this association in your user database
- Include the organization information in the JWT token claims

**Option B: Enable Organization Extraction from JWT Token**
- Ensure your JWT token includes organization information in the claims
- The token should contain either:
  - `organization` field
  - `org` field  
  - `company` field
  - `name` field (as fallback)

Example JWT payload structure:
```json
{
  "sub": "user@example.com",
  "organization": "IRCTC",
  "name": "IRCTC Admin",
  "exp": 1234567890
}
```

#### 2. **Current Mock Organization Extraction**

**IMPORTANT:** The current implementation includes a **mock organization extraction mechanism** that should be replaced in production.

**How the Mock Works:**
- The system currently maps API keys to random organization names using a hash function
- Organization names used: `["irctc", "kisanmitra", "bashadaan", "beml"]`
- This is implemented in the middleware as a placeholder

**Location in code:**
```python
# In middleware.py
def _get_organization_from_api_key(api_key: str) -> str:
    """Map API key to organization name using consistent hashing."""
    organizations = ["irctc", "kisanmitra", "bashadaan", "beml"]
    hash_value = int(hashlib.md5(api_key.encode()).hexdigest(), 16)
    org_index = hash_value % len(organizations)
    return organizations[org_index]
```

**Action Required:**
- **Replace this mock implementation** with your actual organization extraction logic
- Implement proper JWT decoding with your secret key
- Or modify the API key to organization mapping based on your database

#### 3. **Environment Variables**

Set the following environment variables for the observability plugin:

```bash
# Enable the plugin
export DHRUVA_ENTERPRISE_ENABLED=true

# Configure organizations and apps (comma-separated)
export DHRUVA_ENTERPRISE_CUSTOMERS=irctc,kisanmitra,bashadaan,beml
export DHRUVA_ENTERPRISE_APPS=app1,app2,app3

# Optional: Custom endpoints
export DHRUVA_ENTERPRISE_METRICS_PATH=/enterprise/metrics
export DHRUVA_ENTERPRISE_HEALTH_PATH=/enterprise/health

# Optional: Default values
export DHRUVA_ENTERPRISE_DEFAULT_CUSTOMER=default
export DHRUVA_ENTERPRISE_DEFAULT_APP=default

# Optional: Debug mode
export DHRUVA_ENTERPRISE_DEBUG=true
```

#### 4. **Grafana Admin Credentials**

Set Grafana administrator credentials:

```bash
export GRAFANA_ADMIN_USER=admin
export GRAFANA_ADMIN_PASSWORD=your_secure_password
```

---

## Organization Identification Setup

### Understanding Organization Extraction

The observability system uses a **hierarchical identification system**:

```
Organization (Company/Tenant) → Application → Request
```

### Implementation Steps

#### Step 1: Implement JWT Token with Organization Claims

Update your authentication system to include organization information in JWT tokens:

```python
import jwt
from datetime import datetime, timedelta

def create_access_token(user_id: str, organization: str):
    payload = {
        "sub": user_id,
        "organization": organization,  # Include organization
        "name": organization,           # Fallback field
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, "your_secret_key", algorithm="HS256")
    return token
```

#### Step 2: Ensure Middleware Can Extract Organization

The observability middleware automatically extracts organization from:

1. **JWT Token** (Primary method):
   - Decodes the JWT token from `Authorization` header
   - Extracts organization from token claims
   - Fields checked: `organization`, `name`, `sub`

2. **HTTP Headers** (Fallback):
   - `X-Customer-ID` header
   - `X-Organization-ID` header

3. **API Key Mapping** (Current mock - replace this):
   - Hash-based mapping to organization names

#### Step 3: Verify Organization Extraction

Enable debug mode to verify organization extraction:

```bash
export DHRUVA_ENTERPRISE_DEBUG=true
```

Check logs for messages like:
```
🔑 Extracted customer from JWT: irctc
🏢 Mapped API key to organization: kisanmitra
```

---

## Monitoring Infrastructure Setup

### Architecture Overview

```
┌─────────────────┐     ┌──────────────┐     ┌──────────────┐
│  Dhruva Server  │────▶│  Prometheus  │────▶│   Grafana    │
│  (Port 8000)    │     │  (Port 9090) │     │  (Port 3000) │
│                 │     │              │     │              │
│ /enterprise/    │     │  Scrapes     │     │  Visualizes  │
│   metrics       │     │  Metrics     │     │  Dashboards  │
└─────────────────┘     └──────────────┘     └──────────────┘
```

### Step 1: Configure Docker Compose

The monitoring stack is defined in `docker-compose-monitoring.yml`:

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: dhruva-platform-prometheus
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - dhruva-network

  grafana:
    image: grafana/grafana:latest
    container_name: dhruva-platform-grafana
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_ADMIN_USER}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    ports:
      - "3000:3000"
    networks:
      - dhruva-network
```

### Step 2: Configure Prometheus Scraping

The Prometheus configuration (`prometheus/prometheus.yml`) defines how metrics are scraped:

```yaml
scrape_configs:
  # Dhruva Observability Plugin Enterprise Metrics
  - job_name: "dhruva-enterprise-observability"
    scrape_interval: 5s
    static_configs:
      - targets: ["dhruva-platform-server:8000"]
    metrics_path: "/enterprise/metrics"
```

**How Prometheus Scrapes Metrics:**

1. **Prometheus polls** the Dhruva server every 5 seconds
2. **Requests** the `/enterprise/metrics` endpoint
3. **Parses** Prometheus-formatted metrics from the response
4. **Stores** time-series data in its internal database
5. **Makes data available** to Grafana for visualization

**Metrics Endpoint Structure:**

The `/enterprise/metrics` endpoint (implemented in `metrics.py`) exposes metrics in Prometheus format:

```
# HELP dhruva_enterprise_requests_total Total enterprise requests
# TYPE dhruva_enterprise_requests_total counter
dhruva_enterprise_requests_total{organization="irctc",app="app1",method="POST",endpoint="/translation/v1",status_code="200"} 142.0

# HELP dhruva_enterprise_request_duration_seconds Enterprise request duration
# TYPE dhruva_enterprise_request_duration_seconds histogram
dhruva_enterprise_request_duration_seconds_bucket{organization="irctc",app="app1",method="POST",endpoint="/translation/v1",le="0.005"} 12.0
...
```

### Step 3: Start the Monitoring Stack

```bash
# Start Prometheus and Grafana
docker-compose -f docker-compose-monitoring.yml up -d

# Verify Prometheus is scraping
curl http://localhost:9090/api/v1/targets

# Verify metrics endpoint
curl http://localhost:8000/enterprise/metrics
```

### Step 4: Verify Prometheus is Receiving Metrics

1. Open Prometheus UI: `http://localhost:9090`
2. Go to **Status → Targets**
3. Verify `dhruva-enterprise-observability` is **UP**
4. Go to **Graph** and query: `dhruva_enterprise_requests_total`

---

## Grafana Dashboard Configuration

### Understanding Multi-Tenant Dashboard Setup

Grafana supports **multi-tenancy** through Organizations. Each client organization should have:
- A separate **Grafana Organization**
- A dedicated **Prometheus Data Source** (with organization-specific filtering)
- An **imported dashboard** configured to use their data source

### Step 1: Grafana Organizations and Permissions

**IMPORTANT:** Only the **Grafana Server Admin** can create and manage organizations.

#### Access Grafana Admin Panel

1. Login to Grafana: `http://localhost:3000`
2. Use admin credentials:
   - Username: Value of `GRAFANA_ADMIN_USER`
   - Password: Value of `GRAFANA_ADMIN_PASSWORD`
3. Navigate to **Configuration → Server Admin → Organizations**

#### Create Organization for Each Client

For each client organization (e.g., IRCTC, KisanMitra):

1. Click **+ New Organization**
2. Enter organization name: `IRCTC`
3. Click **Create**
4. Switch to the new organization: **Server Admin → Organizations → IRCTC → Switch To**

#### Create Teams (Optional)

Within each organization, you can create teams for granular access control:

1. Go to **Configuration → Teams**
2. Click **New Team**
3. Add team members with appropriate roles (Admin, Editor, Viewer)

### Step 2: Create Prometheus Data Source for Each Organization

**CRITICAL:** Each Grafana organization must have its **own Prometheus data source** configured.

#### Create Data Source

1. **Switch to the client organization** (e.g., IRCTC)
2. Navigate to **Configuration → Data Sources**
3. Click **Add data source**
4. Select **Prometheus**
5. Configure:
   - **Name:** `Prometheus-IRCTC` (or any meaningful name)
   - **URL:** `http://dhruva-platform-prometheus:9090`
   - **Access:** Server (default)
6. Click **Save & Test**

#### Note the Data Source UID

**IMPORTANT:** After creating the data source, note its **UID** (unique identifier):

1. Click on the newly created data source
2. The URL will be: `http://localhost:3000/datasources/edit/<UID>`
3. **Copy the UID** - you will need it for the dashboard JSON configuration

Example UID: `P1809F7CD0C75ACF3` or `prometheus-irctc-uid`

### Step 3: Configure Dashboard JSON with Prometheus Data Source UID

**CRITICAL STEP:** The dashboard JSON file must be updated with the correct Prometheus data source UID for each organization.

#### Locate the Dashboard JSON File

The DevOps Operations Dashboard JSON file is located in:
```
grafana/provisioning/dashboards/Dhruva DevOps Operations Dashboard-v3-1760288510339.json
```

#### Update Data Source UID in Dashboard JSON

**Before importing**, you must manually edit the dashboard JSON:

1. Open the dashboard JSON file in a text editor
2. Search for `"datasource"` or `"uid"` fields
3. Replace the UID with your organization's Prometheus data source UID

**Example:**

Find sections like this:
```json
{
  "datasource": {
    "type": "prometheus",
    "uid": "OLD_UID_HERE"
  }
}
```

Replace with:
```json
{
  "datasource": {
    "type": "prometheus",
    "uid": "P1809F7CD0C75ACF3"  // Your actual data source UID
  }
}
```

**Using Find & Replace:**

In a text editor (VS Code, Sublime, etc.):
- Find: `"uid": "OLD_UID_HERE"`
- Replace with: `"uid": "P1809F7CD0C75ACF3"`
- Replace all occurrences

**Alternative - Using Command Line:**

```bash
# Linux/Mac
sed -i 's/"uid": "OLD_UID_HERE"/"uid": "P1809F7CD0C75ACF3"/g' "Dhruva DevOps Operations Dashboard-v3-1760288510339.json"

# Windows PowerShell
(Get-Content "Dhruva DevOps Operations Dashboard-v3-1760288510339.json") -replace '"uid": "OLD_UID_HERE"', '"uid": "P1809F7CD0C75ACF3"' | Set-Content "Dhruva DevOps Operations Dashboard-v3-1760288510339.json"
```

### Step 4: Import Dashboard into Grafana

1. **Ensure you're in the correct organization** (e.g., IRCTC)
2. Navigate to **Dashboards → Import**
3. Click **Upload JSON file**
4. Select the **modified dashboard JSON file** (with updated UID)
5. Click **Import**
6. The dashboard should now display metrics for the organization

### Step 5: Add Organization Filtering (Optional but Recommended)

To ensure the dashboard only shows metrics for the specific organization:

1. Open the imported dashboard
2. Click **Dashboard settings** (gear icon)
3. Go to **Variables**
4. Add a new variable:
   - **Name:** `organization`
   - **Type:** Constant
   - **Value:** `irctc` (or the organization name)
5. Update dashboard panels to use this variable in queries

Example query:
```promql
dhruva_enterprise_requests_total{organization="$organization"}
```

### Step 6: Repeat for Each Organization

**For each new client organization:**

1. Create a new Grafana organization
2. Create a new Prometheus data source in that organization
3. Note the new data source UID
4. **Create a copy of the dashboard JSON** and update it with the new UID
5. Import the modified dashboard JSON into the organization

### Summary of Manual Steps Required

| Step | Action | Performed By |
|------|--------|--------------|
| 1 | Create Grafana Organization | Grafana Server Admin |
| 2 | Create Prometheus Data Source | Grafana Server Admin / Org Admin |
| 3 | Copy Data Source UID | Admin |
| 4 | Edit Dashboard JSON with UID | Admin / DevOps Engineer |
| 5 | Import Dashboard JSON | Grafana Org Admin |
| 6 | Verify Metrics Display | Admin / DevOps Engineer |

**Important Notes:**

- ✅ The data source UID **must be updated** in the dashboard JSON before importing
- ✅ Each organization **must have its own data source** created manually
- ✅ The dashboard JSON **cannot automatically detect** the data source - it must be configured
- ✅ Changes to the data source UID require **re-importing** the dashboard or manually updating panels

---

## Metrics Reference

### Available Metrics

The observability system collects and exposes the following metrics:

#### Request Metrics

| Metric | Type | Description | Labels |
|--------|------|-------------|--------|
| `dhruva_enterprise_requests_total` | Counter | Total number of requests | organization, app, method, endpoint, status_code |
| `dhruva_enterprise_request_duration_seconds` | Histogram | Request duration in seconds | organization, app, method, endpoint |
| `dhruva_enterprise_errors_total` | Counter | Total number of errors | organization, app, endpoint, status_code, error_type |

#### Service-Specific Metrics

| Metric | Type | Description | Labels |
|--------|------|-------------|--------|
| `dhruva_enterprise_service_requests_total` | Counter | Requests by service type | organization, app, service_type |
| `dhruva_enterprise_component_latency_seconds` | Histogram | Component processing latency | organization, app, component |

#### Data Processing Metrics

| Metric | Type | Description | Labels |
|--------|------|-------------|--------|
| `dhruva_enterprise_llm_tokens_processed_total` | Counter | LLM tokens processed | organization, app, model |
| `dhruva_enterprise_tts_characters_synthesized` | Histogram | TTS characters per request | organization, app, language |
| `dhruva_enterprise_nmt_characters_translated` | Histogram | NMT characters per request | organization, app, source_language, target_language |
| `dhruva_enterprise_asr_audio_seconds_processed` | Histogram | ASR audio seconds per request | organization, app, language |

#### System Metrics

| Metric | Type | Description | Labels |
|--------|------|-------------|--------|
| `dhruva_enterprise_system_cpu_percent` | Gauge | System CPU usage percentage | - |
| `dhruva_enterprise_system_memory_percent` | Gauge | System memory usage percentage | - |
| `dhruva_enterprise_system_peak_throughput_rpm` | Gauge | Peak throughput (requests per minute) | - |

#### SLA Metrics

| Metric | Type | Description | Labels |
|--------|------|-------------|--------|
| `dhruva_enterprise_sla_availability_percent` | Gauge | Service availability percentage | organization, app |
| `dhruva_enterprise_sla_response_time_seconds` | Gauge | Average response time | organization, app |
| `dhruva_enterprise_sla_compliance_percent` | Gauge | SLA compliance percentage | organization, app, sla_type |

#### Organization Quota Metrics

| Metric | Type | Description | Labels |
|--------|------|-------------|--------|
| `dhruva_enterprise_organization_llm_quota_per_month` | Gauge | Monthly LLM quota (tokens) | organization |
| `dhruva_enterprise_organization_tts_quota_per_month` | Gauge | Monthly TTS quota (characters) | organization |
| `dhruva_enterprise_organization_nmt_quota_per_month` | Gauge | Monthly NMT quota (characters) | organization |
| `dhruva_enterprise_organization_asr_quota_per_month` | Gauge | Monthly ASR quota (audio seconds) | organization |

### Example Prometheus Queries

```promql
# Total requests per organization
sum by (organization) (dhruva_enterprise_requests_total)

# Average request duration by service type
rate(dhruva_enterprise_request_duration_seconds_sum[5m]) 
/ 
rate(dhruva_enterprise_request_duration_seconds_count[5m])

# Error rate by organization
rate(dhruva_enterprise_errors_total[5m])

# TTS characters processed (95th percentile)
histogram_quantile(0.95, 
  rate(dhruva_enterprise_tts_characters_synthesized_bucket[5m])
)
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Metrics Not Appearing in Grafana

**Symptoms:** Dashboard shows "No data" or empty panels

**Troubleshooting Steps:**

1. **Verify Prometheus is scraping:**
   ```bash
   curl http://localhost:9090/api/v1/targets
   ```
   Check if `dhruva-enterprise-observability` target is UP

2. **Check metrics endpoint directly:**
   ```bash
   curl http://localhost:8000/enterprise/metrics
   ```
   Verify metrics are being generated

3. **Verify data source UID in dashboard:**
   - Open dashboard settings
   - Check each panel's data source configuration
   - Ensure UID matches your Prometheus data source

4. **Check Prometheus data source connection:**
   - Go to Configuration → Data Sources → Your Prometheus
   - Click "Save & Test"
   - Should show "Data source is working"

#### 2. Wrong Organization Data Showing

**Symptoms:** Dashboard shows data from multiple organizations

**Solutions:**

1. **Verify organization extraction:**
   ```bash
   export DHRUVA_ENTERPRISE_DEBUG=true
   # Check logs for organization extraction
   ```

2. **Add organization filter to queries:**
   ```promql
   dhruva_enterprise_requests_total{organization="irctc"}
   ```

3. **Check JWT token claims:**
   - Decode JWT token to verify organization field
   - Ensure middleware can extract organization

#### 3. Prometheus Data Source UID Mismatch

**Symptoms:** "Data source not found" errors in Grafana

**Solutions:**

1. **Get correct UID:**
   - Go to Configuration → Data Sources
   - Click on your Prometheus data source
   - Copy UID from URL

2. **Update dashboard JSON:**
   - Export current dashboard
   - Replace all UID occurrences
   - Re-import dashboard

3. **Or update via UI:**
   - Edit each panel individually
   - Change data source to correct one

#### 4. Observability Plugin Not Enabled

**Symptoms:** `/enterprise/metrics` endpoint returns 404

**Solutions:**

1. **Verify environment variable:**
   ```bash
   echo $DHRUVA_ENTERPRISE_ENABLED
   # Should output: true
   ```

2. **Check plugin registration:**
   ```python
   # In main.py
   from dhruva_observability import ObservabilityPlugin
   
   enterprise = ObservabilityPlugin()
   enterprise.register_plugin(app)
   ```

3. **Restart application:**
   ```bash
   docker-compose restart dhruva-platform-server
   ```

#### 5. High Memory Usage

**Symptoms:** Prometheus using excessive memory

**Solutions:**

1. **Reduce retention period:**
   ```yaml
   # In docker-compose-monitoring.yml
   command:
     - '--storage.tsdb.retention.time=15d'
   ```

2. **Reduce scrape interval:**
   ```yaml
   # In prometheus.yml
   scrape_interval: 30s  # Instead of 5s
   ```

3. **Limit metric cardinality:**
   - Reduce number of labels
   - Aggregate metrics at application level

---

## Best Practices

### 1. Organization Naming Convention

Use consistent, lowercase organization identifiers:
```
irctc, kisanmitra, bashadaan, beml
```

### 2. Dashboard Naming Convention

Name dashboards clearly:
```
Dhruva DevOps - IRCTC
Dhruva Business Analytics - KisanMitra
```

### 3. Regular Backup

**Backup important configurations:**
```bash
# Backup Grafana dashboards
docker exec dhruva-platform-grafana grafana-cli admin backup

# Backup Prometheus data
docker run -v prometheus_data:/data -v $(pwd):/backup \
  busybox tar czf /backup/prometheus-backup.tar.gz /data
```

### 4. Security Considerations

1. **Change default Grafana admin password**
2. **Use HTTPS for Grafana** in production
3. **Implement JWT signature verification** (not just decoding)
4. **Restrict Prometheus access** to internal network
5. **Use proper RBAC** in Grafana organizations

### 5. Monitoring the Monitors

Monitor Prometheus itself:
```promql
# Prometheus up
up{job="prometheus"}

# Scrape duration
scrape_duration_seconds{job="dhruva-enterprise-observability"}
```

---

## Support and Contact

For issues, questions, or feature requests:

1. **Check logs first:**
   ```bash
   docker logs dhruva-platform-server
   docker logs dhruva-platform-prometheus
   docker logs dhruva-platform-grafana
   ```

2. **Enable debug mode:**
   ```bash
   export DHRUVA_ENTERPRISE_DEBUG=true
   ```

3. **Contact support** with:
   - Error messages from logs
   - Configuration details
   - Steps to reproduce the issue

---

## Appendix

### A. Quick Reference Checklist

#### Pre-Deployment Checklist

- [ ] Organization extraction implemented (JWT or database)
- [ ] Environment variables configured
- [ ] Grafana admin credentials set
- [ ] Docker Compose files reviewed
- [ ] Network connectivity verified

#### Deployment Checklist

- [ ] Prometheus container running
- [ ] Grafana container running
- [ ] Dhruva server exposing `/enterprise/metrics`
- [ ] Prometheus scraping successfully
- [ ] Grafana Organizations created
- [ ] Prometheus Data Sources created (one per org)
- [ ] Data Source UIDs noted
- [ ] Dashboard JSON files updated with UIDs
- [ ] Dashboards imported successfully
- [ ] Metrics displaying correctly

#### Post-Deployment Checklist

- [ ] Organization filtering working
- [ ] Alerts configured (if applicable)
- [ ] Backup procedures in place
- [ ] Team access configured
- [ ] Documentation updated

### B. File Locations Reference

| Component | File Location |
|-----------|---------------|
| Docker Compose | `docker-compose-monitoring.yml` |
| Prometheus Config | `prometheus/prometheus.yml` |
| Dashboard JSON | `grafana/provisioning/dashboards/Dhruva DevOps Operations Dashboard-v3-*.json` |
| Metrics Collector | `server/observability/metrics.py` (source) or `dhruva_observability/metrics.py` (package) |
| Middleware | `server/observability/middleware.py` (source) or `dhruva_observability/middleware.py` (package) |
| Configuration | `server/observability/config.py` (source) or `dhruva_observability/config.py` (package) |

### C. Port Reference

| Service | Port | Purpose |
|---------|------|---------|
| Dhruva Server | 8000 | Application + Metrics endpoint |
| Prometheus | 9090 | Metrics storage + querying |
| Grafana | 3000 | Visualization + dashboards |
| Pushgateway | 9091 | Batch metrics pushing |

---

**Document Version:** 1.0  
**Last Updated:** October 2025  
**Maintained By:** Dhruva Platform Team

