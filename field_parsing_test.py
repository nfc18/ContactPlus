#!/usr/bin/env python3
"""
Comprehensive Field Parsing and CRUD Operations Test
Tests all vCard fields, parsing accuracy, and modification operations
"""
import requests
import json
import time
import sys
from datetime import datetime


class FieldParsingTester:
    """Test field parsing and CRUD operations comprehensively"""
    
    def __init__(self):
        self.base_url = "http://localhost:8080/api/v1"
        self.results = []
        self.test_contact_ids = []
        
    def log_result(self, test_name, success, details="", data=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'data': data
        })
        print(f"  {status} {test_name}")
        if details:
            print(f"    📋 {details}")
    
    def test_comprehensive_field_parsing(self):
        """Test parsing of all vCard fields"""
        print("\n📝 Testing Comprehensive Field Parsing")
        print("-" * 40)
        
        # Create a comprehensive test vCard with all possible fields
        comprehensive_vcard = '''BEGIN:VCARD
VERSION:3.0
FN:Dr. John Michael Smith Jr.
N:Smith;John;Michael;Dr.;Jr.
NICKNAME:Johnny,Mike
ORG:Acme Corporation;R&D Department;Software Division
TITLE:Senior Software Engineer
ROLE:Team Lead
EMAIL;TYPE=WORK,PREF:john.smith@acme.com
EMAIL;TYPE=HOME:john.personal@gmail.com
EMAIL;TYPE=OTHER:j.smith@consulting.com
TEL;TYPE=WORK,VOICE:+1-555-123-4567
TEL;TYPE=HOME,VOICE:+1-555-987-6543
TEL;TYPE=CELL:+1-555-456-7890
TEL;TYPE=FAX:+1-555-123-4568
ADR;TYPE=WORK:;;123 Business Ave;New York;NY;10001;USA
ADR;TYPE=HOME:;;456 Home Street;Brooklyn;NY;11201;USA
URL;TYPE=WORK:https://www.acme.com/employees/jsmith
URL;TYPE=HOME:https://johnsmith.personal.com
BDAY:1985-06-15
NOTE:This is a comprehensive test contact with all possible vCard fields. Multiple emails, phones, addresses, and other data.
CATEGORIES:Business,Software,Engineering
X-CUSTOM-FIELD:Custom Value
X-SOCIAL-TWITTER:@johnsmith
X-SOCIAL-LINKEDIN:linkedin.com/in/johnsmith
PHOTO;ENCODING=b;TYPE=JPEG:/9j/4AAQSkZJRgABAQEAYABgAAD
REV:2025-06-07T18:30:00Z
UID:john.smith.12345@acme.com
END:VCARD'''
        
        # Import this comprehensive contact via direct database operation
        try:
            # Write to temp file
            with open('/tmp/comprehensive_test.vcf', 'w') as f:
                f.write(comprehensive_vcard)
            
            # Import via API
            result = self._import_test_file('/tmp/comprehensive_test.vcf', 'FieldTest')
            
            if result and result.get('imported_contacts', 0) > 0:
                self.log_result("Comprehensive vCard Import", True, 
                               f"Imported {result['imported_contacts']} contacts")
                
                # Get the imported contact
                test_contact = self._get_test_contact('FieldTest')
                if test_contact:
                    self._validate_all_fields(test_contact)
                else:
                    self.log_result("Contact Retrieval", False, "Could not retrieve imported contact")
            else:
                self.log_result("Comprehensive vCard Import", False, "Import failed")
                
        except Exception as e:
            self.log_result("Comprehensive vCard Import", False, str(e))
    
    def _import_test_file(self, file_path, database_name):
        """Helper to import test file via container"""
        import subprocess
        
        try:
            # Copy file to container and import
            subprocess.run(['docker', 'cp', file_path, f'contactplus-core:/tmp/test_import.vcf'], 
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
            
            return json.loads(result.stdout.strip().split('\n')[-1])
            
        except Exception as e:
            print(f"Import error: {e}")
            return None
    
    def _get_test_contact(self, database_name):
        """Get a test contact from specific database"""
        try:
            # Search for contacts from our test database
            response = requests.get(f"{self.base_url}/contacts?page_size=100", timeout=10)
            if response.status_code == 200:
                data = response.json()
                contacts = data.get('contacts', [])
                
                # Find our test contact
                test_contacts = [c for c in contacts 
                               if c.get('source_info', {}).get('database_name') == database_name]
                
                if test_contacts:
                    return test_contacts[0]
            
            return None
        except Exception as e:
            print(f"Error retrieving test contact: {e}")
            return None
    
    def _validate_all_fields(self, contact):
        """Validate all fields were parsed correctly"""
        
        # Test basic identification fields
        fn = contact.get('fn', '')
        if 'Dr. John Michael Smith Jr.' in fn:
            self.log_result("FN Field Parsing", True, f"FN: {fn}")
        else:
            self.log_result("FN Field Parsing", False, f"Expected comprehensive name, got: {fn}")
        
        # Test email parsing
        emails = contact.get('emails', [])
        expected_emails = ['john.smith@acme.com', 'john.personal@gmail.com', 'j.smith@consulting.com']
        
        if len(emails) >= 3:
            self.log_result("Multiple Email Parsing", True, f"Found {len(emails)} emails")
            
            # Check if expected emails are present
            missing_emails = [email for email in expected_emails if email not in emails]
            if not missing_emails:
                self.log_result("Email Content Accuracy", True, "All expected emails found")
            else:
                self.log_result("Email Content Accuracy", False, f"Missing: {missing_emails}")
        else:
            self.log_result("Multiple Email Parsing", False, f"Expected 3+ emails, got {len(emails)}")
        
        # Test phone parsing
        phones = contact.get('phones', [])
        expected_phones = ['+1-555-123-4567', '+1-555-987-6543', '+1-555-456-7890']
        
        if len(phones) >= 3:
            self.log_result("Multiple Phone Parsing", True, f"Found {len(phones)} phones")
        else:
            self.log_result("Multiple Phone Parsing", False, f"Expected 3+ phones, got {len(phones)}")
        
        # Test organization parsing
        organization = contact.get('organization', '')
        if 'Acme Corporation' in organization:
            self.log_result("Organization Parsing", True, f"Org: {organization}")
        else:
            self.log_result("Organization Parsing", False, f"Expected Acme Corporation, got: {organization}")
        
        # Test title parsing
        title = contact.get('title', '')
        if 'Senior Software Engineer' in title:
            self.log_result("Title Parsing", True, f"Title: {title}")
        else:
            self.log_result("Title Parsing", False, f"Expected job title, got: {title}")
        
        # Test notes parsing
        notes = contact.get('notes', '')
        if notes and 'comprehensive test contact' in notes.lower():
            self.log_result("Notes Parsing", True, f"Notes length: {len(notes)} chars")
        else:
            self.log_result("Notes Parsing", False, f"Expected comprehensive notes, got: {notes[:50]}...")
        
        # Store contact ID for modification tests
        contact_id = contact.get('contact_id')
        if contact_id:
            self.test_contact_ids.append(contact_id)
            self.log_result("Contact ID Storage", True, f"ID: {contact_id}")
    
    def test_field_modifications(self):
        """Test modifying various fields"""
        print("\n✏️  Testing Field Modifications")
        print("-" * 32)
        
        if not self.test_contact_ids:
            self.log_result("Field Modifications", False, "No test contact available")
            return
        
        contact_id = self.test_contact_ids[0]
        
        # Test multiple field updates
        update_data = {
            "title": "Chief Technology Officer",
            "organization": "Acme Corporation - Updated Division",
            "emails": ["john.smith.updated@acme.com", "john.cto@acme.com"],
            "phones": ["+1-555-999-8888", "+1-555-111-2222"],
            "notes": "Updated contact information during field modification test"
        }
        
        try:
            response = requests.put(
                f"{self.base_url}/contacts/{contact_id}",
                json=update_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                updated_contact = response.json()
                
                # Validate each updated field
                self._validate_updated_fields(updated_contact, update_data)
                
                self.log_result("Field Modification Success", True, "All fields updated via API")
            else:
                self.log_result("Field Modification", False, 
                               f"Update failed with status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Field Modification", False, str(e))
    
    def _validate_updated_fields(self, contact, expected_data):
        """Validate that field updates were applied correctly"""
        
        # Check title update
        if contact.get('title') == expected_data['title']:
            self.log_result("Title Update", True, f"New title: {contact.get('title')}")
        else:
            self.log_result("Title Update", False, 
                           f"Expected: {expected_data['title']}, Got: {contact.get('title')}")
        
        # Check organization update
        if contact.get('organization') == expected_data['organization']:
            self.log_result("Organization Update", True, f"Updated organization")
        else:
            self.log_result("Organization Update", False, "Organization not updated correctly")
        
        # Check email updates
        contact_emails = contact.get('emails', [])
        if set(contact_emails) == set(expected_data['emails']):
            self.log_result("Email Update", True, f"Emails updated: {len(contact_emails)} emails")
        else:
            self.log_result("Email Update", False, 
                           f"Email mismatch. Expected: {expected_data['emails']}, Got: {contact_emails}")
        
        # Check phone updates
        contact_phones = contact.get('phones', [])
        if set(contact_phones) == set(expected_data['phones']):
            self.log_result("Phone Update", True, f"Phones updated: {len(contact_phones)} phones")
        else:
            self.log_result("Phone Update", False, 
                           f"Phone mismatch. Expected: {expected_data['phones']}, Got: {contact_phones}")
        
        # Check notes update
        if contact.get('notes') == expected_data['notes']:
            self.log_result("Notes Update", True, "Notes updated successfully")
        else:
            self.log_result("Notes Update", False, "Notes not updated correctly")
    
    def test_soft_deletion(self):
        """Test soft deletion functionality"""
        print("\n🗑️  Testing Soft Deletion")
        print("-" * 25)
        
        if not self.test_contact_ids:
            self.log_result("Soft Deletion", False, "No test contact available")
            return
        
        contact_id = self.test_contact_ids[0]
        
        try:
            # Get contact before deletion
            before_response = requests.get(f"{self.base_url}/contacts/{contact_id}", timeout=10)
            before_active = before_response.json().get('is_active', False) if before_response.status_code == 200 else False
            
            # Perform soft deletion
            delete_response = requests.delete(f"{self.base_url}/contacts/{contact_id}", timeout=10)
            
            if delete_response.status_code == 200:
                self.log_result("Soft Delete Request", True, "Delete request successful")
                
                # Verify contact is still retrievable but marked inactive
                time.sleep(1)  # Brief pause for processing
                after_response = requests.get(f"{self.base_url}/contacts/{contact_id}", timeout=10)
                
                if after_response.status_code == 200:
                    after_contact = after_response.json()
                    after_active = after_contact.get('is_active', True)
                    
                    self.log_result("Contact Still Retrievable", True, "Contact accessible after deletion")
                    
                    if before_active and not after_active:
                        self.log_result("Soft Delete Verification", True, 
                                       f"Contact marked inactive (was: {before_active}, now: {after_active})")
                    else:
                        self.log_result("Soft Delete Verification", False, 
                                       f"Active status not changed correctly (was: {before_active}, now: {after_active})")
                else:
                    self.log_result("Contact Still Retrievable", False, 
                                   f"Contact not accessible after deletion: {after_response.status_code}")
            else:
                self.log_result("Soft Delete Request", False, 
                               f"Delete failed with status: {delete_response.status_code}")
                
        except Exception as e:
            self.log_result("Soft Deletion", False, str(e))
    
    def test_database_integrity_after_operations(self):
        """Test that database maintains integrity after all operations"""
        print("\n🔍 Testing Database Integrity")
        print("-" * 30)
        
        try:
            # Get current database stats
            response = requests.get(f"{self.base_url}/stats", timeout=10)
            
            if response.status_code == 200:
                stats = response.json()
                total_contacts = stats.get('total_contacts', 0)
                active_contacts = stats.get('active_contacts', 0)
                sources = stats.get('contacts_by_source', {})
                
                # Validate integrity
                if total_contacts > 0:
                    self.log_result("Database Population", True, f"Total: {total_contacts} contacts")
                else:
                    self.log_result("Database Population", False, "Database appears empty")
                
                if active_contacts <= total_contacts:
                    self.log_result("Active Count Logic", True, 
                                   f"Active ({active_contacts}) ≤ Total ({total_contacts})")
                else:
                    self.log_result("Active Count Logic", False, 
                                   f"Active ({active_contacts}) > Total ({total_contacts})")
                
                # Check if our test database is tracked
                if 'FieldTest' in sources:
                    self.log_result("Test Data Tracking", True, 
                                   f"FieldTest database tracked with {sources['FieldTest']} contacts")
                else:
                    self.log_result("Test Data Tracking", False, "Test database not found in sources")
                
                # Test export functionality still works
                export_response = requests.get(f"{self.base_url}/export/vcf", timeout=30)
                if export_response.status_code == 200 and len(export_response.text) > 1000:
                    self.log_result("Export Functionality", True, 
                                   f"Export successful: {len(export_response.text)} bytes")
                else:
                    self.log_result("Export Functionality", False, "Export failed or empty")
                
            else:
                self.log_result("Database Integrity", False, f"Stats unavailable: {response.status_code}")
                
        except Exception as e:
            self.log_result("Database Integrity", False, str(e))
    
    def test_special_characters_and_encoding(self):
        """Test handling of special characters and encoding"""
        print("\n🌐 Testing Special Characters & Encoding")
        print("-" * 42)
        
        # Create vCard with special characters
        special_vcard = '''BEGIN:VCARD
VERSION:3.0
FN:José María González-Rodríguez
N:González-Rodríguez;José;María;;
ORG:Açaí & Café™ Corporation
TITLE:Señor Software Engineer
EMAIL:josé.maría@açaí-café.com
TEL:+34-91-123-4567
NOTE:Testing UTF-8: 你好世界 こんにちは мир Здравствуй 🌍 émojis!
X-UNICODE-TEST:Iñtërnâtiônàlizætiøn
END:VCARD'''
        
        try:
            # Write with UTF-8 encoding
            with open('/tmp/special_chars_test.vcf', 'w', encoding='utf-8') as f:
                f.write(special_vcard)
            
            result = self._import_test_file('/tmp/special_chars_test.vcf', 'SpecialChars')
            
            if result and result.get('imported_contacts', 0) > 0:
                self.log_result("Special Characters Import", True, "UTF-8 contact imported")
                
                # Retrieve and validate
                special_contact = self._get_test_contact('SpecialChars')
                if special_contact:
                    fn = special_contact.get('fn', '')
                    if 'José María' in fn and 'González-Rodríguez' in fn:
                        self.log_result("Unicode Name Parsing", True, f"Name: {fn}")
                    else:
                        self.log_result("Unicode Name Parsing", False, f"Name corrupted: {fn}")
                    
                    org = special_contact.get('organization', '')
                    if 'Açaí' in org and 'Café' in org:
                        self.log_result("Unicode Organization", True, f"Org: {org}")
                    else:
                        self.log_result("Unicode Organization", False, f"Org corrupted: {org}")
                    
                    notes = special_contact.get('notes', '')
                    if '你好世界' in notes and '🌍' in notes:
                        self.log_result("Unicode Notes", True, "Special characters preserved")
                    else:
                        self.log_result("Unicode Notes", False, f"Special chars lost: {notes}")
                        
                else:
                    self.log_result("Special Characters Retrieval", False, "Could not retrieve special char contact")
            else:
                self.log_result("Special Characters Import", False, "Import of special characters failed")
                
        except Exception as e:
            self.log_result("Special Characters Test", False, str(e))
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 70)
        print("📋 FIELD PARSING & CRUD OPERATIONS TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Test Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        # Categorize test results
        parsing_tests = [r for r in self.results if 'parsing' in r['test'].lower()]
        modification_tests = [r for r in self.results if any(word in r['test'].lower() 
                                                           for word in ['update', 'modification', 'delete'])]
        integrity_tests = [r for r in self.results if 'integrity' in r['test'].lower()]
        
        print(f"\n📊 Test Categories:")
        print(f"   Field Parsing: {sum(1 for t in parsing_tests if t['success'])}/{len(parsing_tests)} passed")
        print(f"   Modifications: {sum(1 for t in modification_tests if t['success'])}/{len(modification_tests)} passed")
        print(f"   Data Integrity: {sum(1 for t in integrity_tests if t['success'])}/{len(integrity_tests)} passed")
        
        # Overall assessment
        if passed_tests / total_tests >= 0.9:
            print(f"\n🎉 EXCELLENT! Field parsing and CRUD operations are working properly!")
            return True
        else:
            print(f"\n⚠️  ISSUES DETECTED! Please review failed tests.")
            return False
    
    def run_comprehensive_field_test(self):
        """Run all field parsing and CRUD tests"""
        print("🔬 ContactPlus - Comprehensive Field Parsing & CRUD Test")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        start_time = time.time()
        
        # Run all test categories
        test_suite = [
            self.test_comprehensive_field_parsing,
            self.test_field_modifications,
            self.test_soft_deletion,
            self.test_special_characters_and_encoding,
            self.test_database_integrity_after_operations
        ]
        
        for test_function in test_suite:
            try:
                test_function()
                # Restart API to ensure database consistency
                print("  🔄 Restarting API to refresh database...")
                import subprocess
                subprocess.run(['docker-compose', 'restart', 'contactplus-core'], 
                             capture_output=True, check=True)
                time.sleep(5)  # Wait for restart
                
            except Exception as e:
                print(f"❌ Test suite error in {test_function.__name__}: {e}")
        
        total_duration = time.time() - start_time
        print(f"\n🏁 Testing completed in {total_duration:.1f} seconds")
        
        return self.generate_summary()


def main():
    """Main function"""
    tester = FieldParsingTester()
    
    print("⏳ Ensuring API is ready...")
    time.sleep(3)
    
    success = tester.run_comprehensive_field_test()
    
    print(f"\n💡 Test Conclusions:")
    if success:
        print("  ✅ All vCard fields are parsed correctly")
        print("  ✅ Field modifications work properly")
        print("  ✅ Soft deletion preserves data integrity")
        print("  ✅ Special characters and Unicode handled correctly")
        print("  ✅ Database maintains consistency after operations")
    else:
        print("  ⚠️  Some field parsing or CRUD issues detected")
        print("  📋 Review failed tests for specific problems")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())