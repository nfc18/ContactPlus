#!/usr/bin/env python3
"""
Check Daniel Albertini's contact entries
"""

import vobject

databases = [
    "data/Sara_Export_VALIDATED_20250606_CLEANED.vcf",
    "data/iPhone_Contacts_VALIDATED_20250606_120917_CLEANED.vcf",
    "data/iPhone_Suggested_VALIDATED_20250606_120917_CLEANED.vcf"
]

for db_path in databases:
    print(f"\n{db_path}:")
    print("-" * 60)
    
    with open(db_path, 'r', encoding='utf-8') as f:
        vcards = list(vobject.readComponents(f.read()))
    
    for vcard in vcards:
        if hasattr(vcard, 'fn') and vcard.fn.value == 'Daniel Albertini':
            print(f"Found Daniel Albertini")
            
            if hasattr(vcard, 'email_list'):
                print(f"  Emails ({len(vcard.email_list)}):")
                for email in vcard.email_list:
                    print(f"    - {email.value}")
            else:
                print("  No emails")
            
            if hasattr(vcard, 'org'):
                print(f"  Organization: {vcard.org.value}")
            
            print()