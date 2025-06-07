#!/usr/bin/env python3
"""
Enhanced macOS Contacts Bridge - Access ALL contact sources (iCloud + local)
"""

import vobject
import json
from datetime import datetime
from collections import defaultdict
import re

try:
    import Contacts
    from Foundation import NSString, NSPredicate
    PYOBJC_AVAILABLE = True
except ImportError:
    PYOBJC_AVAILABLE = False

class EnhancedContactsBridge:
    """Enhanced bridge to access ALL contact sources (iCloud, Exchange, local, etc.)"""
    
    def __init__(self):
        self.contact_store = None
        self.all_contacts = []
        self.phonebook_contacts = []
        self.containers = []
        
        if PYOBJC_AVAILABLE:
            self.setup_contact_store()
    
    def setup_contact_store(self):
        """Initialize contact store and check all containers"""
        try:
            print("🔐 Setting up enhanced Contacts access...")
            self.contact_store = Contacts.CNContactStore.alloc().init()
            
            # Check authorization
            auth_status = Contacts.CNContactStore.authorizationStatusForEntityType_(Contacts.CNEntityTypeContacts)
            if auth_status != Contacts.CNAuthorizationStatusAuthorized:
                print("❌ Contacts access not authorized")
                return False
            
            # Discover all containers (iCloud, Exchange, local, etc.)
            self.discover_containers()
            return True
            
        except Exception as e:
            print(f"❌ Error setting up contacts: {e}")
            return False
    
    def discover_containers(self):
        """Discover all contact containers (iCloud, local, Exchange, etc.)"""
        try:
            print("📦 Discovering contact containers...")
            
            # Get all containers
            containers = self.contact_store.containersMatchingPredicate_error_(None, None)
            
            self.containers = []
            for container in containers:
                try:
                    container_info = {
                        'identifier': str(container.identifier()),
                        'name': str(container.name()) if hasattr(container, 'name') and container.name() else 'Unknown',
                        'type': container.type(),
                        'object': container
                    }
                    
                    # Map container types to readable names
                    type_names = {
                        0: 'Unassigned',
                        1: 'Local',
                        2: 'Exchange', 
                        3: 'CardDAV'  # This includes iCloud
                    }
                    container_info['type_name'] = type_names.get(container_info['type'], f'Unknown ({container_info["type"]})')
                    
                    self.containers.append(container_info)
                    print(f"   📁 {container_info['name']} ({container_info['type_name']})")
                    
                except Exception as e:
                    print(f"   ⚠️  Error processing container: {e}")
            
            print(f"✅ Found {len(self.containers)} containers")
            return self.containers
            
        except Exception as e:
            print(f"❌ Error discovering containers: {e}")
            return []
    
    def fetch_contacts_from_all_sources(self):
        """Fetch contacts from ALL sources (iCloud, local, Exchange, etc.)"""
        if not self.contact_store:
            return []
        
        print("📱 Fetching contacts from ALL sources...")
        
        # Define contact keys to fetch
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
        
        all_contacts = []
        
        # Method 1: Fetch from all containers
        for container in self.containers:
            try:
                print(f"   📂 Fetching from {container['name']} ({container['type_name']})...")
                
                # Create predicate for this container
                predicate = Contacts.CNContact.predicateForContactsInContainerWithIdentifier_(
                    container['identifier']
                )
                
                container_contacts = self.contact_store.unifiedContactsMatchingPredicate_keysToFetch_error_(
                    predicate, keys, None
                )
                
                if container_contacts:
                    for contact in container_contacts:
                        contact_data = self.extract_contact_data(contact)
                        contact_data['source_container'] = container['name']
                        contact_data['source_type'] = container['type_name']
                        all_contacts.append(contact_data)
                    
                    print(f"      ✅ {len(container_contacts)} contacts")
                else:
                    print(f"      📭 No contacts")
                    
            except Exception as e:
                print(f"      ❌ Error fetching from {container['name']}: {e}")
        
        # Method 2: Fallback - fetch ALL contacts without container filtering
        if not all_contacts:
            print("   🔄 Fallback: Fetching all contacts without container filtering...")
            try:
                fetch_request = Contacts.CNContactFetchRequest.alloc().initWithKeysToFetch_(keys)
                
                def contact_handler(contact, stop):
                    contact_data = self.extract_contact_data(contact)
                    contact_data['source_container'] = 'All Sources'
                    contact_data['source_type'] = 'Mixed'
                    all_contacts.append(contact_data)
                    return True
                
                self.contact_store.enumerateContactsWithFetchRequest_error_usingBlock_(
                    fetch_request, None, contact_handler
                )
                
            except Exception as e:
                print(f"      ❌ Fallback method failed: {e}")
        
        print(f"✅ Total contacts fetched: {len(all_contacts)}")
        self.all_contacts = all_contacts
        return all_contacts
    
    def extract_contact_data(self, cn_contact):
        """Extract data from CNContact object"""
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
            'source_container': 'Unknown',
            'source_type': 'Unknown'
        }
        
        # Build full name
        parts = []
        if contact_data['given_name']:
            parts.append(contact_data['given_name'])
        if contact_data['family_name']:
            parts.append(contact_data['family_name'])
        contact_data['full_name'] = ' '.join(parts) if parts else 'No Name'
        
        # Extract emails
        if cn_contact.emailAddresses():
            for email_entry in cn_contact.emailAddresses():
                email_value = str(email_entry.value()).lower().strip()
                contact_data['emails'].append(email_value)
        
        # Extract phones
        if cn_contact.phoneNumbers():
            for phone_entry in cn_contact.phoneNumbers():
                phone_value = str(phone_entry.value().stringValue()).strip()
                contact_data['phones'].append(phone_value)
        
        return contact_data
    
    def load_phonebook_contacts(self):
        """Load our master phonebook"""
        import glob
        
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
                'organization': '',
                'emails': [],
                'phones': []
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
        
        print(f"✅ Loaded {len(contacts)} phonebook contacts")
        self.phonebook_contacts = contacts
        return contacts
    
    def compare_all_contacts(self):
        """Compare ALL macOS contacts with phonebook"""
        print("\n🔍 Comparing ALL macOS contacts with phonebook...")
        
        results = {
            'total_macos_contacts': len(self.all_contacts),
            'total_phonebook_contacts': len(self.phonebook_contacts),
            'by_container': {},
            'perfect_matches': [],
            'partial_matches': [],
            'in_macos_only': [],
            'in_phonebook_only': [],
            'data_differences': []
        }
        
        # Analyze by container
        container_stats = defaultdict(int)
        for contact in self.all_contacts:
            container_stats[contact['source_container']] += 1
        
        results['by_container'] = dict(container_stats)
        
        # Create lookup maps for matching
        macos_by_email = defaultdict(list)
        macos_by_name = defaultdict(list)
        
        for contact in self.all_contacts:
            # Index by email
            for email in contact['emails']:
                macos_by_email[email].append(contact)
            
            # Index by normalized name
            normalized_name = re.sub(r'[^\w\s]', '', contact['full_name'].lower().strip())
            if normalized_name:
                macos_by_name[normalized_name].append(contact)
        
        # Find matches
        matched_macos_ids = set()
        
        for pb_contact in self.phonebook_contacts:
            matches = []
            
            # Try email matching
            for email in pb_contact['emails']:
                if email in macos_by_email:
                    for macos_contact in macos_by_email[email]:
                        matches.append(('email', email, macos_contact))
                        matched_macos_ids.add(macos_contact['identifier'])
            
            # Try name matching
            pb_normalized = re.sub(r'[^\w\s]', '', pb_contact['name'].lower().strip())
            if pb_normalized and pb_normalized in macos_by_name:
                for macos_contact in macos_by_name[pb_normalized]:
                    matches.append(('name', pb_normalized, macos_contact))
                    matched_macos_ids.add(macos_contact['identifier'])
            
            if matches:
                # Deduplicate matches by contact ID
                unique_matches = {}
                for match_type, match_value, macos_contact in matches:
                    unique_matches[macos_contact['identifier']] = (match_type, match_value, macos_contact)
                
                for contact_id, (match_type, match_value, macos_contact) in unique_matches.items():
                    # Check for differences
                    differences = self.find_differences(pb_contact, macos_contact)
                    
                    match_info = {
                        'phonebook_contact': pb_contact,
                        'macos_contact': macos_contact,
                        'match_type': match_type,
                        'match_value': match_value,
                        'differences': differences
                    }
                    
                    if differences:
                        results['data_differences'].append(match_info)
                    else:
                        results['perfect_matches'].append(match_info)
            else:
                results['in_phonebook_only'].append(pb_contact)
        
        # Find macOS-only contacts
        for contact in self.all_contacts:
            if contact['identifier'] not in matched_macos_ids:
                results['in_macos_only'].append(contact)
        
        self.print_enhanced_summary(results)
        return results
    
    def find_differences(self, pb_contact, macos_contact):
        """Find differences between contacts"""
        differences = []
        
        # Email differences
        pb_emails = set(pb_contact['emails'])
        macos_emails = set(macos_contact['emails'])
        
        if pb_emails != macos_emails:
            differences.append({
                'field': 'emails',
                'phonebook_only': list(pb_emails - macos_emails),
                'macos_only': list(macos_emails - pb_emails)
            })
        
        # Phone differences (simplified)
        pb_phones = set(pb_contact['phones'])
        macos_phones = set(macos_contact['phones'])
        
        if pb_phones != macos_phones:
            differences.append({
                'field': 'phones',
                'phonebook_only': list(pb_phones - macos_phones),
                'macos_only': list(macos_phones - pb_phones)
            })
        
        return differences
    
    def print_enhanced_summary(self, results):
        """Print enhanced comparison summary"""
        print("\n📊 ENHANCED COMPARISON SUMMARY")
        print("=" * 70)
        print(f"macOS Contacts (ALL sources): {results['total_macos_contacts']:,}")
        print(f"Phonebook Contacts: {results['total_phonebook_contacts']:,}")
        
        print(f"\n📂 By Container:")
        for container, count in results['by_container'].items():
            print(f"   {container}: {count:,} contacts")
        
        print(f"\n🎯 Matching Results:")
        print(f"   ✅ Perfect Matches: {len(results['perfect_matches'])}")
        print(f"   🔄 Data Differences: {len(results['data_differences'])}")
        print(f"   📱 Only in macOS: {len(results['in_macos_only'])}")
        print(f"   📓 Only in Phonebook: {len(results['in_phonebook_only'])}")
        
        # Show coverage
        total_unique = (len(results['perfect_matches']) + len(results['data_differences']) + 
                       len(results['in_macos_only']) + len(results['in_phonebook_only']))
        match_rate = ((len(results['perfect_matches']) + len(results['data_differences'])) / 
                     results['total_phonebook_contacts'] * 100) if results['total_phonebook_contacts'] > 0 else 0
        
        print(f"\n📈 Coverage:")
        print(f"   Match Rate: {match_rate:.1f}% of phonebook contacts found in macOS")
        print(f"   Total Unique Contacts: {total_unique:,}")
    
    def run_enhanced_analysis(self):
        """Run complete enhanced analysis"""
        print("🔄 ENHANCED CONTACTS ANALYSIS")
        print("=" * 80)
        
        if not PYOBJC_AVAILABLE:
            print("❌ PyObjC not available")
            return None
        
        # Step 1: Fetch from all sources
        print("\n1️⃣ Fetching from ALL contact sources...")
        macos_contacts = self.fetch_contacts_from_all_sources()
        
        # Step 2: Load phonebook
        print("\n2️⃣ Loading master phonebook...")
        phonebook_contacts = self.load_phonebook_contacts()
        
        # Step 3: Compare
        print("\n3️⃣ Comparing all contacts...")
        results = self.compare_all_contacts()
        
        # Step 4: Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = f"data/enhanced_contacts_comparison_{timestamp}.json"
        
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Report saved: {report_path}")
        print("✅ Enhanced analysis complete!")
        
        return results

def main():
    bridge = EnhancedContactsBridge()
    results = bridge.run_enhanced_analysis()
    
    if results:
        print(f"\n💡 Key Discovery:")
        if results['total_macos_contacts'] > 1:
            print(f"   Found {results['total_macos_contacts']} contacts in macOS (including iCloud)")
            print(f"   Your phonebook has {results['total_phonebook_contacts']} contacts")
            
            match_rate = ((len(results['perfect_matches']) + len(results['data_differences'])) / 
                         results['total_phonebook_contacts'] * 100)
            print(f"   {match_rate:.1f}% of your phonebook contacts are already in macOS")
        else:
            print("   macOS Contacts access may be limited")

if __name__ == "__main__":
    main()