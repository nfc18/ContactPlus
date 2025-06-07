#!/usr/bin/env python3
"""
Fix Jaques Grobler and remaining email issues
"""

import os
import vobject
import shutil
from datetime import datetime

def fix_jaques_grobler(vcard):
    """Fix Jaques Grobler - keep only his emails"""
    if hasattr(vcard, 'email_list'):
        # Jaques's actual emails
        jaques_emails = [
            'jaques@anyline.com',
            'jaques.grobler@anyline.com', 
            'j.grobler@anyline.com',
            'jaquesgrobler@gmail.com'
        ]
        
        # Filter emails
        emails_to_keep = []
        removed = []
        
        for email in vcard.email_list:
            if any(je in email.value.lower() for je in jaques_emails):
                emails_to_keep.append(email)
            else:
                removed.append(email.value)
        
        if removed:
            print(f"  Removing {len(removed)} incorrect emails from Jaques Grobler:")
            for email in removed[:5]:
                print(f"    - {email}")
            if len(removed) > 5:
                print(f"    ... and {len(removed) - 5} more")
            
            # Rebuild email list
            vcard.email_list = []
            for email_obj in emails_to_keep:
                new_email = vcard.add('email')
                new_email.value = email_obj.value
                if hasattr(email_obj, 'type_param'):
                    new_email.type_param = email_obj.type_param
            
            return True
    return False

def split_problematic_contact(vcard):
    """Split contacts with too many mixed emails"""
    if not hasattr(vcard, 'email_list') or len(vcard.email_list) < 10:
        return None
    
    # Create individual contacts for each email
    new_vcards = []
    base_name = vcard.fn.value if hasattr(vcard, 'fn') else "Unknown"
    
    print(f"  Splitting {base_name} ({len(vcard.email_list)} emails) into individual contacts")
    
    for email in vcard.email_list:
        if not email.value:
            continue
        
        # Create new vCard
        new_vcard = vobject.vCard()
        new_vcard.add('version')
        new_vcard.version.value = '3.0'
        
        # Extract name from email
        email_local = email.value.split('@')[0]
        if '.' in email_local:
            parts = email_local.split('.')
            first_name = parts[0].capitalize()
            last_name = parts[1].capitalize() if len(parts) > 1 else ''
            new_name = f"{first_name} {last_name}".strip()
        else:
            new_name = email_local.capitalize()
        
        # Add FN and N
        new_vcard.add('fn')
        new_vcard.fn.value = new_name
        
        new_vcard.add('n')
        if '.' in email_local:
            parts = email_local.split('.')
            new_vcard.n.value = vobject.vcard.Name(
                family=parts[1].capitalize() if len(parts) > 1 else '',
                given=parts[0].capitalize()
            )
        else:
            new_vcard.n.value = vobject.vcard.Name(family='', given=new_name)
        
        # Add email
        new_email = new_vcard.add('email')
        new_email.value = email.value
        if hasattr(email, 'type_param'):
            new_email.type_param = email.type_param
        
        # Copy organization if exists
        if hasattr(vcard, 'org'):
            new_vcard.add('org')
            new_vcard.org.value = vcard.org.value
        
        # Add note
        new_vcard.add('note')
        new_vcard.note.value = f"Split from {base_name} on {datetime.now().strftime('%Y-%m-%d')}"
        
        new_vcards.append(new_vcard)
    
    return new_vcards

def fix_database(input_path, output_path):
    """Fix remaining email issues"""
    
    print(f"\nProcessing: {os.path.basename(input_path)}")
    print("-" * 80)
    
    with open(input_path, 'r', encoding='utf-8') as f:
        vcards = list(vobject.readComponents(f.read()))
    
    fixed_vcards = []
    fixes_made = 0
    contacts_split = 0
    
    for vcard in vcards:
        name = vcard.fn.value if hasattr(vcard, 'fn') else "No name"
        
        # Fix Jaques Grobler
        if name == "Jaques Grobler":
            if fix_jaques_grobler(vcard):
                fixes_made += 1
            fixed_vcards.append(vcard)
        
        # Split remaining problematic contacts
        elif name in ["Jakob", "Immanuel Neureiter"] or (
            hasattr(vcard, 'email_list') and len(vcard.email_list) >= 15
        ):
            new_vcards = split_problematic_contact(vcard)
            if new_vcards:
                fixed_vcards.extend(new_vcards)
                contacts_split += 1
            else:
                fixed_vcards.append(vcard)
        
        else:
            fixed_vcards.append(vcard)
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        for vcard in fixed_vcards:
            f.write(vcard.serialize())
    
    print(f"\n✅ Fixed {fixes_made} contacts")
    print(f"✅ Split {contacts_split} problematic contacts")
    print(f"✅ Total contacts: {len(fixed_vcards)}")
    
    return len(fixed_vcards)

def main():
    """Fix the merged database"""
    
    print("Fixing Remaining Email Issues")
    print("=" * 80)
    
    # Backup
    backup_dir = f"backup/email_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Fix the merged file
    input_file = "data/INTELLIGENTLY_MERGED_20250606_133625.vcf"
    output_file = f"data/FINAL_CLEANED_MERGED_{datetime.now().strftime('%Y%m%d_%H%M%S')}.vcf"
    
    # Backup
    backup_path = os.path.join(backup_dir, os.path.basename(input_file))
    shutil.copy2(input_file, backup_path)
    print(f"✓ Backup created: {backup_path}")
    
    # Fix
    total = fix_database(input_file, output_file)
    
    print(f"\n✅ Final cleaned database: {output_file}")
    print(f"   Total contacts: {total}")

if __name__ == "__main__":
    main()