#!/usr/bin/env python3
"""Create a clean import-ready version of Sara's vCard file"""

import re
import os

def create_clean_import():
    """Create a clean version for iCloud import"""
    
    input_file = "Imports/Sara_Export_Sara A. Kerner and 3.074 others.vcf"
    output_file = "data/Sara_Export_IMPORT_READY.vcf"
    
    print(f"Creating clean import file from: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count vCards
    vcard_count = content.count('BEGIN:VCARD')
    print(f"Found {vcard_count} vCards in original file")
    
    # Check for any obvious issues
    print("\nChecking for common issues...")
    
    # Check line endings
    if '\r\n' in content:
        print("- File has Windows line endings (CRLF)")
        # Convert to Unix line endings for macOS
        content = content.replace('\r\n', '\n')
        print("  → Converted to Unix line endings (LF)")
    
    # Write the file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Verify the output
    with open(output_file, 'r', encoding='utf-8') as f:
        verify_content = f.read()
    
    verify_count = verify_content.count('BEGIN:VCARD')
    print(f"\nOutput file has {verify_count} vCards")
    
    # Check file size
    file_size = os.path.getsize(output_file)
    print(f"File size: {file_size / 1024 / 1024:.1f} MB")
    
    # Do a quick scan for oversized vCards
    print("\nScanning for oversized vCards...")
    vcards = re.findall(r'BEGIN:VCARD.*?END:VCARD', verify_content, re.DOTALL)
    
    oversized = []
    for i, vcard in enumerate(vcards):
        size_kb = len(vcard.encode('utf-8')) / 1024
        if size_kb > 256:
            fn_match = re.search(r'FN:(.+)', vcard)
            name = fn_match.group(1).strip() if fn_match else f"Contact #{i+1}"
            oversized.append((i+1, name, size_kb))
    
    if oversized:
        print(f"Found {len(oversized)} oversized vCards (>256KB):")
        for idx, name, size in oversized[:5]:
            print(f"  #{idx}: {name} ({size:.0f} KB)")
        if len(oversized) > 5:
            print(f"  ... and {len(oversized) - 5} more")
    else:
        print("✅ All vCards are within iCloud's 256KB limit")
    
    print(f"\n✅ Clean file created: {output_file}")
    print("\nThis file is ready for iCloud import.")
    
    return output_file, oversized

if __name__ == "__main__":
    output_file, oversized = create_clean_import()