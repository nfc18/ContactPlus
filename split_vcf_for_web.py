#!/usr/bin/env python3
"""Split vCard file into smaller chunks for iCloud.com import"""

import re

def split_vcf_file(input_file, chunk_size=100):
    """Split vCard file into smaller chunks"""
    
    print(f"Splitting {input_file} into chunks of {chunk_size} contacts...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all vCards
    vcards = re.findall(r'BEGIN:VCARD.*?END:VCARD', content, re.DOTALL)
    
    print(f"Found {len(vcards)} contacts")
    
    # Create chunks
    total_chunks = (len(vcards) + chunk_size - 1) // chunk_size
    
    for i in range(total_chunks):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, len(vcards))
        
        chunk_filename = input_file.replace('.vcf', f'_chunk{i+1:02d}.vcf')
        
        with open(chunk_filename, 'w', encoding='utf-8') as f:
            for vcard in vcards[start:end]:
                f.write(vcard + '\n')
        
        print(f"Created: {chunk_filename} ({end - start} contacts)")
    
    print(f"\nCreated {total_chunks} files.")
    print("\nTo import to iCloud.com:")
    print("1. Go to icloud.com and sign in")
    print("2. Open Contacts")
    print("3. Click the gear icon (settings) at bottom left")
    print("4. Choose 'Import vCard...'")
    print("5. Select each chunk file one by one")
    print("\nStart with chunk01 and work your way up.")

if __name__ == "__main__":
    # Use the Unix line endings version
    input_file = "/Users/lukaskinigadner/Developer/Private/ContactPlus/data/Sara_Export_CLEANED_20250605_unix.vcf"
    split_vcf_file(input_file, chunk_size=100)