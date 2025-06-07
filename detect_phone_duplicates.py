#!/usr/bin/env python3
"""
Detect contacts with identical phone numbers
"""

import vobject
import re
from collections import defaultdict

def normalize_phone(phone):
    """Normalize phone number for comparison"""
    if not phone:
        return None
    
    # Remove all non-digits except +
    cleaned = re.sub(r'[^\d+]', '', phone.strip())
    
    # Handle Austrian numbers specifically
    if cleaned.startswith('0043'):
        cleaned = '+43' + cleaned[4:]
    elif cleaned.startswith('043'):
        cleaned = '+43' + cleaned[3:]
    elif cleaned.startswith('0') and len(cleaned) > 1:
        # Austrian domestic format
        cleaned = '+43' + cleaned[1:]
    
    # Ensure + prefix for international numbers
    if cleaned.startswith('43') and not cleaned.startswith('+'):
        cleaned = '+' + cleaned
    elif cleaned.startswith('1') and len(cleaned) == 11:
        cleaned = '+' + cleaned
    
    return cleaned

def detect_phone_duplicates():
    """Find contacts sharing the same phone number"""
    
    # Find latest phonebook
    import glob
    import os
    
    phonebook_files = glob.glob("data/MASTER_PHONEBOOK_*.vcf")
    if not phonebook_files:
        phonebook_files = glob.glob("data/FINAL_MASTER_CONTACTS_*.vcf")
    
    if not phonebook_files:
        print("❌ No master phonebook found!")
        return
    
    latest_phonebook = sorted(phonebook_files)[-1]
    print(f"Analyzing phone duplicates in: {os.path.basename(latest_phonebook)}")
    
    # Load contacts
    with open(latest_phonebook, 'r', encoding='utf-8') as f:
        contacts = list(vobject.readComponents(f.read()))
    
    print(f"✓ Loaded {len(contacts)} contacts")
    
    # Map phone numbers to contacts
    phone_to_contacts = defaultdict(list)
    total_phones = 0
    contacts_with_phones = 0
    
    for i, contact in enumerate(contacts):
        contact_name = contact.fn.value if hasattr(contact, 'fn') and contact.fn.value else f"Contact {i+1}"
        
        contact_phones = []
        
        if hasattr(contact, 'tel_list') and contact.tel_list:
            contacts_with_phones += 1
            
            for tel in contact.tel_list:
                if tel.value:
                    normalized = normalize_phone(tel.value)
                    if normalized and len(normalized) >= 7:  # Valid phone length
                        contact_phones.append({
                            'original': tel.value,
                            'normalized': normalized
                        })
                        phone_to_contacts[normalized].append({
                            'index': i,
                            'name': contact_name,
                            'phone_original': tel.value,
                            'phone_normalized': normalized
                        })
                        total_phones += 1
        
        # Store phones with contact for analysis
        if hasattr(contact, '_contact_phones'):
            contact._contact_phones = contact_phones
        else:
            # Add as a temporary attribute for this analysis
            contact.contact_phones = contact_phones
    
    # Find duplicates
    duplicate_groups = {}
    duplicate_count = 0
    affected_contacts = 0
    
    for phone, contact_list in phone_to_contacts.items():
        if len(contact_list) > 1:
            duplicate_groups[phone] = contact_list
            duplicate_count += len(contact_list)
            affected_contacts += len(set(c['index'] for c in contact_list))
    
    # Display results
    print(f"\n📱 PHONE NUMBER DUPLICATE ANALYSIS")
    print("=" * 60)
    print(f"Total contacts: {len(contacts):,}")
    print(f"Contacts with phones: {contacts_with_phones:,} ({contacts_with_phones/len(contacts)*100:.1f}%)")
    print(f"Total phone numbers: {total_phones:,}")
    print(f"Unique phone numbers: {len(phone_to_contacts):,}")
    print(f"Duplicate phone numbers: {len(duplicate_groups):,}")
    print(f"Contacts affected by duplicates: {affected_contacts:,}")
    print(f"Total duplicate instances: {duplicate_count:,}")
    
    if duplicate_groups:
        print(f"\n🔍 DUPLICATE PHONE GROUPS")
        print("-" * 60)
        
        # Sort by number of duplicates (most problematic first)
        sorted_groups = sorted(duplicate_groups.items(), 
                             key=lambda x: len(x[1]), reverse=True)
        
        for i, (phone, contact_list) in enumerate(sorted_groups[:20]):  # Show top 20
            print(f"\n{i+1}. Phone: {phone} ({len(contact_list)} contacts)")
            
            for contact in contact_list:
                print(f"   • {contact['name']}")
                if contact['phone_original'] != contact['phone_normalized']:
                    print(f"     Original: {contact['phone_original']}")
        
        if len(sorted_groups) > 20:
            print(f"\n... and {len(sorted_groups) - 20} more duplicate groups")
        
        # Analysis of duplicate patterns
        print(f"\n📊 DUPLICATE PATTERNS")
        print("-" * 30)
        
        size_distribution = defaultdict(int)
        for contact_list in duplicate_groups.values():
            size_distribution[len(contact_list)] += 1
        
        for size, count in sorted(size_distribution.items(), reverse=True):
            print(f"  {size} contacts sharing phone: {count} groups")
        
        # Specific insights
        print(f"\n💡 INSIGHTS")
        print("-" * 20)
        
        # Find largest duplicate group
        largest_group = max(duplicate_groups.values(), key=len)
        largest_phone = None
        for phone, contacts in duplicate_groups.items():
            if contacts == largest_group:
                largest_phone = phone
                break
        
        print(f"• Largest duplicate group: {len(largest_group)} contacts sharing {largest_phone}")
        
        # Count Austrian vs international duplicates
        austrian_duplicates = sum(1 for phone in duplicate_groups.keys() if phone.startswith('+43'))
        international_duplicates = len(duplicate_groups) - austrian_duplicates
        
        print(f"• Austrian number duplicates: {austrian_duplicates}")
        print(f"• International number duplicates: {international_duplicates}")
        
        # Identify potential business numbers (multiple people)
        business_numbers = []
        for phone, contact_list in duplicate_groups.items():
            if len(contact_list) >= 3:
                # Check if it's likely a business number
                orgs = set()
                for contact_info in contact_list:
                    try:
                        contact = contacts[contact_info['index']]
                        if hasattr(contact, 'org') and contact.org.value:
                            org = contact.org.value
                            if isinstance(org, list):
                                org = ' '.join(org)
                            orgs.add(str(org).strip().lower())
                    except IndexError:
                        # Skip if contact index is invalid
                        continue
                
                if len(orgs) <= 2:  # Same organization(s)
                    business_numbers.append({
                        'phone': phone,
                        'contacts': len(contact_list),
                        'organizations': list(orgs)
                    })
        
        if business_numbers:
            print(f"• Potential business numbers: {len(business_numbers)}")
            for biz in business_numbers[:5]:
                orgs_str = ', '.join(biz['organizations']) if biz['organizations'] else 'No org'
                print(f"  - {biz['phone']}: {biz['contacts']} contacts ({orgs_str})")
    
    else:
        print("\n✅ No phone number duplicates found!")
    
    return duplicate_groups

if __name__ == "__main__":
    detect_phone_duplicates()