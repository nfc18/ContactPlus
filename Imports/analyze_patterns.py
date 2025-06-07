import sys
import re
from collections import defaultdict

def analyze_email_patterns(filename):
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    in_vcard = False
    email_count = 0
    contact_name = ""
    emails = []
    
    multi_email_contacts = []
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('BEGIN:VCARD'):
            in_vcard = True
            email_count = 0
            contact_name = ""
            emails = []
        
        elif line.startswith('FN:'):
            contact_name = line[3:]
        
        elif 'EMAIL' in line and ':' in line:
            email_count += 1
            email = line.split(':', 1)[1] if ':' in line else ""
            emails.append(email)
        
        elif line.startswith('END:VCARD'):
            if email_count > 3:
                if not contact_name:
                    contact_name = "Unknown"
                multi_email_contacts.append((email_count, contact_name, emails))
            in_vcard = False
    
    # Analyze patterns
    domain_counts = defaultdict(int)
    company_transitions = []
    personal_and_work = []
    
    for count, name, email_list in multi_email_contacts:
        domains = []
        for email in email_list:
            if '@' in email:
                domain = email.split('@')[1].lower()
                domains.append(domain)
                domain_counts[domain] += 1
        
        # Check for company transitions (multiple company domains)
        unique_domains = set(domains)
        company_domains = [d for d in unique_domains if not any(personal in d for personal in 
                          ['gmail', 'hotmail', 'yahoo', 'gmx', 'icloud', 'web.de', 'googlemail'])]
        
        if len(company_domains) > 1:
            company_transitions.append((name, company_domains))
        
        # Check for mix of personal and work emails
        personal_domains = [d for d in unique_domains if any(personal in d for personal in 
                           ['gmail', 'hotmail', 'yahoo', 'gmx', 'icloud', 'web.de', 'googlemail'])]
        
        if personal_domains and company_domains:
            personal_and_work.append((name, personal_domains, company_domains))
    
    print("\nPatterns in Multi-Email Contacts:")
    print("=" * 80)
    
    print("\n1. Top domains among multi-email contacts:")
    sorted_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    for domain, count in sorted_domains:
        print(f"   {domain}: {count} occurrences")
    
    print(f"\n2. Contacts with multiple company transitions ({len(company_transitions)} contacts):")
    for name, companies in company_transitions[:10]:
        print(f"   {name}: {', '.join(companies)}")
    
    print(f"\n3. Contacts mixing personal and work emails ({len(personal_and_work)} contacts):")
    for name, personal, work in personal_and_work[:10]:
        print(f"   {name}:")
        print(f"      Personal: {', '.join(personal)}")
        print(f"      Work: {', '.join(work)}")
    
    # Analyze Anyline-specific patterns
    anyline_contacts = []
    for count, name, email_list in multi_email_contacts:
        anyline_emails = [e for e in email_list if 'anyline' in e.lower()]
        if anyline_emails:
            anyline_contacts.append((name, anyline_emails))
    
    print(f"\n4. Anyline-related contacts ({len(anyline_contacts)} contacts):")
    for name, emails in anyline_contacts[:10]:
        print(f"   {name}: {', '.join(emails)}")

if __name__ == "__main__":
    analyze_email_patterns(sys.argv[1])
