#!/usr/bin/env python3
"""
Remove obvious non-personal email addresses from vCard contacts
"""

import os
import re
import vobject
import shutil
from datetime import datetime
from collections import defaultdict
import json

class EmailCleaner:
    """Clean non-personal emails from vCards"""
    
    def __init__(self):
        # Define non-personal email patterns
        self.non_personal_prefixes = [
            'info', 'contact', 'feedback', 'newsletter', 'hello', 'invest',
            'support', 'office', 'admin', 'sales', 'marketing', 'press',
            'careers', 'jobs', 'hr', 'noreply', 'no-reply', 'postmaster',
            'webmaster', 'notifications', 'team', 'help', 'service',
            'enquiries', 'enquiry', 'booking', 'bookings', 'reception',
            'general', 'mail', 'post', 'reply', 'responses', 'system',
            'mailer', 'bounce', 'bounces', 'abuse', 'legal', 'privacy',
            'security', 'billing', 'accounts', 'accounting', 'finance',
            'shop', 'store', 'orders', 'customerservice', 'customer-service',
            'news', 'updates', 'alerts', 'notification', 'donotreply',
            'do-not-reply', 'undisclosed', 'recipients'
        ]
        
        self.stats = {
            'total_contacts': 0,
            'contacts_modified': 0,
            'emails_removed': 0,
            'emails_by_pattern': defaultdict(int),
            'contacts_with_no_emails_left': 0
        }
    
    def is_non_personal_email(self, email):
        """Check if an email is non-personal"""
        email_lower = email.lower().strip()
        
        # Extract local part (before @)
        if '@' not in email_lower:
            return False
        
        local_part = email_lower.split('@')[0]
        
        # Check against non-personal prefixes
        for prefix in self.non_personal_prefixes:
            if local_part == prefix or local_part.startswith(prefix + '.') or local_part.startswith(prefix + '-'):
                self.stats['emails_by_pattern'][prefix] += 1
                return True
        
        # Check for patterns like "noreply+something@domain.com"
        if 'noreply' in local_part or 'no-reply' in local_part or 'donotreply' in local_part:
            self.stats['emails_by_pattern']['noreply-variants'] += 1
            return True
        
        return False
    
    def clean_vcard_emails(self, vcard):
        """Remove non-personal emails from a vCard"""
        if not hasattr(vcard, 'email_list'):
            return False, 0
        
        original_emails = []
        personal_emails = []
        removed_count = 0
        
        # Collect all emails
        for email in vcard.email_list:
            if email.value:
                original_emails.append(email)
                if not self.is_non_personal_email(email.value):
                    personal_emails.append(email)
                else:
                    removed_count += 1
        
        if removed_count == 0:
            return False, 0
        
        # Remove all email entries
        vcard.email_list = []
        
        # Add back only personal emails
        for email_obj in personal_emails:
            new_email = vcard.add('email')
            new_email.value = email_obj.value
            if hasattr(email_obj, 'type_param'):
                new_email.type_param = email_obj.type_param
        
        return True, removed_count
    
    def clean_file(self, input_path, output_path):
        """Clean non-personal emails from a vCard file"""
        print(f"\nCleaning: {os.path.basename(input_path)}")
        print("-" * 60)
        
        # Load vCards
        with open(input_path, 'r', encoding='utf-8') as f:
            vcards = list(vobject.readComponents(f.read()))
        
        self.stats['total_contacts'] = len(vcards)
        
        # Process each vCard
        for vcard in vcards:
            modified, removed_count = self.clean_vcard_emails(vcard)
            
            if modified:
                self.stats['contacts_modified'] += 1
                self.stats['emails_removed'] += removed_count
                
                # Check if contact has no emails left
                if not hasattr(vcard, 'email_list') or len(vcard.email_list) == 0:
                    self.stats['contacts_with_no_emails_left'] += 1
        
        # Write cleaned file
        with open(output_path, 'w', encoding='utf-8') as f:
            for vcard in vcards:
                f.write(vcard.serialize())
        
        # Print stats
        print(f"Total contacts: {self.stats['total_contacts']}")
        print(f"Contacts modified: {self.stats['contacts_modified']}")
        print(f"Emails removed: {self.stats['emails_removed']}")
        print(f"Contacts with no emails left: {self.stats['contacts_with_no_emails_left']}")
        
        if self.stats['emails_removed'] > 0:
            print(f"\nTop removed patterns:")
            sorted_patterns = sorted(self.stats['emails_by_pattern'].items(), 
                                   key=lambda x: x[1], reverse=True)[:10]
            for pattern, count in sorted_patterns:
                print(f"  {pattern}: {count}")
        
        return self.stats


def main():
    """Clean all validated databases"""
    
    print("Non-Personal Email Removal")
    print("=" * 80)
    
    # Create backup directory
    backup_dir = f"backup/email_cleaning_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    databases = [
        "data/Sara_Export_VALIDATED_20250606.vcf",
        "data/iPhone_Contacts_VALIDATED_20250606_120917.vcf", 
        "data/iPhone_Suggested_VALIDATED_20250606_120917.vcf"
    ]
    
    cleaner = EmailCleaner()
    all_stats = {}
    
    for db_path in databases:
        if not os.path.exists(db_path):
            print(f"Warning: File not found - {db_path}")
            continue
        
        # Backup original
        backup_path = os.path.join(backup_dir, os.path.basename(db_path))
        shutil.copy2(db_path, backup_path)
        print(f"✓ Backed up: {os.path.basename(db_path)}")
        
        # Clean emails
        output_path = db_path.replace('.vcf', '_CLEANED.vcf')
        stats = cleaner.clean_file(db_path, output_path)
        all_stats[os.path.basename(db_path)] = dict(stats)
        
        # Reset stats for next file
        cleaner.stats = {
            'total_contacts': 0,
            'contacts_modified': 0,
            'emails_removed': 0,
            'emails_by_pattern': defaultdict(int),
            'contacts_with_no_emails_left': 0
        }
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    total_removed = sum(s['emails_removed'] for s in all_stats.values())
    total_modified = sum(s['contacts_modified'] for s in all_stats.values())
    
    print(f"Total emails removed: {total_removed}")
    print(f"Total contacts modified: {total_modified}")
    
    # Save report
    report = {
        'cleaning_date': datetime.now().isoformat(),
        'databases': all_stats,
        'backup_location': backup_dir
    }
    
    report_path = f"data/email_cleaning_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Report saved to: {report_path}")
    print(f"💾 Backups saved to: {backup_dir}")
    print(f"\n✅ Cleaned files saved with '_CLEANED' suffix")


if __name__ == "__main__":
    main()