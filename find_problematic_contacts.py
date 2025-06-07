#!/usr/bin/env python3
"""
Find contacts with excessive emails
"""

import vobject
import os

def find_contacts_with_many_emails(filepath, threshold=15):
    """Find contacts with more than threshold emails"""
    
    print(f"\nSearching for contacts with {threshold}+ emails in: {os.path.basename(filepath)}")
    print("-" * 80)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        vcards = list(vobject.readComponents(f.read()))
    
    problematic = []
    
    for vcard in vcards:
        if hasattr(vcard, 'email_list') and len(vcard.email_list) >= threshold:
            name = vcard.fn.value if hasattr(vcard, 'fn') else "No name"
            email_count = len(vcard.email_list)
            
            print(f"\nFound: {name}")
            print(f"  Email count: {email_count}")
            
            # Show first 10 emails
            print("  First 10 emails:")
            for i, email in enumerate(vcard.email_list[:10]):
                print(f"    {i+1}. {email.value}")
            
            if email_count > 10:
                print(f"  ... and {email_count - 10} more emails")
            
            # Check if it has Chuck or Grobler in any field
            all_text = str(vcard.serialize())
            if 'Chuck' in all_text or 'chuck' in all_text.lower():
                print("  ⚠️  Contains 'Chuck' somewhere!")
            if 'Grobler' in all_text or 'grobler' in all_text.lower():
                print("  ⚠️  Contains 'Grobler' somewhere!")
            
            problematic.append((name, email_count))
    
    return problematic

def main():
    # Check the merged file
    merged_file = "data/INTELLIGENTLY_MERGED_20250606_133625.vcf"
    
    if os.path.exists(merged_file):
        problematic = find_contacts_with_many_emails(merged_file, 15)
        
        print(f"\n\nSummary: Found {len(problematic)} contacts with 15+ emails")
        
        # Also check the original iPhone file
        print("\n" + "=" * 80)
        print("Checking original iPhone Contacts file...")
        orig_file = "data/iPhone_Contacts_VALIDATED_20250606_120917_FINAL.vcf"
        if os.path.exists(orig_file):
            find_contacts_with_many_emails(orig_file, 15)

if __name__ == "__main__":
    main()