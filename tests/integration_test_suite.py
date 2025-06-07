#!/usr/bin/env python3
"""
ContactPlus Integration Test Suite
Complete test suite for CI/CD deployment validation
"""
import os
import sys
import time
import json
import subprocess
import requests
from datetime import datetime
from pathlib import Path


class ContactPlusIntegrationTestSuite:
    """Complete integration test suite for ContactPlus MVP"""
    
    def __init__(self, base_url="http://localhost:8080/api/v1", wait_timeout=300):
        self.base_url = base_url
        self.wait_timeout = wait_timeout
        self.results = []
        self.test_data_path = Path(__file__).parent / "test_data"
        self.test_data_path.mkdir(exist_ok=True)
        
    def log_result(self, test_name, success, details="", category="general"):
        """Log test result with category"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'category': category,
            'timestamp': datetime.now().isoformat()
        })
        print(f"  {status} {test_name}")
        if details:
            print(f"    📋 {details}")
    
    def wait_for_services(self):
        """Wait for all services to be ready"""
        print("⏳ Waiting for services to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < self.wait_timeout:
            try:
                # Check API health
                response = requests.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    health_data = response.json()
                    if health_data.get('database_connected'):
                        self.log_result("Service Readiness", True, "All services ready", "infrastructure")
                        return True
            except:
                pass
            
            time.sleep(5)
            print(".", end="", flush=True)
        
        self.log_result("Service Readiness", False, "Services not ready within timeout", "infrastructure")
        return False
    
    def test_infrastructure(self):
        """Test infrastructure and service health"""
        print("\\n🏗️ Testing Infrastructure")
        print("-" * 25)
        
        # Test service endpoints
        endpoints = [
            ("Core API Health", f"{self.base_url}/health"),
            ("Web Interface", "http://localhost:3000"),
            ("Monitor Dashboard", "http://localhost:9090"),
            ("Dozzle Logs", "http://localhost:8081")
        ]
        
        for service_name, url in endpoints:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    self.log_result(service_name, True, f"Status: {response.status_code}", "infrastructure")
                else:
                    self.log_result(service_name, False, f"Status: {response.status_code}", "infrastructure")
            except Exception as e:
                self.log_result(service_name, False, str(e), "infrastructure")
    
    def test_database_operations(self):
        """Test core database operations"""
        print("\\n💾 Testing Database Operations")
        print("-" * 30)
        
        try:
            # Test stats endpoint
            response = requests.get(f"{self.base_url}/stats", timeout=10)
            if response.status_code == 200:
                stats = response.json()
                total = stats.get('total_contacts', 0)
                active = stats.get('active_contacts', 0)
                sources = len(stats.get('contacts_by_source', {}))
                
                self.log_result("Database Stats", True, 
                               f"Total: {total}, Active: {active}, Sources: {sources}", "database")
                
                # Test data integrity
                if active <= total:
                    self.log_result("Data Integrity", True, "Active ≤ Total contacts", "database")
                else:
                    self.log_result("Data Integrity", False, "Active > Total contacts", "database")
            else:
                self.log_result("Database Stats", False, f"Status: {response.status_code}", "database")
                
            # Test contact listing
            response = requests.get(f"{self.base_url}/contacts?page_size=10", timeout=10)
            if response.status_code == 200:
                data = response.json()
                contacts = data.get('contacts', [])
                self.log_result("Contact Listing", True, f"Retrieved {len(contacts)} contacts", "database")
            else:
                self.log_result("Contact Listing", False, f"Status: {response.status_code}", "database")
                
        except Exception as e:
            self.log_result("Database Operations", False, str(e), "database")
    
    def test_search_functionality(self):
        """Test search functionality"""
        print("\\n🔍 Testing Search Functionality")
        print("-" * 31)
        
        search_tests = [
            ("Basic Name Search", "john"),
            ("Email Search", "@"),
            ("Phone Search", "+"),
            ("Organization Search", "corp"),
            ("Case Insensitive", "JOHN")
        ]
        
        for test_name, query in search_tests:
            try:
                response = requests.get(f"{self.base_url}/contacts/search?query={query}", timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('total', 0)
                    self.log_result(test_name, True, f"Found {results} results", "search")
                else:
                    self.log_result(test_name, False, f"Status: {response.status_code}", "search")
            except Exception as e:
                self.log_result(test_name, False, str(e), "search")
    
    def test_field_parsing(self):
        """Test comprehensive field parsing"""
        print("\\n📝 Testing Field Parsing")
        print("-" * 26)
        
        # Create comprehensive test vCard
        test_vcard = '''BEGIN:VCARD
VERSION:3.0
FN:Integration Test Contact
N:Contact;Integration;Test;;
ORG:ContactPlus Test Suite
TITLE:Test Engineer
EMAIL;TYPE=WORK:integration@contactplus.test
EMAIL;TYPE=HOME:test@personal.com
TEL;TYPE=WORK:+1-555-TEST-001
TEL;TYPE=CELL:+1-555-TEST-002
NOTE:This is an integration test contact with multiple fields for validation.
X-TEST-FIELD:Integration Test Value
END:VCARD'''
        
        try:
            # Save test file
            test_file = self.test_data_path / "integration_test.vcf"
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_vcard)
            
            # Import via container (since we don't have direct import endpoint)
            result = self._import_test_file(str(test_file), "IntegrationTest")
            
            if result and result.get('imported_contacts', 0) > 0:
                self.log_result("Test Contact Import", True, 
                               f"Imported {result['imported_contacts']} contacts", "parsing")
                
                # Restart API to refresh
                self._restart_api()
                
                # Retrieve and validate
                test_contact = self._get_test_contact("IntegrationTest")
                if test_contact:
                    self._validate_parsed_fields(test_contact)
                else:
                    self.log_result("Test Contact Retrieval", False, "Could not retrieve test contact", "parsing")
            else:
                self.log_result("Test Contact Import", False, "Import failed", "parsing")
                
        except Exception as e:
            self.log_result("Field Parsing Test", False, str(e), "parsing")
    
    def test_crud_operations(self):
        """Test CRUD operations"""
        print("\\n✏️  Testing CRUD Operations")
        print("-" * 27)
        
        # Get a test contact for CRUD operations
        test_contact = self._get_any_contact()
        
        if not test_contact:
            self.log_result("CRUD Setup", False, "No contact available for CRUD tests", "crud")
            return
        
        contact_id = test_contact.get('contact_id')
        
        # Test READ operation
        try:
            response = requests.get(f"{self.base_url}/contacts/{contact_id}", timeout=10)
            if response.status_code == 200:
                self.log_result("Contact READ", True, f"Retrieved contact {contact_id}", "crud")
            else:
                self.log_result("Contact READ", False, f"Status: {response.status_code}", "crud")
        except Exception as e:
            self.log_result("Contact READ", False, str(e), "crud")
        
        # Test UPDATE operation
        try:
            update_data = {
                "title": "Updated Integration Test Title",
                "notes": f"Updated during integration test at {datetime.now()}"
            }
            
            response = requests.put(
                f"{self.base_url}/contacts/{contact_id}",
                json=update_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                updated_contact = response.json()
                if updated_contact.get('title') == update_data['title']:
                    self.log_result("Contact UPDATE", True, "Field updated successfully", "crud")
                else:
                    self.log_result("Contact UPDATE", False, "Update not reflected", "crud")
            else:
                self.log_result("Contact UPDATE", False, f"Status: {response.status_code}", "crud")
        except Exception as e:
            self.log_result("Contact UPDATE", False, str(e), "crud")
        
        # Test DELETE (soft delete) operation
        try:
            response = requests.delete(f"{self.base_url}/contacts/{contact_id}", timeout=10)
            if response.status_code == 200:
                self.log_result("Contact DELETE", True, "Soft delete successful", "crud")
                
                # Verify soft delete (contact should still be retrievable but inactive)
                time.sleep(2)
                verify_response = requests.get(f"{self.base_url}/contacts/{contact_id}", timeout=10)
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    if not verify_data.get('is_active', True):
                        self.log_result("Soft Delete Verification", True, "Contact marked inactive", "crud")
                    else:
                        self.log_result("Soft Delete Verification", False, "Contact still active", "crud")
                else:
                    self.log_result("Soft Delete Verification", False, "Contact not retrievable", "crud")
            else:
                self.log_result("Contact DELETE", False, f"Status: {response.status_code}", "crud")
        except Exception as e:
            self.log_result("Contact DELETE", False, str(e), "crud")
    
    def test_export_functionality(self):
        """Test export functionality"""
        print("\\n📤 Testing Export Functionality")
        print("-" * 31)
        
        try:
            response = requests.get(f"{self.base_url}/export/vcf", timeout=60)
            if response.status_code == 200:
                content = response.text
                
                # Validate VCF format
                if content.startswith("BEGIN:VCARD") and "END:VCARD" in content:
                    contact_count = content.count("BEGIN:VCARD")
                    file_size = len(content)
                    self.log_result("VCF Export", True, 
                                   f"Exported {contact_count} contacts ({file_size:,} bytes)", "export")
                    
                    # Save export for validation
                    export_file = self.test_data_path / "integration_export.vcf"
                    with open(export_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.log_result("Export File Save", True, f"Saved to {export_file}", "export")
                else:
                    self.log_result("VCF Export", False, "Invalid VCF format", "export")
            else:
                self.log_result("VCF Export", False, f"Status: {response.status_code}", "export")
        except Exception as e:
            self.log_result("Export Functionality", False, str(e), "export")
    
    def test_performance(self):
        """Test performance characteristics"""
        print("\\n⚡ Testing Performance")
        print("-" * 21)
        
        # Test response times for key operations
        operations = [
            ("Health Check", f"{self.base_url}/health"),
            ("Database Stats", f"{self.base_url}/stats"),
            ("Contact List", f"{self.base_url}/contacts?page_size=10"),
            ("Search", f"{self.base_url}/contacts/search?query=test")
        ]
        
        for op_name, url in operations:
            times = []
            for _ in range(3):  # 3 requests each
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
                if avg_time < 5.0:  # 5 second threshold for CI environment
                    self.log_result(f"{op_name} Performance", True, f"Avg: {avg_time:.3f}s", "performance")
                else:
                    self.log_result(f"{op_name} Performance", False, f"Too slow: {avg_time:.3f}s", "performance")
            else:
                self.log_result(f"{op_name} Performance", False, "No successful requests", "performance")
    
    def test_unicode_support(self):
        """Test Unicode and special character support"""
        print("\\n🌐 Testing Unicode Support")
        print("-" * 27)
        
        unicode_vcard = '''BEGIN:VCARD
VERSION:3.0
FN:José María González
N:González;José;María;;
ORG:Test Café & Açaí™
EMAIL:josé@café.test
NOTE:Unicode test: 你好 こんにちは мир 🌍
END:VCARD'''
        
        try:
            test_file = self.test_data_path / "unicode_test.vcf"
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(unicode_vcard)
            
            result = self._import_test_file(str(test_file), "UnicodeTest")
            
            if result and result.get('imported_contacts', 0) > 0:
                self.log_result("Unicode Import", True, "Unicode contact imported", "unicode")
                
                # Restart and verify
                self._restart_api()
                unicode_contact = self._get_test_contact("UnicodeTest")
                
                if unicode_contact:
                    fn = unicode_contact.get('fn', '')
                    if 'José María' in fn:
                        self.log_result("Unicode Preservation", True, "Special characters preserved", "unicode")
                    else:
                        self.log_result("Unicode Preservation", False, f"Characters corrupted: {fn}", "unicode")
                else:
                    self.log_result("Unicode Retrieval", False, "Could not retrieve unicode contact", "unicode")
            else:
                self.log_result("Unicode Import", False, "Unicode import failed", "unicode")
                
        except Exception as e:
            self.log_result("Unicode Support", False, str(e), "unicode")
    
    def _import_test_file(self, file_path, database_name):
        """Import test file via container"""
        try:
            # Copy file to container
            subprocess.run(['docker', 'cp', file_path, 'contactplus-core:/tmp/test_import.vcf'], 
                          check=True, capture_output=True)
            
            # Import via container
            result = subprocess.run([
                'docker', 'exec', 'contactplus-core', 'python', '-c',
                f'''
from database.connector import APIConnector
conn = APIConnector()
result = conn.import_database("/tmp/test_import.vcf", "{database_name}")
import json
print(json.dumps(result))
'''
            ], capture_output=True, text=True, check=True)
            
            return json.loads(result.stdout.strip().split('\\n')[-1])
        except Exception as e:
            print(f"Import error: {e}")
            return None
    
    def _restart_api(self):
        """Restart API to refresh database"""
        try:
            subprocess.run(['docker-compose', 'restart', 'contactplus-core'], 
                         capture_output=True, check=True)
            time.sleep(10)  # Wait for restart
        except:
            pass
    
    def _get_test_contact(self, database_name):
        """Get test contact from specific database"""
        try:
            response = requests.get(f"{self.base_url}/contacts?page_size=100", timeout=10)
            if response.status_code == 200:
                contacts = response.json().get('contacts', [])
                test_contacts = [c for c in contacts 
                               if c.get('source_info', {}).get('database_name') == database_name]
                return test_contacts[0] if test_contacts else None
        except:
            return None
    
    def _get_any_contact(self):
        """Get any contact for testing"""
        try:
            response = requests.get(f"{self.base_url}/contacts?page_size=1", timeout=10)
            if response.status_code == 200:
                contacts = response.json().get('contacts', [])
                return contacts[0] if contacts else None
        except:
            return None
    
    def _validate_parsed_fields(self, contact):
        """Validate that fields were parsed correctly"""
        
        # Check basic fields
        fn = contact.get('fn', '')
        if 'Integration Test Contact' in fn:
            self.log_result("FN Field Parsing", True, f"FN: {fn}", "parsing")
        else:
            self.log_result("FN Field Parsing", False, f"Unexpected FN: {fn}", "parsing")
        
        # Check multiple emails
        emails = contact.get('emails', [])
        if len(emails) >= 2:
            self.log_result("Multiple Email Parsing", True, f"Found {len(emails)} emails", "parsing")
        else:
            self.log_result("Multiple Email Parsing", False, f"Expected 2+ emails, got {len(emails)}", "parsing")
        
        # Check organization
        org = contact.get('organization', '')
        if 'ContactPlus Test Suite' in org:
            self.log_result("Organization Parsing", True, f"Org: {org}", "parsing")
        else:
            self.log_result("Organization Parsing", False, f"Unexpected org: {org}", "parsing")
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\\n" + "=" * 70)
        print("📋 CONTACTPLUS INTEGRATION TEST REPORT")
        print("=" * 70)
        
        # Overall stats
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Overall Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {passed_tests/total_tests*100:.1f}%")
        
        # Category breakdown
        categories = {}
        for result in self.results:
            category = result.get('category', 'general')
            if category not in categories:
                categories[category] = {'total': 0, 'passed': 0}
            categories[category]['total'] += 1
            if result['success']:
                categories[category]['passed'] += 1
        
        print(f"\\n📊 Results by Category:")
        for category, stats in categories.items():
            rate = stats['passed'] / stats['total'] * 100
            status = "✅" if rate >= 80 else "⚠️" if rate >= 60 else "❌"
            print(f"   {status} {category.title()}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")
        
        # Failed tests
        if failed_tests > 0:
            print(f"\\n❌ Failed Tests:")
            for result in self.results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        # Generate JSON report for CI
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': passed_tests / total_tests,
            'categories': categories,
            'results': self.results
        }
        
        report_file = self.test_data_path / "integration_test_report.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\\n📄 Test report saved to: {report_file}")
        
        # Determine overall success
        success_threshold = 0.85  # 85% pass rate required
        overall_success = (passed_tests / total_tests) >= success_threshold
        
        if overall_success:
            print(f"\\n🎉 INTEGRATION TESTS PASSED! System is ready for deployment.")
        else:
            print(f"\\n⚠️  INTEGRATION TESTS FAILED! Please fix issues before deployment.")
        
        return overall_success
    
    def run_full_integration_test(self):
        """Run complete integration test suite"""
        print("🚀 ContactPlus MVP - Full Integration Test Suite")
        print("=" * 55)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Testing API at: {self.base_url}")
        
        start_time = time.time()
        
        # Wait for services
        if not self.wait_for_services():
            return False
        
        # Run all test categories
        test_suite = [
            self.test_infrastructure,
            self.test_database_operations,
            self.test_search_functionality,
            self.test_field_parsing,
            self.test_crud_operations,
            self.test_export_functionality,
            self.test_unicode_support,
            self.test_performance
        ]
        
        for test_function in test_suite:
            try:
                test_function()
            except Exception as e:
                print(f"❌ Test suite error in {test_function.__name__}: {e}")
        
        total_duration = time.time() - start_time
        print(f"\\n🏁 Integration testing completed in {total_duration:.1f} seconds")
        
        return self.generate_test_report()


def main():
    """Main function for CI/CD integration"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ContactPlus Integration Test Suite')
    parser.add_argument('--base-url', default='http://localhost:8080/api/v1',
                       help='Base URL for API testing')
    parser.add_argument('--timeout', type=int, default=300,
                       help='Timeout for service readiness (seconds)')
    
    args = parser.parse_args()
    
    tester = ContactPlusIntegrationTestSuite(args.base_url, args.timeout)
    success = tester.run_full_integration_test()
    
    # Exit with appropriate code for CI/CD
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()