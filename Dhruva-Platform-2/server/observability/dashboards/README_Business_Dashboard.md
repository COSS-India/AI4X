# Dhruva Business Intelligence & Operations Dashboard

## Overview

The **Dhruva Business Intelligence & Operations Dashboard** is a comprehensive monitoring solution designed specifically for the Dhruva Platform's enterprise observability needs. This dashboard provides real-time insights into business KPIs, system health, and operational metrics that are actually being tracked by the Dhruva Enterprise Observability Plugin.

## Available Metrics

Based on the analysis of the `/enterprise/metrics` endpoint, this dashboard utilizes the following metrics that are actually being collected:

### 🏢 Business Metrics

#### Request Tracking
- `dhruva_enterprise_requests_total` - Total enterprise requests by customer, app, method, endpoint, and status code
- `dhruva_enterprise_request_duration_seconds` - Request duration histogram with percentiles
- `dhruva_enterprise_service_requests_total` - Service requests by type (NMT, TTS, LLM, Pipeline)

#### Data Processing Metrics
- `dhruva_enterprise_llm_tokens_processed_total` - LLM tokens processed by customer, app, and model
- `dhruva_enterprise_tts_characters_synthesized_total` - TTS characters by customer, app, and language
- `dhruva_enterprise_nmt_characters_translated_total` - NMT characters by source/target language pairs
- `dhruva_enterprise_data_processed_total` - General data processing by type

#### Customer Quota Management
- `dhruva_enterprise_customer_llm_quota_per_month` - Monthly LLM token quotas
- `dhruva_enterprise_customer_tts_quota_per_month` - Monthly TTS character quotas
- `dhruva_enterprise_customer_nmt_quota_per_month` - Monthly NMT character quotas

### 🛠️ System & Infrastructure Metrics

#### System Health
- `dhruva_enterprise_system_cpu_percent` - Real-time CPU usage
- `dhruva_enterprise_system_memory_percent` - Real-time memory usage
- `dhruva_enterprise_system_peak_throughput_rpm` - Peak requests per minute
- `dhruva_enterprise_system_service_count` - Active services count

#### Component Performance
- `dhruva_enterprise_component_latency_seconds` - Latency tracking for database, model_inference, etc.

### 📊 Quality & SLA Metrics

#### SLA Compliance
- `dhruva_enterprise_sla_availability_percent` - Service availability percentage
- `dhruva_enterprise_sla_response_time_seconds` - Average response time SLA
- `dhruva_enterprise_sla_compliance_percent` - SLA compliance by type (availability, response_time)

#### Error Tracking
- `dhruva_enterprise_errors_total` - Errors by status code, endpoint, and error type
- Error categorization: `client_error` (4xx), `server_error` (5xx), `unknown_error`

## Dashboard Sections

### 1. 📊 Business Overview
- **Total API Requests**: Cumulative request count across all services
- **Request Rate**: Real-time requests per minute
- **System Health Score**: Availability percentage gauge
- **Revenue Impact**: Error count tracking for business impact assessment

### 2. 🏭 Service Usage & Performance
- **Service Distribution**: Pie chart showing usage across NMT, TTS, LLM, and Pipeline services
- **Service Trends**: Time series of request rates by service type
- **Response Time Analysis**: Average, 95th, and 99th percentile response times
- **Error Rate by Endpoint**: Error percentage tracking by API endpoint

### 3. 💰 Business Metrics & Resource Usage
- **Resource Processing Stats**: 
  - LLM tokens processed by customer and model
  - TTS characters synthesized by language
  - NMT characters translated by language pairs
- **Customer Quota Monitoring**:
  - LLM quota usage percentages
  - TTS quota usage percentages  
  - NMT quota usage percentages

### 4. 🖥️ System Health & Infrastructure
- **CPU & Memory Usage**: Real-time system resource monitoring
- **Peak Throughput**: Maximum requests per minute capacity
- **Active Services**: Current service count
- **Component Latency Heatmap**: Database, model inference, and other component performance

### 5. 📈 SLA & Compliance Monitoring
- **SLA Compliance Trends**: Availability and response time SLA tracking
- **Service Availability Status**: Per-customer availability metrics
- **Response Time SLA**: Response time gauge with thresholds

### 6. 🔧 Technical Deep Dive (Collapsible)
- **Data Processing Volume**: Processing trends by data type
- **Error Distribution**: Error categorization by type
- **HTTP Status Codes**: Request distribution by status code

## Key Features

### Dynamic Filtering
- **Customer Filter**: Multi-select dropdown for customer-specific views
- **Application Filter**: Multi-select dropdown for application-specific monitoring
- Filters automatically populate based on available metric labels

### Business Intelligence
- **Quota Management**: Real-time monitoring of customer usage against quotas
- **Revenue Protection**: Error tracking with business impact assessment
- **Performance SLAs**: Automated SLA compliance monitoring
- **Resource Optimization**: System resource usage tracking

### DevOps Capabilities
- **Real-time Monitoring**: 30-second refresh rate for live operational data
- **Component-level Visibility**: Database and model inference latency tracking
- **Error Analysis**: Detailed error categorization and trending
- **Capacity Planning**: Peak throughput and resource usage tracking

## Usage Recommendations

### For Business Stakeholders
1. Monitor **Business Overview** section for high-level KPIs
2. Track **Customer Quota Usage** to prevent service disruptions
3. Use **Service Usage Distribution** for capacity planning
4. Monitor **SLA Compliance** for customer satisfaction metrics

### For DevOps Teams
1. Focus on **System Health & Infrastructure** for operational health
2. Use **Component Latency Heatmap** for performance optimization
3. Monitor **Error Rate by Endpoint** for service reliability
4. Track **Response Time Analysis** for performance SLA compliance

### For Product Teams
1. Analyze **Service Usage Trends** for feature adoption
2. Monitor **Data Processing Volume** for usage patterns
3. Use **Customer-specific** filtering for account management
4. Track **Business Metrics** for growth analysis

## Installation & Setup

1. Ensure the Dhruva Enterprise Observability Plugin is installed and configured
2. Import the dashboard JSON file into your Grafana instance
3. Configure the Prometheus datasource (UID: `kdjfS_R7c`)
4. Set up appropriate access controls and alerts based on your requirements

## Metrics Collection Requirements

This dashboard requires the following to be properly configured:
- Dhruva Enterprise Observability Plugin v1.0.9+
- Prometheus server collecting from `/enterprise/metrics` endpoint
- Proper customer and application labeling in metrics
- System monitoring enabled (CPU, Memory tracking)

## Thresholds & Alerts

The dashboard includes built-in visual thresholds:
- **Green**: Normal operation (availability >99%, CPU <70%, errors <1%)
- **Yellow**: Warning state (availability 95-99%, CPU 70-90%, errors 1-5%)
- **Red**: Critical state (availability <95%, CPU >90%, errors >5%)

Consider setting up Grafana alerts based on these thresholds for proactive monitoring.
