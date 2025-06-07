#!/usr/bin/env python3
"""
ContactPlus MVP - Comprehensive Functionality Test
Specifically designed for Mac deployment testing
"""
import requests
import time
import json
import sys
import os
from datetime import datetime


class ContactPlusTester:
    """Comprehensive functionality tester for ContactPlus MVP"""
    
    def __init__(self):
        self.base_url = "http://localhost:8080/api/v1"
        self.web_url = "http://localhost:3000"
        self.monitor_url = "http://localhost:9090"
        self.dozzle_url = "http://localhost:8081"
        self.results = []
        
    def log_result(self, test_name, success, details="", duration=0):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'duration': duration
        })
        duration_str = f" ({duration:.3f}s)" if duration > 0 else ""
        print(f"  {status} {test_name}{duration_str}")
        if details and not success:
            print(f"    Details: {details}")
    
    def test_service_health(self):
        """Test all service health endpoints"""
        print("\n🏥 Testing Service Health")
        print("-" * 30)
        
        services = [
            ("Core API Health", f"{self.base_url}/health"),
            ("Web Interface", self.web_url),
            ("Monitor Dashboard", self.monitor_url),
            ("Dozzle Logs", self.dozzle_url)
        ]
        
        for service_name, url in services:
            start_time = time.time()
            try:
                response = requests.get(url, timeout=10)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    self.log_result(service_name, True, f"Status: {response.status_code}", duration)
                else:
                    self.log_result(service_name, False, f"Status: {response.status_code}", duration)
            except Exception as e:
                duration = time.time() - start_time
                self.log_result(service_name, False, str(e), duration)
    
    def test_api_endpoints(self):
        """Test core API functionality"""
        print("\n🔌 Testing API Endpoints")
        print("-" * 25)
        
        endpoints = [
            ("Root Endpoint", ""),
            ("Database Stats", "/stats"),
            ("Import Status", "/import/status"),
            ("Contacts List", "/contacts"),
            ("Contact Search", "/contacts/search?query=test")
        ]
        
        for endpoint_name, path in endpoints:
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_url}{path}", timeout=10)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(endpoint_name, True, f"Response size: {len(str(data))} chars", duration)
                else:
                    self.log_result(endpoint_name, False, f"Status: {response.status_code}", duration)
            except Exception as e:
                duration = time.time() - start_time
                self.log_result(endpoint_name, False, str(e), duration)
    
    def test_database_operations(self):
        """Test database operations"""
        print("\n💾 Testing Database Operations")
        print("-" * 30)
        
        try:
            # Get initial stats
            start_time = time.time()
            response = requests.get(f"{self.base_url}/stats", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                stats = response.json()
                self.log_result("Database Stats Retrieval", True, 
                               f"Contacts: {stats.get('active_contacts', 0)}", duration)
                
                # Test export functionality
                start_time = time.time()
                export_response = requests.get(f"{self.base_url}/export/vcf", timeout=15)
                duration = time.time() - start_time
                
                if export_response.status_code == 200:
                    vcf_size = len(export_response.content)
                    self.log_result("VCF Export", True, f"Export size: {vcf_size} bytes", duration)
                else:
                    self.log_result("VCF Export", False, f"Status: {export_response.status_code}", duration)
                
            else:
                self.log_result("Database Stats Retrieval", False, f"Status: {response.status_code}", duration)
                
        except Exception as e:
            self.log_result("Database Operations", False, str(e))
    
    def test_import_functionality(self):
        """Test import functionality"""
        print("\n📥 Testing Import Functionality")
        print("-" * 32)
        
        try:
            start_time = time.time()
            response = requests.post(f"{self.base_url}/import/initial", timeout=30)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                import_result = response.json()
                imported = import_result.get('imported_contacts', 0)
                total = import_result.get('total_contacts', 0)
                errors = len(import_result.get('errors', []))
                
                details = f"Imported: {imported}/{total}, Errors: {errors}"
                self.log_result("Initial Import", True, details, duration)
                
                # Wait a moment and check stats again
                time.sleep(2)
                stats_response = requests.get(f"{self.base_url}/stats", timeout=10)
                if stats_response.status_code == 200:
                    new_stats = stats_response.json()
                    active_contacts = new_stats.get('active_contacts', 0)
                    self.log_result("Post-Import Stats", True, f"Active contacts: {active_contacts}")
                
            else:
                self.log_result("Initial Import", False, f"Status: {response.status_code}", duration)
                
        except Exception as e:
            self.log_result("Initial Import", False, str(e))
    
    def test_search_functionality(self):
        """Test search functionality with different queries"""
        print("\n🔍 Testing Search Functionality")
        print("-" * 31)
        
        search_queries = [
            ("Empty Search", ""),
            ("Name Search", "john"),
            ("Email Search", "@"),
            ("Phone Search", "+"),
            ("Organization Search", "corp")
        ]
        
        for search_name, query in search_queries:
            if query == "":
                # Empty query should return validation error
                try:
                    response = requests.get(f"{self.base_url}/contacts/search", timeout=10)
                    if response.status_code == 422:
                        self.log_result(search_name, True, "Validation error as expected")
                    else:
                        self.log_result(search_name, False, f"Expected 422, got {response.status_code}")
                except Exception as e:
                    self.log_result(search_name, False, str(e))
            else:
                try:
                    start_time = time.time()
                    response = requests.get(f"{self.base_url}/contacts/search?query={query}", timeout=10)
                    duration = time.time() - start_time
                    
                    if response.status_code == 200:
                        data = response.json()
                        results = len(data.get('contacts', []))
                        total = data.get('total', 0)
                        self.log_result(search_name, True, f"Results: {results}/{total}", duration)
                    else:
                        self.log_result(search_name, False, f"Status: {response.status_code}", duration)
                except Exception as e:
                    duration = time.time() - start_time
                    self.log_result(search_name, False, str(e), duration)
    
    def test_web_interface_content(self):
        """Test web interface content and navigation"""
        print("\n🌐 Testing Web Interface Content")
        print("-" * 33)
        
        pages = [
            ("Main Page", ""),
            ("Dashboard", "/dashboard"),
            ("Contacts", "/contacts"),
            ("Import", "/import")
        ]
        
        for page_name, path in pages:
            try:
                start_time = time.time()
                response = requests.get(f"{self.web_url}{path}", timeout=10)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    content = response.text.lower()
                    if "contactplus" in content or "contact" in content:
                        self.log_result(f"Web {page_name}", True, f"Content loaded", duration)
                    else:
                        self.log_result(f"Web {page_name}", False, "Missing expected content", duration)
                else:
                    self.log_result(f"Web {page_name}", False, f"Status: {response.status_code}", duration)
            except Exception as e:
                duration = time.time() - start_time
                self.log_result(f"Web {page_name}", False, str(e), duration)
    
    def test_performance_basic(self):
        """Test basic performance characteristics"""
        print("\n⚡ Testing Basic Performance")
        print("-" * 28)
        
        # Test response times
        endpoints = [
            ("Health Check Speed", "/health"),
            ("Stats Speed", "/stats"),
            ("Contacts Speed", "/contacts?page_size=10")
        ]
        
        for test_name, endpoint in endpoints:
            times = []
            for i in range(5):  # 5 requests to get average
                try:
                    start_time = time.time()
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                    duration = time.time() - start_time
                    if response.status_code == 200:
                        times.append(duration)
                except:
                    pass
            
            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                if avg_time < 2.0:  # Less than 2 seconds average
                    self.log_result(test_name, True, f"Avg: {avg_time:.3f}s, Max: {max_time:.3f}s")
                else:
                    self.log_result(test_name, False, f"Too slow - Avg: {avg_time:.3f}s")
            else:
                self.log_result(test_name, False, "No successful requests")
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        print("\n🔄 Testing Concurrent Requests")
        print("-" * 30)
        
        import threading
        import queue
        
        def make_request(result_queue):
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}/health", timeout=10)
                duration = time.time() - start_time
                result_queue.put((response.status_code == 200, duration))
            except:
                result_queue.put((False, 0))
        
        # Test 10 concurrent requests
        result_queue = queue.Queue()
        threads = []
        
        start_time = time.time()
        for _ in range(10):
            thread = threading.Thread(target=make_request, args=(result_queue,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join(timeout=15)
        
        total_duration = time.time() - start_time
        
        # Collect results
        successes = 0
        response_times = []
        
        while not result_queue.empty():
            success, duration = result_queue.get()
            if success:
                successes += 1
                response_times.append(duration)
        
        success_rate = successes / 10
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        if success_rate >= 0.8:  # 80% success rate
            details = f"Success rate: {success_rate:.1%}, Avg time: {avg_response_time:.3f}s"
            self.log_result("Concurrent Requests", True, details, total_duration)
        else:
            self.log_result("Concurrent Requests", False, f"Low success rate: {success_rate:.1%}")
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['details']}")
        
        print(f"\n⏱️  Performance Summary:")
        fast_tests = [r for r in self.results if r['duration'] > 0 and r['duration'] < 1.0]
        slow_tests = [r for r in self.results if r['duration'] >= 2.0]
        
        print(f"  Fast responses (< 1s): {len(fast_tests)}")
        print(f"  Slow responses (≥ 2s): {len(slow_tests)}")
        
        if slow_tests:
            print(f"  Slow tests:")
            for test in slow_tests:
                print(f"    • {test['test']}: {test['duration']:.3f}s")
        
        # Overall result
        if passed_tests == total_tests:
            print(f"\n🎉 ALL TESTS PASSED! ContactPlus MVP is working perfectly!")
            return True
        elif passed_tests / total_tests >= 0.8:
            print(f"\n✅ MOSTLY PASSING! {passed_tests}/{total_tests} tests passed. System is functional.")
            return True
        else:
            print(f"\n⚠️  ISSUES DETECTED! Only {passed_tests}/{total_tests} tests passed. Please investigate.")
            return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 ContactPlus MVP - Comprehensive Functionality Test")
        print("=" * 55)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        test_suite = [
            self.test_service_health,
            self.test_api_endpoints,
            self.test_database_operations,
            self.test_import_functionality,
            self.test_search_functionality,
            self.test_web_interface_content,
            self.test_performance_basic,
            self.test_concurrent_requests
        ]
        
        start_time = time.time()
        
        for test_function in test_suite:
            try:
                test_function()
            except Exception as e:
                print(f"❌ Test suite error in {test_function.__name__}: {e}")
        
        total_duration = time.time() - start_time
        
        print(f"\n🏁 Testing completed in {total_duration:.1f} seconds")
        
        return self.generate_summary()


def main():
    """Main function"""
    tester = ContactPlusTester()
    
    # Wait a moment for services to be ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(3)
    
    success = tester.run_all_tests()
    
    print(f"\n💡 Next Steps:")
    if success:
        print("  • Open http://localhost:3000 to use the web interface")
        print("  • Import your contact data via the Import page")
        print("  • Explore the API documentation at http://localhost:8080/docs")
        print("  • Monitor logs at http://localhost:8081")
    else:
        print("  • Check container logs: docker-compose logs")
        print("  • Verify all containers are running: docker-compose ps")
        print("  • Try restarting services: docker-compose restart")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())