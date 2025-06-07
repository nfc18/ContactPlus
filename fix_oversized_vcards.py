#!/usr/bin/env python3
"""Fix oversized vCards by resizing photos to meet iCloud limits"""

import re
import base64
from io import BytesIO
from PIL import Image
import config

def resize_photo_data(base64_data, max_size_kb=200):
    """Resize a base64 encoded photo to fit within size limit"""
    try:
        # Decode base64
        img_data = base64.b64decode(base64_data)
        img = Image.open(BytesIO(img_data))
        
        # Start with current size
        quality = 95
        scale = 1.0
        
        while True:
            # Resize if needed
            if scale < 1.0:
                new_size = (int(img.width * scale), int(img.height * scale))
                resized = img.resize(new_size, Image.Resampling.LANCZOS)
            else:
                resized = img
            
            # Save to buffer
            buffer = BytesIO()
            resized.save(buffer, format='JPEG', quality=quality, optimize=True)
            
            # Check size
            size_kb = len(buffer.getvalue()) / 1024
            if size_kb <= max_size_kb:
                # Encode back to base64
                return base64.b64encode(buffer.getvalue()).decode('ascii')
            
            # Reduce quality or scale
            if quality > 60:
                quality -= 10
            else:
                scale *= 0.9
                quality = 85
            
            if scale < 0.3:
                # Too small, give up
                return None
                
    except Exception as e:
        print(f"Error resizing photo: {e}")
        return None

def analyze_and_show_oversized(filename):
    """Show oversized vCards and their details"""
    
    print("Analyzing oversized vCards...")
    print("="*60)
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    vcards = re.findall(r'BEGIN:VCARD.*?END:VCARD', content, re.DOTALL)
    
    oversized = []
    
    for i, vcard in enumerate(vcards):
        vcard_size = len(vcard.encode('utf-8'))
        
        if vcard_size > 256 * 1024:  # 256KB
            fn_match = re.search(r'FN:(.+)', vcard)
            name = fn_match.group(1).strip() if fn_match else f"Contact #{i+1}"
            
            # Check what's taking up space
            has_photo = 'PHOTO;ENCODING=b' in vcard
            photo_size = 0
            
            if has_photo:
                photo_match = re.search(r'PHOTO;ENCODING=b[^\n]*\n((?:[^\n]*\n)*?)(?=\w+:|END:VCARD)', vcard)
                if photo_match:
                    base64_data = photo_match.group(1).replace('\n', '').replace(' ', '')
                    photo_size = len(base64_data) * 0.75 / 1024  # KB
            
            # Check for long notes
            note_match = re.search(r'NOTE:(.+?)(?=\n\w+:|END:VCARD)', vcard, re.DOTALL)
            note_size = len(note_match.group(1).encode('utf-8')) / 1024 if note_match else 0
            
            oversized.append({
                'index': i + 1,
                'name': name,
                'total_size_kb': vcard_size / 1024,
                'has_photo': has_photo,
                'photo_size_kb': photo_size,
                'note_size_kb': note_size,
                'vcard': vcard
            })
    
    print(f"Found {len(oversized)} oversized vCards:\n")
    
    for contact in oversized:
        print(f"#{contact['index']}: {contact['name']}")
        print(f"  Total size: {contact['total_size_kb']:.0f} KB")
        if contact['has_photo']:
            print(f"  Photo size: {contact['photo_size_kb']:.0f} KB")
        if contact['note_size_kb'] > 1:
            print(f"  Note size: {contact['note_size_kb']:.0f} KB")
        print()
    
    return oversized

def create_fixed_version():
    """Create a version with resized photos"""
    print("\nWould you like me to:")
    print("1. Show details of each oversized contact")
    print("2. Create a version with automatically resized photos")
    print("3. Export the oversized contacts separately for manual review")
    
    # For now, let's export them separately
    oversized = analyze_and_show_oversized(config.PROCESSED_VCARD_FILE)
    
    # Export oversized contacts
    with open('data/oversized_contacts.vcf', 'w', encoding='utf-8') as f:
        for contact in oversized:
            f.write(contact['vcard'])
    
    print(f"\nExported {len(oversized)} oversized contacts to: data/oversized_contacts.vcf")
    print("\nThese contacts need manual review to decide how to handle them.")

if __name__ == "__main__":
    create_fixed_version()