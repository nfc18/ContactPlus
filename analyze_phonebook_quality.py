#!/usr/bin/env python3
"""
Comprehensive quality analysis of the master phonebook.
Identifies contacts that would benefit from AI-based corrections.
"""

import re
import sys
from collections import defaultdict

def analyze_phonebook_quality(vcf_file):
    """Analyze the quality of contacts in the phonebook."""
    
    quality_issues = {
        'email_derived_names': [],
        'username_patterns': [],
        'names_with_numbers': [],
        'bot_names': [],
        'names_with_emails': [],
        'incomplete_names': [],
        'weird_characters': [],
        'business_names_as_personal': [],
        'all_caps_words': [],
        'suspicious_patterns': []
    }
    
    total_contacts = 0
    contacts_with_issues = set()
    current_contact = {}
    
    with open(vcf_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            if line == 'BEGIN:VCARD':
                current_contact = {}
                total_contacts += 1
            elif line == 'END:VCARD':
                analyze_contact(current_contact, quality_issues, contacts_with_issues)
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
    
    # Generate report
    print(f"📊 PHONEBOOK QUALITY ANALYSIS")
    print(f"=" * 50)
    print(f"Total contacts: {total_contacts:,}")
    print(f"Contacts with quality issues: {len(contacts_with_issues):,}")
    print(f"Quality score: {((total_contacts - len(contacts_with_issues)) / total_contacts * 100):.1f}%")
    print()
    
    for category, issues in quality_issues.items():
        if issues:
            print(f"🔍 {category.replace('_', ' ').title()}: {len(issues)}")
            for i, issue in enumerate(issues[:5]):  # Show first 5 examples
                print(f"  {i+1}. {issue}")
            if len(issues) > 5:
                print(f"  ... and {len(issues) - 5} more")
            print()
    
    # Summary recommendations
    print(f"📈 RECOMMENDATIONS")
    print(f"=" * 50)
    
    total_fixable = len(contacts_with_issues)
    if total_fixable > 0:
        print(f"• {total_fixable:,} contacts ({(total_fixable/total_contacts*100):.1f}%) would benefit from AI correction")
        print(f"• Priority fixes needed for email-derived names: {len(quality_issues['email_derived_names'])}")
        print(f"• Username patterns to fix: {len(quality_issues['username_patterns'])}")
        print(f"• Names with embedded emails: {len(quality_issues['names_with_emails'])}")
        print(f"• Bot/automated contact cleanup: {len(quality_issues['bot_names'])}")
    else:
        print("• Phonebook quality is excellent - no major issues detected")
    
    return quality_issues, total_contacts, len(contacts_with_issues)

def analyze_contact(contact, quality_issues, contacts_with_issues):
    """Analyze a single contact for quality issues."""
    
    fn = contact.get('FN', '')
    if not fn:
        return
    
    contact_id = fn[:50]  # Use first 50 chars as identifier
    
    # Email-derived names (like claudiaplatzer85)
    if re.match(r'^[a-z]+[0-9]+$', fn.lower()) or '@' in fn.lower():
        quality_issues['email_derived_names'].append(contact_id)
        contacts_with_issues.add(contact_id)
    
    # Username patterns 
    if re.search(r'[a-z]+[0-9]+|[0-9]+[a-z]+', fn.lower()):
        quality_issues['username_patterns'].append(contact_id)
        contacts_with_issues.add(contact_id)
    
    # Names with numbers
    if re.search(r'[0-9]', fn):
        quality_issues['names_with_numbers'].append(contact_id)
        contacts_with_issues.add(contact_id)
    
    # Bot names
    if re.search(r'bot|Bot|chatbot|Chatbot', fn):
        quality_issues['bot_names'].append(contact_id)
        contacts_with_issues.add(contact_id)
    
    # Names containing email addresses
    if '@' in fn:
        quality_issues['names_with_emails'].append(contact_id)
        contacts_with_issues.add(contact_id)
    
    # Incomplete names (single word that looks like username)
    if len(fn.split()) == 1 and len(fn) > 3:
        if re.search(r'[0-9]|@|\.|_', fn):
            quality_issues['incomplete_names'].append(contact_id)
            contacts_with_issues.add(contact_id)
    
    # Weird characters/patterns
    if re.search(r'[^a-zA-Z0-9\s\-\.@(),&]', fn):
        quality_issues['weird_characters'].append(contact_id)
        contacts_with_issues.add(contact_id)
    
    # Business names used as personal names
    business_indicators = ['GmbH', 'AG', 'Ltd', 'Inc', 'Corp', 'LLC', 'Buchhaltung', 'Support', 'Team']
    if any(indicator in fn for indicator in business_indicators):
        quality_issues['business_names_as_personal'].append(contact_id)
        contacts_with_issues.add(contact_id)
    
    # All caps words (but not acronyms)
    words = fn.split()
    for word in words:
        if len(word) > 3 and word.isupper() and not re.match(r'^[A-Z]{2,4}$', word):
            quality_issues['all_caps_words'].append(contact_id)
            contacts_with_issues.add(contact_id)
            break
    
    # Suspicious patterns
    suspicious_patterns = [
        r'^[a-z0-9]+$',  # All lowercase with numbers
        r'^[A-Z0-9]+$',  # All uppercase with numbers  
        r'^\w+\.\w+$',   # word.word pattern
        r'^\w+_\w+$',    # word_word pattern
    ]
    
    for pattern in suspicious_patterns:
        if re.match(pattern, fn):
            quality_issues['suspicious_patterns'].append(contact_id)
            contacts_with_issues.add(contact_id)
            break

if __name__ == "__main__":
    vcf_file = "/Users/lk/Documents/Developer/Private/ContactPlus/data/MASTER_PHONEBOOK_20250607_071756.vcf"
    analyze_phonebook_quality(vcf_file)