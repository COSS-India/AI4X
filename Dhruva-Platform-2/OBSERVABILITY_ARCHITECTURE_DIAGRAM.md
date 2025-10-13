# Dhruva Observability Architecture Diagrams

## System Architecture Overview

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

---

## Request Flow Diagram

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

---

## Organization Extraction Flow

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

---

## Grafana Multi-Tenant Setup Flow

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

---

## Metrics Scraping Flow

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

---

## Data Isolation Architecture

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

## Error Handling Flow

```
┌─────────────────────────┐
│ Request with Invalid JWT│
└───────────┬─────────────┘
            │
            ▼
┌───────────────────────────────┐
│ _decode_jwt_token() fails     │
│ - Returns None                │
│ - Logs error if debug=true    │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│ Fallback to Header            │
│ organization = headers.get(   │
│   "X-Customer-ID", "default") │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│ organization = "default"      │
│ Continue processing request   │
│ (Metrics tagged with "default")
└───────────────────────────────┘

Principle: Never fail the request due to metrics collection issues
```

---

## Summary Flowchart: Complete Request Lifecycle

```
Client Request
      │
      ├─> [Middleware] Extract Org → JWT decode → organization="irctc"
      │
      ├─> [Middleware] Detect Service → Path="/translation/v1" → service="translation"
      │
      ├─> [Middleware] Extract Metrics → Body analysis → characters=42
      │
      ├─> [Dhruva] Process Request → Translate text → Return response
      │
      ├─> [Middleware] Track Metrics → Update Prometheus counters/histograms
      │
      ├─> [Prometheus] Scrape /enterprise/metrics → Store time-series data
      │
      └─> [Grafana] Query Prometheus → Filter by org → Display dashboard
```

---

**Document Version:** 1.0  
**Last Updated:** October 2025

