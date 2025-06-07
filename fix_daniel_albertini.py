#!/usr/bin/env python3
"""
Fix Daniel Albertini's emails and other corrections
"""

import os
import vobject
import shutil
from datetime import datetime

# Emails to remove from Daniel Albertini
daniel_emails_to_remove = [
    'katie@anyline.com',
    'ognjen@anyline.com', 
    'jaques@anyline.com',
    'giulia@anyline.io',
    'papaminion@anyline.com',
    'd1@anyline.com',
    'dani@anyline.com',
    'god@anyline.com'
]

def fix_database(input_path, output_path):
    """Fix specific issues in the database"""
    
    print(f"\nProcessing: {os.path.basename(input_path)}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        vcards = list(vobject.readComponents(f.read()))
    
    fixed_count = 0
    
    for vcard in vcards:
        if hasattr(vcard, 'fn') and vcard.fn.value == 'Daniel Albertini':
            if hasattr(vcard, 'email_list') and len(vcard.email_list) > 5:
                print(f"  Fixing Daniel Albertini ({len(vcard.email_list)} emails)")
                
                # Collect emails to keep
                emails_to_keep = []
                removed = 0
                
                for email in vcard.email_list:
                    if email.value not in daniel_emails_to_remove:
                        emails_to_keep.append(email)
                    else:
                        removed += 1
                        print(f"    Removing: {email.value}")
                
                if removed > 0:
                    # Clear and rebuild email list
                    vcard.email_list = []
                    for email_obj in emails_to_keep:
                        new_email = vcard.add('email')
                        new_email.value = email_obj.value
                        if hasattr(email_obj, 'type_param'):
                            new_email.type_param = email_obj.type_param
                    
                    fixed_count += 1
                    print(f"    Kept {len(emails_to_keep)} emails")
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        for vcard in vcards:
            f.write(vcard.serialize())
    
    return fixed_count


def main():
    """Fix Daniel Albertini and other issues"""
    
    print("Fixing Daniel Albertini's emails")
    print("=" * 80)
    
    # Only need to fix iPhone Contacts database
    input_file = "data/iPhone_Contacts_VALIDATED_20250606_120917_CORRECTED.vcf"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found")
        print("Using CLEANED version instead...")
        input_file = "data/iPhone_Contacts_VALIDATED_20250606_120917_CLEANED.vcf"
    
    # Create backup
    backup_dir = f"backup/daniel_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    backup_path = os.path.join(backup_dir, os.path.basename(input_file))
    shutil.copy2(input_file, backup_path)
    print(f"✓ Backup created: {backup_path}")
    
    # Fix the file
    output_file = "data/iPhone_Contacts_VALIDATED_20250606_120917_FIXED.vcf"
    fixed = fix_database(input_file, output_file)
    
    print(f"\n✅ Fixed {fixed} contacts")
    print(f"✅ Output: {output_file}")
    
    # Now create final CORRECTED versions for all databases
    print("\nCreating final CORRECTED versions...")
    
    files_to_finalize = [
        ("data/Sara_Export_VALIDATED_20250606_CORRECTED.vcf", 
         "data/Sara_Export_VALIDATED_20250606_FINAL.vcf"),
        ("data/iPhone_Contacts_VALIDATED_20250606_120917_FIXED.vcf",
         "data/iPhone_Contacts_VALIDATED_20250606_120917_FINAL.vcf"),
        ("data/iPhone_Suggested_VALIDATED_20250606_120917_CORRECTED.vcf",
         "data/iPhone_Suggested_VALIDATED_20250606_120917_FINAL.vcf")
    ]
    
    for src, dst in files_to_finalize:
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"  ✓ Created: {os.path.basename(dst)}")
    
    print("\n📝 Note: Bernhard Reiterer - There are TWO different people with this name!")
    print("   This needs to be handled during merge.")


if __name__ == "__main__":
    main()