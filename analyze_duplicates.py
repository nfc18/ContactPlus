#!/usr/bin/env python3
"""
Analyze the merged database for potential duplicates using various matching strategies
"""

import os
import re
from collections import defaultdict
import vobject
import phonenumbers
from difflib import SequenceMatcher
import json
from datetime import datetime

class DuplicateAnalyzer:
    """Analyze vCard database for potential duplicates"""
    
    def __init__(self):
        self.potential_duplicates = defaultdict(list)
        self.stats = {
            'total_contacts': 0,
            'exact_name_matches': 0,
            'similar_name_matches': 0,
            'email_matches': 0,
            'phone_matches': 0,
            'organization_matches': 0,
            'fuzzy_matches': 0
        }
    
    def normalize_name(self, name):
        """Normalize name for comparison"""
        if not name:
            return ""
        # Remove extra spaces, convert to lowercase
        name = re.sub(r'\s+', ' ', name.lower().strip())
        # Remove common titles
        titles = ['dr', 'mr', 'mrs', 'ms', 'prof', 'phd', 'md', 'esq', 'jr', 'sr', 'ii', 'iii']
        for title in titles:
            name = re.sub(rf'\b{title}\b\.?', '', name)
        return name.strip()
    
    def normalize_phone(self, phone_str):
        """Normalize phone number for comparison"""
        try:
            parsed = phonenumbers.parse(phone_str, 'US')
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except:
            pass
        # Fallback: just keep digits
        return re.sub(r'\D', '', phone_str)
    
    def normalize_email(self, email):
        """Normalize email for comparison"""
        return email.lower().strip()
    
    def name_similarity(self, name1, name2):
        """Calculate name similarity (0-1)"""
        if not name1 or not name2:
            return 0
        return SequenceMatcher(None, name1, name2).ratio()
    
    def extract_contact_features(self, vcard):
        """Extract all relevant features from a vCard for matching"""
        features = {
            'fn': '',
            'n_parts': [],
            'emails': [],
            'phones': [],
            'org': '',
            'urls': []
        }
        
        # Full name
        if hasattr(vcard, 'fn') and vcard.fn.value:
            features['fn'] = self.normalize_name(vcard.fn.value)
        
        # Name parts
        if hasattr(vcard, 'n') and vcard.n.value:
            n_value = vcard.n.value
            parts = []
            if n_value.given:
                parts.append(self.normalize_name(n_value.given))
            if n_value.family:
                parts.append(self.normalize_name(n_value.family))
            features['n_parts'] = parts
        
        # Emails
        if hasattr(vcard, 'email_list'):
            for email in vcard.email_list:
                if email.value:
                    features['emails'].append(self.normalize_email(email.value))
        
        # Phones
        if hasattr(vcard, 'tel_list'):
            for tel in vcard.tel_list:
                if tel.value:
                    normalized = self.normalize_phone(tel.value)
                    if normalized and len(normalized) >= 7:
                        features['phones'].append(normalized)
        
        # Organization
        if hasattr(vcard, 'org') and vcard.org.value:
            if isinstance(vcard.org.value, list):
                features['org'] = self.normalize_name(' '.join(vcard.org.value))
            else:
                features['org'] = self.normalize_name(str(vcard.org.value))
        
        # URLs
        if hasattr(vcard, 'url_list'):
            for url in vcard.url_list:
                if url.value:
                    features['urls'].append(url.value.lower())
        
        return features
    
    def find_duplicates(self, vcards):
        """Find potential duplicates in a list of vCards"""
        print(f"Analyzing {len(vcards)} contacts for duplicates...")
        self.stats['total_contacts'] = len(vcards)
        
        # Extract features for all contacts
        contacts = []
        for i, vcard in enumerate(vcards):
            features = self.extract_contact_features(vcard)
            contacts.append({
                'index': i,
                'vcard': vcard,
                'features': features
            })
        
        # Build indices for efficient matching
        email_index = defaultdict(list)
        phone_index = defaultdict(list)
        name_index = defaultdict(list)
        org_index = defaultdict(list)
        
        for contact in contacts:
            features = contact['features']
            
            # Index by email
            for email in features['emails']:
                email_index[email].append(contact)
            
            # Index by phone
            for phone in features['phones']:
                phone_index[phone].append(contact)
            
            # Index by name
            if features['fn']:
                name_index[features['fn']].append(contact)
            
            # Index by organization
            if features['org']:
                org_index[features['org']].append(contact)
        
        # Find duplicates
        duplicate_groups = []
        processed = set()
        
        for i, contact in enumerate(contacts):
            if i in processed:
                continue
            
            duplicate_group = [contact]
            processed.add(i)
            
            # Check exact matches
            features = contact['features']
            
            # Email matches
            for email in features['emails']:
                for match in email_index[email]:
                    if match['index'] != i and match['index'] not in processed:
                        duplicate_group.append(match)
                        processed.add(match['index'])
                        self.stats['email_matches'] += 1
            
            # Phone matches
            for phone in features['phones']:
                for match in phone_index[phone]:
                    if match['index'] != i and match['index'] not in processed:
                        duplicate_group.append(match)
                        processed.add(match['index'])
                        self.stats['phone_matches'] += 1
            
            # Exact name matches
            if features['fn']:
                for match in name_index[features['fn']]:
                    if match['index'] != i and match['index'] not in processed:
                        duplicate_group.append(match)
                        processed.add(match['index'])
                        self.stats['exact_name_matches'] += 1
            
            # Fuzzy name matching for remaining contacts
            if len(duplicate_group) == 1 and features['fn']:
                for j, other in enumerate(contacts):
                    if j <= i or j in processed:
                        continue
                    
                    other_features = other['features']
                    
                    # Check name similarity
                    if other_features['fn']:
                        similarity = self.name_similarity(features['fn'], other_features['fn'])
                        if similarity > 0.85:  # High similarity threshold
                            # Additional checks
                            has_common_data = False
                            
                            # Check if they share any email domain
                            if features['emails'] and other_features['emails']:
                                domains1 = {e.split('@')[1] for e in features['emails'] if '@' in e}
                                domains2 = {e.split('@')[1] for e in other_features['emails'] if '@' in e}
                                if domains1 & domains2:
                                    has_common_data = True
                            
                            # Check if they share organization
                            if features['org'] and other_features['org']:
                                if self.name_similarity(features['org'], other_features['org']) > 0.8:
                                    has_common_data = True
                            
                            # Check if phone numbers are similar (last 7 digits)
                            if features['phones'] and other_features['phones']:
                                for p1 in features['phones']:
                                    for p2 in other_features['phones']:
                                        if len(p1) >= 7 and len(p2) >= 7:
                                            if p1[-7:] == p2[-7:]:
                                                has_common_data = True
                            
                            if has_common_data or similarity > 0.95:
                                duplicate_group.append(other)
                                processed.add(j)
                                self.stats['fuzzy_matches'] += 1
            
            if len(duplicate_group) > 1:
                duplicate_groups.append(duplicate_group)
        
        return duplicate_groups
    
    def analyze_file(self, filepath):
        """Analyze a vCard file for duplicates"""
        print(f"\nDuplicate Analysis for: {filepath}")
        print("=" * 80)
        
        # Load vCards
        with open(filepath, 'r', encoding='utf-8') as f:
            vcards = list(vobject.readComponents(f.read()))
        
        # Find duplicates
        duplicate_groups = self.find_duplicates(vcards)
        
        # Generate report
        print(f"\n📊 ANALYSIS RESULTS")
        print(f"Total contacts: {self.stats['total_contacts']}")
        print(f"Duplicate groups found: {len(duplicate_groups)}")
        print(f"Total duplicate contacts: {sum(len(g) for g in duplicate_groups)}")
        
        print(f"\n📈 MATCH TYPES:")
        print(f"  Exact name matches: {self.stats['exact_name_matches']}")
        print(f"  Email matches: {self.stats['email_matches']}")
        print(f"  Phone matches: {self.stats['phone_matches']}")
        print(f"  Fuzzy name matches: {self.stats['fuzzy_matches']}")
        
        # Show sample duplicates
        if duplicate_groups:
            print(f"\n🔍 SAMPLE DUPLICATE GROUPS (first 10):")
            for i, group in enumerate(duplicate_groups[:10]):
                print(f"\nGroup {i+1} ({len(group)} contacts):")
                for contact in group:
                    vcard = contact['vcard']
                    features = contact['features']
                    name = vcard.fn.value if hasattr(vcard, 'fn') else "No name"
                    emails = ', '.join(features['emails'][:2]) if features['emails'] else "No email"
                    phones = ', '.join(features['phones'][:2]) if features['phones'] else "No phone"
                    org = features['org'] if features['org'] else "No org"
                    
                    print(f"  - {name}")
                    if emails != "No email":
                        print(f"    Email: {emails}")
                    if phones != "No phone":
                        print(f"    Phone: {phones}")
                    if org != "No org":
                        print(f"    Org: {org}")
        
        # Save detailed report
        report = {
            'analysis_date': datetime.now().isoformat(),
            'file': filepath,
            'stats': self.stats,
            'duplicate_groups': []
        }
        
        for group in duplicate_groups:
            group_data = []
            for contact in group:
                vcard = contact['vcard']
                features = contact['features']
                group_data.append({
                    'name': vcard.fn.value if hasattr(vcard, 'fn') else None,
                    'emails': features['emails'],
                    'phones': features['phones'],
                    'org': features['org']
                })
            report['duplicate_groups'].append(group_data)
        
        report_path = f"data/duplicate_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_path}")
        
        return duplicate_groups


def main():
    """Analyze the merged database for duplicates"""
    
    # Use the most recent merged file
    merged_file = "data/MERGED_All_Contacts_20250606_123737.vcf"
    
    if not os.path.exists(merged_file):
        print(f"Error: Merged file not found: {merged_file}")
        return
    
    analyzer = DuplicateAnalyzer()
    duplicate_groups = analyzer.analyze_file(merged_file)
    
    if duplicate_groups:
        print(f"\n⚠️  Found {len(duplicate_groups)} groups of potential duplicates")
        print("Next step: Run 'python3 advanced_deduplication.py' to clean these up")
    else:
        print("\n✅ No additional duplicates found!")


if __name__ == "__main__":
    main()