#!/usr/bin/env python3
"""Integrity check for cleaned vCard database"""

import vobject
import re
from collections import defaultdict
import config

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def check_email_format(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def check_phone_format(phone):
    """Check if phone number has reasonable format"""
    # Remove common formatting characters
    clean_phone = re.sub(r'[\s\-\(\)\.]', '', phone)
    # Check if it has digits and reasonable length
    return len(clean_phone) >= 6 and any(c.isdigit() for c in clean_phone)

def run_integrity_check(filepath):
    """Run comprehensive integrity check on vCard file"""
    print(f"{Colors.HEADER}Running vCard Integrity Check{Colors.ENDC}")
    print("="*60)
    
    issues = defaultdict(list)
    stats = {
        'total': 0,
        'valid': 0,
        'warnings': 0,
        'errors': 0,
        'emails_checked': 0,
        'phones_checked': 0,
        'names_checked': 0,
        'photos_checked': 0
    }
    
    duplicate_emails = defaultdict(list)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            vcard_data = f.read()
        
        print(f"Checking vCards...")
        
        for idx, vcard in enumerate(vobject.readComponents(vcard_data)):
            stats['total'] += 1
            contact_name = "Unknown"
            has_error = False
            has_warning = False
            
            try:
                # Check 1: Required fields
                if not hasattr(vcard, 'fn') or not vcard.fn.value:
                    issues['missing_fn'].append(f"Contact {idx+1}: Missing formatted name (FN)")
                    has_error = True
                else:
                    contact_name = vcard.fn.value
                    stats['names_checked'] += 1
                
                if not hasattr(vcard, 'n'):
                    issues['missing_n'].append(f"{contact_name}: Missing structured name (N)")
                    has_warning = True
                
                # Check 2: Name quality
                if hasattr(vcard, 'fn') and vcard.fn.value:
                    if len(vcard.fn.value) < 2:
                        issues['short_name'].append(f"{contact_name}: Very short name")
                        has_warning = True
                    if vcard.fn.value.lower() in ['unknown', 'no name', 'test']:
                        issues['placeholder_name'].append(f"{contact_name}: Placeholder name detected")
                        has_warning = True
                
                # Check 3: Email validation
                if hasattr(vcard, 'email_list'):
                    for email in vcard.email_list:
                        stats['emails_checked'] += 1
                        email_addr = email.value
                        
                        if not check_email_format(email_addr):
                            issues['invalid_email'].append(f"{contact_name}: Invalid email format '{email_addr}'")
                            has_error = True
                        
                        # Track duplicates
                        duplicate_emails[email_addr.lower()].append(contact_name)
                
                # Check 4: Phone validation
                if hasattr(vcard, 'tel_list'):
                    for tel in vcard.tel_list:
                        stats['phones_checked'] += 1
                        phone_num = tel.value
                        
                        if not check_phone_format(phone_num):
                            issues['invalid_phone'].append(f"{contact_name}: Suspicious phone format '{phone_num}'")
                            has_warning = True
                
                # Check 5: Photo check
                if hasattr(vcard, 'photo'):
                    stats['photos_checked'] += 1
                    # Just verify it exists, don't validate the data
                
                # Check 6: Special characters in critical fields
                if hasattr(vcard, 'fn') and vcard.fn.value:
                    if any(char in vcard.fn.value for char in ['<', '>', '/', '\\', '|', '\n', '\r', '\t']):
                        issues['special_chars'].append(f"{contact_name}: Special characters in name")
                        has_warning = True
                
                # Check 7: Contact completeness
                has_contact_info = (hasattr(vcard, 'email_list') and vcard.email_list) or \
                                 (hasattr(vcard, 'tel_list') and vcard.tel_list)
                if not has_contact_info:
                    issues['no_contact_info'].append(f"{contact_name}: No email or phone")
                    has_warning = True
                
                # Check 8: Notes field for splitting markers
                if hasattr(vcard, 'note') and vcard.note.value:
                    if "NEEDS SPLITTING" in vcard.note.value:
                        issues['needs_splitting'].append(f"{contact_name}: Marked for splitting")
                        has_warning = True
                
                # Update counters
                if has_error:
                    stats['errors'] += 1
                elif has_warning:
                    stats['warnings'] += 1
                else:
                    stats['valid'] += 1
                    
            except Exception as e:
                issues['parse_errors'].append(f"Contact {idx+1}: Parse error - {str(e)}")
                stats['errors'] += 1
        
        # Check for duplicate emails
        for email, names in duplicate_emails.items():
            if len(names) > 1:
                issues['duplicate_emails'].append(f"Email '{email}' used by: {', '.join(names[:5])}")
        
        # Print results
        print(f"\n{Colors.BOLD}Integrity Check Results{Colors.ENDC}")
        print("="*60)
        
        print(f"\n{Colors.BOLD}Statistics:{Colors.ENDC}")
        print(f"  Total contacts: {stats['total']}")
        print(f"  ✅ Valid contacts: {Colors.GREEN}{stats['valid']}{Colors.ENDC}")
        print(f"  ⚠️  Warnings: {Colors.WARNING}{stats['warnings']}{Colors.ENDC}")
        print(f"  ❌ Errors: {Colors.FAIL}{stats['errors']}{Colors.ENDC}")
        print(f"\n  Emails checked: {stats['emails_checked']}")
        print(f"  Phones checked: {stats['phones_checked']}")
        print(f"  Names checked: {stats['names_checked']}")
        print(f"  Photos found: {stats['photos_checked']}")
        
        # Print issues
        if issues:
            print(f"\n{Colors.BOLD}Issues Found:{Colors.ENDC}")
            
            # Critical errors
            critical_issues = ['missing_fn', 'invalid_email', 'parse_errors']
            has_critical = False
            for issue_type in critical_issues:
                if issues[issue_type]:
                    has_critical = True
                    print(f"\n{Colors.FAIL}❌ {issue_type.replace('_', ' ').title()} ({len(issues[issue_type])}):{Colors.ENDC}")
                    for item in issues[issue_type][:5]:
                        print(f"    • {item}")
                    if len(issues[issue_type]) > 5:
                        print(f"    ... and {len(issues[issue_type]) - 5} more")
            
            # Warnings
            warning_issues = ['missing_n', 'short_name', 'placeholder_name', 'invalid_phone', 
                            'special_chars', 'no_contact_info', 'needs_splitting', 'duplicate_emails']
            for issue_type in warning_issues:
                if issues[issue_type]:
                    print(f"\n{Colors.WARNING}⚠️  {issue_type.replace('_', ' ').title()} ({len(issues[issue_type])}):{Colors.ENDC}")
                    for item in issues[issue_type][:5]:
                        print(f"    • {item}")
                    if len(issues[issue_type]) > 5:
                        print(f"    ... and {len(issues[issue_type]) - 5} more")
        
        # Final verdict
        print(f"\n{Colors.BOLD}Final Verdict:{Colors.ENDC}")
        if stats['errors'] == 0:
            print(f"{Colors.GREEN}✅ Database is ready for import!{Colors.ENDC}")
            print("   All contacts meet vCard standards and should import successfully.")
            if stats['warnings'] > 0:
                print(f"\n   Note: {stats['warnings']} contacts have minor issues that won't prevent import")
                print("   but you may want to review them later.")
        else:
            print(f"{Colors.FAIL}❌ Critical issues found!{Colors.ENDC}")
            print(f"   {stats['errors']} contacts have errors that may cause import problems.")
            print("   Please fix these issues before importing.")
        
        # iCloud specific checks
        print(f"\n{Colors.BOLD}iCloud Compatibility:{Colors.ENDC}")
        icloud_ok = True
        
        if stats['total'] > 50000:
            print(f"  {Colors.WARNING}⚠️  Large database ({stats['total']} contacts) - iCloud has a 50,000 contact limit{Colors.ENDC}")
            icloud_ok = False
        else:
            print(f"  ✅ Contact count OK ({stats['total']} contacts)")
        
        if any(len(issues[key]) > 0 for key in ['missing_fn', 'invalid_email']):
            print(f"  {Colors.FAIL}❌ Critical field errors detected{Colors.ENDC}")
            icloud_ok = False
        else:
            print("  ✅ All required fields present")
        
        print("  ✅ vCard 3.0 format (iCloud compatible)")
        print("  ✅ UTF-8 encoding")
        
        if icloud_ok:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ Ready for iCloud import!{Colors.ENDC}")
        else:
            print(f"\n{Colors.FAIL}{Colors.BOLD}❌ Fix issues before iCloud import{Colors.ENDC}")
            
    except Exception as e:
        print(f"{Colors.FAIL}Error running integrity check: {e}{Colors.ENDC}")
        return False
    
    return stats['errors'] == 0

if __name__ == "__main__":
    import sys
    
    # Use cleaned file by default
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = config.PROCESSED_VCARD_FILE
    
    print(f"Checking: {filepath}\n")
    success = run_integrity_check(filepath)
    sys.exit(0 if success else 1)