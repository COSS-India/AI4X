"""
Metrics collection system for Dhruva Observability Plugin

Handles Prometheus metrics collection, system monitoring, and business analytics.
"""

import time
import psutil
from typing import Dict, Any, Optional
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    CollectorRegistry,
    generate_latest,
)


class MetricsCollector:
    """Metrics collector for Dhruva Observability."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize metrics collector."""
        self.config = config or {}
        self.registry = CollectorRegistry()
        self._init_metrics()

    def _init_metrics(self):
        """Initialize Prometheus metrics."""
        # Request metrics
        self.enterprise_requests_total = Counter(
            "telemetry_obsv_requests_total",
            "Total enterprise requests",
            ["customer", "app", "method", "endpoint", "status_code"],
            registry=self.registry,
        )

        self.enterprise_request_duration = Histogram(
            "telemetry_obsv_request_duration_seconds",
            "Enterprise request duration",
            ["customer", "app", "method", "endpoint"],
            registry=self.registry,
        )

        # Service metrics
        self.enterprise_service_requests = Counter(
            "telemetry_obsv_service_requests_total",
            "Service requests by type",
            ["customer", "app", "service_type"],
            registry=self.registry,
        )

        # System metrics
        self.enterprise_system_cpu = Gauge(
            "telemetry_obsv_system_cpu_percent",
            "System CPU usage",
            registry=self.registry,
        )

        self.enterprise_system_memory = Gauge(
            "telemetry_obsv_system_memory_percent",
            "System memory usage",
            registry=self.registry,
        )

        # SLA metrics
        self.enterprise_sla_availability = Gauge(
            "telemetry_obsv_sla_availability_percent",
            "Service availability percentage",
            ["customer", "app"],
            registry=self.registry,
        )

        self.enterprise_sla_response_time = Gauge(
            "telemetry_obsv_sla_response_time_seconds",
            "Average response time",
            ["customer", "app"],
            registry=self.registry,
        )

        # Error tracking metrics
        self.enterprise_errors_total = Counter(
            "telemetry_obsv_errors_total",
            "Total errors by status code",
            ["customer", "app", "endpoint", "status_code", "error_type"],
            registry=self.registry,
        )

        # Data processing metrics
        self.enterprise_data_processed_total = Counter(
            "telemetry_obsv_data_processed_total",
            "Total data processed",
            ["customer", "app", "data_type"],
            registry=self.registry,
        )

        # LLM token tracking
        self.enterprise_llm_tokens_processed = Counter(
            "telemetry_obsv_llm_tokens_processed_total",
            "Total LLM tokens processed",
            ["customer", "app", "model"],
            registry=self.registry,
        )

        # TTS character tracking
        self.enterprise_tts_characters_synthesized = Counter(
            "telemetry_obsv_tts_characters_synthesized_total",
            "Total TTS characters synthesized",
            ["customer", "app", "language"],
            registry=self.registry,
        )

        # NMT character tracking
        self.enterprise_nmt_characters_translated = Counter(
            "telemetry_obsv_nmt_characters_translated_total",
            "Total NMT characters translated",
            ["customer", "app", "source_language", "target_language"],
            registry=self.registry,
        )

        # SLA compliance tracking
        self.enterprise_sla_compliance = Gauge(
            "telemetry_obsv_sla_compliance_percent",
            "SLA compliance percentage",
            ["customer", "app", "sla_type"],
            registry=self.registry,
        )

        # Component latency tracking
        self.enterprise_component_latency = Histogram(
            "telemetry_obsv_component_latency_seconds",
            "Component latency",
            ["customer", "app", "component"],
            registry=self.registry,
        )

        # Customer quota tracking
        self.enterprise_customer_llm_quota = Gauge(
            "telemetry_obsv_customer_llm_quota_per_month",
            "Customer LLM quota per month",
            ["customer"],
            registry=self.registry,
        )

        self.enterprise_customer_tts_quota = Gauge(
            "telemetry_obsv_customer_tts_quota_per_month",
            "Customer TTS quota per month",
            ["customer"],
            registry=self.registry,
        )

        self.enterprise_customer_nmt_quota = Gauge(
            "telemetry_obsv_customer_nmt_quota_per_month",
            "Customer NMT quota per month",
            ["customer"],
            registry=self.registry,
        )

        # System metrics
        self.enterprise_system_peak_throughput = Gauge(
            "telemetry_obsv_system_peak_throughput_rpm",
            "Peak throughput requests per minute",
            registry=self.registry,
        )

        self.enterprise_system_service_count = Gauge(
            "telemetry_obsv_system_service_count",
            "Total number of services",
            registry=self.registry,
        )

    def update_system_metrics(self):
        """Update system metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.enterprise_system_cpu.set(cpu_percent)

            # Memory usage
            memory = psutil.virtual_memory()
            self.enterprise_system_memory.set(memory.percent)

            # SLA metrics (simplified)
            customers = self.config.get("customers", ["default"])
            apps = self.config.get("apps", ["default"])

            for customer in customers:
                for app in apps:
                    self.enterprise_sla_availability.labels(
                        customer=customer, app=app
                    ).set(
                        99.9
                    )  # Mock availability

                    self.enterprise_sla_response_time.labels(
                        customer=customer, app=app
                    ).set(
                        0.5
                    )  # Mock response time

        except Exception as e:
            if self.config.get("debug", False):
                print(f"Error updating system metrics: {e}")

    def track_request(
        self,
        customer: str,
        app: str,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
        service_type: str = "unknown",
    ):
        """Track a request."""
        self.enterprise_requests_total.labels(
            customer=customer,
            app=app,
            method=method,
            endpoint=endpoint,
            status_code=str(status_code),
        ).inc()

        self.enterprise_request_duration.labels(
            customer=customer, app=app, method=method, endpoint=endpoint
        ).observe(duration)

        self.enterprise_service_requests.labels(
            customer=customer, app=app, service_type=service_type
        ).inc()

        # Track errors if status code indicates error
        if status_code >= 400:
            error_type = self._get_error_type(status_code)
            self.enterprise_errors_total.labels(
                customer=customer,
                app=app,
                endpoint=endpoint,
                status_code=str(status_code),
                error_type=error_type,
            ).inc()

    def track_data_processing(
        self, customer: str, app: str, data_type: str, amount: int
    ):
        """Track data processing."""
        self.enterprise_data_processed_total.labels(
            customer=customer, app=app, data_type=data_type
        ).inc(amount)

    def track_llm_tokens(self, customer: str, app: str, model: str, tokens: int):
        """Track LLM token processing."""
        self.enterprise_llm_tokens_processed.labels(
            customer=customer, app=app, model=model
        ).inc(tokens)

        # Also track as data processing
        self.track_data_processing(customer, app, "llm_tokens", tokens)

    def track_tts_characters(
        self, customer: str, app: str, language: str, characters: int
    ):
        """Track TTS character synthesis."""
        self.enterprise_tts_characters_synthesized.labels(
            customer=customer, app=app, language=language
        ).inc(characters)

        # Also track as data processing
        self.track_data_processing(customer, app, "tts_characters", characters)

    def track_nmt_characters(
        self,
        customer: str,
        app: str,
        source_lang: str,
        target_lang: str,
        characters: int,
    ):
        """Track NMT character translation."""
        self.enterprise_nmt_characters_translated.labels(
            customer=customer,
            app=app,
            source_language=source_lang,
            target_language=target_lang,
        ).inc(characters)

        # Also track as data processing
        self.track_data_processing(customer, app, "nmt_characters", characters)

    def track_component_latency(
        self, customer: str, app: str, component: str, duration: float
    ):
        """Track component latency."""
        self.enterprise_component_latency.labels(
            customer=customer, app=app, component=component
        ).observe(duration)

    def update_sla_compliance(
        self, customer: str, app: str, sla_type: str, compliance_percent: float
    ):
        """Update SLA compliance."""
        self.enterprise_sla_compliance.labels(
            customer=customer, app=app, sla_type=sla_type
        ).set(compliance_percent)

    def update_customer_quotas(
        self,
        customer: str,
        llm_quota: int = 1000000,
        tts_quota: int = 1000000,
        nmt_quota: int = 1000000,
    ):
        """Update customer quotas."""
        self.enterprise_customer_llm_quota.labels(customer=customer).set(llm_quota)
        self.enterprise_customer_tts_quota.labels(customer=customer).set(tts_quota)
        self.enterprise_customer_nmt_quota.labels(customer=customer).set(nmt_quota)

    def update_system_metrics_advanced(self):
        """Update advanced system metrics."""
        try:
            # Update peak throughput (mock calculation)
            self.enterprise_system_peak_throughput.set(1000)  # Mock value

            # Update service count (mock calculation)
            self.enterprise_system_service_count.set(5)  # Mock value

        except Exception as e:
            if self.config.get("debug", False):
                print(f"Error updating advanced system metrics: {e}")

    def _get_error_type(self, status_code: int) -> str:
        """Get error type from status code."""
        if 400 <= status_code < 500:
            return "client_error"
        elif 500 <= status_code < 600:
            return "server_error"
        else:
            return "unknown_error"

    def get_metrics_text(self) -> str:
        """Get metrics in Prometheus text format."""
        self.update_system_metrics()
        self.update_system_metrics_advanced()
        return generate_latest(self.registry).decode("utf-8")


def prometheus_latest_text() -> str:
    """Get latest Prometheus metrics text."""
    # This would be implemented to return the latest metrics
    # For now, return a placeholder
    return "# Prometheus metrics would be generated here"


# Global metrics collector instance
_global_collector = None


def get_global_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _global_collector
    if _global_collector is None:
        _global_collector = MetricsCollector()
    return _global_collector
