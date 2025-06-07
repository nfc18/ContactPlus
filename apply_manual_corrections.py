#!/usr/bin/env python3
"""
Apply manual corrections based on user feedback
"""

import os
import vobject
import shutil
from datetime import datetime
import json

class ManualCorrections:
    """Apply specific manual corrections to contacts"""
    
    def __init__(self):
        self.stats = {
            'contacts_split': 0,
            'contacts_deleted': 0,
            'emails_removed': 0,
            'new_contacts_created': 0
        }
        
        # Contacts to split (one contact per email)
        self.contacts_to_split = [
            'Neda Norsen',
            'Jakob Hofer'
        ]
        
        # Contacts to delete entirely
        self.contacts_to_delete = [
            'Fax',
            'Angela Brett',  # Not Andrea Brett
            'Fred'
        ]
        
        # Specific email removals
        self.email_removals = {
            'Daniel Albertini': [
                lambda e: e.endswith('@nien.com'),
                lambda e: e == 'com.shack@anyline.com',
                lambda e: e == 'cati@anyline.com',
                lambda e: e == 'julia@anyline.io'
            ]
        }
    
    def should_delete_contact(self, vcard):
        """Check if contact should be deleted"""
        if hasattr(vcard, 'fn') and vcard.fn.value:
            name = vcard.fn.value
            return name in self.contacts_to_delete
        return False
    
    def should_split_contact(self, vcard):
        """Check if contact should be split"""
        if hasattr(vcard, 'fn') and vcard.fn.value:
            name = vcard.fn.value
            return name in self.contacts_to_split
        return False
    
    def split_contact(self, vcard):
        """Split a contact into multiple contacts (one per email)"""
        if not hasattr(vcard, 'email_list') or not vcard.email_list:
            return [vcard]
        
        new_vcards = []
        base_name = vcard.fn.value if hasattr(vcard, 'fn') else "Unknown"
        
        for email in vcard.email_list:
            if not email.value:
                continue
            
            # Create new vCard for each email
            new_vcard = vobject.vCard()
            
            # Add version
            new_vcard.add('version')
            new_vcard.version.value = '3.0'
            
            # Extract name from email if possible
            email_local = email.value.split('@')[0]
            
            # Try to create a proper name from email
            if '.' in email_local:
                parts = email_local.split('.')
                first_name = parts[0].capitalize()
                last_name = parts[1].capitalize() if len(parts) > 1 else ''
                new_name = f"{first_name} {last_name}".strip()
            else:
                new_name = email_local.capitalize()
            
            # Add FN
            new_vcard.add('fn')
            new_vcard.fn.value = new_name
            
            # Add N (structured name)
            new_vcard.add('n')
            if '.' in email_local:
                parts = email_local.split('.')
                new_vcard.n.value = vobject.vcard.Name(
                    family=parts[1].capitalize() if len(parts) > 1 else '',
                    given=parts[0].capitalize()
                )
            else:
                new_vcard.n.value = vobject.vcard.Name(
                    family='',
                    given=new_name
                )
            
            # Add email
            new_email = new_vcard.add('email')
            new_email.value = email.value
            if hasattr(email, 'type_param'):
                new_email.type_param = email.type_param
            
            # Copy organization if exists
            if hasattr(vcard, 'org'):
                new_vcard.add('org')
                new_vcard.org.value = vcard.org.value
            
            # Add note about split
            new_vcard.add('note')
            new_vcard.note.value = f"Split from {base_name} contact on {datetime.now().strftime('%Y-%m-%d')}"
            
            new_vcards.append(new_vcard)
            
        self.stats['new_contacts_created'] += len(new_vcards)
        self.stats['contacts_split'] += 1
        
        return new_vcards
    
    def clean_emails_from_contact(self, vcard):
        """Remove specific emails from a contact"""
        if not hasattr(vcard, 'fn') or not vcard.fn.value:
            return False
        
        name = vcard.fn.value
        if name not in self.email_removals:
            return False
        
        if not hasattr(vcard, 'email_list'):
            return False
        
        removal_rules = self.email_removals[name]
        original_emails = list(vcard.email_list)
        emails_to_keep = []
        removed_count = 0
        
        for email in original_emails:
            should_remove = False
            for rule in removal_rules:
                if rule(email.value):
                    should_remove = True
                    removed_count += 1
                    break
            
            if not should_remove:
                emails_to_keep.append(email)
        
        if removed_count > 0:
            # Clear email list and add back only kept emails
            vcard.email_list = []
            for email_obj in emails_to_keep:
                new_email = vcard.add('email')
                new_email.value = email_obj.value
                if hasattr(email_obj, 'type_param'):
                    new_email.type_param = email_obj.type_param
            
            self.stats['emails_removed'] += removed_count
            return True
        
        return False
    
    def process_file(self, input_path, output_path):
        """Process a vCard file with manual corrections"""
        
        print(f"\nProcessing: {os.path.basename(input_path)}")
        
        # Load vCards
        with open(input_path, 'r', encoding='utf-8') as f:
            vcards = list(vobject.readComponents(f.read()))
        
        corrected_vcards = []
        
        for vcard in vcards:
            # Check if should delete
            if self.should_delete_contact(vcard):
                print(f"  Deleting: {vcard.fn.value if hasattr(vcard, 'fn') else 'Unknown'}")
                self.stats['contacts_deleted'] += 1
                continue
            
            # Check if should split
            if self.should_split_contact(vcard):
                print(f"  Splitting: {vcard.fn.value if hasattr(vcard, 'fn') else 'Unknown'}")
                split_vcards = self.split_contact(vcard)
                corrected_vcards.extend(split_vcards)
                continue
            
            # Check if needs email cleaning
            if self.clean_emails_from_contact(vcard):
                print(f"  Cleaned emails from: {vcard.fn.value}")
            
            corrected_vcards.append(vcard)
        
        # Write corrected file
        with open(output_path, 'w', encoding='utf-8') as f:
            for vcard in corrected_vcards:
                f.write(vcard.serialize())
        
        return len(vcards), len(corrected_vcards)


def main():
    """Apply manual corrections to all databases"""
    
    print("Applying Manual Corrections")
    print("=" * 80)
    
    # Create backup
    backup_dir = f"backup/manual_corrections_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    databases = [
        "data/Sara_Export_VALIDATED_20250606_CLEANED.vcf",
        "data/iPhone_Contacts_VALIDATED_20250606_120917_CLEANED.vcf",
        "data/iPhone_Suggested_VALIDATED_20250606_120917_CLEANED.vcf"
    ]
    
    corrector = ManualCorrections()
    
    for db_path in databases:
        if not os.path.exists(db_path):
            print(f"Warning: File not found - {db_path}")
            continue
        
        # Backup
        backup_path = os.path.join(backup_dir, os.path.basename(db_path))
        shutil.copy2(db_path, backup_path)
        print(f"✓ Backed up: {os.path.basename(db_path)}")
        
        # Apply corrections
        output_path = db_path.replace('_CLEANED.vcf', '_CORRECTED.vcf')
        original_count, corrected_count = corrector.process_file(db_path, output_path)
        
        print(f"  Original: {original_count} → Corrected: {corrected_count}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("CORRECTIONS SUMMARY")
    print("=" * 80)
    print(f"Contacts split: {corrector.stats['contacts_split']}")
    print(f"New contacts created from splits: {corrector.stats['new_contacts_created']}")
    print(f"Contacts deleted: {corrector.stats['contacts_deleted']}")
    print(f"Emails removed: {corrector.stats['emails_removed']}")
    
    # Save report
    report = {
        'correction_date': datetime.now().isoformat(),
        'stats': corrector.stats,
        'corrections_applied': {
            'split_contacts': corrector.contacts_to_split,
            'deleted_contacts': corrector.contacts_to_delete,
            'email_removals': {name: len(rules) for name, rules in corrector.email_removals.items()}
        }
    }
    
    report_path = f"data/manual_corrections_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Report saved to: {report_path}")
    print(f"💾 Backups saved to: {backup_dir}")
    print(f"✅ Corrected files saved with '_CORRECTED' suffix")
    
    # Note about Bernhard Reiterer
    print("\n⚠️  IMPORTANT NOTE:")
    print("   There are TWO different people named 'Bernhard Reiterer':")
    print("   - One who worked at Anyline")
    print("   - One who worked at signd.id")
    print("   This will need to be handled during the merge process.")


if __name__ == "__main__":
    main()