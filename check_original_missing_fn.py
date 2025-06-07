#!/usr/bin/env python3
"""Check the original file for contacts missing FN"""
import re

def check_original():
    """Check original file for missing FN contacts"""
    print("Checking original Sara export for missing FN contacts...\n")
    
    with open("Imports/Sara_Export_Sara A. Kerner and 3.074 others.vcf", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into vCards
    vcards = re.split(r'(?=BEGIN:VCARD)', content)
    vcards = [v for v in vcards if v.strip()]  # Remove empty
    
    missing_fn = []
    for i, vcard in enumerate(vcards):
        if 'FN:' not in vcard:
            # Extract key info
            email_match = re.search(r'EMAIL[^:]*:([^\r\n]+)', vcard)
            tel_match = re.search(r'TEL[^:]*:([^\r\n]+)', vcard)
            n_match = re.search(r'N:([^\r\n]+)', vcard)
            org_match = re.search(r'ORG:([^\r\n]+)', vcard)
            
            info = {
                'index': i,
                'email': email_match.group(1) if email_match else None,
                'tel': tel_match.group(1) if tel_match else None,
                'n': n_match.group(1) if n_match else None,
                'org': org_match.group(1) if org_match else None
            }
            missing_fn.append(info)
    
    print(f"Found {len(missing_fn)} contacts without FN field in original file\n")
    
    # Show samples
    print("First 10 contacts missing FN:")
    print("-" * 80)
    for contact in missing_fn[:10]:
        print(f"\nContact #{contact['index']}:")
        if contact['n']:
            print(f"  N: {contact['n']}")
        if contact['org']:
            print(f"  ORG: {contact['org']}")
        if contact['email']:
            print(f"  EMAIL: {contact['email']}")
        if contact['tel']:
            print(f"  TEL: {contact['tel']}")
        
        # Suggest FN
        print("  Suggested FN: ", end="")
        if contact['n'] and contact['n'] != ';;;;':
            # Parse N field
            parts = contact['n'].split(';')
            name_parts = []
            if len(parts) > 1 and parts[1]:  # First name
                name_parts.append(parts[1])
            if len(parts) > 0 and parts[0]:  # Last name
                name_parts.append(parts[0])
            if name_parts:
                print(' '.join(name_parts))
            else:
                print("(empty N field)")
        elif contact['org']:
            print(contact['org'])
        elif contact['email']:
            print(contact['email'])
        elif contact['tel']:
            print(contact['tel'])
        else:
            print("Unknown Contact")
    
    # Categorize
    categories = {
        'email_only': 0,
        'tel_only': 0,
        'org_present': 0,
        'empty_n': 0,
        'no_data': 0
    }
    
    for contact in missing_fn:
        if contact['n'] == ';;;;':
            categories['empty_n'] += 1
        if contact['email'] and not contact['n'] and not contact['org']:
            categories['email_only'] += 1
        elif contact['tel'] and not contact['email'] and not contact['n'] and not contact['org']:
            categories['tel_only'] += 1
        if contact['org']:
            categories['org_present'] += 1
        if not any([contact['email'], contact['tel'], contact['org']]) and contact['n'] == ';;;;':
            categories['no_data'] += 1
    
    print("\n" + "=" * 80)
    print("Categories:")
    for cat, count in categories.items():
        print(f"  {cat}: {count}")

if __name__ == "__main__":
    check_original()