#!/usr/bin/env python3
"""Analyze contacts missing FN field to determine best approach"""
import re

def analyze_missing_fn():
    """Analyze what data is available for contacts missing FN"""
    print("Analyzing contacts with missing FN field...\n")
    
    with open("data/Sara_Export_IMPORT_READY.vcf", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Process each vCard
    missing_fn_contacts = []
    current_vcard = []
    in_vcard = False
    
    for line in content.split('\n'):
        if line.strip() == 'BEGIN:VCARD':
            in_vcard = True
            current_vcard = [line]
        elif line.strip() == 'END:VCARD':
            current_vcard.append(line)
            vcard_text = '\n'.join(current_vcard)
            
            # Check if FN is missing
            if 'FN:' not in vcard_text:
                # Extract available data
                info = {
                    'vcard': vcard_text,
                    'has_n': False,
                    'n_parts': None,
                    'has_org': False,
                    'org': None,
                    'has_email': False,
                    'email': None,
                    'has_tel': False,
                    'tel': None,
                    'has_note': False,
                    'note_preview': None
                }
                
                # Check N field
                n_match = re.search(r'N:([^;]*);([^;]*);([^;]*);([^;]*);([^;]*)', vcard_text)
                if n_match:
                    info['has_n'] = True
                    info['n_parts'] = {
                        'last': n_match.group(1).strip(),
                        'first': n_match.group(2).strip(),
                        'middle': n_match.group(3).strip(),
                        'prefix': n_match.group(4).strip(),
                        'suffix': n_match.group(5).strip()
                    }
                
                # Check ORG
                org_match = re.search(r'ORG:([^\r\n]+)', vcard_text)
                if org_match:
                    info['has_org'] = True
                    info['org'] = org_match.group(1).strip()
                
                # Check EMAIL
                email_match = re.search(r'EMAIL[^:]*:([^\r\n]+)', vcard_text)
                if email_match:
                    info['has_email'] = True
                    info['email'] = email_match.group(1).strip()
                
                # Check TEL
                tel_match = re.search(r'TEL[^:]*:([^\r\n]+)', vcard_text)
                if tel_match:
                    info['has_tel'] = True
                    info['tel'] = tel_match.group(1).strip()
                
                # Check NOTE
                note_match = re.search(r'NOTE:([^\r\n]{0,50})', vcard_text)
                if note_match:
                    info['has_note'] = True
                    info['note_preview'] = note_match.group(1).strip()
                
                missing_fn_contacts.append(info)
            
            current_vcard = []
            in_vcard = False
        elif in_vcard:
            current_vcard.append(line)
    
    # Analyze patterns
    print(f"Total contacts missing FN: {len(missing_fn_contacts)}\n")
    
    # Count what data is available
    stats = {
        'has_n_with_name': 0,
        'has_n_empty': 0,
        'has_org_only': 0,
        'has_email_only': 0,
        'has_tel_only': 0,
        'has_nothing': 0
    }
    
    print("Sample contacts and available data:")
    print("-" * 80)
    
    for i, contact in enumerate(missing_fn_contacts[:10]):  # Show first 10
        print(f"\nContact #{i+1}:")
        
        # Check N field quality
        if contact['has_n']:
            parts = contact['n_parts']
            has_name = any([parts['first'], parts['last'], parts['middle']])
            if has_name:
                stats['has_n_with_name'] += 1
                print(f"  N field: {parts['last']};{parts['first']};{parts['middle']}")
                suggested_fn = []
                if parts['first']:
                    suggested_fn.append(parts['first'])
                if parts['middle']:
                    suggested_fn.append(parts['middle'])
                if parts['last']:
                    suggested_fn.append(parts['last'])
                print(f"  → Suggested FN: {' '.join(suggested_fn)}")
            else:
                stats['has_n_empty'] += 1
                print("  N field: Empty (;;;;)")
        
        if contact['has_org']:
            print(f"  ORG: {contact['org']}")
            if not contact['has_n'] or not any([contact['n_parts']['first'], contact['n_parts']['last']]):
                stats['has_org_only'] += 1
                print(f"  → Could use ORG as FN: {contact['org']}")
        
        if contact['has_email']:
            print(f"  EMAIL: {contact['email']}")
            if not contact['has_n'] and not contact['has_org']:
                stats['has_email_only'] += 1
                print(f"  → Could use EMAIL as FN: {contact['email']}")
        
        if contact['has_tel']:
            print(f"  TEL: {contact['tel']}")
            if not contact['has_n'] and not contact['has_org'] and not contact['has_email']:
                stats['has_tel_only'] += 1
                print(f"  → Could use TEL as FN: {contact['tel']}")
        
        if not any([contact['has_n'], contact['has_org'], contact['has_email'], contact['has_tel']]):
            stats['has_nothing'] += 1
            print("  ⚠️  No identifying information found!")
    
    # Summary statistics
    print("\n" + "=" * 80)
    print("Summary of data availability:")
    print(f"  - Have N field with names: {sum(1 for c in missing_fn_contacts if c['has_n'] and any([c['n_parts']['first'], c['n_parts']['last'], c['n_parts']['middle']]))}")
    print(f"  - Have N field but empty: {sum(1 for c in missing_fn_contacts if c['has_n'] and not any([c['n_parts']['first'], c['n_parts']['last'], c['n_parts']['middle']]))}")
    print(f"  - Have organization: {sum(1 for c in missing_fn_contacts if c['has_org'])}")
    print(f"  - Have email: {sum(1 for c in missing_fn_contacts if c['has_email'])}")
    print(f"  - Have phone: {sum(1 for c in missing_fn_contacts if c['has_tel'])}")
    print(f"  - Have no data: {sum(1 for c in missing_fn_contacts if not any([c['has_n'], c['has_org'], c['has_email'], c['has_tel']]))}")
    
    print("\n" + "=" * 80)
    print("Recommended FN field strategy:")
    print("1. If N field has name parts → combine them (First Middle Last)")
    print("2. Else if ORG exists → use organization name")
    print("3. Else if EMAIL exists → use email address")
    print("4. Else if TEL exists → use phone number")
    print("5. Else → use 'Contact' or skip the contact entirely")

if __name__ == "__main__":
    analyze_missing_fn()