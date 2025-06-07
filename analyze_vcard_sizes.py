#!/usr/bin/env python3
"""Analyze vCard sizes to identify which ones exceed iCloud limits"""

import re

def analyze_vcard_sizes(filename):
    """Check each vCard size against iCloud limits"""
    
    print(f"Analyzing vCard sizes in {filename}...")
    print(f"iCloud limits: Max 256KB per vCard, max 224KB per photo")
    print("="*60)
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all vCards
    vcards = re.findall(r'BEGIN:VCARD.*?END:VCARD', content, re.DOTALL)
    
    oversized_contacts = []
    photo_issues = []
    total_size = 0
    
    for i, vcard in enumerate(vcards):
        # Calculate size in bytes
        vcard_size = len(vcard.encode('utf-8'))
        total_size += vcard_size
        
        # Extract contact name
        fn_match = re.search(r'FN:(.+)', vcard)
        name = fn_match.group(1).strip() if fn_match else f"Contact #{i+1}"
        
        # Check if oversized
        if vcard_size > 256 * 1024:  # 256KB
            oversized_contacts.append({
                'name': name,
                'size': vcard_size,
                'size_mb': vcard_size / 1024 / 1024,
                'index': i + 1
            })
        
        # Check for photos
        if 'PHOTO;ENCODING=b' in vcard:
            # Estimate photo size (base64 is ~1.33x original)
            photo_match = re.search(r'PHOTO;ENCODING=b[^\n]*\n((?:[^\n]*\n)*?)(?=\w+:|END:VCARD)', vcard)
            if photo_match:
                base64_data = photo_match.group(1).replace('\n', '').replace(' ', '')
                estimated_size = len(base64_data) * 0.75  # Convert from base64 to bytes
                if estimated_size > 224 * 1024:  # 224KB
                    photo_issues.append({
                        'name': name,
                        'photo_size': estimated_size,
                        'photo_size_kb': estimated_size / 1024,
                        'index': i + 1
                    })
    
    # Print results
    print(f"\nTotal vCards: {len(vcards)}")
    print(f"Total file size: {total_size / 1024 / 1024:.1f} MB")
    print(f"Average vCard size: {total_size / len(vcards) / 1024:.1f} KB")
    
    if oversized_contacts:
        print(f"\n❌ Found {len(oversized_contacts)} vCards exceeding 256KB limit:")
        for contact in oversized_contacts[:10]:  # Show first 10
            print(f"  - {contact['name']}: {contact['size_mb']:.2f} MB (vCard #{contact['index']})")
        if len(oversized_contacts) > 10:
            print(f"  ... and {len(oversized_contacts) - 10} more")
    else:
        print(f"\n✅ All vCards are within the 256KB size limit")
    
    if photo_issues:
        print(f"\n⚠️  Found {len(photo_issues)} vCards with photos exceeding 224KB:")
        for contact in photo_issues[:5]:
            print(f"  - {contact['name']}: {contact['photo_size_kb']:.0f} KB photo (vCard #{contact['index']})")
        if len(photo_issues) > 5:
            print(f"  ... and {len(photo_issues) - 5} more")
    
    print(f"\n\nRecommendations:")
    if oversized_contacts:
        print("1. The oversized vCards need to be fixed before import")
        print("2. Options:")
        print("   - Reduce photo sizes in these contacts")
        print("   - Remove excessive notes or other data")
        print("   - Split into multiple contacts if they contain multiple people")
    else:
        print("✅ File should be compatible with iCloud import")
    
    return oversized_contacts, photo_issues

if __name__ == "__main__":
    import config
    oversized, photos = analyze_vcard_sizes(config.PROCESSED_VCARD_FILE)