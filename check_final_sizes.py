#!/usr/bin/env python3
"""Quick check of vCard sizes in the final file"""
import re

def check_sizes():
    with open("data/Sara_Export_ICLOUD_READY.vcf", 'r', encoding='utf-8') as f:
        content = f.read()
    
    vcards = re.findall(r'BEGIN:VCARD.*?END:VCARD', content, re.DOTALL)
    
    oversized = []
    for i, vcard in enumerate(vcards):
        size_kb = len(vcard.encode('utf-8')) / 1024
        if size_kb > 256:
            name_match = re.search(r'FN:(.+)', vcard)
            name = name_match.group(1) if name_match else f"Contact #{i+1}"
            oversized.append((name, size_kb))
    
    print(f"Total vCards: {len(vcards)}")
    print(f"Oversized vCards (>256KB): {len(oversized)}")
    
    if oversized:
        print("\nStill oversized:")
        for name, size in oversized:
            print(f"  {name}: {size:.0f} KB")
    else:
        print("\n✅ All vCards are under 256KB limit!")
        print("✅ Ready for iCloud.com import!")

if __name__ == "__main__":
    check_sizes()