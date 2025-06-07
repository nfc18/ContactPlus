#!/usr/bin/env python3
"""Validate and identify problematic vCards in a chunk"""

import re

def validate_chunk(filename):
    """Check each vCard in the chunk for potential issues"""
    
    print(f"Validating {filename}...")
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all vCards
    vcards = re.findall(r'BEGIN:VCARD.*?END:VCARD', content, re.DOTALL)
    
    print(f"\nFound {len(vcards)} vCards in file")
    
    problematic = []
    
    for i, vcard in enumerate(vcards):
        issues = []
        
        # Check for required fields
        if 'FN:' not in vcard:
            issues.append("Missing FN field")
        
        # Check for empty N field
        if re.search(r'N:;*\s*\n', vcard):
            issues.append("Empty N field")
        
        # Check for special characters that might cause issues
        if '\x00' in vcard or '\x0b' in vcard or '\x0c' in vcard:
            issues.append("Contains control characters")
        
        # Check for extremely long lines
        lines = vcard.split('\n')
        for line in lines:
            if len(line) > 998:  # vCard line limit
                issues.append(f"Line too long: {len(line)} chars")
        
        # Check for missing VERSION
        if 'VERSION:' not in vcard:
            issues.append("Missing VERSION")
        
        # Extract contact name for reporting
        fn_match = re.search(r'FN:(.+)', vcard)
        name = fn_match.group(1).strip() if fn_match else "Unknown"
        
        if issues:
            problematic.append({
                'index': i + 1,
                'name': name,
                'issues': issues,
                'vcard': vcard[:200] + '...' if len(vcard) > 200 else vcard
            })
    
    # Report findings
    if problematic:
        print(f"\n⚠️  Found {len(problematic)} problematic vCards:")
        for p in problematic:
            print(f"\nContact #{p['index']}: {p['name']}")
            for issue in p['issues']:
                print(f"  - {issue}")
            print(f"  Preview: {p['vcard'][:100]}...")
    else:
        print("\n✅ All vCards appear valid")
    
    # Also check for specific patterns that might cause issues
    print("\n\nChecking for specific patterns...")
    
    # Check for base64 encoded photos
    photo_count = len(re.findall(r'PHOTO;ENCODING=b', content))
    if photo_count > 0:
        print(f"  - Found {photo_count} contacts with embedded photos")
    
    # Check for special characters in names
    special_chars = re.findall(r'FN:.*[<>"\'/\\|].*', content)
    if special_chars:
        print(f"  - Found {len(special_chars)} contacts with special characters in names")
        for sc in special_chars[:5]:
            print(f"    • {sc}")

if __name__ == "__main__":
    validate_chunk("/Users/lukaskinigadner/Developer/Private/ContactPlus/data/Sara_Export_CLEANED_20250605_unix_chunk01.vcf")