"""
Manual adapter for Dhruva Observability Plugin
"""
from typing import Optional, Dict, Any
from ..config import PluginConfig
from ..metrics import MetricsCollector


class ManualObservabilityAdapter:
    """Manual adapter for custom integration."""
    
    def __init__(self, config: Optional[PluginConfig] = None):
        """Initialize manual adapter."""
        self.config = config or PluginConfig()
        self.metrics = MetricsCollector(config=self.config.to_dict())
    
    def track_request(self, customer: str, app: str, method: str, endpoint: str, 
                    status_code: int, duration: float, service_type: str = "unknown"):
        """Manually track a request."""
        if not self.config.enabled:
            return
        
        self.metrics.track_request(
            customer=customer,
            app=app,
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            duration=duration,
            service_type=service_type
        )
    
    def get_metrics_text(self) -> str:
        """Get metrics in Prometheus text format."""
        return self.metrics.get_metrics_text()
    
    def update_system_metrics(self):
        """Update system metrics."""
        self.metrics.update_system_metrics()
