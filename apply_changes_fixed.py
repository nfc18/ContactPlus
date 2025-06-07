#!/usr/bin/env python3
"""Apply review decisions to create cleaned vCard file - Fixed version"""

import json
import os
import vobject
from datetime import datetime
import config

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def load_decisions():
    """Load review decisions"""
    if not os.path.exists(config.DECISIONS_FILE):
        print(f"{Colors.FAIL}No decisions found. Run review_cli.py first!{Colors.ENDC}")
        return None
    
    with open(config.DECISIONS_FILE, 'r') as f:
        return json.load(f)

def load_review_queue():
    """Load review queue with original vCards"""
    with open(config.REVIEW_QUEUE_FILE, 'r') as f:
        return json.load(f)

def ensure_vcard_has_fn(vcard):
    """Ensure vCard has FN field"""
    if not hasattr(vcard, 'fn'):
        # Try to construct FN from N
        if hasattr(vcard, 'n'):
            name_parts = []
            if vcard.n.value.given:
                name_parts.append(vcard.n.value.given)
            if vcard.n.value.family:
                name_parts.append(vcard.n.value.family)
            
            if name_parts:
                vcard.add('fn')
                vcard.fn.value = ' '.join(name_parts)
            else:
                # Last resort - use email or org
                if hasattr(vcard, 'email'):
                    vcard.add('fn')
                    vcard.fn.value = vcard.email.value.split('@')[0]
                elif hasattr(vcard, 'org'):
                    vcard.add('fn')
                    vcard.fn.value = str(vcard.org.value[0] if isinstance(vcard.org.value, list) else vcard.org.value)
                else:
                    vcard.add('fn')
                    vcard.fn.value = "Unknown"

def apply_email_changes(vcard, kept_emails):
    """Remove emails not in kept_emails list"""
    # Remove all existing emails
    if hasattr(vcard, 'email_list'):
        for email in list(vcard.email_list):
            vcard.remove(email)
    
    # Add back only kept emails
    for email_addr in kept_emails:
        email = vcard.add('email')
        email.value = email_addr
        email.type_param = 'INTERNET'

def process_decisions():
    """Process all decisions and create new vCard file"""
    print(f"{Colors.HEADER}Applying Review Decisions{Colors.ENDC}")
    print("="*60)
    
    # Load data
    decisions = load_decisions()
    if not decisions:
        return
    
    queue_data = load_review_queue()
    
    # Create lookup for decisions
    decision_map = {}
    for item in queue_data['items']:
        if item['id'] in decisions['decisions']:
            decision_map[item['id']] = {
                'decision': decisions['decisions'][item['id']],
                'original_vcard': item['original_vcard']
            }
    
    # Load original vCard file
    print(f"\nLoading original vCard file...")
    with open(config.SARA_VCARD_FILE, 'r', encoding='utf-8') as f:
        vcard_data = f.read()
    
    # Process changes
    modified_count = 0
    kept_all_count = 0
    primary_only_count = 0
    selected_emails_count = 0
    split_count = 0
    skipped_count = 0
    
    output_vcards = []
    errors = 0
    
    print(f"Processing vCards...")
    
    for vcard in vobject.readComponents(vcard_data):
        try:
            # Ensure vCard has FN
            ensure_vcard_has_fn(vcard)
            
            # Get vCard string for comparison
            vcard_str = vcard.serialize()
            
            modified = False
            for contact_id, data in decision_map.items():
                # Compare normalized versions
                if data['original_vcard'].strip() == vcard_str.strip():
                    decision = data['decision']
                    action = decision['action']
                    
                    if action == 'keep_all':
                        kept_all_count += 1
                        # No changes needed
                    
                    elif action == 'primary_only':
                        primary_only_count += 1
                        # Keep only first email
                        if hasattr(vcard, 'email_list') and len(vcard.email_list) > 1:
                            first_email = vcard.email_list[0].value
                            apply_email_changes(vcard, [first_email])
                            modified = True
                    
                    elif action == 'select_emails':
                        selected_emails_count += 1
                        # Keep only selected emails
                        kept_emails = decision['details'].get('kept_emails', [])
                        if kept_emails:
                            apply_email_changes(vcard, kept_emails)
                            modified = True
                    
                    elif action == 'split_contact':
                        split_count += 1
                        # Mark for manual splitting (add note)
                        if not hasattr(vcard, 'note'):
                            vcard.add('note')
                        vcard.note.value = "NEEDS SPLITTING: Multiple people in one contact"
                        modified = True
                    
                    elif action == 'skip':
                        skipped_count += 1
                    
                    if modified:
                        modified_count += 1
                    
                    break
            
            output_vcards.append(vcard)
            
        except Exception as e:
            errors += 1
            print(f"{Colors.WARNING}Warning: Error processing vCard: {e}{Colors.ENDC}")
            # Still include the vCard even if there was an error
            output_vcards.append(vcard)
    
    # Write output file
    output_file = config.PROCESSED_VCARD_FILE
    print(f"\nWriting cleaned vCard file...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for vcard in output_vcards:
            try:
                f.write(vcard.serialize())
            except Exception as e:
                print(f"{Colors.WARNING}Warning: Could not write vCard: {e}{Colors.ENDC}")
    
    # Print summary
    print(f"\n{Colors.GREEN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Process Complete!{Colors.ENDC}")
    print(f"\nSummary:")
    print(f"  • Total contacts processed: {len(output_vcards)}")
    print(f"  • Contacts modified: {modified_count}")
    print(f"  • Kept all emails: {kept_all_count}")
    print(f"  • Primary email only: {primary_only_count}")
    print(f"  • Selected emails: {selected_emails_count}")
    print(f"  • Marked for splitting: {split_count}")
    print(f"  • Skipped: {skipped_count}")
    if errors > 0:
        print(f"  • Errors encountered: {errors}")
    print(f"\nOutput file: {Colors.GREEN}{output_file}{Colors.ENDC}")
    
    # Create summary report
    report_file = output_file.replace('.vcf', '_report.txt')
    with open(report_file, 'w') as f:
        f.write("Contact Cleaner Report\n")
        f.write("="*50 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total contacts processed: {len(output_vcards)}\n")
        f.write(f"Contacts modified: {modified_count}\n")
        f.write(f"Kept all emails: {kept_all_count}\n")
        f.write(f"Primary email only: {primary_only_count}\n")
        f.write(f"Selected emails: {selected_emails_count}\n")
        f.write(f"Marked for splitting: {split_count}\n")
        f.write(f"Skipped: {skipped_count}\n")
        f.write(f"Errors encountered: {errors}\n")
    
    print(f"Report saved to: {Colors.GREEN}{report_file}{Colors.ENDC}")

if __name__ == "__main__":
    process_decisions()