"""
Django adapter for Dhruva Observability Plugin
"""
from typing import Optional

try:
    from django.http import HttpRequest, HttpResponse
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    HttpRequest = None
    HttpResponse = None

from ..config import PluginConfig
from ..metrics import MetricsCollector


class DjangoObservabilityAdapter:
    """Django adapter for Dhruva Observability."""
    
    def __init__(self, config: Optional[PluginConfig] = None):
        """Initialize Django adapter."""
        self.config = config or PluginConfig()
        self.metrics = MetricsCollector(config=self.config.to_dict())
    
    def register_plugin(self, django_app):
        """Register plugin with Django app."""
        if not self.config.enabled:
            return
        
        # Add Django-specific middleware here
        pass


class DjangoObservabilityMiddleware:
    """Django middleware for observability."""
    
    def __init__(self, get_response):
        """Initialize Django middleware."""
        self.get_response = get_response
        self.config = PluginConfig()
        self.metrics = MetricsCollector(config=self.config.to_dict())
    
    def __call__(self, request: HttpRequest):
        """Process request through Django middleware."""
        if not self.config.enabled:
            return self.get_response(request)
        
        # Add Django-specific request tracking here
        response = self.get_response(request)
        return response
