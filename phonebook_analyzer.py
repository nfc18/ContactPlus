#!/usr/bin/env python3
"""
Comprehensive Phonebook Analysis System
Analyzes the master phonebook for statistics, data quality, and insights
"""

import vobject
import json
import re
from datetime import datetime
from collections import defaultdict, Counter
from urllib.parse import urlparse
import os

class PhonebookAnalyzer:
    """Comprehensive analysis of the master phonebook"""
    
    def __init__(self, phonebook_path):
        self.phonebook_path = phonebook_path
        self.contacts = []
        self.analysis_results = {}
        self.load_phonebook()
    
    def load_phonebook(self):
        """Load and parse the phonebook"""
        print(f"Loading phonebook: {os.path.basename(self.phonebook_path)}")
        
        with open(self.phonebook_path, 'r', encoding='utf-8') as f:
            self.contacts = list(vobject.readComponents(f.read()))
        
        print(f"✓ Loaded {len(self.contacts)} contacts")
    
    def analyze_basic_statistics(self):
        """Basic contact statistics"""
        stats = {
            'total_contacts': len(self.contacts),
            'with_email': 0,
            'with_phone': 0,
            'with_organization': 0,
            'with_all_fields': 0,
            'missing_fn': 0,
            'missing_n': 0,
            'total_emails': 0,
            'total_phones': 0
        }
        
        for contact in self.contacts:
            has_email = hasattr(contact, 'email_list') and contact.email_list
            has_phone = hasattr(contact, 'tel_list') and contact.tel_list  
            has_org = hasattr(contact, 'org') and contact.org.value
            
            if has_email:
                stats['with_email'] += 1
                stats['total_emails'] += len(contact.email_list)
            
            if has_phone:
                stats['with_phone'] += 1
                stats['total_phones'] += len(contact.tel_list)
            
            if has_org:
                stats['with_organization'] += 1
            
            if has_email and has_phone and has_org:
                stats['with_all_fields'] += 1
            
            if not hasattr(contact, 'fn') or not contact.fn.value:
                stats['missing_fn'] += 1
            
            if not hasattr(contact, 'n'):
                stats['missing_n'] += 1
        
        # Calculate percentages
        total = stats['total_contacts']
        stats['email_percentage'] = round((stats['with_email'] / total) * 100, 1)
        stats['phone_percentage'] = round((stats['with_phone'] / total) * 100, 1) 
        stats['organization_percentage'] = round((stats['with_organization'] / total) * 100, 1)
        stats['complete_percentage'] = round((stats['with_all_fields'] / total) * 100, 1)
        
        self.analysis_results['basic_statistics'] = stats
        return stats
    
    def analyze_emails(self):
        """Detailed email analysis"""
        email_data = {
            'domains': Counter(),
            'multi_email_contacts': [],
            'email_formats': {'valid': 0, 'invalid': 0},
            'domain_categories': {
                'personal': Counter(),
                'corporate': Counter(), 
                'anyline': Counter(),
                'other': Counter()
            },
            'top_domains': [],
            'unique_emails': set()
        }
        
        email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        personal_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 
                           'icloud.com', 'me.com', 'googlemail.com', 'web.de', 'gmx.at']
        
        for contact in self.contacts:
            if hasattr(contact, 'email_list') and contact.email_list:
                contact_emails = []
                
                for email in contact.email_list:
                    if email.value:
                        email_addr = email.value.lower().strip()
                        contact_emails.append(email_addr)
                        email_data['unique_emails'].add(email_addr)
                        
                        # Domain analysis
                        domain = email_addr.split('@')[1] if '@' in email_addr else 'invalid'
                        email_data['domains'][domain] += 1
                        
                        # Format validation
                        if email_regex.match(email_addr):
                            email_data['email_formats']['valid'] += 1
                        else:
                            email_data['email_formats']['invalid'] += 1
                        
                        # Categorize domains
                        if domain in personal_domains:
                            email_data['domain_categories']['personal'][domain] += 1
                        elif 'anyline' in domain:
                            email_data['domain_categories']['anyline'][domain] += 1
                        elif domain != 'invalid':
                            # Simple heuristic for corporate vs other
                            if len(domain.split('.')) >= 2:
                                email_data['domain_categories']['corporate'][domain] += 1
                            else:
                                email_data['domain_categories']['other'][domain] += 1
                
                # Track multi-email contacts
                if len(contact_emails) > 1:
                    name = contact.fn.value if hasattr(contact, 'fn') else 'No name'
                    email_data['multi_email_contacts'].append({
                        'name': name,
                        'email_count': len(contact_emails),
                        'emails': contact_emails
                    })
        
        # Top domains
        email_data['top_domains'] = email_data['domains'].most_common(20)
        email_data['unique_email_count'] = len(email_data['unique_emails'])
        
        # Remove the set for JSON serialization
        del email_data['unique_emails']
        
        self.analysis_results['email_analysis'] = email_data
        return email_data
    
    def analyze_phones(self):
        """Detailed phone number analysis"""
        phone_data = {
            'country_codes': Counter(),
            'area_codes': Counter(),
            'formats': Counter(),
            'multi_phone_contacts': [],
            'phone_types': {'mobile': 0, 'landline': 0, 'unknown': 0},
            'unique_phones': set(),
            'formatting_issues': []
        }
        
        for contact in self.contacts:
            if hasattr(contact, 'tel_list') and contact.tel_list:
                contact_phones = []
                
                for tel in contact.tel_list:
                    if tel.value:
                        phone = tel.value.strip()
                        contact_phones.append(phone)
                        phone_data['unique_phones'].add(phone)
                        
                        # Normalize and analyze
                        normalized = re.sub(r'[\s\-\(\)]', '', phone)
                        
                        # Country code detection
                        if normalized.startswith('+43'):
                            phone_data['country_codes']['Austria (+43)'] += 1
                            # Area code for Austria
                            if len(normalized) >= 6:
                                area = normalized[3:6] if normalized[3:4] in '679' else normalized[3:5]
                                phone_data['area_codes'][f'+43-{area}'] += 1
                            
                            # Mobile vs landline (Austria)
                            if normalized[3:4] in '67':
                                phone_data['phone_types']['mobile'] += 1
                            else:
                                phone_data['phone_types']['landline'] += 1
                                
                        elif normalized.startswith('+1'):
                            phone_data['country_codes']['US/Canada (+1)'] += 1
                            phone_data['phone_types']['mobile'] += 1  # Assume mobile for +1
                            
                        elif normalized.startswith('+'):
                            country = normalized[:3] if len(normalized) > 3 else normalized
                            phone_data['country_codes'][f'Other ({country})'] += 1
                            phone_data['phone_types']['unknown'] += 1
                            
                        else:
                            phone_data['country_codes']['No country code'] += 1
                            phone_data['phone_types']['unknown'] += 1
                        
                        # Format analysis
                        if '+' in phone and '(' not in phone and '-' not in phone:
                            phone_data['formats']['International (+XX...)'] += 1
                        elif '(' in phone and ')' in phone:
                            phone_data['formats']['Parentheses format'] += 1
                        elif '-' in phone:
                            phone_data['formats']['Dash format'] += 1
                        elif ' ' in phone:
                            phone_data['formats']['Space separated'] += 1
                        else:
                            phone_data['formats']['No formatting'] += 1
                        
                        # Check for formatting issues
                        if len(normalized) < 7 or len(normalized) > 15:
                            phone_data['formatting_issues'].append({
                                'phone': phone,
                                'issue': 'Invalid length'
                            })
                
                # Track multi-phone contacts
                if len(contact_phones) > 1:
                    name = contact.fn.value if hasattr(contact, 'fn') else 'No name'
                    phone_data['multi_phone_contacts'].append({
                        'name': name,
                        'phone_count': len(contact_phones),
                        'phones': contact_phones
                    })
        
        phone_data['unique_phone_count'] = len(phone_data['unique_phones'])
        phone_data['top_country_codes'] = phone_data['country_codes'].most_common(10)
        phone_data['top_area_codes'] = phone_data['area_codes'].most_common(15)
        
        # Remove set for JSON serialization
        del phone_data['unique_phones']
        
        self.analysis_results['phone_analysis'] = phone_data
        return phone_data
    
    def analyze_organizations(self):
        """Organization and company analysis"""
        org_data = {
            'organizations': Counter(),
            'normalized_orgs': Counter(),
            'org_variations': defaultdict(list),
            'top_organizations': [],
            'contacts_with_orgs': 0,
            'unique_org_count': 0,
            'industry_keywords': Counter()
        }
        
        industry_keywords = [
            'gmbh', 'ag', 'ltd', 'llc', 'inc', 'corp', 'university', 'tech', 
            'software', 'consulting', 'group', 'media', 'design', 'development'
        ]
        
        for contact in self.contacts:
            if hasattr(contact, 'org') and contact.org.value:
                org_data['contacts_with_orgs'] += 1
                
                org_name = contact.org.value
                if isinstance(org_name, list):
                    org_name = ' '.join(org_name)
                
                org_name = str(org_name).strip()
                org_data['organizations'][org_name] += 1
                
                # Normalize for variation detection
                normalized = re.sub(r'[^\w\s]', '', org_name.lower())
                normalized = re.sub(r'\s+', ' ', normalized).strip()
                org_data['normalized_orgs'][normalized] += 1
                org_data['org_variations'][normalized].append(org_name)
                
                # Industry keyword analysis
                for keyword in industry_keywords:
                    if keyword in normalized:
                        org_data['industry_keywords'][keyword] += 1
        
        org_data['top_organizations'] = org_data['organizations'].most_common(20)
        org_data['unique_org_count'] = len(org_data['organizations'])
        
        # Find organization variations
        variations = {}
        for norm_org, variations_list in org_data['org_variations'].items():
            if len(set(variations_list)) > 1:  # Multiple variations
                variations[norm_org] = list(set(variations_list))
        
        org_data['organization_variations'] = dict(list(variations.items())[:10])
        
        self.analysis_results['organization_analysis'] = org_data
        return org_data
    
    def analyze_data_quality(self):
        """Data quality assessment"""
        quality_data = {
            'vcard_compliance': {'valid': 0, 'warnings': 0, 'errors': 0},
            'empty_fields': Counter(),
            'placeholder_patterns': [],
            'name_formatting': {'consistent': 0, 'inconsistent': 0},
            'potential_duplicates': [],
            'data_completeness_score': 0
        }
        
        placeholder_patterns = ['contact', 'unknown', 'test', 'no name', '+43', '@']
        
        name_variations = defaultdict(list)
        
        for i, contact in enumerate(self.contacts):
            # Name formatting analysis
            if hasattr(contact, 'fn') and contact.fn.value:
                name = contact.fn.value.strip()
                
                # Check for placeholder patterns
                for pattern in placeholder_patterns:
                    if pattern.lower() in name.lower():
                        quality_data['placeholder_patterns'].append({
                            'contact_index': i,
                            'name': name,
                            'pattern': pattern
                        })
                
                # Name consistency (basic check)
                normalized_name = re.sub(r'[^\w\s]', '', name.lower())
                if normalized_name:
                    name_variations[normalized_name].append((i, name))
            else:
                quality_data['empty_fields']['name'] += 1
            
            # Check for empty critical fields
            if not hasattr(contact, 'email_list') or not contact.email_list:
                quality_data['empty_fields']['email'] += 1
            
            if not hasattr(contact, 'tel_list') or not contact.tel_list:
                quality_data['empty_fields']['phone'] += 1
            
            if not hasattr(contact, 'org') or not contact.org.value:
                quality_data['empty_fields']['organization'] += 1
        
        # Find potential name duplicates
        for norm_name, variations in name_variations.items():
            if len(variations) > 1:
                # Check if they're actually different contacts
                names = [v[1] for v in variations]
                if len(set(names)) > 1:
                    quality_data['potential_duplicates'].append({
                        'normalized_name': norm_name,
                        'variations': names[:5]  # Limit to first 5
                    })
        
        # Calculate data completeness score
        total_contacts = len(self.contacts)
        if total_contacts > 0:
            basic_stats = self.analysis_results.get('basic_statistics', {})
            completeness = (
                basic_stats.get('with_email', 0) * 0.4 +
                basic_stats.get('with_phone', 0) * 0.4 +
                basic_stats.get('with_organization', 0) * 0.2
            ) / total_contacts
            quality_data['data_completeness_score'] = round(completeness * 100, 1)
        
        self.analysis_results['data_quality'] = quality_data
        return quality_data
    
    def generate_summary(self):
        """Generate human-readable summary"""
        basic = self.analysis_results.get('basic_statistics', {})
        emails = self.analysis_results.get('email_analysis', {})
        phones = self.analysis_results.get('phone_analysis', {})
        orgs = self.analysis_results.get('organization_analysis', {})
        quality = self.analysis_results.get('data_quality', {})
        
        summary = f"""
📱 PHONEBOOK ANALYSIS SUMMARY
{'='*60}

📊 BASIC STATISTICS
• Total Contacts: {basic.get('total_contacts', 0):,}
• With Email: {basic.get('with_email', 0):,} ({basic.get('email_percentage', 0)}%)
• With Phone: {basic.get('with_phone', 0):,} ({basic.get('phone_percentage', 0)}%)
• With Organization: {basic.get('with_organization', 0):,} ({basic.get('organization_percentage', 0)}%)
• Complete Profiles: {basic.get('with_all_fields', 0):,} ({basic.get('complete_percentage', 0)}%)

📧 EMAIL ANALYSIS
• Unique Emails: {emails.get('unique_email_count', 0):,}
• Top Domains: {', '.join([f"{d[0]} ({d[1]})" for d in emails.get('top_domains', [])[:5]])}
• Multi-email Contacts: {len(emails.get('multi_email_contacts', []))}
• Personal Domains: {sum(emails.get('domain_categories', {}).get('personal', {}).values())}
• Corporate Domains: {sum(emails.get('domain_categories', {}).get('corporate', {}).values())}
• Anyline Domains: {sum(emails.get('domain_categories', {}).get('anyline', {}).values())}

📞 PHONE ANALYSIS  
• Unique Numbers: {phones.get('unique_phone_count', 0):,}
• Austrian Numbers: {phones.get('country_codes', {}).get('Austria (+43)', 0)}
• US/Canada Numbers: {phones.get('country_codes', {}).get('US/Canada (+1)', 0)}
• Mobile Numbers: {phones.get('phone_types', {}).get('mobile', 0)}
• Multi-phone Contacts: {len(phones.get('multi_phone_contacts', []))}

🏢 ORGANIZATION ANALYSIS
• Unique Organizations: {orgs.get('unique_org_count', 0):,}
• Contacts with Orgs: {orgs.get('contacts_with_orgs', 0):,}
• Top Organizations: {', '.join([f"{org[0]} ({org[1]})" for org in orgs.get('top_organizations', [])[:3]])}

🔍 DATA QUALITY
• Completeness Score: {quality.get('data_completeness_score', 0)}%
• Placeholder Entries: {len(quality.get('placeholder_patterns', []))}
• Potential Duplicates: {len(quality.get('potential_duplicates', []))}
• Empty Names: {quality.get('empty_fields', {}).get('name', 0)}
"""
        
        return summary
    
    def run_complete_analysis(self):
        """Run all analysis modules"""
        print("\nRunning Comprehensive Phonebook Analysis...")
        print("=" * 60)
        
        print("📊 Analyzing basic statistics...")
        self.analyze_basic_statistics()
        
        print("📧 Analyzing email data...")
        self.analyze_emails()
        
        print("📞 Analyzing phone numbers...")
        self.analyze_phones()
        
        print("🏢 Analyzing organizations...")
        self.analyze_organizations()
        
        print("🔍 Assessing data quality...")
        self.analyze_data_quality()
        
        # Add metadata
        self.analysis_results['metadata'] = {
            'analysis_date': datetime.now().isoformat(),
            'phonebook_file': self.phonebook_path,
            'analyzer_version': '1.0.0'
        }
        
        # Generate summary
        summary = self.generate_summary()
        
        # Save detailed results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"data/phonebook_analysis_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.analysis_results, f, indent=2, default=str)
        
        print(f"\n✅ Analysis complete!")
        print(f"📄 Detailed results saved to: {results_file}")
        print(summary)
        
        return self.analysis_results, summary

def main():
    """Main analysis function"""
    
    # Find the latest master phonebook
    import glob
    phonebook_files = glob.glob("data/MASTER_PHONEBOOK_*.vcf")
    
    if not phonebook_files:
        # Fallback to final master
        phonebook_files = glob.glob("data/FINAL_MASTER_CONTACTS_*.vcf")
    
    if not phonebook_files:
        print("❌ No master phonebook found!")
        return
    
    latest_phonebook = sorted(phonebook_files)[-1]
    
    # Run analysis
    analyzer = PhonebookAnalyzer(latest_phonebook)
    results, summary = analyzer.run_complete_analysis()
    
    return results

if __name__ == "__main__":
    main()