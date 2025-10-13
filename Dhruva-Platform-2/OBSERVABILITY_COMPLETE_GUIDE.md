# Dhruva Observability Package - Complete Guide

> **Comprehensive documentation combining all observability setup, configuration, architecture, and troubleshooting guides.**

---

## 📑 Table of Contents

### Part 1: Getting Started
- [1.1 Overview and Introduction](#11-overview-and-introduction)
- [1.2 Documentation Structure](#12-documentation-structure)
- [1.3 Quick Start Path](#13-quick-start-path)
- [1.4 Key Features](#14-key-features)

### Part 2: Quick Setup Guide
- [2.1 Prerequisites (Must Complete First!)](#21-prerequisites-must-complete-first)
- [2.2 Installation](#22-installation)
- [2.3 Configuration](#23-configuration)
- [2.4 Start Monitoring Stack](#24-start-monitoring-stack)
- [2.5 Grafana Setup (Manual Steps)](#25-grafana-setup-manual-steps)
- [2.6 Verification Checklist](#26-verification-checklist)

### Part 3: Technical Documentation
- [3.1 Installation Options](#31-installation-options)
- [3.2 Prerequisites and Requirements](#32-prerequisites-and-requirements)
- [3.3 Organization Identification Setup](#33-organization-identification-setup)
- [3.4 Monitoring Infrastructure Setup](#34-monitoring-infrastructure-setup)
- [3.5 Grafana Dashboard Configuration](#35-grafana-dashboard-configuration)
- [3.6 Metrics Reference](#36-metrics-reference)
- [3.7 Best Practices](#37-best-practices)

### Part 4: Architecture Diagrams
- [4.1 System Architecture Overview](#41-system-architecture-overview)
- [4.2 Request Flow Diagram](#42-request-flow-diagram)
- [4.3 Organization Extraction Flow](#43-organization-extraction-flow)
- [4.4 Grafana Multi-Tenant Setup Flow](#44-grafana-multi-tenant-setup-flow)
- [4.5 Metrics Scraping Flow](#45-metrics-scraping-flow)
- [4.6 Data Isolation Architecture](#46-data-isolation-architecture)

### Part 5: Local Development Setup
- [5.1 Local Observability Package Setup](#51-local-observability-package-setup)
- [5.2 Deployment Steps](#52-deployment-steps)
- [5.3 Testing Customer Name Extraction](#53-testing-customer-name-extraction)
- [5.4 Environment Variables](#54-environment-variables)
- [5.5 Benefits of Local Package Approach](#55-benefits-of-local-package-approach)

### Part 6: Troubleshooting
- [6.1 Common Issues and Solutions](#61-common-issues-and-solutions)
- [6.2 Quick Fixes](#62-quick-fixes)
- [6.3 Troubleshooting Commands](#63-troubleshooting-commands)

### Part 7: Appendices
- [7.1 File Locations Reference](#71-file-locations-reference)
- [7.2 Port Reference](#72-port-reference)
- [7.3 Deployment Checklists](#73-deployment-checklists)
- [7.4 Support and Contact](#74-support-and-contact)

---

# Part 1: Getting Started

## 1.1 Overview and Introduction

The Dhruva Observability Package is an enterprise-grade monitoring and metrics collection system designed to provide comprehensive observability for Dhruva platform deployments. It enables multi-tenant monitoring, SLA tracking, business analytics, and real-time performance insights.

This comprehensive guide combines all observability documentation into a single reference, making it easier to find information and understand the complete system.

## 1.2 Documentation Structure

This complete guide integrates multiple documentation files designed for different use cases:

### Original Documentation Files

This guide combines the following individual documents:

1. **OBSERVABILITY_README.md** - Documentation index and overview
2. **OBSERVABILITY_QUICK_SETUP_GUIDE.md** - Fast setup steps for DevOps engineers
3. **OBSERVABILITY_TECHNICAL_DOCUMENTATION.md** - Complete technical reference
4. **OBSERVABILITY_ARCHITECTURE_DIAGRAM.md** - Visual architecture diagrams
5. **LOCAL_OBSERVABILITY_SETUP.md** - Local development setup guide

**Note:** All individual files are still available separately if you prefer focused documentation.

## 1.3 Quick Start Path

Follow this path for fastest deployment:

```
1. Read: Section 2 (Quick Setup Guide)
   └─> Get up and running quickly
   
2. Read: Section 3.3 (Organization Identification Setup)
   └─> Implement organization extraction (REQUIRED)
   
3. Reference: Section 3 (Technical Documentation)
   └─> For detailed information and troubleshooting
   
4. Review: Section 4 (Architecture Diagrams)
   └─> Understand system architecture
```

## 1.4 Key Features

- **Multi-tenant metrics collection** with organization-level isolation
- **Automatic service detection** (Translation, TTS, ASR, LLM, etc.)
- **Real-time monitoring** via Prometheus and Grafana
- **Pre-built dashboards** for DevOps and business analytics
- **SLA tracking and compliance** monitoring
- **Resource usage monitoring** (CPU, memory, requests, errors)
- **Character/token/audio tracking** for billing and quota management

---

# Part 2: Quick Setup Guide

> **For:** DevOps engineers who want to get up and running quickly

## 2.1 Prerequisites (Must Complete First!)

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

## 2.2 Installation

### Option 1: pip Package (Quick)
```bash
pip install dhruva-observability
```

### Option 2: Source Code (Customizable)
Copy the `observability` folder from `observability__module` branch into your `server/` directory.

## 2.3 Configuration

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

## 2.4 Start Monitoring Stack

```bash
# Start Prometheus + Grafana
docker-compose -f docker-compose-monitoring.yml up -d

# Verify metrics endpoint
curl http://localhost:8000/enterprise/metrics

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets
```

## 2.5 Grafana Setup (Manual Steps)

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

### Repeat for Each Organization

For each new client (KisanMitra, BashaDaan, BEML, etc.):

1. ✅ Create new Grafana Organization
2. ✅ Create new Prometheus Data Source in that org
3. ✅ Copy the Data Source UID
4. ✅ **Make a copy of dashboard JSON** and update UID
5. ✅ Import the modified JSON into the organization

## 2.6 Verification Checklist

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

# Part 3: Technical Documentation

> **For:** System architects, platform engineers, and technical decision-makers

## 3.1 Installation Options

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

## 3.2 Prerequisites and Requirements

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

## 3.3 Organization Identification Setup

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

## 3.4 Monitoring Infrastructure Setup

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

## 3.5 Grafana Dashboard Configuration

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

## 3.6 Metrics Reference

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

## 3.7 Best Practices

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

# Part 4: Architecture Diagrams

> **Visual representations of system architecture and data flow**

## 4.1 System Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT REQUEST                                   │
│                   (with JWT token or API key)                                 │
└───────────────────────────────────┬──────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                        DHRUVA PLATFORM SERVER                                 │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                  ObservabilityMiddleware                               │  │
│  │                                                                        │  │
│  │  1. Intercept Request                                                  │  │
│  │     ├─> Extract JWT token from Authorization header                   │  │
│  │     ├─> Decode token (with verification)                              │  │
│  │     └─> Extract organization from token claims                        │  │
│  │                                                                        │  │
│  │  2. Service Detection                                                  │  │
│  │     ├─> /translation/* → service="translation"                        │  │
│  │     ├─> /tts/*         → service="tts"                                │  │
│  │     ├─> /asr/*         → service="asr"                                │  │
│  │     └─> /llm/*         → service="llm"                                │  │
│  │                                                                        │  │
│  │  3. Request Body Analysis                                              │  │
│  │     ├─> Extract character count (TTS, NMT)                            │  │
│  │     ├─> Extract token count (LLM)                                     │  │
│  │     └─> Extract audio length (ASR)                                    │  │
│  │                                                                        │  │
│  │  4. Process Request                                                    │  │
│  │     └─> Pass to actual Dhruva handlers                                │  │
│  │                                                                        │  │
│  │  5. Track Metrics                                                      │  │
│  │     ├─> Request count (by org, app, endpoint, status)                 │  │
│  │     ├─> Request duration (histogram)                                  │  │
│  │     ├─> Error tracking (by error type)                                │  │
│  │     ├─> Service-specific metrics                                      │  │
│  │     └─> SLA compliance                                                 │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                    MetricsCollector                                    │  │
│  │                                                                        │  │
│  │  Prometheus Metrics Storage:                                           │  │
│  │  ├─> dhruva_enterprise_requests_total                                 │  │
│  │  ├─> dhruva_enterprise_request_duration_seconds                       │  │
│  │  ├─> dhruva_enterprise_service_requests_total                         │  │
│  │  ├─> dhruva_enterprise_llm_tokens_processed_total                     │  │
│  │  ├─> dhruva_enterprise_tts_characters_synthesized                     │  │
│  │  ├─> dhruva_enterprise_nmt_characters_translated                      │  │
│  │  ├─> dhruva_enterprise_asr_audio_seconds_processed                    │  │
│  │  ├─> dhruva_enterprise_errors_total                                   │  │
│  │  ├─> dhruva_enterprise_system_cpu_percent                             │  │
│  │  ├─> dhruva_enterprise_system_memory_percent                          │  │
│  │  └─> ... (50+ metrics total)                                          │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  Exposed Endpoints:                                                           │
│  ├─> GET  /enterprise/metrics  (Prometheus format)                           │
│  ├─> GET  /enterprise/health   (Health check)                                │
│  └─> POST /translation/v1      (Example Dhruva endpoint)                     │
│                                                                               │
│  Port: 8000                                                                   │
└───────────────────────────────────┬──────────────────────────────────────────┘
                                    │
                                    │ HTTP GET /enterprise/metrics
                                    │ (Every 5 seconds)
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            PROMETHEUS                                         │
│                                                                               │
│  Scrape Configuration (prometheus.yml):                                      │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ scrape_configs:                                                        │  │
│  │   - job_name: "dhruva-enterprise-observability"                        │  │
│  │     scrape_interval: 5s                                                │  │
│  │     static_configs:                                                    │  │
│  │       - targets: ["dhruva-platform-server:8000"]                       │  │
│  │     metrics_path: "/enterprise/metrics"                                │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  Time-Series Database:                                                        │
│  ├─> Stores all metrics with timestamps                                      │
│  ├─> Retention: 15 days (configurable)                                       │
│  ├─> Query language: PromQL                                                  │
│  └─> Provides HTTP API for queries                                           │
│                                                                               │
│  Web UI: http://localhost:9090                                               │
│  Port: 9090                                                                   │
└───────────────────────────────────┬──────────────────────────────────────────┘
                                    │
                                    │ PromQL Queries
                                    │ (Data visualization requests)
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                              GRAFANA                                          │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  Server Admin Panel                                                    │  │
│  │  └─> Manages all organizations                                         │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  Organization: IRCTC                                                   │  │
│  │                                                                        │  │
│  │  Data Source:                                                          │  │
│  │  ├─> Name: Prometheus-IRCTC                                           │  │
│  │  ├─> Type: Prometheus                                                  │  │
│  │  ├─> URL: http://dhruva-platform-prometheus:9090                      │  │
│  │  └─> UID: P1809F7CD0C75ACF3  ← Important! Used in dashboard          │  │
│  │                                                                        │  │
│  │  Dashboard: Dhruva DevOps Operations                                   │  │
│  │  ├─> Data Source: P1809F7CD0C75ACF3                                   │  │
│  │  ├─> Organization Filter: {organization="irctc"}                      │  │
│  │  └─> Panels:                                                           │  │
│  │       ├─> Total Requests                                               │  │
│  │       ├─> Request Rate                                                 │  │
│  │       ├─> Error Rate                                                   │  │
│  │       ├─> Service Breakdown                                            │  │
│  │       ├─> Response Time                                                │  │
│  │       └─> Resource Usage                                               │  │
│  │                                                                        │  │
│  │  Teams & Users:                                                        │  │
│  │  ├─> IRCTC Admins (Admin role)                                        │  │
│  │  ├─> IRCTC DevOps (Editor role)                                       │  │
│  │  └─> IRCTC Viewers (Viewer role)                                      │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  Organization: KisanMitra                                              │  │
│  │                                                                        │  │
│  │  Data Source:                                                          │  │
│  │  ├─> Name: Prometheus-KisanMitra                                      │  │
│  │  ├─> UID: XYZ789ABC123DEF456  ← Different UID!                        │  │
│  │  └─> Same Prometheus, different data filtering                        │  │
│  │                                                                        │  │
│  │  Dashboard: Dhruva DevOps Operations                                   │  │
│  │  ├─> Data Source: XYZ789ABC123DEF456                                  │  │
│  │  └─> Organization Filter: {organization="kisanmitra"}                 │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  Organization: BashaDaan                                               │  │
│  │  ... (similar structure)                                               │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  Web UI: http://localhost:3000                                               │
│  Port: 3000                                                                   │
└──────────────────────────────────────────────────────────────────────────────┘
```

## 4.2 Request Flow Diagram

```
┌─────────┐
│ Client  │
└────┬────┘
     │
     │ 1. HTTP Request
     │    POST /translation/v1
     │    Authorization: Bearer eyJhbGc...
     │    Body: {"input": [{"source": "Hello"}]}
     │
     ▼
┌────────────────────────────────────────────┐
│  ObservabilityMiddleware.dispatch()       │
└────┬───────────────────────────────────────┘
     │
     │ 2. Extract Organization
     │    ├─> Decode JWT token
     │    ├─> Get "organization" claim
     │    └─> organization = "irctc"
     │
     ▼
┌────────────────────────────────────────────┐
│  Detect Service Type                       │
└────┬───────────────────────────────────────┘
     │
     │ 3. Path Analysis
     │    ├─> path = "/translation/v1"
     │    └─> service_type = "translation"
     │
     ▼
┌────────────────────────────────────────────┐
│  Extract Request Metrics                   │
└────┬───────────────────────────────────────┘
     │
     │ 4. Body Analysis
     │    ├─> Parse JSON body
     │    ├─> Count characters: "Hello" = 5
     │    └─> translation_characters = 5
     │
     ▼
┌────────────────────────────────────────────┐
│  Start Timer & Process Request             │
└────┬───────────────────────────────────────┘
     │
     │ 5. Call Next Handler
     │    response = await call_next(request)
     │    status_code = 200
     │
     ▼
┌────────────────────────────────────────────┐
│  Stop Timer & Calculate Duration           │
└────┬───────────────────────────────────────┘
     │
     │ 6. duration = time.time() - start_time
     │    duration = 0.234 seconds
     │
     ▼
┌────────────────────────────────────────────┐
│  Track Metrics                             │
└────┬───────────────────────────────────────┘
     │
     │ 7. Update Prometheus Metrics
     │
     ├─> dhruva_enterprise_requests_total
     │   {org="irctc", app="app1", method="POST", 
     │    endpoint="/translation/v1", status="200"} +1
     │
     ├─> dhruva_enterprise_request_duration_seconds
     │   {org="irctc", app="app1", method="POST",
     │    endpoint="/translation/v1"} observe(0.234)
     │
     ├─> dhruva_enterprise_service_requests_total
     │   {org="irctc", app="app1", 
     │    service_type="translation"} +1
     │
     ├─> dhruva_enterprise_nmt_characters_translated
     │   {org="irctc", app="app1", source_lang="en",
     │    target_lang="hi"} observe(5)
     │
     └─> dhruva_enterprise_component_latency_seconds
         {org="irctc", app="app1", 
          component="translation"} observe(0.234)
     │
     ▼
┌────────────────────────────────────────────┐
│  Return Response to Client                 │
└────────────────────────────────────────────┘
```

## 4.3 Organization Extraction Flow

```
┌─────────────────────────────────────────────────────────────┐
│              Request Headers                                │
│  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6...      │
│  X-Customer-ID: irctc (optional fallback)                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────┐
        │  Extract Authorization Header     │
        └───────────┬───────────────────────┘
                    │
                    ▼
        ┌───────────────────────────────────┐
        │  Check if starts with "Bearer "   │
        └───────┬───────────┬───────────────┘
                │           │
            YES │           │ NO
                │           │
                ▼           ▼
    ┌──────────────────┐   ┌──────────────────┐
    │ Extract Token    │   │ Use X-Customer-ID│
    │ token = header[7:]│  │ header or default│
    └────┬─────────────┘   └──────────────────┘
         │
         ▼
    ┌──────────────────────────────────┐
    │  Decode JWT Token                │
    │  jwt.decode(token, secret, ...)  │
    └────┬─────────────────────────────┘
         │
         ▼
    ┌──────────────────────────────────────────┐
    │  Extract Organization from Token Claims  │
    │                                          │
    │  Priority Order:                         │
    │  1. decoded["organization"]              │
    │  2. decoded["org"]                       │
    │  3. decoded["name"]                      │
    │  4. decoded["company"]                   │
    └────┬─────────────────────────────────────┘
         │
         ▼
    ┌──────────────────────────────────┐
    │  Organization Found?             │
    └────┬──────────────┬──────────────┘
         │              │
     YES │              │ NO
         │              │
         ▼              ▼
    ┌─────────┐   ┌──────────────────┐
    │ Return  │   │ Return "default" │
    │ org name│   │ organization     │
    └─────────┘   └──────────────────┘
         │              │
         └──────┬───────┘
                │
                ▼
    ┌──────────────────────────────────┐
    │  Use Organization in Metrics     │
    │  {organization="irctc", ...}     │
    └──────────────────────────────────┘
```

## 4.4 Grafana Multi-Tenant Setup Flow

```
┌────────────────────────────────────────────────────────┐
│  Grafana Server Admin                                  │
│  Login: http://localhost:3000                          │
│  User: admin, Pass: <GRAFANA_ADMIN_PASSWORD>           │
└───────────────┬────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────┐
│  STEP 1: Create Organization                           │
│  Server Admin → Organizations → New Organization       │
│  Name: "IRCTC"                                         │
└───────────────┬────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────┐
│  STEP 2: Switch to Organization                        │
│  Server Admin → Organizations → IRCTC → Switch To      │
└───────────────┬────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────┐
│  STEP 3: Create Prometheus Data Source                 │
│  Configuration → Data Sources → Add data source        │
│                                                         │
│  Settings:                                              │
│  - Type: Prometheus                                     │
│  - Name: Prometheus-IRCTC                              │
│  - URL: http://dhruva-platform-prometheus:9090         │
│                                                         │
│  Click "Save & Test"                                    │
└───────────────┬────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────┐
│  STEP 4: Note Data Source UID                          │
│                                                         │
│  URL shows: /datasources/edit/P1809F7CD0C75ACF3        │
│                                    ↑                    │
│                             Copy this UID!              │
│                                                         │
│  UID = "P1809F7CD0C75ACF3"                             │
└───────────────┬────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────┐
│  STEP 5: Update Dashboard JSON (Outside Grafana)       │
│                                                         │
│  File: grafana/provisioning/dashboards/                │
│        Dhruva DevOps Operations Dashboard-*.json       │
│                                                         │
│  Find & Replace:                                        │
│  FROM: "uid": "OLD_UID_HERE"                           │
│  TO:   "uid": "P1809F7CD0C75ACF3"                      │
│                                                         │
│  Replace ALL occurrences in the file                   │
└───────────────┬────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────┐
│  STEP 6: Import Dashboard                              │
│  Dashboards → Import → Upload JSON file                │
│                                                         │
│  Select: Modified dashboard JSON file                  │
│  (with updated UID)                                     │
│                                                         │
│  Click "Import"                                         │
└───────────────┬────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────┐
│  STEP 7: Verify Dashboard                              │
│                                                         │
│  Dashboard should show:                                 │
│  ✅ Data loading (not "No data")                       │
│  ✅ Metrics filtered for "irctc" organization          │
│  ✅ All panels working                                 │
└───────────────┬────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────┐
│  STEP 8: Repeat for Next Organization                  │
│  - Create new organization (e.g., "KisanMitra")        │
│  - Create new data source (different UID!)             │
│  - Make NEW copy of dashboard JSON                     │
│  - Update with NEW UID                                 │
│  - Import into KisanMitra organization                 │
└────────────────────────────────────────────────────────┘
```

## 4.5 Metrics Scraping Flow

```
┌────────────────────────────────────────────────────────┐
│  Prometheus (Every 5 seconds)                          │
└───────────────┬────────────────────────────────────────┘
                │
                ▼
        ┌──────────────────┐
        │ HTTP GET Request │
        │ To: dhruva-platform-server:8000/enterprise/metrics
        └────┬─────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────┐
│  Dhruva Server: MetricsCollector.get_metrics_text()   │
└───────────────┬────────────────────────────────────────┘
                │
                ▼
        ┌──────────────────────────────┐
        │ Generate Prometheus Format   │
        │                              │
        │ # HELP metric_name           │
        │ # TYPE metric_name counter   │
        │ metric_name{labels} value    │
        └────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────┐
│  Example Metrics Response:                               │
│                                                           │
│  dhruva_enterprise_requests_total{                       │
│    organization="irctc",                                 │
│    app="app1",                                           │
│    method="POST",                                        │
│    endpoint="/translation/v1",                           │
│    status_code="200"                                     │
│  } 1523.0                                                │
│                                                           │
│  dhruva_enterprise_request_duration_seconds_bucket{      │
│    organization="irctc",                                 │
│    app="app1",                                           │
│    method="POST",                                        │
│    endpoint="/translation/v1",                           │
│    le="0.5"                                              │
│  } 1420.0                                                │
│                                                           │
│  dhruva_enterprise_nmt_characters_translated_bucket{     │
│    organization="irctc",                                 │
│    app="app1",                                           │
│    source_language="en",                                 │
│    target_language="hi",                                 │
│    le="100.0"                                            │
│  } 856.0                                                 │
└───────────────┬──────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────┐
│  Prometheus Stores Metrics                             │
│  - Timestamp: 2025-10-13 10:30:15                      │
│  - Metric: dhruva_enterprise_requests_total            │
│  - Labels: {organization="irctc", ...}                 │
│  - Value: 1523.0                                       │
└───────────────┬────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────┐
│  Grafana Queries Prometheus                            │
│  - PromQL: rate(dhruva_enterprise_requests_total[5m])  │
│  - Filters: {organization="irctc"}                     │
│  - Returns: Time-series data for visualization         │
└────────────────────────────────────────────────────────┘
```

## 4.6 Data Isolation Architecture

```
                    ┌──────────────────────┐
                    │   Prometheus DB      │
                    │  (All Organizations) │
                    └──────────┬───────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
            ▼                  ▼                  ▼
  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
  │ Metrics with    │ │ Metrics with    │ │ Metrics with    │
  │ org="irctc"     │ │ org="kisanmitra"│ │ org="bashadaan" │
  └─────────────────┘ └─────────────────┘ └─────────────────┘
            │                  │                  │
            │                  │                  │
  ┌─────────▼────────┐ ┌──────▼──────────┐ ┌────▼────────────┐
  │ Grafana Org:     │ │ Grafana Org:    │ │ Grafana Org:    │
  │ IRCTC            │ │ KisanMitra      │ │ BashaDaan       │
  │                  │ │                 │ │                 │
  │ Data Source:     │ │ Data Source:    │ │ Data Source:    │
  │ UID: ABC123      │ │ UID: XYZ789     │ │ UID: DEF456     │
  │                  │ │                 │ │                 │
  │ Dashboard Query: │ │ Dashboard Query:│ │ Dashboard Query:│
  │ {org="irctc"}    │ │ {org="kisan*"}  │ │ {org="basha*"}  │
  └──────────────────┘ └─────────────────┘ └─────────────────┘
            │                  │                  │
            ▼                  ▼                  ▼
  ┌──────────────────┐ ┌─────────────────┐ ┌─────────────────┐
  │ IRCTC sees only  │ │ KisanMitra sees │ │ BashaDaan sees  │
  │ IRCTC metrics    │ │ only KM metrics │ │ only BD metrics │
  └──────────────────┘ └─────────────────┘ └─────────────────┘

Key Points:
- All metrics stored in same Prometheus instance
- Isolation achieved through organization labels
- Each Grafana org has separate data source (different UID)
- Dashboard queries filter by organization
- Users can only access their organization in Grafana
```

---

# Part 5: Local Development Setup

> **For:** Developers working with local observability package

## 5.1 Local Observability Package Setup

### Overview
This section describes how to configure the Dhruva Platform to use the **local observability package** instead of installing from TestPyPI.

### Changes Made

#### 1. Copied Local Package to Server Directory
```bash
cp -r dhruva_observability_package/dhruva_observability server/
```

This copies the latest observability code directly into the server directory so it gets included in the Docker build.

#### 2. Requirements.txt Configuration
The `server/requirements.txt` already has the TestPyPI package commented out:
```
# dhruva-observability==1.0.9
```

#### 3. Server Code (main.py)
The server imports the observability plugin locally:
```python
from dhruva_observability import ObservabilityPlugin
```

Since we copied the package to `server/dhruva_observability/`, Python will find it locally first before looking for installed packages.

### Key Features of the Latest Middleware

#### Customer Name Extraction from JWT
The middleware now extracts customer names from JWT tokens in the Authorization header:

```python
def _extract_customer_from_token(self, request: Request) -> str:
    """Extract customer name from JWT token in authorization header."""
    auth_header = request.headers.get("authorization", "")
    
    if auth_header:
        decoded_token = self._decode_jwt_token(auth_header)
        if decoded_token:
            # Extract customer name from 'name' field in token
            customer_name = decoded_token.get("name")
            if customer_name:
                return customer_name
            
            # Fallback: try to extract from 'sub' field if 'name' is not available
            sub = decoded_token.get("sub")
            if sub:
                return sub
    
    return self.config.default_customer
```

#### Debug Logging
When `DHRUVA_ENTERPRISE_DEBUG=true`, the middleware logs detailed request information:
```python
print(f"🔍 Request: {method} {path} -> Service: {service_type}, Customer: {customer}, App: {app}")
print(f"🔑 Extracted customer from JWT: {customer_name}")
```

## 5.2 Deployment Steps

### 1. Stop All Containers
```bash
sudo docker compose -f docker-compose-db.yml -f docker-compose-metering.yml -f docker-compose-monitoring.yml -f docker-compose-app.yml down
```

### 2. Clear Prometheus Data (Optional)
```bash
sudo rm -rf prometheus/data
```

### 3. Clear Docker Build Cache (Optional)
```bash
sudo docker builder prune -af
```

### 4. Copy Local Package
```bash
cp -r dhruva_observability_package/dhruva_observability server/
```

### 5. Rebuild Server and Worker Images
```bash
sudo docker compose -f docker-compose-db.yml -f docker-compose-metering.yml -f docker-compose-monitoring.yml -f docker-compose-app.yml build server worker
```

### 6. Start All Services
```bash
sudo docker compose -f docker-compose-db.yml -f docker-compose-metering.yml -f docker-compose-monitoring.yml -f docker-compose-app.yml up -d
```

## 5.3 Testing Customer Name Extraction

### 1. Generate a Test JWT Token
```bash
python3 -c "
import jwt
import datetime

payload = {
    'name': 'TestCustomer123',
    'sub': 'user@example.com',
    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
}

token = jwt.encode(payload, 'secret', algorithm='HS256')
print(f'Bearer {token}')
"
```

### 2. Make a Request with the Token
```bash
TOKEN="<your-generated-token>"
curl -X GET "http://localhost:8000/enterprise/health" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Check the Logs
```bash
sudo docker logs dhruva-platform-server --tail 20 | grep "🔍\|🔑"
```

You should see output like:
```
🔍 Request: GET /enterprise/health -> Service: enterprise, Customer: TestCustomer123, App: default
🔑 Extracted customer from JWT: TestCustomer123
```

## 5.4 Environment Variables

The observability plugin is configured with these environment variables (in `docker-compose-app.yml`):

```yaml
environment:
  - DHRUVA_ENTERPRISE_ENABLED=true
  - DHRUVA_ENTERPRISE_DEBUG=true
  - DHRUVA_ENTERPRISE_CUSTOMERS=cust1,cust2,default
  - DHRUVA_ENTERPRISE_APPS=app1,app2,default
  - DHRUVA_ENTERPRISE_METRICS_PATH=/enterprise/metrics
  - DHRUVA_ENTERPRISE_HEALTH_PATH=/enterprise/health
```

### Prometheus Metrics

The middleware tracks metrics by customer and app:
- `dhruva_enterprise_requests_total{customer="TestCustomer123", app="default"}`
- `dhruva_enterprise_request_duration_seconds{customer="TestCustomer123", app="default"}`

Access metrics at: http://localhost:8000/enterprise/metrics

### Troubleshooting

#### Check if Local Package is Being Used
```bash
sudo docker exec dhruva-platform-server ls -la /app/dhruva_observability/
```

#### Check Installed Package Version vs Local Code
```bash
sudo docker exec dhruva-platform-server cat /app/dhruva_observability/middleware.py | grep "# Debug logging" -A 2
```

Should show:
```python
# Debug logging
if self.config.debug:
    print(f"🔍 Request: {method} {path} -> Service: {service_type}, Customer: {customer}, App: {app}")
```

#### View Real-time Logs
```bash
sudo docker logs -f dhruva-platform-server
```

## 5.5 Benefits of Local Package Approach

1. **No TestPyPI Dependency**: No need to publish to TestPyPI for every change
2. **Instant Updates**: Changes to local code are immediately available after rebuild
3. **Development Speed**: Faster iteration during development
4. **Version Control**: The exact code version is in the repository

### Future Migration to Published Package

When ready to use a published package:

1. Uncomment in `server/requirements.txt`:
   ```
   dhruva-observability==1.0.10
   ```

2. Remove the local copy:
   ```bash
   rm -rf server/dhruva_observability/
   ```

3. Rebuild containers

---

# Part 6: Troubleshooting

## 6.1 Common Issues and Solutions

### 1. Metrics Not Appearing in Grafana

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

### 2. Wrong Organization Data Showing

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

### 3. Prometheus Data Source UID Mismatch

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

### 4. Observability Plugin Not Enabled

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

### 5. High Memory Usage

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

## 6.2 Quick Fixes

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

## 6.3 Troubleshooting Commands

```bash
# View all metrics
curl http://localhost:8000/enterprise/metrics

# Restart monitoring stack
docker-compose -f docker-compose-monitoring.yml restart

# View Prometheus targets
open http://localhost:9090/targets

# Access Grafana
open http://localhost:3000

# Check Prometheus data
curl http://localhost:9090/api/v1/query?query=dhruva_enterprise_requests_total

# View server logs
docker logs dhruva-platform-server

# View Prometheus logs
docker logs dhruva-platform-prometheus

# View Grafana logs
docker logs dhruva-platform-grafana
```

---

# Part 7: Appendices

## 7.1 File Locations Reference

| Component | File Location |
|-----------|---------------|
| **Documentation** | |
| Complete Guide (This File) | `OBSERVABILITY_COMPLETE_GUIDE.md` |
| Quick Setup Guide | `OBSERVABILITY_QUICK_SETUP_GUIDE.md` |
| Technical Docs | `OBSERVABILITY_TECHNICAL_DOCUMENTATION.md` |
| Architecture Diagrams | `OBSERVABILITY_ARCHITECTURE_DIAGRAM.md` |
| Local Setup Guide | `LOCAL_OBSERVABILITY_SETUP.md` |
| Documentation Index | `OBSERVABILITY_README.md` |
| **Source Code** | |
| Metrics Collector | `server/observability/metrics.py` |
| Middleware | `server/observability/middleware.py` |
| Configuration | `server/observability/config.py` |
| Plugin | `server/observability/plugin.py` |
| **Infrastructure** | |
| Docker Compose | `docker-compose-monitoring.yml` |
| Prometheus Config | `prometheus/prometheus.yml` |
| Dashboard JSONs | `grafana/provisioning/dashboards/*.json` |
| Grafana Datasources | `grafana/provisioning/datasources/*.yml` |

## 7.2 Port Reference

| Service | Port | Purpose |
|---------|------|---------|
| Dhruva Server | 8000 | Application + Metrics endpoint |
| Prometheus | 9090 | Metrics storage + querying |
| Grafana | 3000 | Visualization + dashboards |
| Pushgateway | 9091 | Batch metrics pushing (optional) |

## 7.3 Deployment Checklists

### Pre-Deployment Checklist

- [ ] Read all documentation sections
- [ ] Implement organization extraction
- [ ] Test organization extraction with debug mode
- [ ] Set environment variables
- [ ] Configure Grafana admin credentials

### Deployment Checklist

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

### Post-Deployment Checklist

- [ ] Verify organization isolation
- [ ] Test with multiple organizations
- [ ] Configure backup procedures
- [ ] Document organization-specific configurations
- [ ] Train team on dashboard usage

## 7.4 Support and Contact

### Getting Help

1. **Check documentation** in this complete guide
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

## Document Information

**Document Version:** 1.0  
**Last Updated:** October 2025  
**Maintained By:** Dhruva Platform Team

**Combined from:**
- OBSERVABILITY_README.md
- OBSERVABILITY_QUICK_SETUP_GUIDE.md
- OBSERVABILITY_TECHNICAL_DOCUMENTATION.md
- OBSERVABILITY_ARCHITECTURE_DIAGRAM.md
- LOCAL_OBSERVABILITY_SETUP.md

---

**End of Complete Guide**


