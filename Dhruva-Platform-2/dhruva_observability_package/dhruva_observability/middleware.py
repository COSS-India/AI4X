"""
Middleware for Dhruva Observability Plugin

Handles request tracking, service detection, and metrics collection.
"""
import time
from typing import Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from .config import PluginConfig
from .metrics import MetricsCollector


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Middleware for tracking requests and collecting metrics."""
    
    def __init__(self, app, metrics_collector: Optional[MetricsCollector] = None, 
                 config: Optional[PluginConfig] = None):
        """Initialize middleware."""
        super().__init__(app)
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.config = config or PluginConfig()
    
    async def dispatch(self, request: Request, call_next):
        """Process request through middleware."""
        if not self.config.enabled:
            return await call_next(request)
        
        start_time = time.time()
        
        # Extract metadata from request
        path = request.url.path
        method = request.method
        headers = request.headers
        
        # Extract customer and app
        customer = headers.get("x-customer-id", self.config.default_customer)
        app = headers.get("x-app-id", self.config.default_app)
        
        # Validate against allowed lists
        if not self.config.is_customer_allowed(customer):
            customer = self.config.default_customer
        if not self.config.is_app_allowed(app):
            app = self.config.default_app
        
        # Detect service type
        service_type = self._detect_service_type(path)
        
        # Debug logging
        if self.config.debug:
            print(f"🔍 Request: {method} {path} -> Service: {service_type}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Track request
        try:
            self.metrics_collector.track_request(
                customer=customer,
                app=app,
                method=method,
                endpoint=path,
                status_code=response.status_code,
                duration=duration,
                service_type=service_type
            )
            
            # Track additional metrics based on service type
            self._track_additional_metrics(customer, app, service_type, path, duration)
            
        except Exception as e:
            # Don't let metrics collection break the request
            if self.config.debug:
                print(f"⚠️ Metrics collection failed: {e}")

        return response
    
    def _extract_customer_app(self, request: Request) -> tuple:
        """Extract customer and app from request headers."""
        customer = request.headers.get("X-Customer-ID", "default")
        app = request.headers.get("X-App-ID", "default")
        
        # Validate against allowed lists
        if not self.config.is_customer_allowed(customer):
            customer = self.config.default_customer
        if not self.config.is_app_allowed(app):
            app = self.config.default_app
            
        return customer, app
    
    def _detect_service_type(self, path: str) -> str:
        """Detect service type from URL path."""
        path_lower = path.lower()
        
        # Check for specific service patterns
        if any(pattern in path_lower for pattern in ["/translation", "/nmt", "/translate"]):
            return "translation"
        elif any(pattern in path_lower for pattern in ["/asr", "/transcribe", "/speech"]):
            return "asr"
        elif any(pattern in path_lower for pattern in ["/tts", "/synthesize", "/speak"]):
            return "tts"
        elif any(pattern in path_lower for pattern in ["/ner", "/entity", "/entities"]):
            return "ner"
        elif any(pattern in path_lower for pattern in ["/transliteration", "/xlit", "/transliterate"]):
            return "transliteration"
        elif any(pattern in path_lower for pattern in ["/llm", "/generate", "/chat", "/completion"]):
            return "llm"
        elif any(pattern in path_lower for pattern in ["/enterprise", "/health", "/metrics", "/config"]):
            return "enterprise"
        elif any(pattern in path_lower for pattern in ["/docs", "/openapi", "/redoc"]):
            return "documentation"
        else:
            return "unknown"
    
    def _track_additional_metrics(self, customer: str, app: str, service_type: str, path: str, duration: float):
        """Track additional metrics based on service type."""
        try:
            # Track component latency
            self.metrics_collector.track_component_latency(
                customer=customer,
                app=app,
                component=service_type,
                duration=duration
            )
            
            # Track data processing based on service type
            if service_type == "llm":
                # Mock LLM token processing
                tokens = self._estimate_llm_tokens(path)
                self.metrics_collector.track_llm_tokens(
                    customer=customer,
                    app=app,
                    model="gpt-3.5-turbo",  # Mock model
                    tokens=tokens
                )
            elif service_type == "tts":
                # Mock TTS character synthesis
                characters = self._estimate_tts_characters(path)
                self.metrics_collector.track_tts_characters(
                    customer=customer,
                    app=app,
                    language="en",  # Mock language
                    characters=characters
                )
            elif service_type == "translation":
                # Mock NMT character translation
                characters = self._estimate_nmt_characters(path)
                self.metrics_collector.track_nmt_characters(
                    customer=customer,
                    app=app,
                    source_lang="en",
                    target_lang="hi",
                    characters=characters
                )
            
            # Update SLA compliance (mock calculation)
            compliance = self._calculate_sla_compliance(service_type, duration)
            self.metrics_collector.update_sla_compliance(
                customer=customer,
                app=app,
                sla_type=f"{service_type}_availability",
                compliance_percent=compliance
            )
            
        except Exception as e:
            if self.config.debug:
                print(f"⚠️ Additional metrics tracking failed: {e}")
    
    def _estimate_llm_tokens(self, path: str) -> int:
        """Estimate LLM tokens based on path."""
        # Mock estimation - in real implementation, this would analyze request content
        return 100  # Mock value
    
    def _estimate_tts_characters(self, path: str) -> int:
        """Estimate TTS characters based on path."""
        # Mock estimation - in real implementation, this would analyze request content
        return 50  # Mock value
    
    def _estimate_nmt_characters(self, path: str) -> int:
        """Estimate NMT characters based on path."""
        # Mock estimation - in real implementation, this would analyze request content
        return 200  # Mock value
    
    def _calculate_sla_compliance(self, service_type: str, duration: float) -> float:
        """Calculate SLA compliance based on service type and duration."""
        # Mock SLA compliance calculation
        if service_type == "llm":
            return 99.5 if duration < 2.0 else 95.0
        elif service_type == "tts":
            return 99.8 if duration < 1.0 else 97.0
        elif service_type == "translation":
            return 99.9 if duration < 0.5 else 98.0
        else:
            return 99.0
