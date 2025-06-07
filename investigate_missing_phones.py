#!/usr/bin/env python3
"""
Investigate the 7 missing phone numbers from iPhone Contacts
"""

import vobject
import re

# The 7 missing phone numbers
missing_phones = [
    "+431386525251",
    "+431386525269", 
    "+431386525299",
    "+436641360251",
    "+436764676783",
    "12035580815",
    "494369498"
]

def normalize_phone(phone):
    """Normalize phone number for comparison"""
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)
    return digits

def find_contacts_with_phones(filepath, target_phones):
    """Find contacts that have the target phone numbers"""
    found_contacts = []
    
    # Normalize target phones for comparison
    normalized_targets = {normalize_phone(p): p for p in target_phones}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        vcards = list(vobject.readComponents(f.read()))
    
    for vcard in vcards:
        if hasattr(vcard, 'tel_list'):
            for tel in vcard.tel_list:
                if tel.value:
                    normalized = normalize_phone(tel.value)
                    if normalized in normalized_targets:
                        contact_info = {
                            'phone': normalized_targets[normalized],
                            'original_phone': tel.value,
                            'name': vcard.fn.value if hasattr(vcard, 'fn') else 'No name',
                            'org': None,
                            'emails': [],
                            'all_phones': [],
                            'vcard': vcard
                        }
                        
                        # Get organization
                        if hasattr(vcard, 'org') and vcard.org.value:
                            org = vcard.org.value
                            if isinstance(org, list):
                                org = ' '.join(org)
                            contact_info['org'] = org
                        
                        # Get all emails
                        if hasattr(vcard, 'email_list'):
                            contact_info['emails'] = [e.value for e in vcard.email_list if e.value]
                        
                        # Get all phones
                        if hasattr(vcard, 'tel_list'):
                            contact_info['all_phones'] = [t.value for t in vcard.tel_list if t.value]
                        
                        found_contacts.append(contact_info)
                        break
    
    return found_contacts

print("Investigating Missing Phone Numbers")
print("=" * 80)
print(f"Looking for 7 missing phones in original iPhone Contacts...")

# Check original iPhone Contacts
iphone_path = "Imports/iPhone_Contacts_Contacts.vcf"
found = find_contacts_with_phones(iphone_path, missing_phones)

print(f"\nFound {len(found)} contacts with missing phone numbers:\n")

# Analyze what we found
service_numbers = []
real_contacts = []

for contact in found:
    print(f"Phone: {contact['phone']}")
    print(f"  Name: {contact['name']}")
    if contact['org']:
        print(f"  Organization: {contact['org']}")
    if contact['emails']:
        print(f"  Emails: {', '.join(contact['emails'])}")
    print(f"  All phones: {', '.join(contact['all_phones'])}")
    
    # Determine if it's a service number
    is_service = False
    phone = contact['phone']
    name_lower = contact['name'].lower()
    
    # Check for service number patterns
    if phone.startswith("+4313865252"):  # Anyline office numbers
        is_service = True
        reason = "Anyline office extension"
    elif "service" in name_lower or "support" in name_lower or "hotline" in name_lower:
        is_service = True
        reason = "Service/support number"
    elif contact['name'] == contact['phone'] or contact['name'].startswith('+'):
        is_service = True
        reason = "No real name (just phone number)"
    elif len(phone) < 10:
        is_service = True
        reason = "Too short to be a real phone number"
    
    if is_service:
        print(f"  ⚠️  Likely service number: {reason}")
        service_numbers.append(contact)
    else:
        print(f"  ✓ Appears to be a real contact")
        real_contacts.append(contact)
    
    print()

print("=" * 80)
print(f"Summary:")
print(f"  Service/hotline numbers: {len(service_numbers)}")
print(f"  Real contacts to add: {len(real_contacts)}")

# Save real contacts to add
if real_contacts:
    print(f"\nPreparing to add {len(real_contacts)} real contacts to master phonebook...")
    
    # Create VCF file with contacts to add
    output_path = "data/missing_contacts_to_add.vcf"
    with open(output_path, 'w', encoding='utf-8') as f:
        for contact in real_contacts:
            f.write(contact['vcard'].serialize())
    
    print(f"Saved contacts to add: {output_path}")
else:
    print("\nNo real contacts found to add - all appear to be service numbers.")