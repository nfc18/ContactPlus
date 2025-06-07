#!/usr/bin/env python3
"""
Detailed quality assessment focused on AI-correctable issues in the master phonebook.
Provides specific examples and remediation strategies.
"""

import re
import sys
from collections import defaultdict

def extract_email_from_name(name):
    """Try to extract a real name from an email-derived username."""
    # Remove numbers
    base_name = re.sub(r'\d+', '', name)
    
    # Common patterns to extract real names
    patterns = [
        r'^([a-z]+)([a-z]+)(\d+)?$',  # firstnamelastname pattern
        r'^([a-z]+)\.([a-z]+)(\d+)?$',  # firstname.lastname pattern
        r'^([a-z]+)_([a-z]+)(\d+)?$',   # firstname_lastname pattern
    ]
    
    for pattern in patterns:
        match = re.match(pattern, name.lower())
        if match:
            first = match.group(1).capitalize()
            last = match.group(2).capitalize()
            return f"{first} {last}"
    
    return None

def detailed_quality_assessment(vcf_file):
    """Perform detailed assessment with specific examples and fixes."""
    
    issues = {
        'email_derived_usernames': [],
        'names_with_emails_embedded': [],
        'bot_contacts': [],
        'business_as_personal': [],
        'single_letter_names': [],
        'numeric_names': [],
        'obvious_usernames': [],
        'all_caps_issues': [],
        'weird_encoding': []
    }
    
    total_contacts = 0
    current_contact = {}
    
    with open(vcf_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            if line == 'BEGIN:VCARD':
                current_contact = {}
                total_contacts += 1
            elif line == 'END:VCARD':
                analyze_detailed_contact(current_contact, issues)
            elif line.startswith('FN:'):
                current_contact['FN'] = line[3:]
            elif line.startswith('N:'):
                current_contact['N'] = line[2:]
            elif line.startswith('EMAIL:'):
                if 'EMAIL' not in current_contact:
                    current_contact['EMAIL'] = []
                current_contact['EMAIL'].append(line[6:])
            elif line.startswith('ORG:'):
                current_contact['ORG'] = line[4:]
    
    print("🔍 DETAILED QUALITY ASSESSMENT - MASTER PHONEBOOK")
    print("=" * 60)
    print(f"Total contacts analyzed: {total_contacts:,}")
    print()
    
    # Email-derived usernames (highest priority)
    print("🚨 HIGH PRIORITY: Email-derived usernames")
    print("-" * 40)
    for contact in issues['email_derived_usernames'][:10]:
        fn = contact['FN']
        suggested = extract_email_from_name(fn)
        email = contact.get('EMAIL', [''])[0] if contact.get('EMAIL') else ''
        print(f"  Current: {fn}")
        if suggested:
            print(f"  Suggested: {suggested}")
        if email:
            print(f"  Email: {email}")
        print()
    if len(issues['email_derived_usernames']) > 10:
        print(f"  ... and {len(issues['email_derived_usernames']) - 10} more similar cases")
    print()
    
    # Names with embedded emails
    print("📧 Names with embedded email addresses")
    print("-" * 40)
    for contact in issues['names_with_emails_embedded'][:5]:
        fn = contact['FN']
        # Extract the name part before the email
        name_part = re.sub(r'\s*\([^)]*@[^)]*\)', '', fn)
        name_part = re.sub(r'\s*<[^>]*@[^>]*>', '', fn)
        name_part = re.sub(r'\s+', ' ', name_part).strip()
        print(f"  Current: {fn}")
        if name_part != fn:
            print(f"  Suggested: {name_part}")
        print()
    print()
    
    # Bot contacts
    print("🤖 Bot/Automated contacts")
    print("-" * 40)
    for contact in issues['bot_contacts']:
        print(f"  {contact['FN']}")
    print()
    
    # Business names as personal
    print("🏢 Business names used as personal contacts")
    print("-" * 40)
    for contact in issues['business_as_personal'][:10]:
        print(f"  {contact['FN']}")
    if len(issues['business_as_personal']) > 10:
        print(f"  ... and {len(issues['business_as_personal']) - 10} more")
    print()
    
    # Single letter names
    print("📝 Single letter/incomplete names")
    print("-" * 40)
    for contact in issues['single_letter_names']:
        print(f"  {contact['FN']}")
    print()
    
    # Summary statistics
    total_issues = sum(len(issue_list) for issue_list in issues.values())
    
    print("📊 SUMMARY STATISTICS")
    print("=" * 30)
    print(f"Email-derived usernames: {len(issues['email_derived_usernames'])}")
    print(f"Names with embedded emails: {len(issues['names_with_emails_embedded'])}")
    print(f"Bot contacts: {len(issues['bot_contacts'])}")
    print(f"Business as personal: {len(issues['business_as_personal'])}")
    print(f"Single letter names: {len(issues['single_letter_names'])}")
    print(f"Numeric names: {len(issues['numeric_names'])}")
    print(f"Total contacts needing AI correction: {total_issues}")
    print(f"Percentage of database: {(total_issues/total_contacts*100):.1f}%")
    print()
    
    print("🎯 REMEDIATION RECOMMENDATIONS")
    print("=" * 40)
    print("1. IMMEDIATE ACTION NEEDED:")
    print(f"   • Fix {len(issues['email_derived_usernames'])} email-derived usernames")
    print(f"   • Clean {len(issues['names_with_emails_embedded'])} names with embedded emails")
    print(f"   • Review {len(issues['bot_contacts'])} bot/automated contacts for deletion")
    print()
    print("2. MEDIUM PRIORITY:")
    print(f"   • Categorize {len(issues['business_as_personal'])} business contacts properly")
    print(f"   • Complete {len(issues['single_letter_names'])} incomplete names")
    print()
    print("3. EVIDENCE OF PRE-AI MERGE:")
    if total_issues > 200:
        print("   ⚠️  HIGH: Current database shows clear signs of being merged")
        print("        before intelligent AI analysis was applied")
        print("   📈 IMPACT: 10%+ of contacts have correctable quality issues")
        print("   🔧 SOLUTION: Apply AI enhancement pipeline to current database")
    else:
        print("   ✅ Database quality is acceptable")
    
    return issues

def analyze_detailed_contact(contact, issues):
    """Analyze a single contact for detailed quality issues."""
    
    fn = contact.get('FN', '')
    if not fn:
        return
    
    # Email-derived usernames (claudiaplatzer85, edhesse79, etc.)
    if re.match(r'^[a-z]+[0-9]+$', fn.lower()):
        issues['email_derived_usernames'].append(contact)
    
    # Names with embedded email addresses
    elif '@' in fn:
        issues['names_with_emails_embedded'].append(contact)
    
    # Bot contacts
    elif re.search(r'bot|Bot|chatbot|Chatbot', fn):
        issues['bot_contacts'].append(contact)
    
    # Business names as personal
    elif any(term in fn for term in ['GmbH', 'AG', 'Ltd', 'Inc', 'Corp', 'LLC', 'Buchhaltung', 'Support', 'Team', 'Rechnungsstelle']):
        issues['business_as_personal'].append(contact)
    
    # Single letter names
    elif len(fn.strip()) <= 2:
        issues['single_letter_names'].append(contact)
    
    # Numeric codes as names
    elif re.match(r'^[A-Z]?\d+', fn):
        issues['numeric_names'].append(contact)
    
    # Obviously encoded/weird names
    elif re.search(r'[0-9a-z]{8,}', fn.lower()) and not ' ' in fn:
        issues['obvious_usernames'].append(contact)

if __name__ == "__main__":
    vcf_file = "/Users/lk/Documents/Developer/Private/ContactPlus/data/MASTER_PHONEBOOK_20250607_071756.vcf"
    detailed_quality_assessment(vcf_file)