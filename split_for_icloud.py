#!/usr/bin/env python3
"""Split vCard file into smaller chunks for iCloud.com"""
import re

def split_for_icloud():
    """Split into smaller files for easier import"""
    print("Splitting vCard file for iCloud.com import...")
    
    with open("data/Sara_Export_READY_FOR_ICLOUD.vcf", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all vCards
    vcards = re.findall(r'BEGIN:VCARD.*?END:VCARD', content, re.DOTALL)
    
    # Split into chunks of 500 contacts
    chunk_size = 500
    
    for i in range(0, len(vcards), chunk_size):
        chunk = vcards[i:i+chunk_size]
        chunk_num = (i // chunk_size) + 1
        
        filename = f"data/icloud_import_part{chunk_num:02d}.vcf"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(chunk))
        
        print(f"  Created {filename} ({len(chunk)} contacts)")
    
    total_files = (len(vcards) + chunk_size - 1) // chunk_size
    print(f"\n✅ Split into {total_files} files")
    print("\nImport instructions:")
    print("1. Go to icloud.com → Contacts")
    print("2. Import each file one by one, starting with part01")
    print("3. Wait for each import to complete before importing the next")

if __name__ == "__main__":
    split_for_icloud()