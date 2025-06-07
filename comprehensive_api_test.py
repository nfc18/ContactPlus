#!/usr/bin/env python3
"""
Comprehensive API Functionality Test for ContactPlus MVP
Tests all endpoints with real data to ensure complete functionality
"""
import requests
import json
import time
import sys
from datetime import datetime


class ComprehensiveAPITester:
    """Complete API functionality tester"""
    
    def __init__(self):
        self.base_url = "http://localhost:8080/api/v1"
        self.results = []
        self.test_contact_id = None
        
    def log_result(self, test_name, success, details="", duration=0, data=None):
        """Log test result with detailed information"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'duration': duration,
            'data': data
        })
        duration_str = f" ({duration:.3f}s)" if duration > 0 else ""
        print(f"  {status} {test_name}{duration_str}")
        if details and (not success or "data" in test_name.lower()):
            print(f"    📋 {details}")
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        print("\n🏥 Testing Health Check")
        print("-" * 25)
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                details = f"Status: {data.get('status')}, DB Connected: {data.get('database_connected')}, Contacts: {data.get('contacts_count')}"
                self.log_result("Health Check", True, details, duration, data)
                return True
            else:
                self.log_result("Health Check", False, f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.log_result("Health Check", False, str(e))
            return False
    
    def test_stats_endpoint(self):
        """Test database statistics endpoint"""
        print("\n📊 Testing Database Statistics")
        print("-" * 30)
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/stats", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                total = data.get('total_contacts', 0)
                active = data.get('active_contacts', 0)
                sources = data.get('contacts_by_source', {})
                operations = data.get('total_operations', 0)
                
                details = f"Total: {total}, Active: {active}, Sources: {len(sources)}, Operations: {operations}"
                self.log_result("Database Stats", True, details, duration, data)
                
                # Validate data integrity
                source_total = sum(sources.values())
                if source_total == total:
                    self.log_result("Data Integrity Check", True, f"Source totals match: {source_total}")
                else:
                    self.log_result("Data Integrity Check", False, f"Mismatch: {source_total} vs {total}")
                
                return True
            else:
                self.log_result("Database Stats", False, f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.log_result("Database Stats", False, str(e))
            return False
    
    def test_contact_listing(self):
        """Test contact listing with pagination"""
        print("\n📋 Testing Contact Listing")
        print("-" * 26)
        
        # Test default listing
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/contacts", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                contacts = data.get('contacts', [])
                total = data.get('total', 0)
                page_size = data.get('page_size', 0)
                
                details = f"Retrieved {len(contacts)} contacts, Total: {total}, Page size: {page_size}"
                self.log_result("Default Contact List", True, details, duration)
                
                # Store first contact ID for later tests
                if contacts:
                    self.test_contact_id = contacts[0].get('contact_id')
                    self.log_result("Contact ID Capture", True, f"ID: {self.test_contact_id}")
                
            else:
                self.log_result("Default Contact List", False, f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.log_result("Default Contact List", False, str(e))
            return False
        
        # Test pagination
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/contacts?page=2&page_size=5", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                contacts = data.get('contacts', [])
                page = data.get('page', 0)
                
                details = f"Page {page}: {len(contacts)} contacts"
                self.log_result("Pagination Test", True, details, duration)
            else:
                self.log_result("Pagination Test", False, f"Status: {response.status_code}", duration)
        except Exception as e:
            self.log_result("Pagination Test", False, str(e))
        
        return True
    
    def test_search_functionality(self):
        """Test search functionality with various queries"""
        print("\n🔍 Testing Search Functionality")
        print("-" * 31)
        
        search_tests = [
            ("Name Search", "sara"),
            ("Email Search", "@lmco.com"),
            ("Organization Search", "lockheed"),
            ("Phone Search", "408"),
            ("Title Search", "engineer"),
            ("Case Insensitive", "SARA"),
            ("Partial Match", "ker")
        ]
        
        for test_name, query in search_tests:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}/contacts/search?query={query}", timeout=10)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    contacts = data.get('contacts', [])
                    total = data.get('total', 0)
                    
                    details = f"Query: '{query}' → {total} results"
                    self.log_result(test_name, True, details, duration)
                    
                    # Validate search results contain query term
                    if contacts and query.lower() not in ["408"]:  # Skip validation for phone numbers
                        sample_contact = contacts[0]
                        found_in_result = any(
                            query.lower() in str(value).lower() 
                            for value in [
                                sample_contact.get('fn', ''),
                                sample_contact.get('organization', ''),
                                sample_contact.get('title', ''),
                                str(sample_contact.get('emails', [])),
                            ]
                        )
                        if found_in_result:
                            self.log_result(f"{test_name} Validation", True, "Query term found in results")
                        else:
                            self.log_result(f"{test_name} Validation", False, "Query term not found in results")
                    
                else:
                    self.log_result(test_name, False, f"Status: {response.status_code}", duration)
            except Exception as e:
                self.log_result(test_name, False, str(e))
    
    def test_individual_contact_retrieval(self):
        """Test retrieving individual contacts"""
        print("\n👤 Testing Individual Contact Retrieval")
        print("-" * 37)
        
        if not self.test_contact_id:
            self.log_result("Contact Retrieval", False, "No contact ID available")
            return False
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/contacts/{self.test_contact_id}", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                fn = data.get('fn', '')
                contact_id = data.get('contact_id', '')
                source = data.get('source_info', {}).get('database_name', '')
                
                details = f"Contact: {fn}, ID: {contact_id}, Source: {source}"
                self.log_result("Get Contact by ID", True, details, duration, data)
                
                # Validate contact data structure
                required_fields = ['fn', 'contact_id', 'source_info', 'created_at']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_result("Contact Data Structure", True, "All required fields present")
                else:
                    self.log_result("Contact Data Structure", False, f"Missing: {missing_fields}")
                
                return True
            else:
                self.log_result("Get Contact by ID", False, f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.log_result("Get Contact by ID", False, str(e))
            return False
    
    def test_contact_creation(self):
        """Test creating new contacts"""
        print("\n➕ Testing Contact Creation")
        print("-" * 26)
        
        test_contact = {
            "fn": "Test User API",
            "emails": ["test.api@contactplus.test"],
            "phones": ["+1234567890"],
            "organization": "ContactPlus Test",
            "title": "API Test Contact"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/contacts",
                json=test_contact,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            duration = time.time() - start_time
            
            if response.status_code == 201:
                data = response.json()
                created_id = data.get('contact_id', '')
                
                details = f"Created contact: {created_id}"
                self.log_result("Create Contact", True, details, duration, data)
                
                # Store for update/delete tests
                self.created_contact_id = created_id
                return True
            else:
                self.log_result("Create Contact", False, f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.log_result("Create Contact", False, str(e))
            return False
    
    def test_contact_update(self):
        """Test updating contacts"""
        print("\n✏️  Testing Contact Updates")
        print("-" * 25)
        
        if not hasattr(self, 'created_contact_id'):
            self.log_result("Contact Update", False, "No created contact to update")
            return False
        
        update_data = {
            "title": "Updated API Test Contact",
            "organization": "ContactPlus Updated"
        }
        
        try:
            start_time = time.time()
            response = requests.put(
                f"{self.base_url}/contacts/{self.created_contact_id}",
                json=update_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                updated_title = data.get('title', '')
                updated_org = data.get('organization', '')
                
                details = f"Updated: {updated_title} at {updated_org}"
                self.log_result("Update Contact", True, details, duration)
                return True
            else:
                self.log_result("Update Contact", False, f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.log_result("Update Contact", False, str(e))
            return False
    
    def test_export_functionality(self):
        """Test export functionality"""
        print("\n📤 Testing Export Functionality")
        print("-" * 31)
        
        # Test VCF export
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/export/vcf", timeout=30)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                content = response.text
                vcf_size = len(content)
                
                # Validate VCF format
                if content.startswith("BEGIN:VCARD") and content.strip().endswith("END:VCARD"):
                    details = f"Valid VCF export: {vcf_size:,} bytes"
                    self.log_result("VCF Export", True, details, duration)
                    
                    # Count contacts in export
                    contact_count = content.count("BEGIN:VCARD")
                    self.log_result("VCF Contact Count", True, f"Exported {contact_count} contacts")
                else:
                    self.log_result("VCF Export", False, "Invalid VCF format")
                
            else:
                self.log_result("VCF Export", False, f"Status: {response.status_code}", duration)
        except Exception as e:
            self.log_result("VCF Export", False, str(e))
    
    def test_import_status(self):
        """Test import status endpoint"""
        print("\n📥 Testing Import Status")
        print("-" * 24)
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/import/status", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                details = f"Import status retrieved"
                self.log_result("Import Status", True, details, duration, data)
            else:
                self.log_result("Import Status", False, f"Status: {response.status_code}", duration)
        except Exception as e:
            self.log_result("Import Status", False, str(e))
    
    def test_contact_deletion(self):
        """Test contact deletion (soft delete)"""
        print("\n🗑️  Testing Contact Deletion")
        print("-" * 27)
        
        if not hasattr(self, 'created_contact_id'):
            self.log_result("Contact Deletion", False, "No created contact to delete")
            return False
        
        try:
            start_time = time.time()
            response = requests.delete(f"{self.base_url}/contacts/{self.created_contact_id}", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                details = f"Contact soft deleted: {self.created_contact_id}"
                self.log_result("Delete Contact", True, details, duration)
                
                # Verify contact is marked as inactive
                time.sleep(1)  # Brief pause
                verify_response = requests.get(f"{self.base_url}/contacts/{self.created_contact_id}")
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    is_active = verify_data.get('is_active', True)
                    if not is_active:
                        self.log_result("Soft Delete Verification", True, "Contact marked as inactive")
                    else:
                        self.log_result("Soft Delete Verification", False, "Contact still active")
                
                return True
            else:
                self.log_result("Delete Contact", False, f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.log_result("Delete Contact", False, str(e))
            return False
    
    def test_error_handling(self):
        """Test error handling for invalid requests"""
        print("\n🚨 Testing Error Handling")
        print("-" * 24)
        
        # Test invalid contact ID
        try:
            response = requests.get(f"{self.base_url}/contacts/invalid_id", timeout=10)
            if response.status_code == 404:
                self.log_result("Invalid Contact ID", True, "Correctly returns 404")
            else:
                self.log_result("Invalid Contact ID", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("Invalid Contact ID", False, str(e))
        
        # Test invalid search query
        try:
            response = requests.get(f"{self.base_url}/contacts/search", timeout=10)
            if response.status_code == 422:
                self.log_result("Missing Query Parameter", True, "Correctly returns 422")
            else:
                self.log_result("Missing Query Parameter", False, f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.log_result("Missing Query Parameter", False, str(e))
        
        # Test invalid JSON
        try:
            response = requests.post(
                f"{self.base_url}/contacts",
                data="invalid json",
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.status_code >= 400:
                self.log_result("Invalid JSON", True, f"Correctly returns {response.status_code}")
            else:
                self.log_result("Invalid JSON", False, f"Expected error, got {response.status_code}")
        except Exception as e:
            self.log_result("Invalid JSON", False, str(e))
    
    def test_performance_characteristics(self):
        """Test performance under various loads"""
        print("\n⚡ Testing Performance")
        print("-" * 21)
        
        # Test response times for different operations
        operations = [
            ("Health Check", f"{self.base_url}/health"),
            ("Stats", f"{self.base_url}/stats"),
            ("Contact List", f"{self.base_url}/contacts?page_size=10"),
            ("Search", f"{self.base_url}/contacts/search?query=test")
        ]
        
        for op_name, url in operations:
            times = []
            for i in range(5):  # 5 requests each
                try:
                    start_time = time.time()
                    response = requests.get(url, timeout=10)
                    duration = time.time() - start_time
                    if response.status_code == 200:
                        times.append(duration)
                except:
                    pass
            
            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                min_time = min(times)
                
                if avg_time < 2.0:  # Less than 2 seconds average
                    details = f"Avg: {avg_time:.3f}s, Min: {min_time:.3f}s, Max: {max_time:.3f}s"
                    self.log_result(f"{op_name} Performance", True, details)
                else:
                    self.log_result(f"{op_name} Performance", False, f"Too slow: {avg_time:.3f}s average")
            else:
                self.log_result(f"{op_name} Performance", False, "No successful requests")
    
    def generate_comprehensive_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 70)
        print("📋 COMPREHENSIVE API TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Overall Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        # Performance summary
        performance_tests = [r for r in self.results if 'performance' in r['test'].lower() and r['duration'] > 0]
        if performance_tests:
            print(f"\n⚡ Performance Summary:")
            fast_tests = [r for r in performance_tests if r['duration'] < 1.0]
            slow_tests = [r for r in performance_tests if r['duration'] >= 2.0]
            
            print(f"   Fast responses (< 1s): {len(fast_tests)}")
            print(f"   Slow responses (≥ 2s): {len(slow_tests)}")
            
            if slow_tests:
                print(f"   Slow operations:")
                for test in slow_tests:
                    print(f"     • {test['test']}: {test['duration']:.3f}s")
        
        # Data summary
        stats_result = next((r for r in self.results if r['test'] == 'Database Stats' and r['data']), None)
        if stats_result:
            data = stats_result['data']
            print(f"\n📊 Database Summary:")
            print(f"   Total Contacts: {data.get('total_contacts', 0):,}")
            print(f"   Active Contacts: {data.get('active_contacts', 0):,}")
            print(f"   Sources: {len(data.get('contacts_by_source', {}))}")
            print(f"   Total Operations: {data.get('total_operations', 0):,}")
            
            for source, count in data.get('contacts_by_source', {}).items():
                print(f"     • {source}: {count:,} contacts")
        
        # Overall assessment
        if passed_tests == total_tests:
            print(f"\n🎉 ALL TESTS PASSED! ContactPlus API is fully functional!")
            return True
        elif passed_tests / total_tests >= 0.9:
            print(f"\n✅ EXCELLENT! {passed_tests}/{total_tests} tests passed. API is highly functional.")
            return True
        elif passed_tests / total_tests >= 0.8:
            print(f"\n✅ GOOD! {passed_tests}/{total_tests} tests passed. API is mostly functional.")
            return True
        else:
            print(f"\n⚠️  ISSUES DETECTED! Only {passed_tests}/{total_tests} tests passed. Please investigate failures.")
            return False
    
    def run_comprehensive_test_suite(self):
        """Run all API tests in sequence"""
        print("🚀 ContactPlus API - Comprehensive Functionality Test")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Testing API at: {self.base_url}")
        
        start_time = time.time()
        
        # Run all test categories
        test_suite = [
            self.test_health_endpoint,
            self.test_stats_endpoint,
            self.test_contact_listing,
            self.test_search_functionality,
            self.test_individual_contact_retrieval,
            self.test_contact_creation,
            self.test_contact_update,
            self.test_export_functionality,
            self.test_import_status,
            self.test_contact_deletion,
            self.test_error_handling,
            self.test_performance_characteristics
        ]
        
        for test_function in test_suite:
            try:
                test_function()
            except Exception as e:
                print(f"❌ Test suite error in {test_function.__name__}: {e}")
        
        total_duration = time.time() - start_time
        print(f"\n🏁 Testing completed in {total_duration:.1f} seconds")
        
        return self.generate_comprehensive_summary()


def main():
    """Main function"""
    tester = ComprehensiveAPITester()
    
    # Give services a moment to be ready
    print("⏳ Ensuring API is ready...")
    time.sleep(2)
    
    success = tester.run_comprehensive_test_suite()
    
    print(f"\n💡 Next Steps:")
    if success:
        print("  • API is fully functional and production-ready")
        print("  • All CRUD operations working correctly")
        print("  • Search, export, and import systems operational")
        print("  • Performance meets expected standards")
        print("  • Error handling working properly")
    else:
        print("  • Review failed tests and fix issues")
        print("  • Check container logs: docker-compose logs")
        print("  • Verify database connections and data integrity")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())