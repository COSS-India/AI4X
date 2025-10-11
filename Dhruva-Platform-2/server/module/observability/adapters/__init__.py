"""
Framework adapters for Dhruva Observability Plugin

Provides adapters for different web frameworks to enable universal compatibility.
"""
# Import adapters with optional dependencies
try:
    from .flask_adapter import FlaskObservabilityAdapter
except ImportError:
    FlaskObservabilityAdapter = None

try:
    from .django_adapter import DjangoObservabilityAdapter, DjangoObservabilityMiddleware
except ImportError:
    DjangoObservabilityAdapter = None
    DjangoObservabilityMiddleware = None

from .generic_adapter import GenericObservabilityAdapter
from .manual_adapter import ManualObservabilityAdapter

__all__ = [
    "GenericObservabilityAdapter",
    "ManualObservabilityAdapter",
]

# Add optional adapters if available
if FlaskObservabilityAdapter is not None:
    __all__.append("FlaskObservabilityAdapter")

if DjangoObservabilityAdapter is not None:
    __all__.extend(["DjangoObservabilityAdapter", "DjangoObservabilityMiddleware"])
