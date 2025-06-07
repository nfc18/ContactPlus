#!/usr/bin/env python3
"""Remove photos and fix vCards for iCloud.com compatibility"""

import re

def clean_vcards_for_web(input_file):
    """Clean vCards for web import by removing photos and fixing issues"""
    
    print(f"Cleaning {input_file} for web import...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove all PHOTO fields (they span multiple lines)
    content = re.sub(r'PHOTO;[^\n]*\n(?:[^\n]*\n)*?(?=\w+:|END:VCARD)', '', content, flags=re.MULTILINE)
    
    # Fix empty N fields
    content = re.sub(r'N:;*\s*\n', 'N:;;;;\\n', content)
    
    # Remove any remaining base64 encoded data
    content = re.sub(r'^[A-Za-z0-9+/=]{76,}$', '', content, flags=re.MULTILINE)
    
    # Clean up extra blank lines
    content = re.sub(r'\n\n+', '\n', content)
    
    # Split into individual vCards
    vcards = re.findall(r'BEGIN:VCARD.*?END:VCARD', content, re.DOTALL)
    
    cleaned_vcards = []
    skipped_count = 0
    
    for vcard in vcards:
        # Check if vCard has FN field
        if 'FN:' not in vcard:
            skipped_count += 1
            print(f"  Skipping vCard without FN field")
            continue
            
        # Extract FN value to check if it's empty
        fn_match = re.search(r'FN:(.+)', vcard)
        if fn_match:
            fn_value = fn_match.group(1).strip()
            if not fn_value:
                skipped_count += 1
                print(f"  Skipping vCard with empty FN field")
                continue
        
        # Ensure each vCard ends with a newline after END:VCARD
        vcard = vcard.strip() + '\n'
        cleaned_vcards.append(vcard)
    
    if skipped_count > 0:
        print(f"  Skipped {skipped_count} contacts without names")
    
    return cleaned_vcards

def process_all_chunks():
    """Process all chunk files"""
    import os
    
    data_dir = "/Users/lukaskinigadner/Developer/Private/ContactPlus/data/"
    
    # Find all chunk files
    chunk_files = [f for f in os.listdir(data_dir) if f.startswith('Sara_Export_CLEANED_20250605_unix_chunk') and f.endswith('.vcf')]
    chunk_files.sort()
    
    for chunk_file in chunk_files:
        input_path = os.path.join(data_dir, chunk_file)
        output_path = input_path.replace('_unix_chunk', '_web_chunk')
        
        cleaned_vcards = clean_vcards_for_web(input_path)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for vcard in cleaned_vcards:
                f.write(vcard)
        
        print(f"Created: {output_path} ({len(cleaned_vcards)} contacts)")
    
    print("\n✅ Created web-compatible versions of all chunks")
    print("\nThese files have:")
    print("- No embedded photos")
    print("- Fixed empty N fields")
    print("- Proper line endings")
    print("\nTry importing the '_web_chunk' files to iCloud.com")

if __name__ == "__main__":
    process_all_chunks()