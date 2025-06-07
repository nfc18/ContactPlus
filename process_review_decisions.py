#!/usr/bin/env python3
"""
Process user decisions from the smart contact review
"""

import os
import json
import shutil
import vobject
from datetime import datetime
import re

class DecisionProcessor:
    """Process user decisions to clean databases"""
    
    def __init__(self):
        self.stats = {
            'contacts_split': 0,
            'contacts_deleted': 0,
            'contacts_kept': 0,
            'new_contacts_created': 0,
            'total_processed': 0
        }
    
    def load_decisions_from_browser(self):
        """Load decisions from browser localStorage or manual input"""
        print("Loading your review decisions...")
        
        # Try to get decisions from user input since we can't directly access browser localStorage
        print("\nPlease provide your decisions in one of these ways:")
        print("1. If you exported decisions: provide the JSON file path")
        print("2. Manual entry: I'll prompt you for each decision")
        print("3. Browser storage: copy the decisions from browser console")
        
        choice = input("\nEnter choice (1/2/3): ").strip()
        
        if choice == "1":
            file_path = input("Enter path to exported decisions JSON file: ").strip()
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            else:
                print(f"File not found: {file_path}")
                return None
        
        elif choice == "2":
            return self.manual_decision_entry()
        
        elif choice == "3":
            print("\nIn your browser console, type: JSON.stringify(localStorage.getItem('contact_decisions'))")
            print("Copy the output and paste it here:")
            decisions_str = input("Paste decisions JSON: ").strip()
            try:
                # Remove outer quotes if present
                if decisions_str.startswith('"') and decisions_str.endswith('"'):
                    decisions_str = decisions_str[1:-1]
                # Unescape JSON
                decisions_str = decisions_str.replace('\\"', '"').replace('\\\\', '\\')
                return json.loads(decisions_str)
            except json.JSONDecodeError as e:
                print(f"Invalid JSON: {e}")
                return None
        
        return None
    
    def manual_decision_entry(self):
        """Manual entry of decisions"""
        # Load the analysis report to get contact list
        analysis_files = [f for f in os.listdir('data') if f.startswith('smart_analysis_report_') and f.endswith('.json')]
        if not analysis_files:
            print("No analysis report found!")
            return None
        
        latest_report = sorted(analysis_files)[-1]
        report_path = os.path.join('data', latest_report)
        
        with open(report_path, 'r') as f:
            analysis = json.load(f)
        
        # Get contacts that need review
        review_contacts = analysis['results']['borderline'] + analysis['results']['problematic']
        
        decisions = {}
        print(f"\nEntering decisions for {len(review_contacts)} contacts...")
        print("Options: 'split', 'delete', 'keep'")
        
        for i, contact in enumerate(review_contacts):
            print(f"\n{i+1}/{len(review_contacts)}: {contact['name']}")
            print(f"  Database: {contact['source_database']}")
            print(f"  Emails: {contact['email_count']}")
            print(f"  Classification: {contact['classification']} ({contact['confidence']}%)")
            print(f"  Recommendation: {contact['recommendation']}")
            
            while True:
                decision = input("  Decision (split/delete/keep): ").strip().lower()
                if decision in ['split', 'delete', 'keep']:
                    decisions[str(i)] = decision
                    break
                else:
                    print("  Invalid choice. Please enter 'split', 'delete', or 'keep'")
        
        return decisions
    
    def split_contact(self, vcard):
        """Split a contact into individual contacts (one per email)"""
        if not hasattr(vcard, 'email_list') or not vcard.email_list:
            return [vcard]
        
        new_vcards = []
        base_name = vcard.fn.value if hasattr(vcard, 'fn') else "Unknown"
        
        for email in vcard.email_list:
            if not email.value:
                continue
            
            # Create new vCard
            new_vcard = vobject.vCard()
            new_vcard.add('version')
            new_vcard.version.value = '3.0'
            
            # Generate name from email
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
            
            # Add note about split
            new_vcard.add('note')
            new_vcard.note.value = f"Split from '{base_name}' on {datetime.now().strftime('%Y-%m-%d')}"
            
            new_vcards.append(new_vcard)
        
        self.stats['new_contacts_created'] += len(new_vcards)
        return new_vcards
    
    def process_database(self, db_path, decisions, review_contacts):
        """Process a single database based on decisions"""
        
        print(f"\nProcessing: {os.path.basename(db_path)}")
        print("-" * 60)
        
        # Load database
        with open(db_path, 'r', encoding='utf-8') as f:
            vcards = list(vobject.readComponents(f.read()))
        
        # Create mapping of contacts to review
        review_map = {}
        for i, contact in enumerate(review_contacts):
            if contact['source_database'] == os.path.basename(db_path):
                review_map[contact['name']] = {
                    'index': i,
                    'decision': decisions.get(str(i), 'keep')
                }
        
        # Process contacts
        processed_vcards = []
        
        for vcard in vcards:
            name = vcard.fn.value if hasattr(vcard, 'fn') else "No name"
            
            if name in review_map:
                decision_info = review_map[name]
                decision = decision_info['decision']
                
                print(f"  {name}: {decision}")
                
                if decision == 'split':
                    split_contacts = self.split_contact(vcard)
                    processed_vcards.extend(split_contacts)
                    self.stats['contacts_split'] += 1
                    
                elif decision == 'delete':
                    self.stats['contacts_deleted'] += 1
                    # Don't add to processed_vcards (effectively deleted)
                    
                elif decision == 'keep':
                    processed_vcards.append(vcard)
                    self.stats['contacts_kept'] += 1
                
                self.stats['total_processed'] += 1
            else:
                # Contact not in review list, keep as-is
                processed_vcards.append(vcard)
        
        return processed_vcards
    
    def apply_decisions(self, decisions):
        """Apply decisions to all databases"""
        
        print("Applying Review Decisions")
        print("=" * 80)
        
        # Load analysis report to get review contacts
        analysis_files = [f for f in os.listdir('data') if f.startswith('smart_analysis_report_') and f.endswith('.json')]
        if not analysis_files:
            print("No analysis report found!")
            return
        
        latest_report = sorted(analysis_files)[-1]
        report_path = os.path.join('data', latest_report)
        
        with open(report_path, 'r') as f:
            analysis = json.load(f)
        
        review_contacts = analysis['results']['borderline'] + analysis['results']['problematic']
        
        # Create backup
        backup_dir = f"backup/decision_processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Process each database
        databases = [
            "data/Sara_Export_VALIDATED_20250606_FINAL.vcf",
            "data/iPhone_Contacts_VALIDATED_20250606_120917_FINAL.vcf",
            "data/iPhone_Suggested_VALIDATED_20250606_120917_FINAL.vcf"
        ]
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for db_path in databases:
            if not os.path.exists(db_path):
                print(f"Warning: Database not found - {db_path}")
                continue
            
            # Backup
            backup_path = os.path.join(backup_dir, os.path.basename(db_path))
            shutil.copy2(db_path, backup_path)
            print(f"✓ Backed up: {os.path.basename(db_path)}")
            
            # Process
            processed_vcards = self.process_database(db_path, decisions, review_contacts)
            
            # Save cleaned version
            output_path = db_path.replace('_FINAL.vcf', f'_CLEANED_{timestamp}.vcf')
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for vcard in processed_vcards:
                    f.write(vcard.serialize())
            
            print(f"  ✓ Saved cleaned database: {os.path.basename(output_path)}")
            print(f"    Original: {len(list(vobject.readComponents(open(db_path).read())))} contacts")
            print(f"    Cleaned: {len(processed_vcards)} contacts")
        
        # Print summary
        print("\n" + "=" * 80)
        print("PROCESSING COMPLETE")
        print("=" * 80)
        print(f"Contacts split: {self.stats['contacts_split']}")
        print(f"Contacts deleted: {self.stats['contacts_deleted']}")
        print(f"Contacts kept: {self.stats['contacts_kept']}")
        print(f"New contacts created from splits: {self.stats['new_contacts_created']}")
        print(f"Total decisions processed: {self.stats['total_processed']}")
        
        print(f"\n💾 Backups saved to: {backup_dir}")
        print(f"✅ Clean databases ready for merging!")
        
        # Save processing report
        report = {
            'processing_date': datetime.now().isoformat(),
            'decisions_applied': decisions,
            'statistics': self.stats,
            'backup_location': backup_dir
        }
        
        report_path = f"data/decision_processing_report_{timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Processing report saved to: {report_path}")


def main():
    """Main processing function"""
    
    processor = DecisionProcessor()
    
    # Load decisions
    decisions = processor.load_decisions_from_browser()
    
    if decisions is None:
        print("Could not load decisions. Exiting.")
        return
    
    print(f"\nLoaded {len(decisions)} decisions")
    
    # Apply decisions
    processor.apply_decisions(decisions)


if __name__ == "__main__":
    main()