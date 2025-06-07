#!/usr/bin/env python3
"""
Verify all phone numbers from original databases are in the master phonebook
"""

import vobject
import os
import re
from collections import defaultdict

def normalize_phone(phone):
    """Normalize phone number for comparison"""
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)
    # Remove leading zeros
    digits = digits.lstrip('0')
    # Handle Austrian numbers
    if digits.startswith('43'):
        return '+' + digits
    elif len(digits) == 10 and digits[0] in '6789':  # Austrian mobile
        return '+43' + digits
    return digits

def extract_phones_from_vcf(filepath):
    """Extract all phone numbers from a VCF file"""
    phones = set()
    contact_count = 0
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            vcards = list(vobject.readComponents(f.read()))
        
        for vcard in vcards:
            contact_count += 1
            if hasattr(vcard, 'tel_list'):
                for tel in vcard.tel_list:
                    if tel.value:
                        normalized = normalize_phone(tel.value)
                        if normalized and len(normalized) > 5:  # Skip very short numbers
                            phones.add(normalized)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return phones, 0
    
    return phones, contact_count

print("Phone Number Verification")
print("=" * 80)

# Define the original databases
original_dbs = {
    "Sara Export": "Imports/Sara_Export_Sara A. Kerner and 3.074 others.vcf",
    "iPhone Contacts": "Imports/iPhone_Contacts_Contacts.vcf",
    "iPhone Suggested": "Imports/iPhone_Suggested_Suggested Contacts.vcf",
    "Edgar Export": "Imports/Edgar_Export_Edgar A and 24.836 others.vcf"
}

# Also check the cleaned versions we actually used
cleaned_dbs = {
    "Sara Cleaned": "data/Sara_Export_VALIDATED_20250606_CLEANED_20250606_141000.vcf",
    "iPhone Cleaned": "data/iPhone_Contacts_VALIDATED_20250606_120917_CLEANED_20250606_141000.vcf",
    "iPhone Suggested Cleaned": "data/iPhone_Suggested_VALIDATED_20250606_120917_CLEANED_20250606_141000.vcf"
}

# Extract phones from master
print("Loading master phonebook...")
master_phones, master_count = extract_phones_from_vcf("data/FINAL_MASTER_CONTACTS_20250606_143247.vcf")
print(f"Master phonebook: {master_count} contacts, {len(master_phones)} unique phone numbers")

print("\nChecking original databases:")
print("-" * 80)

all_original_phones = set()
missing_phones_by_db = defaultdict(set)

for db_name, db_path in original_dbs.items():
    if os.path.exists(db_path):
        phones, count = extract_phones_from_vcf(db_path)
        all_original_phones.update(phones)
        
        # Find phones missing in master
        missing = phones - master_phones
        if missing:
            missing_phones_by_db[db_name] = missing
        
        print(f"\n{db_name}:")
        print(f"  Contacts: {count}")
        print(f"  Phone numbers: {len(phones)}")
        print(f"  Missing in master: {len(missing)}")
        
        if missing and len(missing) <= 10:
            print("  Missing numbers:")
            for phone in sorted(missing)[:10]:
                print(f"    {phone}")
    else:
        print(f"\n{db_name}: Not found (skipped)")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total unique phones in original databases: {len(all_original_phones)}")
print(f"Total unique phones in master: {len(master_phones)}")
print(f"Missing phones: {len(all_original_phones - master_phones)}")

# Check cleaned databases too
print("\nChecking cleaned databases (what we actually merged):")
print("-" * 80)

all_cleaned_phones = set()
for db_name, db_path in cleaned_dbs.items():
    if os.path.exists(db_path):
        phones, count = extract_phones_from_vcf(db_path)
        all_cleaned_phones.update(phones)
        missing = phones - master_phones
        
        print(f"\n{db_name}:")
        print(f"  Phone numbers: {len(phones)}")
        print(f"  Missing in master: {len(missing)}")

print(f"\nTotal unique phones in cleaned databases: {len(all_cleaned_phones)}")
print(f"Missing from cleaned to master: {len(all_cleaned_phones - master_phones)}")

# Show some examples of missing phones if any
all_missing = all_original_phones - master_phones
if all_missing:
    print(f"\nExamples of missing phone numbers (showing first 20):")
    for i, phone in enumerate(sorted(all_missing)[:20]):
        print(f"  {i+1}. {phone}")
        # Try to find which database it came from
        sources = []
        for db_name, missing_set in missing_phones_by_db.items():
            if phone in missing_set:
                sources.append(db_name)
        if sources:
            print(f"     From: {', '.join(sources)}")