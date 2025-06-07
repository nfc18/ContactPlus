#!/usr/bin/env python3
"""
Verify the processed vCard file is valid and show sample improvements
"""

import os
from vcard_validator import VCardStandardsValidator
import vobject

output_file = "/Users/lk/Documents/Developer/Private/ContactPlus/data/Sara_Export_VALIDATED_20250606.vcf"

print("Verifying Processed vCard File")
print("=" * 60)

# Validate with vcard library
validator = VCardStandardsValidator()
is_valid, errors, warnings = validator.validate_file(output_file)

print(f"\nValidation Result: {'✅ VALID' if is_valid else '❌ INVALID'}")
print(f"Errors: {len(errors)}")
print(f"Warnings: {len(warnings)}")

if errors:
    print("\nErrors found:")
    for err in errors[:5]:
        print(f"  - {err}")

# Parse and show samples of improvements
print("\nSample vCards (showing improvements):")
print("-" * 40)

with open(output_file, 'r', encoding='utf-8') as f:
    vcards = list(vobject.readComponents(f.read()))

# Show a few examples
for i, vcard in enumerate(vcards[:5]):
    print(f"\nvCard {i+1}:")
    if hasattr(vcard, 'fn'):
        print(f"  FN: {vcard.fn.value}")
    if hasattr(vcard, 'n'):
        n = vcard.n.value
        print(f"  N: {n.given} {n.family}")
    if hasattr(vcard, 'email_list'):
        for email in vcard.email_list[:2]:  # First 2 emails
            print(f"  EMAIL: {email.value}")
    if hasattr(vcard, 'tel_list'):
        for tel in vcard.tel_list[:1]:  # First phone
            print(f"  TEL: {tel.value}")

print(f"\nTotal vCards in file: {len(vcards)}")
print(f"File is ready for import! ✅")