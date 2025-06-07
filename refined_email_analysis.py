#!/usr/bin/env python3
"""
Refined analysis to separate legitimate multi-email contacts from problematic ones
"""

import os
import re
import vobject
from collections import defaultdict
import json
from datetime import datetime
from difflib import SequenceMatcher

class RefinedEmailAnalyzer:
    """Separate legitimate multi-email patterns from problematic ones"""
    
    def __init__(self):
        self.legitimate_multi_email = []
        self.truly_problematic = []
        self.stats = defaultdict(int)
        
        # Common personal email domains
        self.personal_domains = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'icloud.com', 'me.com', 'aol.com', 'gmx.at', 'gmx.de',
            'gmx.net', 'web.de', 'live.com', 'msn.com', 'mail.com',
            'googlemail.com', 'protonmail.com', 'ymail.com'
        ]
    
    def extract_email_parts(self, email):
        """Extract local and domain parts of email"""
        if '@' not in email:
            return None, None
        parts = email.lower().split('@')
        return parts[0], parts[1]
    
    def extract_name_from_email(self, email):
        """Try to extract a person's name from email local part"""
        local, _ = self.extract_email_parts(email)
        if not local:
            return None
        
        # Common patterns: firstname.lastname, firstname_lastname, firstnamelastname
        # Remove numbers and special characters first
        clean_local = re.sub(r'[\d\-\+]', '', local)
        
        # Split by . or _
        parts = re.split(r'[._]', clean_local)
        parts = [p for p in parts if len(p) > 2]  # Filter out initials
        
        if parts:
            return parts
        return None
    
    def is_same_person_emails(self, emails):
        """Check if multiple emails likely belong to the same person"""
        name_parts_list = []
        
        for email in emails:
            name_parts = self.extract_name_from_email(email)
            if name_parts:
                name_parts_list.append(name_parts)
        
        if len(name_parts_list) < 2:
            return True  # Can't determine, assume it's OK
        
        # Check if there's overlap in name parts
        first_names = set()
        last_names = set()
        
        for parts in name_parts_list:
            if len(parts) >= 1:
                first_names.add(parts[0])
            if len(parts) >= 2:
                last_names.add(parts[1])
        
        # If all emails share a common first or last name, likely same person
        if len(first_names) == 1 or len(last_names) == 1:
            return True
        
        # Check for variations (e.g., 'john' and 'johnny')
        first_list = list(first_names)
        for i in range(len(first_list)):
            for j in range(i+1, len(first_list)):
                similarity = SequenceMatcher(None, first_list[i], first_list[j]).ratio()
                if similarity > 0.8:
                    return True
        
        return False
    
    def analyze_email_pattern(self, contact_name, emails):
        """Analyze if email pattern is legitimate or problematic"""
        
        # Group emails by domain
        domains = defaultdict(list)
        personal_emails = []
        work_emails = []
        
        for email in emails:
            local, domain = self.extract_email_parts(email)
            if domain:
                domains[domain].append(email)
                
                # Categorize as personal or work
                if any(pd in domain for pd in self.personal_domains):
                    personal_emails.append(email)
                else:
                    work_emails.append(email)
        
        # Pattern 1: Personal + Work emails (legitimate)
        if personal_emails and work_emails:
            if len(personal_emails) <= 2 and len(domains) <= 3:
                return 'personal_plus_work', 90
        
        # Pattern 2: Multiple emails from same company (job role changes)
        if len(domains) == 1:
            domain = list(domains.keys())[0]
            if domain not in [pd for pd in self.personal_domains]:
                # Check if emails suggest same person
                if self.is_same_person_emails(emails):
                    return 'same_company_evolution', 95
        
        # Pattern 3: Company change (emails from 2-3 related companies)
        if 2 <= len(domains) <= 3 and not personal_emails:
            # Check if email local parts are similar (same person)
            if self.is_same_person_emails(emails):
                return 'company_change', 85
        
        # Pattern 4: Freelancer/Consultant (personal + multiple client emails)
        if personal_emails and len(work_emails) >= 2:
            if self.is_same_person_emails(emails):
                return 'freelancer_pattern', 80
        
        # Pattern 5: Check if it's mixing different people's emails
        if not self.is_same_person_emails(emails):
            # Different names in emails = problematic
            return 'mixed_people', 10
        
        # Pattern 6: Too many domains or emails
        if len(domains) >= 4 or len(emails) >= 8:
            return 'excessive_emails', 20
        
        # Pattern 7: Multiple personal email accounts
        if len(personal_emails) >= 3 and not work_emails:
            return 'multiple_personal', 70
        
        # Default: unclear pattern
        return 'unclear', 50
    
    def categorize_contact(self, vcard):
        """Categorize a contact based on email patterns"""
        
        # Extract basic info
        name = "No name"
        if hasattr(vcard, 'fn') and vcard.fn.value:
            name = vcard.fn.value
        
        org = None
        if hasattr(vcard, 'org') and vcard.org.value:
            if isinstance(vcard.org.value, list):
                org = ' '.join(vcard.org.value)
            else:
                org = str(vcard.org.value)
        
        # Get emails
        emails = []
        if hasattr(vcard, 'email_list'):
            emails = [e.value for e in vcard.email_list if e.value]
        
        if len(emails) < 4:
            return None
        
        # Analyze pattern
        pattern, confidence = self.analyze_email_pattern(name, emails)
        
        # Group emails by domain for display
        domains = defaultdict(list)
        for email in emails:
            _, domain = self.extract_email_parts(email)
            if domain:
                domains[domain].append(email)
        
        contact_info = {
            'name': name,
            'organization': org,
            'email_count': len(emails),
            'emails': emails,
            'domains': dict(domains),
            'pattern': pattern,
            'confidence': confidence,
            'is_legitimate': confidence >= 70
        }
        
        return contact_info
    
    def analyze_file(self, filepath):
        """Analyze a vCard file"""
        
        print(f"Analyzing: {os.path.basename(filepath)}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            vcards = list(vobject.readComponents(f.read()))
        
        for vcard in vcards:
            contact_info = self.categorize_contact(vcard)
            
            if contact_info and contact_info['email_count'] >= 4:
                self.stats[contact_info['pattern']] += 1
                
                if contact_info['is_legitimate']:
                    self.legitimate_multi_email.append(contact_info)
                else:
                    self.truly_problematic.append(contact_info)


def generate_html_report(contacts, title, filename):
    """Generate HTML report for contacts"""
    
    with open(filename, 'w') as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        h1 {{ color: #333; }}
        .summary {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .contact {{ background: white; border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 8px; }}
        .legitimate {{ border-left: 5px solid #28a745; }}
        .problematic {{ border-left: 5px solid #dc3545; }}
        .pattern {{ display: inline-block; background: #e9ecef; padding: 4px 8px; border-radius: 4px; font-size: 12px; }}
        .confidence {{ float: right; font-weight: bold; color: #666; }}
        .email-group {{ margin: 10px 0; background: #f8f9fa; padding: 10px; border-radius: 5px; }}
        .domain {{ font-weight: bold; color: #495057; margin-bottom: 5px; }}
        .email {{ color: #007bff; margin-left: 20px; }}
        .org {{ color: #6c757d; font-style: italic; }}
        .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat-box {{ background: #007bff; color: white; padding: 15px; border-radius: 5px; text-align: center; }}
        .stat-number {{ font-size: 24px; font-weight: bold; }}
        .pattern-personal_plus_work {{ background-color: #d4edda; color: #155724; }}
        .pattern-same_company_evolution {{ background-color: #d4edda; color: #155724; }}
        .pattern-company_change {{ background-color: #d1ecf1; color: #0c5460; }}
        .pattern-freelancer_pattern {{ background-color: #d1ecf1; color: #0c5460; }}
        .pattern-mixed_people {{ background-color: #f8d7da; color: #721c24; }}
        .pattern-excessive_emails {{ background-color: #f8d7da; color: #721c24; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
""")
        
        # Group by pattern
        patterns = defaultdict(list)
        for contact in contacts:
            patterns[contact['pattern']].append(contact)
        
        # Add summary
        f.write(f"""
    <div class="summary">
        <h2>Summary</h2>
        <div class="stats">
            <div class="stat-box">
                <div class="stat-number">{len(contacts)}</div>
                <div>Total Contacts</div>
            </div>
""")
        
        for pattern, pattern_contacts in patterns.items():
            readable_pattern = pattern.replace('_', ' ').title()
            f.write(f"""
            <div class="stat-box">
                <div class="stat-number">{len(pattern_contacts)}</div>
                <div>{readable_pattern}</div>
            </div>
""")
        
        f.write("""
        </div>
    </div>
""")
        
        # Add contacts grouped by pattern
        pattern_descriptions = {
            'personal_plus_work': 'Personal email + work email(s) - Common and legitimate',
            'same_company_evolution': 'Multiple emails from same company - Likely role changes',
            'company_change': 'Emails from different companies - Likely job changes',
            'freelancer_pattern': 'Personal + multiple work emails - Freelancer/consultant pattern',
            'mixed_people': 'Emails appear to belong to different people - PROBLEMATIC',
            'excessive_emails': 'Too many emails/domains - NEEDS REVIEW',
            'multiple_personal': 'Multiple personal email accounts',
            'unclear': 'Pattern unclear - needs manual review'
        }
        
        for pattern, pattern_contacts in sorted(patterns.items(), key=lambda x: -x[1][0]['confidence']):
            readable_pattern = pattern.replace('_', ' ').title()
            description = pattern_descriptions.get(pattern, '')
            
            f.write(f"""
    <h2>{readable_pattern}</h2>
    <p>{description}</p>
""")
            
            for contact in sorted(pattern_contacts, key=lambda x: -x['confidence']):
                class_name = 'legitimate' if contact['is_legitimate'] else 'problematic'
                
                f.write(f"""
    <div class="contact {class_name}">
        <div class="confidence">Confidence: {contact['confidence']}%</div>
        <h3>{contact['name']}</h3>
        <span class="pattern pattern-{contact['pattern']}">{readable_pattern}</span>
        {f'<div class="org">Organization: {contact["organization"]}</div>' if contact['organization'] else ''}
        <div>Total emails: {contact['email_count']}</div>
        
        <div class="email-groups">
""")
                
                for domain, domain_emails in sorted(contact['domains'].items()):
                    f.write(f"""
            <div class="email-group">
                <div class="domain">{domain}:</div>
""")
                    for email in domain_emails:
                        f.write(f'                <div class="email">{email}</div>\n')
                    f.write('            </div>\n')
                
                f.write("""
        </div>
    </div>
""")
        
        f.write("""
</body>
</html>
""")


def main():
    """Run refined analysis"""
    
    print("Refined Email Pattern Analysis")
    print("=" * 80)
    
    databases = [
        "data/Sara_Export_VALIDATED_20250606_CLEANED.vcf",
        "data/iPhone_Contacts_VALIDATED_20250606_120917_CLEANED.vcf",
        "data/iPhone_Suggested_VALIDATED_20250606_120917_CLEANED.vcf"
    ]
    
    analyzer = RefinedEmailAnalyzer()
    
    # Analyze all databases
    for db_path in databases:
        if os.path.exists(db_path):
            analyzer.analyze_file(db_path)
    
    # Generate reports
    print(f"\nAnalysis complete!")
    print(f"Legitimate multi-email contacts: {len(analyzer.legitimate_multi_email)}")
    print(f"Truly problematic contacts: {len(analyzer.truly_problematic)}")
    
    print("\nPattern distribution:")
    for pattern, count in sorted(analyzer.stats.items(), key=lambda x: -x[1]):
        print(f"  {pattern}: {count}")
    
    # Generate HTML reports
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Legitimate contacts
    if analyzer.legitimate_multi_email:
        legitimate_file = f"data/legitimate_multi_email_{timestamp}.html"
        generate_html_report(
            analyzer.legitimate_multi_email,
            "Legitimate Multi-Email Contacts (OK to keep as-is)",
            legitimate_file
        )
        print(f"\n✅ Legitimate contacts report: {legitimate_file}")
    
    # Problematic contacts
    if analyzer.truly_problematic:
        problematic_file = f"data/problematic_multi_email_{timestamp}.html"
        generate_html_report(
            analyzer.truly_problematic,
            "Problematic Multi-Email Contacts (Need Review)",
            problematic_file
        )
        print(f"⚠️  Problematic contacts report: {problematic_file}")
    
    # Save JSON summary
    summary = {
        'analysis_date': datetime.now().isoformat(),
        'stats': dict(analyzer.stats),
        'legitimate_count': len(analyzer.legitimate_multi_email),
        'problematic_count': len(analyzer.truly_problematic),
        'legitimate_contacts': analyzer.legitimate_multi_email,
        'problematic_contacts': analyzer.truly_problematic
    }
    
    summary_file = f"data/refined_email_analysis_{timestamp}.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"📄 Detailed analysis saved: {summary_file}")


if __name__ == "__main__":
    main()