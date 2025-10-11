"""
Flask adapter for Dhruva Observability Plugin
"""
from typing import Optional

try:
    from flask import Flask
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    Flask = None

from ..config import PluginConfig
from ..metrics import MetricsCollector


class FlaskObservabilityAdapter:
    """Flask adapter for Dhruva Observability."""
    
    def __init__(self, config: Optional[PluginConfig] = None):
        """Initialize Flask adapter."""
        self.config = config or PluginConfig()
        self.metrics = MetricsCollector(config=self.config.to_dict())
    
    def register_plugin(self, app: Flask):
        """Register plugin with Flask app."""
        if not self.config.enabled:
            return
        
        # Add Flask-specific middleware here
        pass
