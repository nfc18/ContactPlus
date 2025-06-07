#!/usr/bin/env python3
"""
Advanced deduplication for merged vCard database
Intelligently merges duplicate contacts while preserving all unique information
"""

import os
import shutil
from datetime import datetime
from collections import defaultdict
import vobject
import json
from analyze_duplicates import DuplicateAnalyzer
from vcard_validator import VCardStandardsValidator
from vcard_soft_compliance import SoftComplianceChecker
import re

class AdvancedDeduplicator:
    """Advanced deduplication with intelligent merging"""
    
    def __init__(self):
        self.analyzer = DuplicateAnalyzer()
        self.validator = VCardStandardsValidator()
        self.soft_checker = SoftComplianceChecker()
        self.merge_stats = {
            'groups_processed': 0,
            'contacts_merged': 0,
            'contacts_removed': 0,
            'data_preserved': {
                'emails': 0,
                'phones': 0,
                'addresses': 0,
                'urls': 0,
                'notes': 0,
                'organizations': 0
            }
        }
    
    def score_vcard_completeness(self, vcard):
        """Score a vCard based on data completeness (0-100)"""
        score = 0
        
        # Name quality (30 points)
        if hasattr(vcard, 'fn') and vcard.fn.value:
            score += 10
            if len(vcard.fn.value) > 5:
                score += 10
        if hasattr(vcard, 'n') and vcard.n.value:
            n_val = vcard.n.value
            if n_val.given:
                score += 5
            if n_val.family:
                score += 5
        
        # Contact info (30 points)
        if hasattr(vcard, 'email_list') and vcard.email_list:
            score += 15
        if hasattr(vcard, 'tel_list') and vcard.tel_list:
            score += 15
        
        # Organization (20 points)
        if hasattr(vcard, 'org') and vcard.org.value:
            score += 10
            if hasattr(vcard, 'title') and vcard.title.value:
                score += 10
        
        # Additional data (20 points)
        if hasattr(vcard, 'adr_list') and vcard.adr_list:
            score += 5
        if hasattr(vcard, 'url_list') and vcard.url_list:
            score += 5
        if hasattr(vcard, 'note') and vcard.note.value:
            score += 5
        if hasattr(vcard, 'photo'):
            score += 5
        
        return score
    
    def merge_vcard_group(self, vcard_group):
        """Intelligently merge a group of duplicate vCards"""
        if len(vcard_group) == 1:
            return vcard_group[0]['vcard']
        
        # Score and sort vCards by completeness
        scored_vcards = []
        for contact in vcard_group:
            vcard = contact['vcard']
            score = self.score_vcard_completeness(vcard)
            scored_vcards.append((score, vcard))
        
        scored_vcards.sort(reverse=True, key=lambda x: x[0])
        
        # Use most complete vCard as base
        base_vcard = scored_vcards[0][1]
        
        # Merge data from other vCards
        for score, vcard in scored_vcards[1:]:
            self._merge_into_base(base_vcard, vcard)
        
        self.merge_stats['groups_processed'] += 1
        self.merge_stats['contacts_merged'] += len(vcard_group) - 1
        self.merge_stats['contacts_removed'] += len(vcard_group) - 1
        
        return base_vcard
    
    def _merge_into_base(self, base, source):
        """Merge source vCard data into base vCard"""
        
        # Merge names (improve if base is incomplete)
        if hasattr(source, 'n') and source.n.value:
            if not hasattr(base, 'n') or not base.n.value:
                base.add('n')
                base.n.value = source.n.value
            else:
                # Merge name components
                base_n = base.n.value
                source_n = source.n.value
                if not base_n.given and source_n.given:
                    base_n.given = source_n.given
                if not base_n.family and source_n.family:
                    base_n.family = source_n.family
                if not base_n.additional and source_n.additional:
                    base_n.additional = source_n.additional
        
        # Merge emails (unique)
        if hasattr(source, 'email_list'):
            existing_emails = set()
            if hasattr(base, 'email_list'):
                existing_emails = {self.analyzer.normalize_email(e.value) for e in base.email_list}
            
            for email in source.email_list:
                normalized = self.analyzer.normalize_email(email.value)
                if normalized not in existing_emails:
                    new_email = base.add('email')
                    new_email.value = email.value
                    if hasattr(email, 'type_param'):
                        new_email.type_param = email.type_param
                    existing_emails.add(normalized)
                    self.merge_stats['data_preserved']['emails'] += 1
        
        # Merge phones (unique)
        if hasattr(source, 'tel_list'):
            existing_phones = set()
            if hasattr(base, 'tel_list'):
                existing_phones = {self.analyzer.normalize_phone(t.value) for t in base.tel_list}
            
            for tel in source.tel_list:
                normalized = self.analyzer.normalize_phone(tel.value)
                if normalized and normalized not in existing_phones:
                    new_tel = base.add('tel')
                    new_tel.value = tel.value
                    if hasattr(tel, 'type_param'):
                        new_tel.type_param = tel.type_param
                    existing_phones.add(normalized)
                    self.merge_stats['data_preserved']['phones'] += 1
        
        # Merge addresses
        if hasattr(source, 'adr_list'):
            existing_addrs = set()
            if hasattr(base, 'adr_list'):
                for adr in base.adr_list:
                    if adr.value:
                        addr_str = str(adr.value).lower()
                        existing_addrs.add(addr_str)
            
            for adr in source.adr_list:
                if adr.value:
                    addr_str = str(adr.value).lower()
                    if addr_str not in existing_addrs:
                        new_adr = base.add('adr')
                        new_adr.value = adr.value
                        if hasattr(adr, 'type_param'):
                            new_adr.type_param = adr.type_param
                        existing_addrs.add(addr_str)
                        self.merge_stats['data_preserved']['addresses'] += 1
        
        # Merge organization (if base doesn't have one)
        if hasattr(source, 'org') and source.org.value:
            if not hasattr(base, 'org') or not base.org.value:
                base.add('org')
                base.org.value = source.org.value
                self.merge_stats['data_preserved']['organizations'] += 1
        
        # Merge title (if base doesn't have one)
        if hasattr(source, 'title') and source.title.value:
            if not hasattr(base, 'title') or not base.title.value:
                base.add('title')
                base.title.value = source.title.value
        
        # Merge URLs (unique)
        if hasattr(source, 'url_list'):
            existing_urls = set()
            if hasattr(base, 'url_list'):
                existing_urls = {u.value.lower() for u in base.url_list}
            
            for url in source.url_list:
                if url.value.lower() not in existing_urls:
                    new_url = base.add('url')
                    new_url.value = url.value
                    existing_urls.add(url.value.lower())
                    self.merge_stats['data_preserved']['urls'] += 1
        
        # Merge notes (append unique content)
        if hasattr(source, 'note') and source.note.value:
            source_note = source.note.value.strip()
            if source_note:
                if hasattr(base, 'note') and base.note.value:
                    if source_note not in base.note.value:
                        base.note.value += f"\n{source_note}"
                        self.merge_stats['data_preserved']['notes'] += 1
                else:
                    base.add('note')
                    base.note.value = source_note
                    self.merge_stats['data_preserved']['notes'] += 1
        
        # Keep photo from source if base doesn't have one
        if hasattr(source, 'photo') and not hasattr(base, 'photo'):
            base.add('photo')
            base.photo.value = source.photo.value
            if hasattr(source.photo, 'encoding_param'):
                base.photo.encoding_param = source.photo.encoding_param
            if hasattr(source.photo, 'type_param'):
                base.photo.type_param = source.photo.type_param
    
    def deduplicate_file(self, input_path, output_path):
        """Deduplicate a vCard file"""
        print("\nAdvanced vCard Deduplication")
        print("=" * 80)
        
        # Create backup
        backup_dir = f"backup/dedup_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, os.path.basename(input_path))
        shutil.copy2(input_path, backup_path)
        print(f"✓ Backup created: {backup_path}")
        
        # Load vCards
        print("\n1. Loading vCards...")
        with open(input_path, 'r', encoding='utf-8') as f:
            all_vcards = list(vobject.readComponents(f.read()))
        print(f"   Loaded {len(all_vcards)} contacts")
        
        # Find duplicates
        print("\n2. Finding duplicates...")
        duplicate_groups = self.analyzer.find_duplicates(all_vcards)
        print(f"   Found {len(duplicate_groups)} duplicate groups")
        
        # Create mapping of vCards to process
        print("\n3. Merging duplicates...")
        processed_indices = set()
        merged_vcards = []
        
        # Process duplicate groups
        for group in duplicate_groups:
            merged = self.merge_vcard_group(group)
            merged_vcards.append(merged)
            
            # Mark all indices in group as processed
            for contact in group:
                processed_indices.add(contact['index'])
        
        # Add non-duplicate vCards
        for i, vcard in enumerate(all_vcards):
            if i not in processed_indices:
                merged_vcards.append(vcard)
        
        print(f"   Merged {self.merge_stats['contacts_merged']} duplicates")
        print(f"   Final count: {len(merged_vcards)} contacts")
        
        # Write temporary output
        print("\n4. Writing deduplicated file...")
        temp_output = output_path.replace('.vcf', '_temp.vcf')
        with open(temp_output, 'w', encoding='utf-8') as f:
            for vcard in merged_vcards:
                f.write(vcard.serialize())
        
        # Apply soft compliance
        print("\n5. Applying soft compliance...")
        soft_output = output_path.replace('.vcf', '_soft.vcf')
        soft_result = self.soft_checker.check_and_fix_file(temp_output, soft_output)
        
        # Final validation
        print("\n6. Final validation...")
        is_valid, errors, warnings = self.validator.validate_file(soft_output)
        
        # Move to final output
        shutil.move(soft_output, output_path)
        
        # Clean up temp file
        if os.path.exists(temp_output):
            os.remove(temp_output)
        
        # Print summary
        print("\n" + "=" * 80)
        print("DEDUPLICATION SUMMARY")
        print("=" * 80)
        print(f"Original contacts: {len(all_vcards):,}")
        print(f"Duplicate groups: {len(duplicate_groups)}")
        print(f"Contacts merged: {self.merge_stats['contacts_merged']}")
        print(f"Final contacts: {len(merged_vcards):,}")
        print(f"Reduction: {len(all_vcards) - len(merged_vcards):,} contacts")
        
        print("\n📊 DATA PRESERVED:")
        for data_type, count in self.merge_stats['data_preserved'].items():
            if count > 0:
                print(f"  {data_type}: {count}")
        
        if soft_result:
            print(f"\n📈 SOFT COMPLIANCE FIXES:")
            for fix, count in soft_result['fixes_applied'].items():
                if count > 0 and fix != 'total_improved':
                    print(f"  {fix}: {count}")
        
        print(f"\n✅ Validation: {len(errors)} errors, {len(warnings)} warnings")
        print(f"✅ Deduplicated file saved to: {output_path}")
        print(f"💾 Backup saved to: {backup_path}")
        
        # Save deduplication report
        report = {
            'deduplication_date': datetime.now().isoformat(),
            'input_file': input_path,
            'output_file': output_path,
            'original_count': len(all_vcards),
            'final_count': len(merged_vcards),
            'stats': self.merge_stats,
            'validation': {
                'errors': len(errors),
                'warnings': len(warnings)
            }
        }
        
        report_path = f"data/deduplication_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Report saved to: {report_path}")
        
        return len(merged_vcards)


def main():
    """Run advanced deduplication on merged database"""
    
    # Input and output paths
    input_file = "data/MERGED_All_Contacts_20250606_123737.vcf"
    date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"data/FINAL_Deduplicated_Contacts_{date_str}.vcf"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return
    
    # Run deduplication
    deduplicator = AdvancedDeduplicator()
    final_count = deduplicator.deduplicate_file(input_file, output_file)
    
    print(f"\n🎉 Deduplication complete!")
    print(f"   Your cleaned contact database has {final_count:,} unique contacts")
    print(f"   Ready for import: {output_file}")


if __name__ == "__main__":
    main()