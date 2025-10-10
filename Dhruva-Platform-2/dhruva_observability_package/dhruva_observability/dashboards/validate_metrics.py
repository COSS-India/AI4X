#!/usr/bin/env python3
"""
Dhruva Dashboard Metrics Validator

This script validates that all metrics used in the dashboard are actually available
from the enterprise metrics endpoint.
"""

import json
import re
import sys
from pathlib import Path

def extract_metrics_from_dashboard(dashboard_path):
    """Extract all Prometheus metrics from dashboard JSON."""
    with open(dashboard_path, 'r') as f:
        dashboard = json.load(f)
    
    metrics = set()
    
    def find_metrics_in_obj(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == 'expr' and isinstance(value, str):
                    # Extract metrics from Prometheus expressions
                    metric_matches = re.findall(r'dhruva_enterprise_[a-zA-Z_]+', value)
                    metrics.update(metric_matches)
                else:
                    find_metrics_in_obj(value)
        elif isinstance(obj, list):
            for item in obj:
                find_metrics_in_obj(item)
    
    find_metrics_in_obj(dashboard)
    return sorted(metrics)

def get_available_metrics():
    """Define the metrics that are actually available from the enterprise endpoint."""
    base_metrics = {
        'dhruva_enterprise_requests_total',
        'dhruva_enterprise_request_duration_seconds',
        'dhruva_enterprise_service_requests_total', 
        'dhruva_enterprise_system_cpu_percent',
        'dhruva_enterprise_system_memory_percent',
        'dhruva_enterprise_sla_availability_percent',
        'dhruva_enterprise_sla_response_time_seconds',
        'dhruva_enterprise_errors_total',
        'dhruva_enterprise_data_processed_total',
        'dhruva_enterprise_llm_tokens_processed_total',
        'dhruva_enterprise_tts_characters_synthesized_total',
        'dhruva_enterprise_nmt_characters_translated_total',
        'dhruva_enterprise_sla_compliance_percent',
        'dhruva_enterprise_component_latency_seconds',
        'dhruva_enterprise_customer_llm_quota_per_month',
        'dhruva_enterprise_customer_tts_quota_per_month',
        'dhruva_enterprise_customer_nmt_quota_per_month',
        'dhruva_enterprise_system_peak_throughput_rpm',
        'dhruva_enterprise_system_service_count'
    }
    
    # Add histogram variants for histogram metrics
    histogram_metrics = {
        'dhruva_enterprise_request_duration_seconds',
        'dhruva_enterprise_component_latency_seconds'
    }
    
    all_metrics = base_metrics.copy()
    for metric in histogram_metrics:
        all_metrics.add(f"{metric}_bucket")
        all_metrics.add(f"{metric}_count") 
        all_metrics.add(f"{metric}_sum")
        all_metrics.add(f"{metric}_created")
    
    # Add counter _created variants
    counter_metrics = {
        'dhruva_enterprise_requests_total',
        'dhruva_enterprise_service_requests_total',
        'dhruva_enterprise_errors_total',
        'dhruva_enterprise_data_processed_total',
        'dhruva_enterprise_llm_tokens_processed_total',
        'dhruva_enterprise_tts_characters_synthesized_total',
        'dhruva_enterprise_nmt_characters_translated_total'
    }
    
    for metric in counter_metrics:
        all_metrics.add(f"{metric}_created")
    
    return all_metrics

def validate_dashboard_metrics(dashboard_path):
    """Validate that dashboard only uses available metrics."""
    print(f"🔍 Validating metrics in {dashboard_path}")
    
    dashboard_metrics = extract_metrics_from_dashboard(dashboard_path)
    available_metrics = get_available_metrics()
    
    print(f"📊 Found {len(dashboard_metrics)} unique metrics in dashboard")
    print(f"✅ {len(available_metrics)} metrics available from enterprise endpoint")
    
    # Check for metrics used in dashboard but not available
    missing_metrics = set(dashboard_metrics) - available_metrics
    if missing_metrics:
        print(f"\n❌ MISSING METRICS ({len(missing_metrics)}):")
        for metric in sorted(missing_metrics):
            print(f"   - {metric}")
        return False
    
    # Check for available metrics not used in dashboard  
    unused_metrics = available_metrics - set(dashboard_metrics)
    if unused_metrics:
        print(f"\n💡 UNUSED AVAILABLE METRICS ({len(unused_metrics)}):")
        for metric in sorted(unused_metrics):
            print(f"   - {metric}")
    
    print(f"\n✅ All dashboard metrics are available!")
    print(f"📈 Dashboard uses {len(dashboard_metrics)}/{len(available_metrics)} available metrics")
    
    return True

def main():
    """Main validation function."""
    script_dir = Path(__file__).parent
    dashboard_path = script_dir / "dhruva_business_dashboard.json"
    
    if not dashboard_path.exists():
        print(f"❌ Dashboard file not found: {dashboard_path}")
        return 1
    
    success = validate_dashboard_metrics(dashboard_path)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
