#!/usr/bin/env python3
"""
Example usage of the updated ObservabilityMiddleware with JWT token extraction
"""
from fastapi import FastAPI, Request
from dhruva_observability import ObservabilityMiddleware, MetricsCollector, PluginConfig

# Create FastAPI app
app = FastAPI()

# Configure the observability plugin
config = PluginConfig(
    enabled=True,
    debug=True,  # Enable debug logging to see JWT extraction
    default_customer="unknown",
    default_app="default_app"
)

# Initialize metrics collector
metrics_collector = MetricsCollector()

# Add the middleware
app.add_middleware(
    ObservabilityMiddleware,
    metrics_collector=metrics_collector,
    config=config
)

@app.get("/services/inference/translation")
async def translation_endpoint(request: Request):
    """Example translation endpoint that would receive the curl request."""
    return {
        "message": "Translation service",
        "customer": getattr(request.state, 'customer', 'not_set'),
        "extracted_from": "JWT token or headers"
    }

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint."""
    return {"message": "Test endpoint"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting server with JWT-enabled ObservabilityMiddleware...")
    print("📋 Test with your curl command to see customer name extraction in action!")
    print("🔍 Debug logs will show JWT decoding process")
    uvicorn.run(app, host="0.0.0.0", port=8000)
