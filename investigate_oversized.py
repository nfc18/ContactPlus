#!/usr/bin/env python3
"""Investigate what's causing oversized vCards"""

import re

def investigate_oversized():
    """Check what fields are causing the large sizes"""
    
    with open('data/oversized_contacts.vcf', 'r', encoding='utf-8') as f:
        content = f.read()
    
    vcards = re.findall(r'BEGIN:VCARD.*?END:VCARD', content, re.DOTALL)
    
    print(f"Investigating {len(vcards)} oversized vCards...")
    print("="*60)
    
    for i, vcard in enumerate(vcards[:3]):  # Check first 3 in detail
        fn_match = re.search(r'FN:(.+)', vcard)
        name = fn_match.group(1).strip() if fn_match else f"Contact #{i+1}"
        
        print(f"\n{name}:")
        print(f"Total size: {len(vcard.encode('utf-8')) / 1024:.0f} KB")
        
        # Check each field type
        fields = {}
        
        # Common fields
        for field in ['FN', 'N', 'ORG', 'TITLE', 'TEL', 'EMAIL', 'ADR', 'URL', 'NOTE']:
            pattern = rf'{field}[^:]*:.*?(?=\n(?:[A-Z]+:|END:VCARD))'
            matches = re.findall(pattern, vcard, re.DOTALL)
            if matches:
                total_size = sum(len(m.encode('utf-8')) for m in matches)
                if total_size > 100:  # Only show if significant
                    fields[field] = total_size / 1024
        
        # Check for item fields (URLs, labels, etc.)
        item_matches = re.findall(r'item\d+\.[^:]+:.*', vcard)
        if item_matches:
            total_size = sum(len(m.encode('utf-8')) for m in item_matches)
            fields['item fields'] = total_size / 1024
        
        # Check for X- fields
        x_matches = re.findall(r'X-[^:]+:.*', vcard)
        if x_matches:
            total_size = sum(len(m.encode('utf-8')) for m in x_matches)
            fields['X- fields'] = total_size / 1024
        
        # Sort by size
        sorted_fields = sorted(fields.items(), key=lambda x: x[1], reverse=True)
        
        print("\nField sizes:")
        for field, size_kb in sorted_fields:
            print(f"  {field}: {size_kb:.1f} KB")
        
        # Show first few lines of largest field
        if sorted_fields:
            largest_field = sorted_fields[0][0]
            if largest_field != 'item fields' and largest_field != 'X- fields':
                pattern = rf'{largest_field}[^:]*:(.*?)(?=\n(?:[A-Z]+:|END:VCARD))'
                match = re.search(pattern, vcard, re.DOTALL)
                if match:
                    content = match.group(1).strip()
                    preview = content[:200] + '...' if len(content) > 200 else content
                    print(f"\n  Preview of {largest_field}: {preview}")

if __name__ == "__main__":
    investigate_oversized()