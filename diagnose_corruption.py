#!/usr/bin/env python3
"""Diagnose and fix corrupted vCards"""

import re

def diagnose_corruption():
    """Check for corrupted vCards in the cleaned file"""
    
    with open('/Users/lukaskinigadner/Developer/Private/ContactPlus/data/Sara_Export_CLEANED_20250605.vcf', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all vCards
    vcards = re.findall(r'BEGIN:VCARD.*?END:VCARD', content, re.DOTALL)
    
    print(f"Total vCards: {len(vcards)}")
    
    corrupted = []
    
    for i, vcard in enumerate(vcards):
        # Check if N field contains VCARD
        if re.search(r'N:.*VCARD', vcard, re.DOTALL):
            fn_match = re.search(r'FN:(.+)', vcard)
            name = fn_match.group(1).strip() if fn_match else f"Contact #{i+1}"
            
            # Check size
            size_kb = len(vcard.encode('utf-8')) / 1024
            
            corrupted.append({
                'index': i + 1,
                'name': name,
                'size_kb': size_kb
            })
    
    print(f"\nFound {len(corrupted)} corrupted vCards with VCARD data in N field:")
    for c in corrupted[:10]:
        print(f"  #{c['index']}: {c['name']} ({c['size_kb']:.0f} KB)")
    
    if len(corrupted) > 10:
        print(f"  ... and {len(corrupted) - 10} more")
    
    return corrupted

def create_fixed_version():
    """Create a version without corrupted vCards"""
    
    with open('/Users/lukaskinigadner/Developer/Private/ContactPlus/data/Sara_Export_CLEANED_20250605.vcf', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Process line by line to fix corruption
    lines = content.split('\n')
    fixed_lines = []
    in_n_field = False
    skip_until_end = False
    skipped_count = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if skip_until_end:
            if line.strip() == 'END:VCARD':
                skip_until_end = False
                skipped_count += 1
            i += 1
            continue
        
        if line.startswith('N:') and 'VCARD' in line:
            # Found corrupted N field
            print(f"Found corrupted N field at line {i+1}")
            # Skip this entire vCard
            skip_until_end = True
            # Go back to find BEGIN:VCARD
            j = i - 1
            while j >= 0 and not lines[j].strip().startswith('BEGIN:VCARD'):
                j -= 1
            # Remove already added lines for this vCard
            while fixed_lines and not fixed_lines[-1].strip().startswith('BEGIN:VCARD'):
                fixed_lines.pop()
            if fixed_lines and fixed_lines[-1].strip().startswith('BEGIN:VCARD'):
                fixed_lines.pop()
        else:
            fixed_lines.append(line)
        
        i += 1
    
    # Write fixed version
    output_file = '/Users/lukaskinigadner/Developer/Private/ContactPlus/data/Sara_Export_CLEANED_20250605_fixed.vcf'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print(f"\nCreated fixed file: {output_file}")
    print(f"Removed {skipped_count} corrupted vCards")
    
    # Count remaining vCards
    remaining = len(re.findall(r'BEGIN:VCARD', '\n'.join(fixed_lines)))
    print(f"Remaining valid vCards: {remaining}")

if __name__ == "__main__":
    corrupted = diagnose_corruption()
    if corrupted:
        print("\nCreating fixed version...")
        create_fixed_version()