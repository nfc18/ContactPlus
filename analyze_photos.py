#!/usr/bin/env python3
"""
Analyze photos in the master phonebook
"""

import vobject
import base64
import os
from collections import Counter

def analyze_photos():
    """Analyze photos in the phonebook"""
    
    # Find latest phonebook
    import glob
    phonebook_files = glob.glob("data/MASTER_PHONEBOOK_*.vcf")
    if not phonebook_files:
        phonebook_files = glob.glob("data/FINAL_MASTER_CONTACTS_*.vcf")
    
    if not phonebook_files:
        print("❌ No master phonebook found!")
        return
    
    latest_phonebook = sorted(phonebook_files)[-1]
    print(f"Analyzing photos in: {os.path.basename(latest_phonebook)}")
    
    # Load contacts
    with open(latest_phonebook, 'r', encoding='utf-8') as f:
        contacts = list(vobject.readComponents(f.read()))
    
    print(f"✓ Loaded {len(contacts)} contacts")
    
    # Photo analysis
    photo_stats = {
        'total_contacts': len(contacts),
        'with_photos': 0,
        'without_photos': 0,
        'photo_sizes': [],
        'photo_formats': Counter(),
        'contacts_with_photos': []
    }
    
    for i, contact in enumerate(contacts):
        has_photo = False
        contact_name = contact.fn.value if hasattr(contact, 'fn') and contact.fn.value else f"Contact {i+1}"
        
        # Check for PHOTO property
        if hasattr(contact, 'photo'):
            has_photo = True
            try:
                photo_data = contact.photo.value
                
                # Try to determine format and size
                if isinstance(photo_data, str):
                    # Base64 encoded
                    try:
                        decoded = base64.b64decode(photo_data)
                        size = len(decoded)
                        photo_stats['photo_sizes'].append(size)
                        
                        # Try to detect format from data
                        if decoded.startswith(b'\xff\xd8\xff'):
                            photo_stats['photo_formats']['JPEG'] += 1
                        elif decoded.startswith(b'\x89PNG'):
                            photo_stats['photo_formats']['PNG'] += 1
                        elif decoded.startswith(b'GIF'):
                            photo_stats['photo_formats']['GIF'] += 1
                        else:
                            photo_stats['photo_formats']['Unknown'] += 1
                            
                    except Exception as e:
                        photo_stats['photo_formats']['Invalid Base64'] += 1
                        size = len(photo_data)
                        photo_stats['photo_sizes'].append(size)
                        
                elif isinstance(photo_data, bytes):
                    # Raw bytes
                    size = len(photo_data)
                    photo_stats['photo_sizes'].append(size)
                    
                    if photo_data.startswith(b'\xff\xd8\xff'):
                        photo_stats['photo_formats']['JPEG'] += 1
                    elif photo_data.startswith(b'\x89PNG'):
                        photo_stats['photo_formats']['PNG'] += 1
                    else:
                        photo_stats['photo_formats']['Unknown'] += 1
                else:
                    photo_stats['photo_formats']['Other'] += 1
                    size = 0
                    photo_stats['photo_sizes'].append(size)
                
                photo_stats['contacts_with_photos'].append({
                    'name': contact_name,
                    'size_bytes': size,
                    'size_kb': round(size / 1024, 1) if size > 0 else 0
                })
                    
            except Exception as e:
                print(f"Error processing photo for {contact_name}: {e}")
                photo_stats['photo_formats']['Error'] += 1
        
        # Also check for other photo properties (some vCards use different names)
        for attr_name in dir(contact):
            if 'photo' in attr_name.lower() and not attr_name.startswith('_'):
                if not has_photo:  # Only count if we haven't found a photo yet
                    has_photo = True
                    photo_stats['contacts_with_photos'].append({
                        'name': contact_name,
                        'size_bytes': 0,
                        'size_kb': 0,
                        'property': attr_name
                    })
        
        if has_photo:
            photo_stats['with_photos'] += 1
        else:
            photo_stats['without_photos'] += 1
    
    # Calculate statistics
    if photo_stats['photo_sizes']:
        photo_stats['avg_photo_size_kb'] = round(sum(photo_stats['photo_sizes']) / len(photo_stats['photo_sizes']) / 1024, 1)
        photo_stats['max_photo_size_kb'] = round(max(photo_stats['photo_sizes']) / 1024, 1)
        photo_stats['min_photo_size_kb'] = round(min(photo_stats['photo_sizes']) / 1024, 1)
    else:
        photo_stats['avg_photo_size_kb'] = 0
        photo_stats['max_photo_size_kb'] = 0
        photo_stats['min_photo_size_kb'] = 0
    
    # Display results
    print("\n📸 PHOTO ANALYSIS RESULTS")
    print("=" * 50)
    print(f"Total Contacts: {photo_stats['total_contacts']:,}")
    print(f"With Photos: {photo_stats['with_photos']:,} ({photo_stats['with_photos']/photo_stats['total_contacts']*100:.1f}%)")
    print(f"Without Photos: {photo_stats['without_photos']:,} ({photo_stats['without_photos']/photo_stats['total_contacts']*100:.1f}%)")
    
    if photo_stats['with_photos'] > 0:
        print(f"\n📊 PHOTO STATISTICS")
        print(f"Average Photo Size: {photo_stats['avg_photo_size_kb']} KB")
        print(f"Largest Photo: {photo_stats['max_photo_size_kb']} KB")
        print(f"Smallest Photo: {photo_stats['min_photo_size_kb']} KB")
        
        print(f"\n🎨 PHOTO FORMATS")
        for format_type, count in photo_stats['photo_formats'].most_common():
            print(f"  {format_type}: {count}")
        
        print(f"\n👥 SOME CONTACTS WITH PHOTOS")
        # Show first 10 contacts with photos, sorted by size
        sorted_photos = sorted(photo_stats['contacts_with_photos'], 
                             key=lambda x: x.get('size_kb', 0), reverse=True)
        
        for contact in sorted_photos[:10]:
            if contact.get('size_kb', 0) > 0:
                print(f"  {contact['name']}: {contact['size_kb']} KB")
            else:
                print(f"  {contact['name']}: Photo present (size unknown)")
    
    return photo_stats

if __name__ == "__main__":
    analyze_photos()