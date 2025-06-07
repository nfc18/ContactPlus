#!/usr/bin/env python3
"""Remove photos from oversized vCards to make them iCloud compatible"""
import re

def remove_large_photos():
    """Remove photos from vCards that are too large"""
    print("Removing photos from oversized vCards...")
    
    with open("data/Sara_Export_IMPORT_READY.vcf", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Process each vCard
    vcards = []
    current_vcard = []
    in_vcard = False
    
    for line in content.split('\n'):
        if line.strip() == 'BEGIN:VCARD':
            in_vcard = True
            current_vcard = [line]
        elif line.strip() == 'END:VCARD':
            current_vcard.append(line)
            
            # Check vCard size
            vcard_text = '\n'.join(current_vcard)
            size_kb = len(vcard_text.encode('utf-8')) / 1024
            
            if size_kb > 256:
                # Find name for logging
                name = "Unknown"
                for vline in current_vcard:
                    if vline.startswith('FN:'):
                        name = vline[3:]
                        break
                
                print(f"  Removing photo from {name} ({size_kb:.0f} KB)")
                
                # Remove PHOTO lines
                cleaned_vcard = []
                skip_continuation = False
                
                for vline in current_vcard:
                    # Skip PHOTO lines and their continuations
                    if vline.startswith('PHOTO;') or vline.startswith('PHOTO:'):
                        skip_continuation = True
                        continue
                    elif skip_continuation and (vline.startswith(' ') or vline.startswith('\t')):
                        # Skip continuation lines
                        continue
                    else:
                        skip_continuation = False
                        cleaned_vcard.append(vline)
                
                vcards.append('\n'.join(cleaned_vcard))
            else:
                vcards.append(vcard_text)
            
            current_vcard = []
            in_vcard = False
        elif in_vcard:
            current_vcard.append(line)
    
    # Write cleaned file
    output_file = "data/Sara_Export_ICLOUD_FINAL.vcf"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(vcards))
    
    print(f"\n✅ Created: {output_file}")
    
    # Verify all are under limit
    with open(output_file, 'r', encoding='utf-8') as f:
        verify_content = f.read()
    
    verify_vcards = re.findall(r'BEGIN:VCARD.*?END:VCARD', verify_content, re.DOTALL)
    oversized_count = sum(1 for v in verify_vcards if len(v.encode('utf-8')) > 256 * 1024)
    
    print(f"✅ Total vCards: {len(verify_vcards)}")
    print(f"✅ Oversized vCards: {oversized_count}")
    
    if oversized_count == 0:
        print("\n🎉 All vCards are now under 256KB!")
        print("🎉 Ready for iCloud.com import!")

if __name__ == "__main__":
    remove_large_photos()