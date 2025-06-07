#!/usr/bin/env python3
"""
Intelligent Contact Merge System
Implements the comprehensive merge strategy with photo handling
"""

import os
import hashlib
import json
import shutil
from datetime import datetime
from collections import defaultdict
from difflib import SequenceMatcher
import vobject
import phonenumbers
import re
from PIL import Image
import io
import base64

class IntelligentContactMerger:
    """Advanced contact merger with photo handling"""
    
    def __init__(self):
        # Database priorities
        self.db_priorities = {
            'sara': 100,
            'iphone_contacts': 80,
            'iphone_suggested': 60
        }
        
        # Known duplicate names
        self.known_duplicates = {
            'Bernhard Reiterer': ['Anyline', 'signd.id'],
            'Christian Pichler': ['Anyline', 'Tyrolit']
        }
        
        # Statistics
        self.stats = {
            'total_input': 0,
            'auto_merged': 0,
            'manual_review': 0,
            'kept_separate': 0,
            'photos_processed': 0,
            'photos_optimized': 0
        }
        
        # Match groups
        self.match_groups = []
        self.review_needed = []
        
    def normalize_phone(self, phone_str):
        """Normalize phone number for comparison"""
        try:
            parsed = phonenumbers.parse(phone_str, 'US')
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except:
            pass
        # Fallback: just digits
        digits = re.sub(r'\D', '', phone_str)
        return digits[-10:] if len(digits) >= 10 else digits
    
    def normalize_email(self, email):
        """Normalize email for comparison"""
        return email.lower().strip()
    
    def name_similarity(self, name1, name2):
        """Calculate name similarity score"""
        if not name1 or not name2:
            return 0
        name1 = name1.lower().strip()
        name2 = name2.lower().strip()
        return SequenceMatcher(None, name1, name2).ratio()
    
    def extract_org_name(self, vcard):
        """Extract organization name from vCard"""
        if hasattr(vcard, 'org') and vcard.org.value:
            if isinstance(vcard.org.value, list):
                return ' '.join(vcard.org.value).strip()
            return str(vcard.org.value).strip()
        return None
    
    def check_known_duplicate(self, vcard):
        """Check if this is a known duplicate name"""
        if not hasattr(vcard, 'fn') or not vcard.fn.value:
            return False
        
        name = vcard.fn.value
        org = self.extract_org_name(vcard)
        
        for dup_name, orgs in self.known_duplicates.items():
            if dup_name in name:
                # Check if org matches any known org
                if org:
                    for known_org in orgs:
                        if known_org.lower() in org.lower():
                            return True
        return False
    
    def calculate_match_confidence(self, vcard1, vcard2, match_type):
        """Calculate confidence score for a potential match"""
        
        # Extract names
        name1 = vcard1.fn.value if hasattr(vcard1, 'fn') else ""
        name2 = vcard2.fn.value if hasattr(vcard2, 'fn') else ""
        
        # Check for known duplicates
        if self.check_known_duplicate(vcard1) and self.check_known_duplicate(vcard2):
            # If both are known duplicates, check if they're the same person
            org1 = self.extract_org_name(vcard1)
            org2 = self.extract_org_name(vcard2)
            if org1 and org2 and org1.lower() != org2.lower():
                return 0  # Different people
        
        # Email match
        if match_type == 'email':
            base_confidence = 95
            # Reduce confidence if names are very different
            if self.name_similarity(name1, name2) < 0.5:
                base_confidence -= 10
            return base_confidence
        
        # Phone match
        elif match_type == 'phone':
            base_confidence = 90
            # Boost if names are similar
            if self.name_similarity(name1, name2) > 0.8:
                base_confidence += 5
            return base_confidence
        
        # Name + Organization match
        elif match_type == 'name_org':
            if self.name_similarity(name1, name2) > 0.9:
                return 85
            return 75
        
        # Combined criteria
        elif match_type == 'combined':
            return 98
        
        return 50
    
    def find_matches(self, vcards_with_source):
        """Find potential matches across databases"""
        
        # Build indices
        email_index = defaultdict(list)
        phone_index = defaultdict(list)
        name_org_index = defaultdict(list)
        
        for i, (source, vcard) in enumerate(vcards_with_source):
            # Index by email
            if hasattr(vcard, 'email_list'):
                for email in vcard.email_list:
                    if email.value:
                        normalized = self.normalize_email(email.value)
                        email_index[normalized].append((i, source, vcard))
            
            # Index by phone
            if hasattr(vcard, 'tel_list'):
                for tel in vcard.tel_list:
                    if tel.value:
                        normalized = self.normalize_phone(tel.value)
                        if normalized:
                            phone_index[normalized].append((i, source, vcard))
            
            # Index by name+org
            if hasattr(vcard, 'fn') and vcard.fn.value:
                org = self.extract_org_name(vcard)
                if org:
                    key = f"{vcard.fn.value.lower()}|{org.lower()}"
                    name_org_index[key].append((i, source, vcard))
        
        # Find matches
        processed = set()
        match_groups = []
        
        # Process email matches
        for email, contacts in email_index.items():
            if len(contacts) > 1:
                group = []
                for idx, source, vcard in contacts:
                    if idx not in processed:
                        processed.add(idx)
                        group.append((idx, source, vcard))
                
                if len(group) > 1:
                    confidence = self.calculate_match_confidence(
                        group[0][2], group[1][2], 'email'
                    )
                    match_groups.append({
                        'contacts': group,
                        'match_type': 'email',
                        'match_value': email,
                        'confidence': confidence
                    })
        
        # Process phone matches
        for phone, contacts in phone_index.items():
            if len(contacts) > 1:
                unprocessed = [(i, s, v) for i, s, v in contacts if i not in processed]
                if len(unprocessed) > 1:
                    for idx, source, vcard in unprocessed:
                        processed.add(idx)
                    
                    confidence = self.calculate_match_confidence(
                        unprocessed[0][2], unprocessed[1][2], 'phone'
                    )
                    match_groups.append({
                        'contacts': unprocessed,
                        'match_type': 'phone',
                        'match_value': phone,
                        'confidence': confidence
                    })
        
        return match_groups
    
    def assess_photo_quality(self, photo_data):
        """Assess quality of a contact photo"""
        score = 0
        
        try:
            # Decode photo if base64
            if isinstance(photo_data, str):
                photo_bytes = base64.b64decode(photo_data)
            else:
                photo_bytes = photo_data
            
            # Get image info
            img = Image.open(io.BytesIO(photo_bytes))
            width, height = img.size
            file_size = len(photo_bytes)
            
            # Resolution score (40 points)
            if width >= 500 and height >= 500:
                score += 40
            elif width >= 200 and height >= 200:
                score += 20
            else:
                score += 5
            
            # File size score (30 points)
            if file_size > 100_000:
                score += 30
            elif file_size > 20_000:
                score += 15
            else:
                score += 5
            
            # Format score (20 points)
            if img.format in ['PNG', 'JPEG']:
                score += 20
            else:
                score += 10
            
            # Type score (10 points) - simplified
            # Would need more sophisticated analysis for real implementation
            score += 5
            
            return {
                'score': score,
                'width': width,
                'height': height,
                'size': file_size,
                'format': img.format
            }
            
        except Exception as e:
            return {
                'score': 0,
                'error': str(e)
            }
    
    def select_best_photo(self, photos_with_source):
        """Select the best photo from multiple options"""
        best_photo = None
        best_score = 0
        best_source = None
        
        for source, photo_data in photos_with_source:
            quality = self.assess_photo_quality(photo_data)
            
            # Apply source priority bonus
            source_bonus = self.db_priorities.get(source, 50) / 100 * 10
            total_score = quality['score'] + source_bonus
            
            if total_score > best_score:
                best_score = total_score
                best_photo = photo_data
                best_source = source
        
        return best_photo, best_source, best_score
    
    def merge_contact_group(self, group):
        """Merge a group of matched contacts"""
        
        # Sort by database priority
        sorted_contacts = sorted(
            group['contacts'],
            key=lambda x: self.db_priorities.get(x[1], 0),
            reverse=True
        )
        
        # Use highest priority contact as base
        base_idx, base_source, base_vcard = sorted_contacts[0]
        
        # Collect all unique data
        all_emails = set()
        all_phones = set()
        all_urls = set()
        all_addresses = []
        all_notes = []
        all_photos = []
        
        for idx, source, vcard in sorted_contacts:
            # Emails
            if hasattr(vcard, 'email_list'):
                for email in vcard.email_list:
                    if email.value:
                        all_emails.add(email.value)
            
            # Phones
            if hasattr(vcard, 'tel_list'):
                for tel in vcard.tel_list:
                    if tel.value:
                        all_phones.add(tel.value)
            
            # URLs
            if hasattr(vcard, 'url_list'):
                for url in vcard.url_list:
                    if url.value:
                        all_urls.add(url.value)
            
            # Notes
            if hasattr(vcard, 'note') and vcard.note.value:
                all_notes.append(f"[From {source}]: {vcard.note.value}")
            
            # Photos
            if hasattr(vcard, 'photo') and vcard.photo.value:
                all_photos.append((source, vcard.photo.value))
        
        # Create merged vCard
        merged = vobject.vCard()
        
        # Version
        merged.add('version')
        merged.version.value = '3.0'
        
        # Name (from base)
        if hasattr(base_vcard, 'fn'):
            merged.add('fn')
            merged.fn.value = base_vcard.fn.value
        
        if hasattr(base_vcard, 'n'):
            merged.add('n')
            merged.n.value = base_vcard.n.value
        
        # Organization (from base or most complete)
        if hasattr(base_vcard, 'org'):
            merged.add('org')
            merged.org.value = base_vcard.org.value
        
        # Title (from base)
        if hasattr(base_vcard, 'title'):
            merged.add('title')
            merged.title.value = base_vcard.title.value
        
        # Add all unique emails
        for email in all_emails:
            email_field = merged.add('email')
            email_field.value = email
            email_field.type_param = 'INTERNET'
        
        # Add all unique phones
        for phone in all_phones:
            tel_field = merged.add('tel')
            tel_field.value = phone
        
        # Add all unique URLs
        for url in all_urls:
            url_field = merged.add('url')
            url_field.value = url
        
        # Merge notes
        if all_notes:
            merged.add('note')
            merged.note.value = '\n\n'.join(all_notes)
        
        # Select best photo
        if all_photos:
            best_photo, photo_source, photo_score = self.select_best_photo(all_photos)
            if best_photo:
                merged.add('photo')
                merged.photo.value = best_photo
                merged.photo.encoding_param = 'b'
                self.stats['photos_processed'] += 1
        
        return merged
    
    def generate_review_file(self, review_groups, output_path):
        """Generate HTML file for manual review"""
        
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Contact Merge Review</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .match-group { background: white; margin: 20px 0; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .confidence { float: right; font-weight: bold; padding: 5px 10px; border-radius: 5px; }
        .high-conf { background: #d4edda; color: #155724; }
        .med-conf { background: #fff3cd; color: #856404; }
        .low-conf { background: #f8d7da; color: #721c24; }
        .contact { border: 1px solid #ddd; margin: 10px 0; padding: 10px; background: #f9f9f9; }
        .source { font-weight: bold; color: #007bff; }
        .field { margin: 5px 0; }
        .field-label { font-weight: bold; display: inline-block; width: 100px; }
        .match-reason { background: #e3f2fd; padding: 10px; margin: 10px 0; border-left: 4px solid #2196f3; }
        .actions { margin-top: 20px; }
        button { padding: 10px 20px; margin: 5px; cursor: pointer; }
        .merge-btn { background: #28a745; color: white; border: none; }
        .separate-btn { background: #dc3545; color: white; border: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Contact Merge Review</h1>
        <p>Review these potential matches and decide whether to merge or keep separate.</p>
"""
        
        for i, group in enumerate(review_groups):
            conf_class = 'high-conf' if group['confidence'] >= 85 else 'med-conf' if group['confidence'] >= 70 else 'low-conf'
            
            html += f"""
        <div class="match-group" id="group-{i}">
            <div class="confidence {conf_class}">Confidence: {group['confidence']}%</div>
            <h3>Potential Match #{i+1}</h3>
            
            <div class="match-reason">
                <strong>Match Type:</strong> {group['match_type']}<br>
                <strong>Match Value:</strong> {group['match_value']}
            </div>
"""
            
            for idx, source, vcard in group['contacts']:
                name = vcard.fn.value if hasattr(vcard, 'fn') else "No name"
                org = self.extract_org_name(vcard) or "No organization"
                
                html += f"""
            <div class="contact">
                <div class="source">Source: {source}</div>
                <div class="field"><span class="field-label">Name:</span> {name}</div>
                <div class="field"><span class="field-label">Organization:</span> {org}</div>
"""
                
                if hasattr(vcard, 'email_list'):
                    emails = [e.value for e in vcard.email_list if e.value]
                    if emails:
                        html += f'<div class="field"><span class="field-label">Emails:</span> {", ".join(emails)}</div>'
                
                if hasattr(vcard, 'tel_list'):
                    phones = [t.value for t in vcard.tel_list if t.value]
                    if phones:
                        html += f'<div class="field"><span class="field-label">Phones:</span> {", ".join(phones)}</div>'
                
                html += """
            </div>
"""
            
            html += """
            <div class="actions">
                <button class="merge-btn" onclick="markDecision('merge', """ + str(i) + """)">MERGE</button>
                <button class="separate-btn" onclick="markDecision('separate', """ + str(i) + """)">KEEP SEPARATE</button>
            </div>
        </div>
"""
        
        html += """
    </div>
    <script>
        function markDecision(decision, groupId) {
            const group = document.getElementById('group-' + groupId);
            group.style.opacity = '0.5';
            group.setAttribute('data-decision', decision);
            
            // In real implementation, would save to file
            console.log('Group ' + groupId + ': ' + decision);
        }
    </script>
</body>
</html>
"""
        
        with open(output_path, 'w') as f:
            f.write(html)
    
    def merge_databases(self, database_paths, output_path):
        """Main merge function"""
        
        print("Intelligent Contact Merge System")
        print("=" * 80)
        
        # Step 1: Load all contacts with source info
        print("\n1. Loading databases...")
        all_contacts = []
        
        for db_name, db_path in database_paths.items():
            print(f"   Loading {db_name}...")
            with open(db_path, 'r', encoding='utf-8') as f:
                vcards = list(vobject.readComponents(f.read()))
            
            for vcard in vcards:
                all_contacts.append((db_name, vcard))
            
            print(f"   Loaded {len(vcards)} contacts from {db_name}")
            self.stats['total_input'] += len(vcards)
        
        # Step 2: Find matches
        print("\n2. Finding matches...")
        match_groups = self.find_matches(all_contacts)
        print(f"   Found {len(match_groups)} potential match groups")
        
        # Step 3: Separate by confidence
        auto_merge = []
        manual_review = []
        
        for group in match_groups:
            if group['confidence'] >= 95:
                auto_merge.append(group)
            elif group['confidence'] >= 70:
                manual_review.append(group)
            # else: keep separate (confidence < 70)
        
        print(f"\n3. Match distribution:")
        print(f"   Auto-merge (95%+): {len(auto_merge)} groups")
        print(f"   Manual review (70-94%): {len(manual_review)} groups")
        
        # Step 4: Process auto-merge
        print("\n4. Processing auto-merge groups...")
        merged_contacts = []
        merged_indices = set()
        
        for group in auto_merge:
            merged = self.merge_contact_group(group)
            merged_contacts.append(merged)
            
            # Track which contacts were merged
            for idx, _, _ in group['contacts']:
                merged_indices.add(idx)
            
            self.stats['auto_merged'] += len(group['contacts']) - 1
        
        # Step 5: Add unmatched contacts
        print("\n5. Processing unmatched contacts...")
        for i, (source, vcard) in enumerate(all_contacts):
            if i not in merged_indices:
                merged_contacts.append(vcard)
        
        print(f"   Total unique contacts: {len(merged_contacts)}")
        
        # Step 6: Generate review file
        if manual_review:
            review_path = output_path.replace('.vcf', '_review.html')
            self.generate_review_file(manual_review, review_path)
            print(f"\n6. Manual review needed: {len(manual_review)} groups")
            print(f"   Review file: {review_path}")
            self.stats['manual_review'] = len(manual_review)
        
        # Step 7: Write output
        print(f"\n7. Writing merged database...")
        with open(output_path, 'w', encoding='utf-8') as f:
            for vcard in merged_contacts:
                f.write(vcard.serialize())
        
        # Step 8: Generate report
        self.generate_merge_report(output_path)
        
        return self.stats
    
    def generate_merge_report(self, output_path):
        """Generate detailed merge report"""
        
        report = {
            'merge_date': datetime.now().isoformat(),
            'statistics': self.stats,
            'output_file': output_path
        }
        
        report_path = output_path.replace('.vcf', '_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n" + "=" * 80)
        print("MERGE COMPLETE")
        print("=" * 80)
        print(f"Input contacts: {self.stats['total_input']:,}")
        print(f"Auto-merged: {self.stats['auto_merged']}")
        print(f"Manual review needed: {self.stats['manual_review']}")
        print(f"Photos processed: {self.stats['photos_processed']}")
        print(f"\nOutput: {output_path}")
        print(f"Report: {report_path}")


def main():
    """Run the intelligent merge"""
    
    # Create backup
    backup_dir = f"backup/intelligent_merge_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Define database paths
    databases = {
        'sara': 'data/Sara_Export_VALIDATED_20250606_FINAL.vcf',
        'iphone_contacts': 'data/iPhone_Contacts_VALIDATED_20250606_120917_FINAL.vcf',
        'iphone_suggested': 'data/iPhone_Suggested_VALIDATED_20250606_120917_FINAL.vcf'
    }
    
    # Backup all files
    print("Creating backups...")
    for db_name, db_path in databases.items():
        if os.path.exists(db_path):
            backup_path = os.path.join(backup_dir, os.path.basename(db_path))
            shutil.copy2(db_path, backup_path)
            print(f"✓ Backed up {db_name}")
    
    # Run merge
    merger = IntelligentContactMerger()
    output_path = f"data/INTELLIGENTLY_MERGED_{datetime.now().strftime('%Y%m%d_%H%M%S')}.vcf"
    
    stats = merger.merge_databases(databases, output_path)
    
    print(f"\n💾 Backups saved to: {backup_dir}")


if __name__ == "__main__":
    main()