#!/usr/bin/env python3
"""Examine oversized vCards to understand the issue"""

import re

def examine_oversized():
    """Look at what's making vCards oversized"""
    
    with open("data/Sara_Export_IMPORT_READY.vcf", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find Daniel Albertini's vCard
    vcards = re.findall(r'BEGIN:VCARD.*?END:VCARD', content, re.DOTALL)
    
    print("Looking for Daniel Albertini (vCard #30)...")
    
    daniel_vcard = vcards[29]  # 0-indexed
    
    # Check size
    size_kb = len(daniel_vcard.encode('utf-8')) / 1024
    print(f"\nTotal size: {size_kb:.0f} KB")
    
    # Extract components
    lines = daniel_vcard.split('\n')
    print(f"Total lines: {len(lines)}")
    
    # Look for photo
    photo_lines = []
    in_photo = False
    for line in lines:
        if line.startswith('PHOTO'):
            in_photo = True
        if in_photo:
            photo_lines.append(line)
            if line and not line.startswith(' ') and not line.startswith('PHOTO'):
                break
    
    if photo_lines:
        photo_data = '\n'.join(photo_lines)
        photo_size_kb = len(photo_data.encode('utf-8')) / 1024
        print(f"\nPhoto field size: {photo_size_kb:.0f} KB")
        print(f"Photo is {photo_size_kb/size_kb*100:.1f}% of the vCard")
    
    # Show first few lines
    print("\nFirst 20 lines of vCard:")
    for i, line in enumerate(lines[:20]):
        if len(line) > 100:
            print(f"{i+1}: {line[:100]}...")
        else:
            print(f"{i+1}: {line}")

if __name__ == "__main__":
    examine_oversized()