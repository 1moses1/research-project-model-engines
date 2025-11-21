"""
Test script for ENGINE 3: XGBoost Compliance API
"""

import requests
import json
import time

API_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("\n" + "=" * 80)
    print("TEST 1: Health Check")
    print("=" * 80)

    response = requests.get(f"{API_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✅ Health check passed")


def test_model_info():
    """Test model info endpoint"""
    print("\n" + "=" * 80)
    print("TEST 2: Model Information")
    print("=" * 80)

    response = requests.get(f"{API_URL}/model/info")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Model Type: {data['model_type']}")
    print(f"Framework: {data['framework']}")
    print(f"Total Features: {data['features']['total']}")
    print(f"Classes: {data['classes']}")
    print(f"Total Controls: {data['controls']['total']}")
    print(f"F1 Score: {data['performance']['f1_score']}")
    assert response.status_code == 200
    print("✅ Model info retrieved successfully")


def test_single_classification_compliant():
    """Test single event classification - compliant"""
    print("\n" + "=" * 80)
    print("TEST 3: Single Classification - Compliant Event")
    print("=" * 80)

    event = {
        "log_message": "User admin logged in successfully",
        "status_code": 200,
        "hour_of_day": 14,
        "port": 443
    }

    print(f"Input Event: {json.dumps(event, indent=2)}")

    start_time = time.time()
    response = requests.post(f"{API_URL}/classify", json=event)
    latency = (time.time() - start_time) * 1000

    print(f"\nStatus Code: {response.status_code}")
    data = response.json()
    print(f"Prediction: {data['prediction']}")
    print(f"Confidence: {data['confidence']:.3f}")
    print(f"Probabilities: {json.dumps(data['probabilities'], indent=2)}")
    print(f"Inference Time (API): {data['inference_time_ms']:.3f}ms")
    print(f"Latency (Total): {latency:.3f}ms")

    assert response.status_code == 200
    assert data['prediction'] in ['compliant', 'non_compliant']
    print("✅ Single classification passed")


def test_single_classification_non_compliant():
    """Test single event classification - non-compliant"""
    print("\n" + "=" * 80)
    print("TEST 4: Single Classification - Non-Compliant Event")
    print("=" * 80)

    event = {
        "log_message": "Failed login attempt for user admin from 192.168.1.100",
        "status_code": 401,
        "hour_of_day": 2,
        "port": 22
    }

    print(f"Input Event: {json.dumps(event, indent=2)}")

    response = requests.post(f"{API_URL}/classify", json=event)
    data = response.json()

    print(f"\nPrediction: {data['prediction']}")
    print(f"Confidence: {data['confidence']:.3f}")
    print(f"Probabilities: {json.dumps(data['probabilities'], indent=2)}")
    print(f"Inference Time: {data['inference_time_ms']:.3f}ms")

    assert response.status_code == 200
    print("✅ Non-compliant classification passed")


def test_batch_classification():
    """Test batch classification"""
    print("\n" + "=" * 80)
    print("TEST 5: Batch Classification")
    print("=" * 80)

    events = {
        "events": [
            {
                "log_message": "User admin logged in successfully",
                "status_code": 200,
                "hour_of_day": 14,
                "port": 443
            },
            {
                "log_message": "Failed login attempt",
                "status_code": 401,
                "hour_of_day": 2,
                "port": 22
            },
            {
                "log_message": "File access granted to user john",
                "status_code": 200,
                "hour_of_day": 10,
                "port": 443
            },
            {
                "log_message": "Unauthorized access attempt detected",
                "status_code": 403,
                "hour_of_day": 3,
                "port": 80
            },
            {
                "log_message": "System backup completed successfully",
                "status_code": 200,
                "hour_of_day": 1,
                "port": 443
            }
        ]
    }

    print(f"Batch Size: {len(events['events'])} events")

    start_time = time.time()
    response = requests.post(f"{API_URL}/classify/batch", json=events)
    total_latency = (time.time() - start_time) * 1000

    print(f"\nStatus Code: {response.status_code}")
    data = response.json()

    print(f"\nResults:")
    print(f"  Total Events: {data['total_events']}")
    print(f"  Total Inference Time: {data['total_inference_time_ms']:.3f}ms")
    print(f"  Avg Inference Time: {data['avg_inference_time_ms']:.3f}ms")
    print(f"  Total Latency: {total_latency:.3f}ms")

    print(f"\nPredictions:")
    for i, pred in enumerate(data['predictions']):
        print(f"  Event {i+1}: {pred['prediction']:<15} (confidence: {pred['confidence']:.3f})")

    assert response.status_code == 200
    assert data['total_events'] == 5
    print("✅ Batch classification passed")


def test_metrics():
    """Test metrics endpoint"""
    print("\n" + "=" * 80)
    print("TEST 6: Metrics Endpoint")
    print("=" * 80)

    response = requests.get(f"{API_URL}/metrics")
    print(f"Status Code: {response.status_code}")
    print(f"Metrics: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ Metrics endpoint passed")


def run_performance_test(num_requests=100):
    """Run performance test"""
    print("\n" + "=" * 80)
    print(f"PERFORMANCE TEST: {num_requests} Requests")
    print("=" * 80)

    event = {
        "log_message": "User login successful",
        "status_code": 200,
        "hour_of_day": 14,
        "port": 443
    }

    latencies = []

    print(f"Sending {num_requests} classification requests...")
    start_time = time.time()

    for i in range(num_requests):
        req_start = time.time()
        response = requests.post(f"{API_URL}/classify", json=event)
        req_end = time.time()

        if response.status_code == 200:
            latencies.append((req_end - req_start) * 1000)

        if (i + 1) % 10 == 0:
            print(f"  Progress: {i + 1}/{num_requests}")

    total_time = time.time() - start_time

    print(f"\n📊 Performance Results:")
    print(f"  Total Requests: {num_requests}")
    print(f"  Total Time: {total_time:.2f}s")
    print(f"  Requests/sec: {num_requests / total_time:.2f}")
    print(f"  Avg Latency: {sum(latencies) / len(latencies):.3f}ms")
    print(f"  Min Latency: {min(latencies):.3f}ms")
    print(f"  Max Latency: {max(latencies):.3f}ms")
    print(f"  P50 Latency: {sorted(latencies)[len(latencies)//2]:.3f}ms")
    print(f"  P95 Latency: {sorted(latencies)[int(len(latencies)*0.95)]:.3f}ms")
    print(f"  P99 Latency: {sorted(latencies)[int(len(latencies)*0.99)]:.3f}ms")

    print("✅ Performance test completed")


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("ENGINE 3: XGBoost Compliance API - Test Suite")
    print("=" * 80)

    try:
        # Basic tests
        test_health_check()
        test_model_info()
        test_single_classification_compliant()
        test_single_classification_non_compliant()
        test_batch_classification()
        test_metrics()

        # Performance test
        run_performance_test(100)

        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
