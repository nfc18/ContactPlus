#!/usr/bin/env python3
"""
macOS Contacts Bridge - Access native Contacts app data and compare with phonebook

🔒 CRITICAL: This module follows the MANDATORY phonebook editing protocol
when making any modifications to the master phonebook.
"""

import vobject
import json
from datetime import datetime
from collections import defaultdict
import re

try:
    import Contacts
    from Foundation import NSString
    PYOBJC_AVAILABLE = True
except ImportError:
    PYOBJC_AVAILABLE = False
    print("⚠️  PyObjC Contacts framework not available")

class MacOSContactsBridge:
    """Bridge between macOS Contacts app and our phonebook system"""
    
    def __init__(self):
        self.contact_store = None
        self.macos_contacts = []
        self.phonebook_contacts = []
        self.comparison_results = {}
        
        if PYOBJC_AVAILABLE:
            self.setup_contact_store()
        else:
            print("❌ PyObjC not available - install with: pip install pyobjc-framework-Contacts")
    
    def setup_contact_store(self):
        """Initialize the macOS Contacts store"""
        try:
            print("🔐 Requesting access to Contacts...")
            self.contact_store = Contacts.CNContactStore.alloc().init()
            
            # Request authorization
            auth_status = Contacts.CNContactStore.authorizationStatusForEntityType_(Contacts.CNEntityTypeContacts)
            
            if auth_status == Contacts.CNAuthorizationStatusNotDetermined:
                print("📱 Permission dialog will appear - please grant access to Contacts")
                # Note: In a real app, we'd use requestAccessForEntityType_completionHandler_
                # For CLI, we'll try to access and see if permission is granted
            
            elif auth_status == Contacts.CNAuthorizationStatusDenied:
                print("❌ Access to Contacts denied. Please enable in System Preferences > Privacy & Security > Contacts")
                return False
                
            elif auth_status == Contacts.CNAuthorizationStatusAuthorized:
                print("✅ Access to Contacts authorized")
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting up Contacts access: {e}")
            return False
    
    def fetch_macos_contacts(self):
        """Fetch all contacts from macOS Contacts app"""
        if not self.contact_store:
            print("❌ Contact store not available")
            return []
        
        try:
            print("📱 Fetching contacts from macOS Contacts app...")
            
            # Define which contact properties we want to fetch
            keys = [
                Contacts.CNContactGivenNameKey,
                Contacts.CNContactFamilyNameKey, 
                Contacts.CNContactEmailAddressesKey,
                Contacts.CNContactPhoneNumbersKey,
                Contacts.CNContactOrganizationNameKey,
                Contacts.CNContactJobTitleKey,
                Contacts.CNContactImageDataAvailableKey,
                Contacts.CNContactImageDataKey
            ]
            
            # Create fetch request
            fetch_request = Contacts.CNContactFetchRequest.alloc().initWithKeysToFetch_(keys)
            
            contacts = []
            
            def contact_handler(contact, stop):
                """Handler for each contact"""
                try:
                    contact_data = self.extract_contact_data(contact)
                    contacts.append(contact_data)
                except Exception as e:
                    print(f"⚠️  Error processing contact: {e}")
                return True  # Continue enumeration
            
            # Fetch all contacts
            success = self.contact_store.enumerateContactsWithFetchRequest_error_usingBlock_(
                fetch_request, None, contact_handler
            )
            
            if success:
                print(f"✅ Fetched {len(contacts)} contacts from macOS Contacts")
                self.macos_contacts = contacts
                return contacts
            else:
                print("❌ Failed to fetch contacts")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching contacts: {e}")
            if "NSCocoaErrorDomain" in str(e) and "100" in str(e):
                print("💡 This might be a permission issue. Check System Preferences > Privacy & Security > Contacts")
            return []
    
    def extract_contact_data(self, cn_contact):
        """Extract data from a CNContact object"""
        contact_data = {
            'identifier': str(cn_contact.identifier()) if cn_contact.identifier() else None,
            'given_name': str(cn_contact.givenName()) if cn_contact.givenName() else '',
            'family_name': str(cn_contact.familyName()) if cn_contact.familyName() else '',
            'full_name': '',
            'organization': str(cn_contact.organizationName()) if cn_contact.organizationName() else '',
            'job_title': str(cn_contact.jobTitle()) if cn_contact.jobTitle() else '',
            'emails': [],
            'phones': [],
            'has_image': bool(cn_contact.imageDataAvailable()),
            'image_data': None,
            'creation_date': None,
            'modification_date': None
        }
        
        # Build full name
        full_name_parts = []
        if contact_data['given_name']:
            full_name_parts.append(contact_data['given_name'])
        if contact_data['family_name']:
            full_name_parts.append(contact_data['family_name'])
        contact_data['full_name'] = ' '.join(full_name_parts) if full_name_parts else 'No Name'
        
        # Extract emails
        if cn_contact.emailAddresses():
            for email_entry in cn_contact.emailAddresses():
                email_value = str(email_entry.value())
                email_label = str(email_entry.label()) if email_entry.label() else 'other'
                contact_data['emails'].append({
                    'value': email_value.lower().strip(),
                    'label': email_label
                })
        
        # Extract phone numbers
        if cn_contact.phoneNumbers():
            for phone_entry in cn_contact.phoneNumbers():
                phone_value = str(phone_entry.value().stringValue())
                phone_label = str(phone_entry.label()) if phone_entry.label() else 'other'
                contact_data['phones'].append({
                    'value': phone_value.strip(),
                    'label': phone_label
                })
        
        # Extract image if available
        if contact_data['has_image'] and cn_contact.imageData():
            contact_data['image_data'] = cn_contact.imageData()
        
        return contact_data
    
    def load_phonebook_contacts(self):
        """Load contacts from our master phonebook"""
        import glob
        
        # Find latest phonebook
        phonebook_files = glob.glob("data/MASTER_PHONEBOOK_*.vcf")
        if not phonebook_files:
            phonebook_files = glob.glob("data/FINAL_MASTER_CONTACTS_*.vcf")
        
        if not phonebook_files:
            print("❌ No master phonebook found!")
            return []
        
        latest_phonebook = sorted(phonebook_files)[-1]
        print(f"📱 Loading phonebook: {latest_phonebook}")
        
        with open(latest_phonebook, 'r', encoding='utf-8') as f:
            vcards = list(vobject.readComponents(f.read()))
        
        contacts = []
        for i, vcard in enumerate(vcards):
            contact_data = {
                'index': i,
                'name': vcard.fn.value if hasattr(vcard, 'fn') and vcard.fn.value else f'Contact {i+1}',
                'organization': None,
                'emails': [],
                'phones': [],
                'has_photo': hasattr(vcard, 'photo')
            }
            
            # Organization
            if hasattr(vcard, 'org') and vcard.org.value:
                org = vcard.org.value
                if isinstance(org, list):
                    org = ' '.join(org)
                contact_data['organization'] = str(org).strip()
            
            # Emails
            if hasattr(vcard, 'email_list'):
                for email in vcard.email_list:
                    if email.value:
                        contact_data['emails'].append(email.value.lower().strip())
            
            # Phones
            if hasattr(vcard, 'tel_list'):
                for tel in vcard.tel_list:
                    if tel.value:
                        contact_data['phones'].append(tel.value.strip())
            
            contacts.append(contact_data)
        
        print(f"✅ Loaded {len(contacts)} contacts from phonebook")
        self.phonebook_contacts = contacts
        return contacts
    
    def normalize_phone(self, phone):
        """Normalize phone number for comparison"""
        if not phone:
            return None
        
        # Remove all non-digits except +
        cleaned = re.sub(r'[^\d+]', '', phone.strip())
        
        # Austrian number normalization
        if cleaned.startswith('0043'):
            cleaned = '+43' + cleaned[4:]
        elif cleaned.startswith('043'):
            cleaned = '+43' + cleaned[3:]
        elif cleaned.startswith('0') and len(cleaned) > 1:
            cleaned = '+43' + cleaned[1:]
        elif cleaned.startswith('43') and not cleaned.startswith('+'):
            cleaned = '+' + cleaned
        elif cleaned.startswith('1') and len(cleaned) == 11:
            cleaned = '+' + cleaned
        
        return cleaned
    
    def normalize_name(self, name):
        """Normalize name for comparison"""
        if not name:
            return ''
        return re.sub(r'[^\w\s]', '', name.lower().strip())
    
    def compare_contacts(self):
        """Compare macOS Contacts with phonebook contacts"""
        if not self.macos_contacts or not self.phonebook_contacts:
            print("❌ Need both macOS contacts and phonebook contacts loaded")
            return
        
        print("\n🔍 Comparing macOS Contacts with phonebook...")
        
        results = {
            'total_macos_contacts': len(self.macos_contacts),
            'total_phonebook_contacts': len(self.phonebook_contacts),
            'matches': [],
            'in_macos_only': [],
            'in_phonebook_only': [],
            'partial_matches': [],
            'data_differences': []
        }
        
        # Create lookup maps
        macos_by_email = defaultdict(list)
        macos_by_phone = defaultdict(list)
        macos_by_name = defaultdict(list)
        
        for contact in self.macos_contacts:
            # Index by email
            for email_info in contact['emails']:
                macos_by_email[email_info['value']].append(contact)
            
            # Index by phone
            for phone_info in contact['phones']:
                normalized_phone = self.normalize_phone(phone_info['value'])
                if normalized_phone:
                    macos_by_phone[normalized_phone].append(contact)
            
            # Index by name
            normalized_name = self.normalize_name(contact['full_name'])
            if normalized_name:
                macos_by_name[normalized_name].append(contact)
        
        # Compare each phonebook contact
        matched_macos_contacts = set()
        
        for pb_contact in self.phonebook_contacts:
            matches = []
            
            # Try to match by email
            for email in pb_contact['emails']:
                if email in macos_by_email:
                    for macos_contact in macos_by_email[email]:
                        matches.append(('email', email, macos_contact))
                        matched_macos_contacts.add(macos_contact['identifier'])
            
            # Try to match by phone
            for phone in pb_contact['phones']:
                normalized_phone = self.normalize_phone(phone)
                if normalized_phone and normalized_phone in macos_by_phone:
                    for macos_contact in macos_by_phone[normalized_phone]:
                        matches.append(('phone', normalized_phone, macos_contact))
                        matched_macos_contacts.add(macos_contact['identifier'])
            
            # Try to match by name
            normalized_name = self.normalize_name(pb_contact['name'])
            if normalized_name and normalized_name in macos_by_name:
                for macos_contact in macos_by_name[normalized_name]:
                    matches.append(('name', normalized_name, macos_contact))
                    matched_macos_contacts.add(macos_contact['identifier'])
            
            if matches:
                # Found matches - analyze the differences
                unique_matches = {}
                for match_type, match_value, macos_contact in matches:
                    unique_matches[macos_contact['identifier']] = (match_type, match_value, macos_contact)
                
                for identifier, (match_type, match_value, macos_contact) in unique_matches.items():
                    match_info = {
                        'phonebook_contact': pb_contact,
                        'macos_contact': macos_contact,
                        'match_type': match_type,
                        'match_value': match_value,
                        'differences': self.find_contact_differences(pb_contact, macos_contact)
                    }
                    
                    if match_info['differences']:
                        results['data_differences'].append(match_info)
                    else:
                        results['matches'].append(match_info)
            else:
                results['in_phonebook_only'].append(pb_contact)
        
        # Find contacts that are in macOS but not in phonebook
        for contact in self.macos_contacts:
            if contact['identifier'] not in matched_macos_contacts:
                results['in_macos_only'].append(contact)
        
        self.comparison_results = results
        self.print_comparison_summary(results)
        return results
    
    def find_contact_differences(self, pb_contact, macos_contact):
        """Find differences between phonebook and macOS contact"""
        differences = []
        
        # Compare emails
        pb_emails = set(pb_contact['emails'])
        macos_emails = set(email['value'] for email in macos_contact['emails'])
        
        if pb_emails != macos_emails:
            differences.append({
                'field': 'emails',
                'phonebook': list(pb_emails),
                'macos': list(macos_emails),
                'missing_in_phonebook': list(macos_emails - pb_emails),
                'missing_in_macos': list(pb_emails - macos_emails)
            })
        
        # Compare phones
        pb_phones = set(self.normalize_phone(p) for p in pb_contact['phones'] if self.normalize_phone(p))
        macos_phones = set(self.normalize_phone(p['value']) for p in macos_contact['phones'] if self.normalize_phone(p['value']))
        
        if pb_phones != macos_phones:
            differences.append({
                'field': 'phones',
                'phonebook': list(pb_phones),
                'macos': list(macos_phones),
                'missing_in_phonebook': list(macos_phones - pb_phones),
                'missing_in_macos': list(pb_phones - macos_phones)
            })
        
        # Compare organization
        pb_org = pb_contact.get('organization', '').strip()
        macos_org = macos_contact.get('organization', '').strip()
        
        if pb_org != macos_org and (pb_org or macos_org):
            differences.append({
                'field': 'organization',
                'phonebook': pb_org,
                'macos': macos_org
            })
        
        # Compare photos
        pb_has_photo = pb_contact.get('has_photo', False)
        macos_has_photo = macos_contact.get('has_image', False)
        
        if pb_has_photo != macos_has_photo:
            differences.append({
                'field': 'photo',
                'phonebook': pb_has_photo,
                'macos': macos_has_photo
            })
        
        return differences
    
    def print_comparison_summary(self, results):
        """Print summary of comparison results"""
        print("\n📊 COMPARISON SUMMARY")
        print("=" * 60)
        print(f"macOS Contacts: {results['total_macos_contacts']:,}")
        print(f"Phonebook Contacts: {results['total_phonebook_contacts']:,}")
        print(f"")
        print(f"✅ Perfect Matches: {len(results['matches'])}")
        print(f"🔄 Contacts with Differences: {len(results['data_differences'])}")
        print(f"📱 Only in macOS Contacts: {len(results['in_macos_only'])}")
        print(f"📓 Only in Phonebook: {len(results['in_phonebook_only'])}")
        
        # Show some examples
        if results['in_macos_only']:
            print(f"\n📱 EXAMPLES - Only in macOS Contacts:")
            for contact in results['in_macos_only'][:5]:
                emails = ', '.join(e['value'] for e in contact['emails'][:2])
                print(f"  • {contact['full_name']} ({emails})")
        
        if results['in_phonebook_only']:
            print(f"\n📓 EXAMPLES - Only in Phonebook:")
            for contact in results['in_phonebook_only'][:5]:
                emails = ', '.join(contact['emails'][:2])
                print(f"  • {contact['name']} ({emails})")
        
        if results['data_differences']:
            print(f"\n🔄 EXAMPLES - Data Differences:")
            for diff in results['data_differences'][:3]:
                print(f"  • {diff['phonebook_contact']['name']} <-> {diff['macos_contact']['full_name']}")
                for d in diff['differences'][:2]:
                    if d['field'] == 'emails' and d['missing_in_phonebook']:
                        print(f"    Missing emails in phonebook: {', '.join(d['missing_in_phonebook'])}")
                    elif d['field'] == 'phones' and d['missing_in_phonebook']:
                        print(f"    Missing phones in phonebook: {', '.join(d['missing_in_phonebook'])}")
    
    def save_comparison_report(self):
        """Save detailed comparison report"""
        if not self.comparison_results:
            print("❌ No comparison results to save")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = f"data/macos_contacts_comparison_{timestamp}.json"
        
        # Convert for JSON serialization
        serializable_results = {}
        for key, value in self.comparison_results.items():
            if key in ['matches', 'data_differences']:
                # These contain complex objects, convert to serializable format
                serializable_results[key] = []
                for item in value:
                    serializable_item = {
                        'phonebook_contact': item['phonebook_contact'],
                        'macos_contact': {
                            'full_name': item['macos_contact']['full_name'],
                            'organization': item['macos_contact']['organization'],
                            'emails': [e['value'] for e in item['macos_contact']['emails']],
                            'phones': [p['value'] for p in item['macos_contact']['phones']],
                            'has_image': item['macos_contact']['has_image']
                        },
                        'match_type': item['match_type'],
                        'match_value': item['match_value'],
                        'differences': item.get('differences', [])
                    }
                    serializable_results[key].append(serializable_item)
            else:
                serializable_results[key] = value
        
        with open(report_path, 'w') as f:
            json.dump(serializable_results, f, indent=2, default=str)
        
        print(f"📄 Comparison report saved: {report_path}")
        return report_path
    
    def run_full_analysis(self):
        """Run complete analysis comparing macOS Contacts with phonebook"""
        print("🔄 Starting macOS Contacts vs Phonebook Analysis")
        print("=" * 80)
        
        if not PYOBJC_AVAILABLE:
            print("❌ PyObjC framework not available")
            return None
        
        # Step 1: Load data
        print("\n1️⃣ Loading contacts from macOS Contacts app...")
        macos_contacts = self.fetch_macos_contacts()
        
        if not macos_contacts:
            print("❌ Could not access macOS Contacts")
            return None
        
        print("\n2️⃣ Loading contacts from master phonebook...")
        phonebook_contacts = self.load_phonebook_contacts()
        
        if not phonebook_contacts:
            print("❌ Could not load phonebook contacts")
            return None
        
        # Step 2: Compare
        print("\n3️⃣ Comparing contacts...")
        results = self.compare_contacts()
        
        # Step 3: Save report
        print("\n4️⃣ Saving comparison report...")
        report_path = self.save_comparison_report()
        
        print("\n✅ Analysis complete!")
        return results


def main():
    """Main function to run the bridge analysis"""
    
    if not PYOBJC_AVAILABLE:
        print("❌ PyObjC Contacts framework not installed")
        print("💡 Install with: pip install pyobjc-framework-Contacts")
        return
    
    bridge = MacOSContactsBridge()
    results = bridge.run_full_analysis()
    
    if results:
        print("\n🎯 Key Insights:")
        print(f"• {len(results['in_macos_only'])} contacts in macOS but missing from phonebook")
        print(f"• {len(results['data_differences'])} contacts have data differences")
        print(f"• {len(results['matches'])} contacts match perfectly")
        
        if results['in_macos_only']:
            print(f"\n💡 Consider adding the {len(results['in_macos_only'])} missing contacts to your phonebook")
        
        if results['data_differences']:
            print(f"💡 Consider updating {len(results['data_differences'])} contacts with fresh data from macOS")

if __name__ == "__main__":
    main()