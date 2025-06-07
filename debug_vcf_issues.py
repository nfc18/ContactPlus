#!/usr/bin/env python3
"""Debug vCard issues that might prevent iCloud import"""
import re

def debug_vcards():
    """Check for various vCard issues"""
    print("Debugging vCard file for iCloud compatibility...\n")
    
    with open("data/Sara_Export_ICLOUD_FINAL.vcf", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check line endings
    if '\r\n' in content:
        print("❌ File has Windows (CRLF) line endings")
    else:
        print("✅ File has Unix (LF) line endings")
    
    # Check for BOM
    if content.startswith('\ufeff'):
        print("❌ File has BOM (Byte Order Mark)")
    else:
        print("✅ No BOM found")
    
    # Check vCard structure
    vcards = content.split('BEGIN:VCARD')
    vcards = ['BEGIN:VCARD' + v for v in vcards[1:]]  # Skip empty first element
    
    print(f"\nTotal vCard blocks: {len(vcards)}")
    
    # Check for common issues
    issues = {
        'missing_end': 0,
        'missing_version': 0,
        'missing_fn': 0,
        'empty_lines': 0,
        'long_lines': 0,
        'special_chars': 0,
        'malformed': 0
    }
    
    for i, vcard in enumerate(vcards):
        # Check END:VCARD
        if not vcard.strip().endswith('END:VCARD'):
            issues['missing_end'] += 1
            print(f"  ❌ vCard {i+1} missing END:VCARD")
        
        # Check VERSION
        if 'VERSION:' not in vcard:
            issues['missing_version'] += 1
        
        # Check FN
        if 'FN:' not in vcard:
            issues['missing_fn'] += 1
            
        # Check for empty lines within vCard
        lines = vcard.split('\n')
        for line in lines[1:-1]:  # Skip BEGIN and END
            if line.strip() == '':
                issues['empty_lines'] += 1
                break
                
        # Check for overly long lines
        for line in lines:
            if len(line) > 998:  # RFC limit
                issues['long_lines'] += 1
                break
    
    # Print summary
    print("\nIssue Summary:")
    print(f"  Missing END:VCARD: {issues['missing_end']}")
    print(f"  Missing VERSION: {issues['missing_version']}")
    print(f"  Missing FN: {issues['missing_fn']}")
    print(f"  Empty lines in vCard: {issues['empty_lines']}")
    print(f"  Lines too long: {issues['long_lines']}")
    
    # Check encoding
    try:
        content.encode('ascii')
        print("\n✅ File is pure ASCII")
    except UnicodeEncodeError:
        print("\n⚠️  File contains non-ASCII characters (this is usually OK)")
    
    # Sample first vCard
    print("\nFirst vCard sample:")
    print("-" * 50)
    first_vcard = vcards[0] if vcards else ""
    print(first_vcard[:500] + "..." if len(first_vcard) > 500 else first_vcard)

if __name__ == "__main__":
    debug_vcards()