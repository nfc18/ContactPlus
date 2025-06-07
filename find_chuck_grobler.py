#!/usr/bin/env python3
"""
Find Chuck Grobler and analyze where it came from
"""

import vobject
import os

def search_for_chuck(filepath):
    """Search for Chuck Grobler in a file"""
    print(f"\nSearching in: {os.path.basename(filepath)}")
    print("-" * 60)
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        vcards = list(vobject.readComponents(content))
    
    found = False
    for i, vcard in enumerate(vcards):
        if hasattr(vcard, 'fn') and vcard.fn.value:
            if 'Chuck' in vcard.fn.value and 'Grobler' in vcard.fn.value:
                found = True
                print(f"\nFOUND: {vcard.fn.value} at position {i}")
                
                # Show all fields
                if hasattr(vcard, 'n'):
                    print(f"  N: {vcard.n.value}")
                
                if hasattr(vcard, 'email_list'):
                    print(f"  Emails ({len(vcard.email_list)}):")
                    for email in vcard.email_list[:10]:  # First 10
                        print(f"    - {email.value}")
                    if len(vcard.email_list) > 10:
                        print(f"    ... and {len(vcard.email_list) - 10} more")
                
                if hasattr(vcard, 'tel_list'):
                    print(f"  Phones ({len(vcard.tel_list)}):")
                    for tel in vcard.tel_list[:5]:
                        print(f"    - {tel.value}")
                
                if hasattr(vcard, 'note'):
                    print(f"  Note: {vcard.note.value[:100]}...")
                
                if hasattr(vcard, 'org'):
                    print(f"  Organization: {vcard.org.value}")
    
    if not found:
        # Also search in raw text
        if 'Chuck' in content and 'Grobler' in content:
            print("Found 'Chuck' and 'Grobler' in file text but not as FN")
            # Find context
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'Chuck' in line or 'Grobler' in line:
                    print(f"  Line {i}: {line}")

def main():
    """Search all versions of files"""
    
    print("Searching for Chuck Grobler")
    print("=" * 80)
    
    # Search in order of processing
    files_to_check = [
        # Original
        "Imports/iPhone_Contacts_Contacts.vcf",
        # After validation
        "data/iPhone_Contacts_VALIDATED_20250606_120917.vcf",
        # After cleaning non-personal emails
        "data/iPhone_Contacts_VALIDATED_20250606_120917_CLEANED.vcf",
        # After corrections (splitting)
        "data/iPhone_Contacts_VALIDATED_20250606_120917_CORRECTED.vcf",
        # After Daniel fix
        "data/iPhone_Contacts_VALIDATED_20250606_120917_FIXED.vcf",
        # Final
        "data/iPhone_Contacts_VALIDATED_20250606_120917_FINAL.vcf",
        # Merged
        "data/INTELLIGENTLY_MERGED_20250606_133625.vcf"
    ]
    
    for filepath in files_to_check:
        search_for_chuck(filepath)

if __name__ == "__main__":
    main()