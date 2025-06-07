#!/usr/bin/env python3
"""CLI-based contact review tool"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
import config

# Colors for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def load_review_queue() -> Dict[str, Any]:
    """Load review queue from JSON file"""
    if not os.path.exists(config.REVIEW_QUEUE_FILE):
        print(f"{Colors.FAIL}Error: No review queue found. Run analyze_contacts.py first!{Colors.ENDC}")
        sys.exit(1)
    
    with open(config.REVIEW_QUEUE_FILE, 'r') as f:
        return json.load(f)

def load_decisions() -> Dict[str, Any]:
    """Load existing decisions"""
    if not os.path.exists(config.DECISIONS_FILE):
        return {'decisions': {}, 'stats': {'reviewed': 0}}
    
    with open(config.DECISIONS_FILE, 'r') as f:
        return json.load(f)

def save_decisions(decisions: Dict[str, Any]):
    """Save decisions to file"""
    with open(config.DECISIONS_FILE, 'w') as f:
        json.dump(decisions, f, indent=2, ensure_ascii=False)

def print_contact(contact: Dict[str, Any], current: int, total: int):
    """Pretty print contact information"""
    clear_screen()
    
    # Header
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Contact Review - {current} of {total} ({current/total*100:.0f}%){Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    
    # Contact name and organization
    name = contact.get('formatted_name', 'No Name')
    print(f"{Colors.BOLD}{Colors.CYAN}Name:{Colors.ENDC} {name}")
    
    if contact.get('organizations'):
        orgs = ', '.join(contact['organizations'])
        print(f"{Colors.BOLD}{Colors.CYAN}Organization:{Colors.ENDC} {orgs}")
    
    print()
    
    # Email addresses
    print(f"{Colors.BOLD}{Colors.WARNING}📧 Email Addresses ({len(contact['emails'])}){Colors.ENDC}")
    print("-" * 40)
    for idx, email in enumerate(contact['emails'], 1):
        email_addr = email['address']
        types = ', '.join(email.get('type', [])) if email.get('type') else ''
        type_str = f" ({types})" if types else ""
        primary = " [PRIMARY]" if idx == 1 else ""
        print(f"{idx}. {email_addr}{type_str}{Colors.GREEN}{primary}{Colors.ENDC}")
    
    # Phone numbers
    if contact.get('phones'):
        print(f"\n{Colors.BOLD}📱 Phone Numbers{Colors.ENDC}")
        print("-" * 40)
        for phone in contact['phones']:
            phone_num = phone['number']
            types = ', '.join(phone.get('type', [])) if phone.get('type') else ''
            type_str = f" ({types})" if types else ""
            print(f"• {phone_num}{type_str}")
    
    # Issues
    print(f"\n{Colors.BOLD}{Colors.FAIL}⚠️  Issues Found{Colors.ENDC}")
    print("-" * 40)
    for issue in contact.get('issues', []):
        if issue['type'] == 'too_many_emails':
            print(f"• Too many email addresses ({issue['count']})")
        elif issue['type'] == 'mixed_domains':
            print(f"• Mixed email domains ({issue['domain_count']} different domains)")
        else:
            print(f"• {issue['type']}")
    
    print()

def get_user_action() -> tuple:
    """Get user's decision for the contact"""
    print(f"\n{Colors.BOLD}Available Actions:{Colors.ENDC}")
    print(f"1. {Colors.GREEN}Keep All{Colors.ENDC} - Keep all email addresses")
    print(f"2. {Colors.BLUE}Primary Only{Colors.ENDC} - Keep only the first (primary) email")
    print(f"3. {Colors.WARNING}Select Emails{Colors.ENDC} - Choose which emails to keep")
    print(f"4. {Colors.FAIL}Split Contact{Colors.ENDC} - Mark for splitting into multiple contacts")
    print("5. Skip - Review this contact later")
    print("6. Quit - Save progress and exit")
    
    while True:
        choice = input(f"\n{Colors.BOLD}Enter your choice (1-6):{Colors.ENDC} ").strip()
        
        if choice == '1':
            return 'keep_all', {}
        elif choice == '2':
            return 'primary_only', {}
        elif choice == '3':
            return 'select_emails', {}
        elif choice == '4':
            return 'split_contact', {}
        elif choice == '5':
            return 'skip', {}
        elif choice == '6':
            return 'quit', {}
        else:
            print(f"{Colors.FAIL}Invalid choice. Please enter 1-6.{Colors.ENDC}")

def select_emails_interactive(emails: List[Dict[str, str]]) -> List[str]:
    """Interactive email selection"""
    print(f"\n{Colors.BOLD}Select emails to KEEP:{Colors.ENDC}")
    print("Enter the numbers of emails to keep, separated by spaces")
    print("Example: 1 3 4")
    print(f"Press Enter to keep ALL, or type '0' to keep NONE")
    
    while True:
        selection = input("\nYour selection: ").strip()
        
        if not selection:  # Keep all
            return [email['address'] for email in emails]
        
        if selection == '0':  # Keep none
            print(f"{Colors.FAIL}You must keep at least one email!{Colors.ENDC}")
            continue
        
        try:
            indices = [int(x) - 1 for x in selection.split()]
            if all(0 <= i < len(emails) for i in indices):
                selected = [emails[i]['address'] for i in indices]
                
                # Confirm selection
                print(f"\n{Colors.BOLD}You selected:{Colors.ENDC}")
                for email in selected:
                    print(f"  ✓ {email}")
                
                confirm = input("\nConfirm? (y/n): ").lower()
                if confirm == 'y':
                    return selected
            else:
                print(f"{Colors.FAIL}Invalid selection. Please use numbers 1-{len(emails)}{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}Invalid input. Please enter numbers only.{Colors.ENDC}")

def review_contacts():
    """Main review loop"""
    # Load data
    queue_data = load_review_queue()
    decisions = load_decisions()
    
    items = queue_data.get('items', [])
    total_items = len(items)
    
    if total_items == 0:
        print(f"{Colors.WARNING}No contacts to review!{Colors.ENDC}")
        return
    
    # Find unreviewed contacts
    unreviewed = [item for item in items if item['id'] not in decisions['decisions']]
    
    if not unreviewed:
        print(f"{Colors.GREEN}All contacts have been reviewed!{Colors.ENDC}")
        show_summary(decisions)
        return
    
    print(f"{Colors.BOLD}Starting review of {len(unreviewed)} contacts...{Colors.ENDC}")
    input("Press Enter to begin...")
    
    # Review loop
    for idx, contact in enumerate(unreviewed, 1):
        current_total = len(decisions['decisions']) + idx
        print_contact(contact, current_total, total_items)
        
        action, details = get_user_action()
        
        if action == 'quit':
            save_decisions(decisions)
            print(f"\n{Colors.GREEN}Progress saved. You can resume later.{Colors.ENDC}")
            return
        
        if action == 'skip':
            continue
        
        # Handle email selection
        if action == 'select_emails':
            kept_emails = select_emails_interactive(contact['emails'])
            removed_emails = [e['address'] for e in contact['emails'] if e['address'] not in kept_emails]
            details = {
                'kept_emails': kept_emails,
                'removed_emails': removed_emails
            }
        elif action == 'primary_only':
            details = {
                'primary_email': contact['emails'][0]['address'],
                'removed_emails': [e['address'] for e in contact['emails'][1:]]
            }
        
        # Save decision
        decisions['decisions'][contact['id']] = {
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'details': details,
            'contact_name': contact.get('formatted_name', 'Unknown')
        }
        
        # Update stats
        decisions['stats']['reviewed'] = len(decisions['decisions'])
        decisions['stats']['last_review'] = datetime.now().isoformat()
        
        # Save after each decision
        save_decisions(decisions)
        print(f"\n{Colors.GREEN}✓ Decision saved{Colors.ENDC}")
        
        if idx < len(unreviewed):
            input("\nPress Enter for next contact...")
    
    # Show summary
    print(f"\n{Colors.GREEN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Review Complete!{Colors.ENDC}")
    show_summary(decisions)

def show_summary(decisions: Dict[str, Any]):
    """Show review summary"""
    print(f"\n{Colors.BOLD}Review Summary:{Colors.ENDC}")
    print(f"Total reviewed: {len(decisions['decisions'])}")
    
    # Count actions
    action_counts = {}
    for decision in decisions['decisions'].values():
        action = decision['action']
        action_counts[action] = action_counts.get(action, 0) + 1
    
    print(f"\n{Colors.BOLD}Actions taken:{Colors.ENDC}")
    for action, count in action_counts.items():
        print(f"  • {action.replace('_', ' ').title()}: {count}")

def main():
    """Main entry point"""
    print(f"{Colors.HEADER}Contact Cleaner - CLI Review Tool{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    
    # Check for existing decisions
    decisions = load_decisions()
    reviewed = len(decisions.get('decisions', {}))
    
    if reviewed > 0:
        print(f"Found {reviewed} existing review decisions.")
        choice = input("Continue from where you left off? (y/n): ").lower()
        if choice != 'y':
            print("Exiting...")
            return
    
    review_contacts()

if __name__ == "__main__":
    main()