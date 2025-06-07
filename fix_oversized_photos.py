#!/usr/bin/env python3
"""Fix oversized vCards by compressing photos to meet iCloud limits"""
import re
import base64
from io import BytesIO
from PIL import Image

def compress_photo(base64_data, max_size_kb=200):
    """Compress a base64 photo to fit within size limit"""
    try:
        # Decode base64 to image
        img_data = base64.b64decode(base64_data)
        img = Image.open(BytesIO(img_data))
        
        # Start with original quality
        quality = 95
        output = BytesIO()
        
        # Keep reducing quality until it fits
        while quality > 10:
            output.seek(0)
            output.truncate()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            
            # Check size
            size_kb = len(output.getvalue()) / 1024
            if size_kb <= max_size_kb:
                break
            
            # Reduce quality
            quality -= 5
        
        # If still too large, resize image
        if len(output.getvalue()) / 1024 > max_size_kb:
            # Reduce dimensions
            width, height = img.size
            scale = 0.8
            while len(output.getvalue()) / 1024 > max_size_kb and scale > 0.1:
                new_width = int(width * scale)
                new_height = int(height * scale)
                resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                output.seek(0)
                output.truncate()
                resized.save(output, format='JPEG', quality=quality, optimize=True)
                scale -= 0.1
        
        # Encode back to base64
        return base64.b64encode(output.getvalue()).decode('ascii')
        
    except Exception as e:
        print(f"  Error processing photo: {e}")
        return None

def fix_oversized_vcards():
    """Fix oversized vCards by compressing photos"""
    print("Fixing oversized vCards in Sara's database...")
    
    with open("data/Sara_Export_IMPORT_READY.vcf", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all vCards
    vcards = re.findall(r'BEGIN:VCARD.*?END:VCARD', content, re.DOTALL)
    
    fixed_vcards = []
    fixed_count = 0
    
    for i, vcard in enumerate(vcards):
        vcard_size = len(vcard.encode('utf-8'))
        
        # Check if oversized (256KB limit)
        if vcard_size > 256 * 1024:
            # Extract name for reporting
            name_match = re.search(r'FN:(.+)', vcard)
            name = name_match.group(1) if name_match else f"Contact #{i+1}"
            
            print(f"\nFixing {name} ({vcard_size // 1024} KB)...")
            
            # Find photo data
            photo_match = re.search(r'PHOTO;[^:]+:([A-Za-z0-9+/\r\n]+={0,2})', vcard)
            
            if photo_match:
                old_photo = photo_match.group(1)
                # Remove newlines from base64
                clean_photo = old_photo.replace('\n', '').replace('\r', '')
                
                # Compress photo
                new_photo = compress_photo(clean_photo, max_size_kb=200)
                
                if new_photo:
                    # Replace photo in vCard
                    vcard = vcard.replace(old_photo, new_photo)
                    new_size = len(vcard.encode('utf-8'))
                    print(f"  Compressed to {new_size // 1024} KB")
                    fixed_count += 1
                else:
                    print(f"  Failed to compress, removing photo")
                    # Remove entire PHOTO line if compression failed
                    vcard = re.sub(r'PHOTO;[^:]+:[A-Za-z0-9+/\r\n]+={0,2}\r?\n', '', vcard)
                    fixed_count += 1
        
        fixed_vcards.append(vcard)
    
    # Write fixed file
    output_file = "data/Sara_Export_ICLOUD_READY.vcf"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_vcards))
    
    print(f"\n✅ Fixed {fixed_count} oversized vCards")
    print(f"✅ Created: {output_file}")
    print(f"\nThis file is ready for iCloud.com import!")

if __name__ == "__main__":
    fix_oversized_vcards()