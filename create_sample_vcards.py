#!/usr/bin/env python3
"""
Create a sample vCard file for testing the complete workflow
"""

import vobject

# Read first 10 vCards from Sara's file
input_file = "/Users/lk/Documents/Developer/Private/ContactPlus/Imports/Sara_Export_Sara A. Kerner and 3.074 others.vcf"
output_file = "sample_10_vcards.vcf"

with open(input_file, 'r', encoding='utf-8') as f:
    vcard_data = f.read()

vcards = list(vobject.readComponents(vcard_data))[:10]

# Add some soft compliance issues to demonstrate
if len(vcards) > 2:
    # Make one name all caps
    if hasattr(vcards[2], 'fn'):
        vcards[2].fn.value = vcards[2].fn.value.upper()
    
    # Add email to notes
    if hasattr(vcards[3], 'note'):
        vcards[3].note.value += " Contact: test@example.com"
    else:
        vcards[3].add('note')
        vcards[3].note.value = "Contact: test@example.com"

# Write sample file
with open(output_file, 'w', encoding='utf-8') as f:
    for vcard in vcards:
        f.write(vcard.serialize())

print(f"Created {output_file} with {len(vcards)} vCards")