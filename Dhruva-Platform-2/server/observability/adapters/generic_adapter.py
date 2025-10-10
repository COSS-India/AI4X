"""
Generic adapter for Dhruva Observability Plugin
"""
from typing import Optional, Any
from ..config import PluginConfig
from ..metrics import MetricsCollector


class GenericObservabilityAdapter:
    """Generic adapter for any web framework."""
    
    def __init__(self, config: Optional[PluginConfig] = None):
        """Initialize generic adapter."""
        self.config = config or PluginConfig()
        self.metrics = MetricsCollector(config=self.config.to_dict())
    
    def register_plugin(self, app: Any):
        """Register plugin with any app."""
        if not self.config.enabled:
            return
        
        # Add generic framework integration here
        pass
