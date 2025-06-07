"""
Performance and Load Testing for ContactPlus
"""
import pytest
import requests
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestLoadTesting:
    """Load testing for API endpoints"""
    
    def test_health_endpoint_load(self, api_base_url):
        """Test health endpoint under load"""
        
        def make_request():
            start_time = time.time()
            try:
                response = requests.get(f"{api_base_url}/health", timeout=10)
                end_time = time.time()
                return {
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "success": response.status_code == 200
                }
            except Exception as e:
                return {
                    "status_code": 0,
                    "response_time": time.time() - start_time,
                    "success": False,
                    "error": str(e)
                }
        
        # Test with 50 concurrent requests
        num_requests = 50
        results = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            
            for future in as_completed(futures):
                results.append(future.result())
        
        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in successful_requests]
        
        success_rate = len(successful_requests) / num_requests
        avg_response_time = statistics.mean(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        print(f"Load test results:")
        print(f"  Success rate: {success_rate:.2%} ({len(successful_requests)}/{num_requests})")
        print(f"  Average response time: {avg_response_time:.3f}s")
        print(f"  Max response time: {max_response_time:.3f}s")
        
        # Assertions
        assert success_rate >= 0.95, f"Success rate too low: {success_rate:.2%}"
        assert avg_response_time < 2.0, f"Average response time too high: {avg_response_time:.3f}s"
        assert max_response_time < 5.0, f"Max response time too high: {max_response_time:.3f}s"
    
    def test_contacts_endpoint_load(self, api_base_url):
        """Test contacts listing endpoint under load"""
        
        def make_request():
            start_time = time.time()
            try:
                response = requests.get(f"{api_base_url}/contacts?page=1&page_size=20", timeout=15)
                end_time = time.time()
                return {
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "success": response.status_code == 200,
                    "data_size": len(response.content)
                }
            except Exception as e:
                return {
                    "status_code": 0,
                    "response_time": time.time() - start_time,
                    "success": False,
                    "error": str(e)
                }
        
        # Test with 30 concurrent requests
        num_requests = 30
        results = []
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            
            for future in as_completed(futures):
                results.append(future.result())
        
        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in successful_requests]
        
        success_rate = len(successful_requests) / num_requests
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        print(f"Contacts endpoint load test:")
        print(f"  Success rate: {success_rate:.2%}")
        print(f"  Average response time: {avg_response_time:.3f}s")
        
        assert success_rate >= 0.90, f"Success rate too low: {success_rate:.2%}"
        assert avg_response_time < 3.0, f"Average response time too high: {avg_response_time:.3f}s"
    
    def test_search_endpoint_load(self, api_base_url):
        """Test search endpoint under load with various queries"""
        
        search_queries = [
            "test", "john", "example", "@", "corp", "smith", 
            "data", "tech", "software", "manager"
        ]
        
        def make_request():
            import random
            query = random.choice(search_queries)
            start_time = time.time()
            try:
                response = requests.get(f"{api_base_url}/contacts/search?query={query}", timeout=15)
                end_time = time.time()
                return {
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "success": response.status_code == 200,
                    "query": query
                }
            except Exception as e:
                return {
                    "status_code": 0,
                    "response_time": time.time() - start_time,
                    "success": False,
                    "error": str(e),
                    "query": query
                }
        
        # Test with 25 concurrent search requests
        num_requests = 25
        results = []
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            
            for future in as_completed(futures):
                results.append(future.result())
        
        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in successful_requests]
        
        success_rate = len(successful_requests) / num_requests
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        print(f"Search endpoint load test:")
        print(f"  Success rate: {success_rate:.2%}")
        print(f"  Average response time: {avg_response_time:.3f}s")
        
        assert success_rate >= 0.85, f"Search success rate too low: {success_rate:.2%}"
        assert avg_response_time < 4.0, f"Search response time too high: {avg_response_time:.3f}s"


class TestMemoryLeaks:
    """Test for potential memory leaks"""
    
    def test_repeated_requests_memory_stable(self, api_base_url, docker_client):
        """Test that repeated requests don't cause memory leaks"""
        
        container = docker_client.containers.get("contactplus-core")
        
        def get_memory_usage():
            stats = container.stats(stream=False)
            memory_stats = stats.get("memory_stats", {})
            return memory_stats.get("usage", 0)
        
        # Get initial memory usage
        initial_memory = get_memory_usage()
        
        # Make many requests
        for i in range(100):
            try:
                requests.get(f"{api_base_url}/health", timeout=5)
                if i % 20 == 0:
                    time.sleep(0.1)  # Small pause every 20 requests
            except:
                pass
        
        # Wait for any cleanup
        time.sleep(5)
        
        # Get final memory usage
        final_memory = get_memory_usage()
        
        if initial_memory > 0 and final_memory > 0:
            memory_increase = final_memory - initial_memory
            memory_increase_mb = memory_increase / (1024 * 1024)
            
            print(f"Memory usage: {initial_memory/(1024*1024):.1f}MB -> {final_memory/(1024*1024):.1f}MB")
            print(f"Memory increase: {memory_increase_mb:.1f}MB")
            
            # Allow some memory increase but not excessive
            assert memory_increase_mb < 100, f"Excessive memory increase: {memory_increase_mb:.1f}MB"
        else:
            pytest.skip("Could not measure memory usage")


class TestStressTest:
    """Stress testing scenarios"""
    
    def test_mixed_load_stress(self, api_base_url):
        """Test system under mixed load of different operations"""
        
        def health_worker():
            results = []
            for _ in range(20):
                start_time = time.time()
                try:
                    response = requests.get(f"{api_base_url}/health", timeout=5)
                    results.append({
                        "endpoint": "health",
                        "success": response.status_code == 200,
                        "response_time": time.time() - start_time
                    })
                except:
                    results.append({
                        "endpoint": "health",
                        "success": False,
                        "response_time": time.time() - start_time
                    })
                time.sleep(0.1)
            return results
        
        def stats_worker():
            results = []
            for _ in range(10):
                start_time = time.time()
                try:
                    response = requests.get(f"{api_base_url}/stats", timeout=8)
                    results.append({
                        "endpoint": "stats",
                        "success": response.status_code == 200,
                        "response_time": time.time() - start_time
                    })
                except:
                    results.append({
                        "endpoint": "stats",
                        "success": False,
                        "response_time": time.time() - start_time
                    })
                time.sleep(0.2)
            return results
        
        def contacts_worker():
            results = []
            for _ in range(15):
                start_time = time.time()
                try:
                    response = requests.get(f"{api_base_url}/contacts?page=1&page_size=10", timeout=10)
                    results.append({
                        "endpoint": "contacts",
                        "success": response.status_code == 200,
                        "response_time": time.time() - start_time
                    })
                except:
                    results.append({
                        "endpoint": "contacts",
                        "success": False,
                        "response_time": time.time() - start_time
                    })
                time.sleep(0.3)
            return results
        
        # Run workers concurrently
        workers = [health_worker, stats_worker, contacts_worker]
        all_results = []
        
        with ThreadPoolExecutor(max_workers=len(workers)) as executor:
            futures = [executor.submit(worker) for worker in workers]
            
            for future in as_completed(futures):
                all_results.extend(future.result())
        
        # Analyze results by endpoint
        endpoint_stats = {}
        for result in all_results:
            endpoint = result["endpoint"]
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {"total": 0, "successful": 0, "response_times": []}
            
            endpoint_stats[endpoint]["total"] += 1
            if result["success"]:
                endpoint_stats[endpoint]["successful"] += 1
                endpoint_stats[endpoint]["response_times"].append(result["response_time"])
        
        print("Mixed load stress test results:")
        for endpoint, stats in endpoint_stats.items():
            success_rate = stats["successful"] / stats["total"]
            avg_response_time = statistics.mean(stats["response_times"]) if stats["response_times"] else 0
            
            print(f"  {endpoint}: {success_rate:.2%} success rate, {avg_response_time:.3f}s avg response time")
            
            # Relax success rate requirements under stress
            assert success_rate >= 0.80, f"{endpoint} success rate too low under stress: {success_rate:.2%}"
    
    def test_rapid_fire_requests(self, api_base_url):
        """Test system with rapid-fire requests"""
        
        def rapid_requests():
            results = []
            for _ in range(50):
                start_time = time.time()
                try:
                    response = requests.get(f"{api_base_url}/health", timeout=3)
                    results.append(response.status_code == 200)
                except:
                    results.append(False)
                # No sleep - rapid fire
            return results
        
        # Start multiple rapid-fire threads
        num_threads = 5
        all_results = []
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(rapid_requests) for _ in range(num_threads)]
            
            for future in as_completed(futures):
                all_results.extend(future.result())
        
        success_count = sum(all_results)
        total_requests = len(all_results)
        success_rate = success_count / total_requests
        
        print(f"Rapid-fire test: {success_rate:.2%} success rate ({success_count}/{total_requests})")
        
        # Under rapid-fire conditions, we still expect reasonable success rate
        assert success_rate >= 0.70, f"Rapid-fire success rate too low: {success_rate:.2%}"


class TestLongRunningStability:
    """Test long-running stability"""
    
    @pytest.mark.slow
    def test_extended_operation(self, api_base_url):
        """Test system stability over extended period"""
        
        def make_periodic_requests():
            results = []
            for i in range(60):  # 60 requests over 5 minutes
                start_time = time.time()
                try:
                    response = requests.get(f"{api_base_url}/health", timeout=10)
                    success = response.status_code == 200
                    results.append({
                        "iteration": i,
                        "success": success,
                        "response_time": time.time() - start_time,
                        "timestamp": time.time()
                    })
                except Exception as e:
                    results.append({
                        "iteration": i,
                        "success": False,
                        "response_time": time.time() - start_time,
                        "timestamp": time.time(),
                        "error": str(e)
                    })
                
                time.sleep(5)  # 5 second intervals
            
            return results
        
        print("Starting 5-minute stability test...")
        results = make_periodic_requests()
        
        successful_requests = [r for r in results if r["success"]]
        success_rate = len(successful_requests) / len(results)
        
        response_times = [r["response_time"] for r in successful_requests]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        print(f"Extended operation test:")
        print(f"  Success rate: {success_rate:.2%}")
        print(f"  Average response time: {avg_response_time:.3f}s")
        print(f"  Total requests: {len(results)}")
        
        # Check for stability issues
        if len(response_times) > 10:
            # Check if response times are getting worse over time
            first_half = response_times[:len(response_times)//2]
            second_half = response_times[len(response_times)//2:]
            
            first_half_avg = statistics.mean(first_half)
            second_half_avg = statistics.mean(second_half)
            
            degradation = (second_half_avg - first_half_avg) / first_half_avg
            print(f"  Performance degradation: {degradation:.2%}")
            
            assert degradation < 0.5, f"Performance degraded significantly: {degradation:.2%}"
        
        assert success_rate >= 0.95, f"Extended test success rate too low: {success_rate:.2%}"