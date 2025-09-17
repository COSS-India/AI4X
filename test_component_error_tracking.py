#!/usr/bin/env python3
"""
Test component error tracking fix - verifies that service failures are properly tracked
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_component_error_tracking():
    """Test that component errors are tracked correctly when services return success=False"""
    try:
        from metrics import metrics_collector, prometheus_latest_text
        
        print("🔧 Testing Component Error Tracking Fix")
        print("=" * 50)
        
        # Get baseline metrics
        print("\n1. Getting baseline metrics...")
        baseline_metrics = prometheus_latest_text()
        
        def count_error_metrics(metrics_text, error_type="processing_error"):
            """Count error metrics in prometheus text"""
            count = 0
            for line in metrics_text.split('\n'):
                if 'ai4x_errors_total' in line and error_type in line and not line.startswith('#'):
                    try:
                        count += float(line.split()[-1])
                    except:
                        pass
            return count
        
        baseline_processing_errors = count_error_metrics(baseline_metrics, "processing_error")
        print(f"   Baseline processing errors: {baseline_processing_errors}")
        
        # Test scenario: Simulate component failures like the real services do
        print("\n2. Simulating component failures...")
        
        customer = "test_customer"
        app = "test_app"
        
        # Test 1: NMT component failure
        print("   Test 1: NMT component failure (success=False)")
        rid1 = metrics_collector.start_request(customer, app, "/nmt/translate", "test", "nmt")
        metrics_collector.start_component(rid1, "NMT")
        # Simulate service returning success=False (like real NMT service does)
        metrics_collector.end_component(rid1, "NMT", success=False)
        metrics_collector.end_request(rid1, 200)  # Request completes but service failed
        
        # Test 2: TTS component failure
        print("   Test 2: TTS component failure (success=False)")
        rid2 = metrics_collector.start_request(customer, app, "/tts/speak", "test", "tts")
        metrics_collector.start_component(rid2, "TTS")
        # Simulate service returning success=False (like real TTS service does)
        metrics_collector.end_component(rid2, "TTS", success=False)
        metrics_collector.end_request(rid2, 500)  # Request fails due to service failure
        
        # Test 3: LLM component failure
        print("   Test 3: LLM component failure (success=False)")
        rid3 = metrics_collector.start_request(customer, app, "/llm/generate", "test", "llm")
        metrics_collector.start_component(rid3, "LLM")
        # Simulate service returning success=False (like real LLM service does)
        metrics_collector.end_component(rid3, "LLM", success=False)
        metrics_collector.end_request(rid3, 500)  # Request fails due to service failure
        
        # Test 4: BackNMT component failure in pipeline
        print("   Test 4: BackNMT component failure (success=False)")
        rid4 = metrics_collector.start_request(customer, app, "/pipeline", "test", "pipeline")
        metrics_collector.start_component(rid4, "BackNMT")
        # Simulate service returning success=False (like real BackNMT service does)
        metrics_collector.end_component(rid4, "BackNMT", success=False)
        metrics_collector.end_request(rid4, 200)  # Pipeline continues even if BackNMT fails
        
        # Get updated metrics
        print("\n3. Checking updated metrics...")
        updated_metrics = prometheus_latest_text()
        
        updated_processing_errors = count_error_metrics(updated_metrics, "processing_error")
        error_increase = updated_processing_errors - baseline_processing_errors
        
        print(f"   Updated processing errors: {updated_processing_errors}")
        print(f"   📈 Processing error increase: +{error_increase}")
        
        # Check specific error metrics
        print("\n4. 🎯 SPECIFIC ERROR METRICS FOUND:")
        print("   " + "=" * 40)
        
        component_errors = {"NMT": 0, "TTS": 0, "LLM": 0, "BackNMT": 0}
        
        for line in updated_metrics.split('\n'):
            if 'ai4x_errors_total' in line and 'processing_error' in line and not line.startswith('#'):
                # Extract component from labels if possible
                for component in component_errors.keys():
                    if component.lower() in line.lower():
                        try:
                            count = float(line.split()[-1])
                            component_errors[component] += count
                        except:
                            pass
                print(f"   {line}")
        
        print(f"\n5. 📊 COMPONENT ERROR SUMMARY:")
        print("   " + "=" * 30)
        for component, count in component_errors.items():
            print(f"   {component}: {count} errors")
        
        # Verify the fix worked
        print(f"\n6. ✅ VERIFICATION:")
        print("   " + "=" * 20)
        
        if error_increase >= 4:  # We simulated 4 component failures
            print(f"   ✅ SUCCESS: Error tracking is working correctly!")
            print(f"   ✅ Component failures are now properly tracked as processing errors")
            print(f"   ✅ Services returning success=False now increment error metrics")
        else:
            print(f"   ⚠️  WARNING: Expected at least 4 new errors, got {error_increase}")
            print(f"   ⚠️  This might indicate the fix didn't work completely")
        
        # Show what to monitor
        print(f"\n7. 📝 WHAT TO MONITOR:")
        print("   " + "=" * 25)
        print("   For component errors (services returning success=False):")
        print("   - Metric: ai4x_errors_total")
        print("   - Labels: error_type=\"processing_error\", status_series=\"5xx\"")
        print("   - Query: ai4x_errors_total{error_type=\"processing_error\"}")
        
        print("\n   For external API errors (Dhruva/Gemini API failures):")
        print("   - Metric: ai4x_external_api_errors_total")
        print("   - Labels: external_service=\"dhruva|gemini\", status_series=\"5xx\"")
        print("   - Query: ai4x_external_api_errors_total{status_series=\"5xx\"}")
        
        # Save full metrics for debugging
        with open('component_error_tracking_debug.txt', 'w') as f:
            f.write(updated_metrics)
        print(f"\n📄 Full metrics saved to: component_error_tracking_debug.txt")
        
        return error_increase >= 4
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_component_error_tracking()
    if success:
        print(f"\n🎉 COMPONENT ERROR TRACKING FIX: SUCCESS!")
        print(f"   TTS 500 errors and all other service failures should now be tracked correctly.")
    else:
        print(f"\n❌ COMPONENT ERROR TRACKING FIX: FAILED!")
        print(f"   Please check the implementation.")
    
    sys.exit(0 if success else 1)
