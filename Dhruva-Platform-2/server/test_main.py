import os
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app, CollectorRegistry, Counter, Histogram

# Create a simple registry for testing
test_registry = CollectorRegistry()

# Simple test app
app = FastAPI(
    title="Dhruva API Test",
    description="Test version for metrics endpoints",
)

# Test if observability plugin is available
try:
    from dhruva_observability import ObservabilityPlugin
    OBSERVABILITY_AVAILABLE = True
    print("✅ Dhruva Observability Plugin available")
except ImportError:
    OBSERVABILITY_AVAILABLE = False
    print("❌ Dhruva Observability Plugin not available")

# Initialize plugin if available
if OBSERVABILITY_AVAILABLE and os.environ.get("DHRUVA_OBSERVABILITY_ENABLED", "false").lower() == "true":
    try:
        enterprise = ObservabilityPlugin()
        enterprise.register_plugin(app)
        print("✅ Dhruva Observability Plugin initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Dhruva Observability Plugin: {e}")
        OBSERVABILITY_AVAILABLE = False

# Create simple test metrics
TEST_REQUESTS = Counter(
    "dhruva_test_requests_total",
    "Total test requests",
    registry=test_registry,
    labelnames=["endpoint", "status"]
)

# Mount metrics endpoint with test registry
metrics_app = make_asgi_app(registry=test_registry)
app.mount("/metrics", metrics_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    TEST_REQUESTS.labels(endpoint="/", status="success").inc()
    return "Welcome to Dhruva API Test!"

@app.get("/health")
def health_check():
    TEST_REQUESTS.labels(endpoint="/health", status="success").inc()
    return {"status": "healthy", "service": "dhruva-test"}

@app.get("/metrics-info")
def metrics_info():
    """Information about available metrics endpoints"""
    TEST_REQUESTS.labels(endpoint="/metrics-info", status="success").inc()
    return {
        "endpoints": {
            "/metrics": "Test metrics from Prometheus client",
            "/enterprise/metrics": f"Enterprise metrics (available: {OBSERVABILITY_AVAILABLE})",
            "/enterprise/health": f"Enterprise health (available: {OBSERVABILITY_AVAILABLE})"
        },
        "plugin_status": {
            "available": OBSERVABILITY_AVAILABLE,
            "enabled": os.environ.get("DHRUVA_OBSERVABILITY_ENABLED", "false")
        }
    }

@app.get("/enterprise/health")
def enterprise_health():
    """Enterprise plugin health endpoint"""
    TEST_REQUESTS.labels(endpoint="/enterprise/health", status="success").inc()
    if OBSERVABILITY_AVAILABLE:
        return {
            "status": "healthy",
            "plugin": "dhruva-enterprise",
            "version": "1.0.9",
            "enabled": True,
            "customers": os.environ.get("DHRUVA_OBSERVABILITY_CUSTOMERS", "default").split(","),
            "apps": os.environ.get("DHRUVA_OBSERVABILITY_APPS", "default").split(","),
        }
    else:
        return {
            "status": "unavailable",
            "plugin": "dhruva-enterprise",
            "enabled": False,
            "message": "Observability plugin not available"
        }

@app.get("/enterprise/metrics")
def enterprise_metrics():
    """Enterprise plugin metrics endpoint"""
    TEST_REQUESTS.labels(endpoint="/enterprise/metrics", status="success").inc()
    
    # Sample enterprise metrics data
    metrics_data = f"""# HELP telemetry_obsv_info Plugin information
# TYPE telemetry_obsv_info gauge
telemetry_obsv_info{{version="1.0.9",status="active",available="{OBSERVABILITY_AVAILABLE}"}} 1

# HELP telemetry_obsv_requests_total Total number of requests processed
# TYPE telemetry_obsv_requests_total counter
telemetry_obsv_requests_total{{app="default",customer="default",endpoint="/",status="success"}} 1
telemetry_obsv_requests_total{{app="default",customer="default",endpoint="/health",status="success"}} 1
telemetry_obsv_requests_total{{app="default",customer="default",endpoint="/metrics-info",status="success"}} 1

# HELP telemetry_obsv_request_duration_seconds Request duration in seconds
# TYPE telemetry_obsv_request_duration_seconds histogram
telemetry_obsv_request_duration_seconds_bucket{{app="default",customer="default",endpoint="/",le="0.05"}} 1
telemetry_obsv_request_duration_seconds_bucket{{app="default",customer="default",endpoint="/",le="0.1"}} 1
telemetry_obsv_request_duration_seconds_bucket{{app="default",customer="default",endpoint="/",le="+Inf"}} 1
telemetry_obsv_request_duration_seconds_sum{{app="default",customer="default",endpoint="/"}} 0.001
telemetry_obsv_request_duration_seconds_count{{app="default",customer="default",endpoint="/"}} 1

# HELP telemetry_obsv_system_info System information
# TYPE telemetry_obsv_system_info gauge
telemetry_obsv_system_info{{hostname="dhruva-test",environment="development"}} 1
"""
    
    return Response(content=metrics_data, media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
