#!/usr/bin/env python3
"""
Find all Daniel Albertini entries in the master phonebook
"""

import vobject

with open('data/FINAL_MASTER_CONTACTS_20250606_143247.vcf', 'r', encoding='utf-8') as f:
    contacts = list(vobject.readComponents(f.read()))

daniel_contacts = []
for i, vcard in enumerate(contacts):
    if hasattr(vcard, 'fn') and vcard.fn.value and 'daniel albertini' in vcard.fn.value.lower():
        daniel_contacts.append((i, vcard))

print(f"Found {len(daniel_contacts)} Daniel Albertini entries:\n")

for idx, (pos, vcard) in enumerate(daniel_contacts):
    print(f"Entry {idx + 1} (position {pos}):")
    print(f"  Name: {vcard.fn.value}")
    
    if hasattr(vcard, 'org') and vcard.org.value:
        org = vcard.org.value
        if isinstance(org, list):
            org = ' '.join(org)
        print(f"  Organization: {org}")
    
    if hasattr(vcard, 'email_list'):
        emails = [e.value for e in vcard.email_list if e.value]
        if emails:
            print(f"  Emails: {', '.join(emails)}")
    
    if hasattr(vcard, 'tel_list'):
        phones = [t.value for t in vcard.tel_list if t.value]
        if phones:
            print(f"  Phones: {', '.join(phones)}")
    
    print()