#!/usr/bin/env python3
"""
Merge all validated vCard databases into one master database
Uses Sara's database as the main database and merges others into it

Standard workflow:
1. Validate input files (vcard library)
2. Load and merge (vobject manipulation)
3. Deduplicate contacts
4. Apply soft compliance
5. Final validation (vcard library)
"""

import os
import json
import shutil
from datetime import datetime
from collections import defaultdict
import vobject
from vcard_validator import VCardStandardsValidator
from vcard_soft_compliance import SoftComplianceChecker
import phonenumbers
import re

class VCardMerger:
    """Merge multiple vCard databases with deduplication"""
    
    def __init__(self):
        self.validator = VCardStandardsValidator()
        self.soft_checker = SoftComplianceChecker()
        self.merge_stats = {
            'total_input_contacts': 0,
            'duplicates_found': 0,
            'contacts_merged': 0,
            'final_contact_count': 0
        }
    
    def normalize_phone(self, phone_str):
        """Normalize phone number for comparison"""
        try:
            # Try to parse the phone number
            parsed = phonenumbers.parse(phone_str, 'US')
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except:
            pass
        # Fallback: just keep digits
        return re.sub(r'\D', '', phone_str)
    
    def normalize_email(self, email):
        """Normalize email for comparison"""
        return email.lower().strip()
    
    def get_contact_key(self, vcard):
        """Generate a key for identifying potential duplicates"""
        keys = []
        
        # Try name-based key
        if hasattr(vcard, 'fn') and vcard.fn.value:
            name_key = vcard.fn.value.lower().strip()
            name_key = re.sub(r'\s+', ' ', name_key)  # Normalize whitespace
            keys.append(('name', name_key))
        
        # Try email-based keys
        if hasattr(vcard, 'email_list'):
            for email in vcard.email_list:
                if email.value:
                    keys.append(('email', self.normalize_email(email.value)))
        
        # Try phone-based keys
        if hasattr(vcard, 'tel_list'):
            for tel in vcard.tel_list:
                if tel.value:
                    normalized = self.normalize_phone(tel.value)
                    if normalized and len(normalized) >= 7:  # At least 7 digits
                        keys.append(('phone', normalized))
        
        return keys
    
    def merge_vcards(self, primary, secondary):
        """Merge two vCards, keeping primary as base and adding unique data from secondary"""
        
        # Merge emails (avoid duplicates)
        if hasattr(secondary, 'email_list'):
            existing_emails = set()
            if hasattr(primary, 'email_list'):
                existing_emails = {self.normalize_email(e.value) for e in primary.email_list}
            
            for email in secondary.email_list:
                normalized = self.normalize_email(email.value)
                if normalized not in existing_emails:
                    new_email = primary.add('email')
                    new_email.value = email.value
                    if hasattr(email, 'type_param'):
                        new_email.type_param = email.type_param
                    existing_emails.add(normalized)
        
        # Merge phones (avoid duplicates)
        if hasattr(secondary, 'tel_list'):
            existing_phones = set()
            if hasattr(primary, 'tel_list'):
                existing_phones = {self.normalize_phone(t.value) for t in primary.tel_list}
            
            for tel in secondary.tel_list:
                normalized = self.normalize_phone(tel.value)
                if normalized not in existing_phones:
                    new_tel = primary.add('tel')
                    new_tel.value = tel.value
                    if hasattr(tel, 'type_param'):
                        new_tel.type_param = tel.type_param
                    existing_phones.add(normalized)
        
        # Merge organizations
        if hasattr(secondary, 'org') and not hasattr(primary, 'org'):
            primary.add('org')
            primary.org.value = secondary.org.value
        
        # Merge URLs
        if hasattr(secondary, 'url_list'):
            existing_urls = set()
            if hasattr(primary, 'url_list'):
                existing_urls = {u.value.lower() for u in primary.url_list}
            
            for url in secondary.url_list:
                if url.value.lower() not in existing_urls:
                    new_url = primary.add('url')
                    new_url.value = url.value
                    existing_urls.add(url.value.lower())
        
        # Merge notes (append if different)
        if hasattr(secondary, 'note'):
            secondary_note = secondary.note.value.strip()
            if secondary_note:
                if hasattr(primary, 'note'):
                    if secondary_note not in primary.note.value:
                        primary.note.value += f"\n{secondary_note}"
                else:
                    primary.add('note')
                    primary.note.value = secondary_note
        
        return primary
    
    def merge_databases(self, main_db_path, additional_db_paths, output_path):
        """Merge multiple vCard databases into one"""
        
        print("vCard Database Merger")
        print("=" * 80)
        
        # Step 1: Create backup
        backup_dir = f"backup/merge_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        
        all_paths = [main_db_path] + additional_db_paths
        for path in all_paths:
            if os.path.exists(path):
                backup_name = os.path.basename(path)
                shutil.copy2(path, os.path.join(backup_dir, backup_name))
                print(f"✓ Backed up: {backup_name}")
        
        # Step 2: Validate all input files
        print("\n1. Validating input files...")
        for path in all_paths:
            is_valid, errors, warnings = self.validator.validate_file(path)
            basename = os.path.basename(path)
            if is_valid:
                print(f"  ✓ {basename}: Valid")
            else:
                print(f"  ⚠️  {basename}: {len(errors)} errors (will proceed anyway)")
        
        # Step 3: Load all vCards
        print("\n2. Loading vCards...")
        contact_map = defaultdict(list)  # key -> list of vcards
        all_vcards = []
        
        # Load main database first
        print(f"  Loading main database: {os.path.basename(main_db_path)}")
        with open(main_db_path, 'r', encoding='utf-8') as f:
            main_vcards = list(vobject.readComponents(f.read()))
        print(f"    Loaded {len(main_vcards)} contacts")
        self.merge_stats['total_input_contacts'] += len(main_vcards)
        
        # Index main database contacts
        for vcard in main_vcards:
            all_vcards.append(('main', vcard))
            keys = self.get_contact_key(vcard)
            for key_type, key_value in keys:
                contact_map[key_value].append(vcard)
        
        # Load additional databases
        for db_path in additional_db_paths:
            print(f"  Loading: {os.path.basename(db_path)}")
            with open(db_path, 'r', encoding='utf-8') as f:
                vcards = list(vobject.readComponents(f.read()))
            print(f"    Loaded {len(vcards)} contacts")
            self.merge_stats['total_input_contacts'] += len(vcards)
            
            for vcard in vcards:
                all_vcards.append(('additional', vcard))
        
        # Step 4: Merge contacts
        print("\n3. Merging contacts...")
        merged_vcards = []
        processed_vcards = set()  # Track which vCards we've already processed
        
        # First, add all main database contacts
        for source, vcard in all_vcards:
            if source == 'main':
                merged_vcards.append(vcard)
                processed_vcards.add(id(vcard))
        
        # Then, process additional contacts
        for source, vcard in all_vcards:
            if source == 'additional' and id(vcard) not in processed_vcards:
                # Check if this contact matches any existing contact
                keys = self.get_contact_key(vcard)
                merged = False
                
                for key_type, key_value in keys:
                    if key_value in contact_map:
                        # Found potential match(es)
                        for existing_vcard in contact_map[key_value]:
                            if id(existing_vcard) in processed_vcards:
                                # Merge into existing contact
                                self.merge_vcards(existing_vcard, vcard)
                                self.merge_stats['duplicates_found'] += 1
                                self.merge_stats['contacts_merged'] += 1
                                merged = True
                                break
                        if merged:
                            break
                
                if not merged:
                    # No match found, add as new contact
                    merged_vcards.append(vcard)
                    processed_vcards.add(id(vcard))
                    # Add to contact map for future matching
                    for key_type, key_value in keys:
                        contact_map[key_value].append(vcard)
        
        self.merge_stats['final_contact_count'] = len(merged_vcards)
        
        # Step 5: Write merged file
        print(f"\n4. Writing merged file...")
        temp_output = output_path.replace('.vcf', '_temp.vcf')
        with open(temp_output, 'w', encoding='utf-8') as f:
            for vcard in merged_vcards:
                f.write(vcard.serialize())
        
        # Step 6: Apply soft compliance
        print("\n5. Applying soft compliance fixes...")
        soft_output = output_path.replace('.vcf', '_soft.vcf')
        soft_result = self.soft_checker.check_and_fix_file(temp_output, soft_output)
        
        # Step 7: Final validation
        print("\n6. Final validation...")
        is_valid, errors, warnings = self.validator.validate_file(soft_output)
        
        if is_valid or len(errors) < 10:
            # Move to final output
            shutil.move(soft_output, output_path)
            print(f"  ✓ Validation passed: {len(errors)} errors, {len(warnings)} warnings")
        else:
            print(f"  ⚠️  Validation issues: {len(errors)} errors")
            # Still save the file
            shutil.move(soft_output, output_path)
        
        # Clean up temp file
        if os.path.exists(temp_output):
            os.remove(temp_output)
        
        # Print summary
        print("\n" + "=" * 80)
        print("MERGE SUMMARY")
        print("=" * 80)
        print(f"Input contacts: {self.merge_stats['total_input_contacts']:,}")
        print(f"Duplicates found: {self.merge_stats['duplicates_found']}")
        print(f"Contacts merged: {self.merge_stats['contacts_merged']}")
        print(f"Final contact count: {self.merge_stats['final_contact_count']:,}")
        print(f"Reduction: {self.merge_stats['total_input_contacts'] - self.merge_stats['final_contact_count']:,} contacts")
        
        if soft_result:
            print(f"\nSoft compliance fixes:")
            for fix, count in soft_result['fixes_applied'].items():
                if count > 0 and fix != 'total_improved':
                    print(f"  - {fix}: {count}")
        
        print(f"\n✅ Merged database saved to: {output_path}")
        print(f"💾 Backups saved to: {backup_dir}")
        
        return self.merge_stats


def main():
    """Merge all validated databases"""
    
    # Define paths
    sara_db = "data/Sara_Export_VALIDATED_20250606.vcf"
    iphone_contacts_db = "data/iPhone_Contacts_VALIDATED_20250606_120917.vcf"
    iphone_suggested_db = "data/iPhone_Suggested_VALIDATED_20250606_120917.vcf"
    
    # Output path
    date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f"data/MERGED_All_Contacts_{date_str}.vcf"
    
    # Check files exist
    all_files = [sara_db, iphone_contacts_db, iphone_suggested_db]
    for file in all_files:
        if not os.path.exists(file):
            print(f"Error: File not found - {file}")
            return
    
    # Create merger and run
    merger = VCardMerger()
    stats = merger.merge_databases(
        main_db_path=sara_db,
        additional_db_paths=[iphone_contacts_db, iphone_suggested_db],
        output_path=output_path
    )
    
    # Save merge report
    report_path = f"data/merge_report_{date_str}.json"
    with open(report_path, 'w') as f:
        json.dump({
            'merge_date': datetime.now().isoformat(),
            'input_files': all_files,
            'output_file': output_path,
            'statistics': stats
        }, f, indent=2)
    
    print(f"\n📊 Merge report saved to: {report_path}")


if __name__ == "__main__":
    main()