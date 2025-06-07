#!/usr/bin/env python3
"""
Smart categorization of contacts with multiple emails for manual review
Identifies the most problematic contacts that need human judgment
"""

import os
import re
import vobject
from collections import defaultdict
import json
from datetime import datetime

class SmartEmailReviewer:
    """Intelligently categorize contacts for review"""
    
    def __init__(self):
        self.problematic_contacts = []
        self.auto_fixable = []
        self.stats = {
            'total_analyzed': 0,
            'multi_email_contacts': 0,
            'auto_fixed': 0,
            'needs_review': 0
        }
    
    def extract_email_parts(self, email):
        """Extract local and domain parts of email"""
        if '@' not in email:
            return None, None
        parts = email.lower().split('@')
        return parts[0], parts[1]
    
    def calculate_severity_score(self, vcard, emails):
        """Calculate how problematic this contact is (0-100)"""
        score = 0
        
        # Factor 1: Number of emails (max 40 points)
        email_count = len(emails)
        if email_count >= 10:
            score += 40
        elif email_count >= 6:
            score += 30
        elif email_count >= 4:
            score += 20
        else:
            score += email_count * 5
        
        # Factor 2: Domain diversity (max 30 points)
        domains = set()
        for email in emails:
            _, domain = self.extract_email_parts(email)
            if domain:
                domains.add(domain)
        
        if len(domains) >= 5:
            score += 30
        elif len(domains) >= 3:
            score += 20
        elif len(domains) >= 2:
            score += 10
        
        # Factor 3: Suspicious patterns (max 30 points)
        local_parts = []
        for email in emails:
            local, _ = self.extract_email_parts(email)
            if local:
                local_parts.append(local)
        
        # Check for mixed personal names in emails
        unique_names = set()
        name_pattern = re.compile(r'^[a-z]+\.[a-z]+$|^[a-z]+$')
        for local in local_parts:
            if name_pattern.match(local):
                # Extract potential first name
                name = local.split('.')[0] if '.' in local else local
                if len(name) > 2:  # Avoid initials
                    unique_names.add(name)
        
        if len(unique_names) >= 3:
            score += 30  # Multiple different names = very suspicious
        elif len(unique_names) == 2:
            score += 20
        
        # Check for numbered emails (like user1@, user2@)
        numbered_pattern = re.compile(r'.*\d+$')
        numbered_count = sum(1 for local in local_parts if numbered_pattern.match(local))
        if numbered_count >= 2:
            score += 10
        
        return score
    
    def categorize_contact(self, vcard, emails):
        """Categorize a contact and determine if it needs review"""
        
        # Extract contact info
        name = "No name"
        if hasattr(vcard, 'fn') and vcard.fn.value:
            name = vcard.fn.value
        
        org = None
        if hasattr(vcard, 'org') and vcard.org.value:
            if isinstance(vcard.org.value, list):
                org = ' '.join(vcard.org.value)
            else:
                org = str(vcard.org.value)
        
        # Analyze email patterns
        domains = defaultdict(list)
        for email in emails:
            local, domain = self.extract_email_parts(email)
            if domain:
                domains[domain].append(email)
        
        # Calculate severity
        severity = self.calculate_severity_score(vcard, emails)
        
        # Determine category
        category = "unknown"
        auto_fix_suggestion = None
        
        if len(emails) >= 10:
            category = "excessive_emails"
        elif len(domains) >= 4:
            category = "multi_company_mix"
        elif len(domains) == 1:
            # All emails from same domain
            domain = list(domains.keys())[0]
            local_parts = [self.extract_email_parts(e)[0] for e in emails]
            
            # Check if one email matches the contact name
            contact_first_name = name.lower().split()[0] if name != "No name" else ""
            matching_emails = [e for e in emails if contact_first_name and contact_first_name in e.lower()]
            
            if matching_emails:
                category = "same_domain_with_match"
                auto_fix_suggestion = {
                    'action': 'keep_only_matching',
                    'keep': matching_emails,
                    'remove': [e for e in emails if e not in matching_emails]
                }
            else:
                category = "same_domain_no_match"
        else:
            # Multiple domains
            category = "multi_domain"
            
            # Check if there's a personal email domain
            personal_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 
                               'icloud.com', 'me.com', 'aol.com', 'gmx.at', 'gmx.de']
            personal_emails = []
            work_emails = []
            
            for domain, domain_emails in domains.items():
                if any(pd in domain for pd in personal_domains):
                    personal_emails.extend(domain_emails)
                else:
                    work_emails.extend(domain_emails)
            
            if personal_emails and len(personal_emails) == 1 and len(work_emails) <= 2:
                category = "likely_personal_plus_work"
                # This might be OK - person with personal + work emails
                severity -= 20  # Reduce severity
        
        contact_info = {
            'name': name,
            'organization': org,
            'email_count': len(emails),
            'emails': emails,
            'domains': dict(domains),
            'category': category,
            'severity': severity,
            'auto_fix_suggestion': auto_fix_suggestion
        }
        
        return contact_info
    
    def analyze_file(self, filepath):
        """Analyze a vCard file for problematic email patterns"""
        
        print(f"\nAnalyzing: {os.path.basename(filepath)}")
        
        # Load vCards
        with open(filepath, 'r', encoding='utf-8') as f:
            vcards = list(vobject.readComponents(f.read()))
        
        self.stats['total_analyzed'] += len(vcards)
        
        # Analyze each vCard
        for vcard in vcards:
            if hasattr(vcard, 'email_list') and len(vcard.email_list) >= 4:
                emails = [e.value for e in vcard.email_list if e.value]
                
                if len(emails) >= 4:
                    self.stats['multi_email_contacts'] += 1
                    contact_info = self.categorize_contact(vcard, emails)
                    
                    if contact_info['auto_fix_suggestion']:
                        self.auto_fixable.append(contact_info)
                    else:
                        self.problematic_contacts.append(contact_info)
    
    def generate_review_list(self, max_items=50):
        """Generate prioritized list for manual review"""
        
        # Sort by severity (highest first)
        self.problematic_contacts.sort(key=lambda x: x['severity'], reverse=True)
        
        # Take top N
        review_list = self.problematic_contacts[:max_items]
        
        # Group by category for better review experience
        categorized = defaultdict(list)
        for contact in review_list:
            categorized[contact['category']].append(contact)
        
        return categorized, review_list


def main():
    """Analyze cleaned databases and generate review list"""
    
    print("Smart Email Review System")
    print("=" * 80)
    
    databases = [
        "data/Sara_Export_VALIDATED_20250606_CLEANED.vcf",
        "data/iPhone_Contacts_VALIDATED_20250606_120917_CLEANED.vcf",
        "data/iPhone_Suggested_VALIDATED_20250606_120917_CLEANED.vcf"
    ]
    
    reviewer = SmartEmailReviewer()
    
    # Analyze all databases
    for db_path in databases:
        if os.path.exists(db_path):
            reviewer.analyze_file(db_path)
        else:
            print(f"Warning: Cleaned file not found - {db_path}")
    
    # Generate review list
    categorized, review_list = reviewer.generate_review_list(max_items=50)
    
    # Print summary
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"Total contacts analyzed: {reviewer.stats['total_analyzed']}")
    print(f"Contacts with 4+ emails: {reviewer.stats['multi_email_contacts']}")
    print(f"Auto-fixable contacts: {len(reviewer.auto_fixable)}")
    print(f"Needs manual review: {len(reviewer.problematic_contacts)}")
    
    # Print categories
    print("\n📊 CONTACTS BY CATEGORY (Top 50 for review):")
    for category, contacts in categorized.items():
        print(f"\n{category.upper().replace('_', ' ')} ({len(contacts)} contacts):")
        for contact in contacts[:5]:  # Show first 5 of each category
            print(f"  - {contact['name']}")
            print(f"    Emails: {contact['email_count']} | Severity: {contact['severity']}")
            print(f"    Domains: {', '.join(contact['domains'].keys())}")
    
    # Generate review file
    review_data = {
        'review_date': datetime.now().isoformat(),
        'summary': {
            'total_multi_email_contacts': reviewer.stats['multi_email_contacts'],
            'auto_fixable': len(reviewer.auto_fixable),
            'needs_review': len(review_list),
            'excluded_from_review': len(reviewer.problematic_contacts) - len(review_list)
        },
        'review_list': review_list,
        'auto_fixable': reviewer.auto_fixable
    }
    
    review_file = f"data/email_review_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(review_file, 'w') as f:
        json.dump(review_data, f, indent=2)
    
    # Generate human-readable review file
    review_html = f"data/email_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(review_html, 'w') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Email Review List</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .contact { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
        .high-severity { background-color: #ffe6e6; }
        .medium-severity { background-color: #fff4e6; }
        .low-severity { background-color: #f0f8ff; }
        .email-list { margin: 10px 0; }
        .email { background: #f5f5f5; padding: 5px; margin: 2px 0; border-radius: 3px; }
        h1 { color: #333; }
        .category { color: #666; font-size: 14px; }
        .severity { float: right; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Contact Email Review List</h1>
    <p>Total contacts for review: """ + str(len(review_list)) + """</p>
    <hr>
""")
        
        for i, contact in enumerate(review_list, 1):
            severity_class = 'high-severity' if contact['severity'] >= 70 else 'medium-severity' if contact['severity'] >= 40 else 'low-severity'
            f.write(f"""
    <div class="contact {severity_class}">
        <div class="severity">Severity: {contact['severity']}</div>
        <h3>{i}. {contact['name']}</h3>
        <div class="category">Category: {contact['category']}</div>
        <div>Organization: {contact['organization'] or 'None'}</div>
        <div>Total emails: {contact['email_count']}</div>
        <div class="email-list">
            <strong>Emails by domain:</strong><br>
""")
            for domain, emails in contact['domains'].items():
                f.write(f"            <strong>{domain}:</strong><br>")
                for email in emails:
                    f.write(f'            <div class="email">{email}</div>')
            f.write("""
        </div>
    </div>
""")
        
        f.write("""
</body>
</html>
""")
    
    print(f"\n✅ Review files generated:")
    print(f"   - JSON: {review_file}")
    print(f"   - HTML: {review_html}")
    print(f"\n📋 Next steps:")
    print(f"   1. Review the {len(review_list)} contacts in the HTML file")
    print(f"   2. {len(reviewer.auto_fixable)} contacts can be auto-fixed")
    print(f"   3. {len(reviewer.problematic_contacts) - len(review_list)} lower-priority contacts excluded from review")


if __name__ == "__main__":
    main()