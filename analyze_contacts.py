#!/usr/bin/env python3
"""Analyze Sara's contacts and create review queue

Follows the standard pattern:
- vcard library for validation
- vobject for manipulation
"""

import json
import os
from parser import VCardParser
from analyzer import ContactAnalyzer
from vcard_validator import VCardStandardsValidator
import config

def main():
    # Ensure data directory exists
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    print("Contact Cleaner - Analysis Phase")
    print("================================")
    print(f"Analyzing: {os.path.basename(config.SARA_VCARD_FILE)}")
    print("\nFollowing standard pattern: vcard for validation, vobject for manipulation")
    
    # Step 0: Validate first (following the standard)
    print("\n0. Validating vCard file with vcard library...")
    validator = VCardStandardsValidator(strict=False)
    is_valid, errors, warnings = validator.validate_file(config.SARA_VCARD_FILE)
    print(f"   ✓ Validation complete: {len(errors)} errors, {len(warnings)} warnings")
    
    if not is_valid and len(errors) > 100:
        print(f"   ❌ Too many validation errors. Please fix the file first.")
        return
    
    # Parse vCard file (now using vobject after validation)
    print("\n1. Parsing vCard file with vobject...")
    parser = VCardParser(config.SARA_VCARD_FILE)
    contacts = parser.parse()
    print(f"   ✓ Parsed {len(contacts)} contacts")
    
    # Show validation report from parser
    if hasattr(parser, 'validation_report') and parser.validation_report:
        print(f"   ℹ️  Parser validation: {parser.validation_report['error_count']} errors")
    
    # Find issues
    print("\n2. Identifying issues...")
    contacts_with_issues = parser.find_issues()
    print(f"   ✓ Found {len(contacts_with_issues)} contacts with potential issues")
    
    # Analyze contacts
    print("\n3. Analyzing contacts...")
    analyzer = ContactAnalyzer(contacts)
    stats = analyzer.analyze()
    
    # Print statistics
    print("\n4. Statistics:")
    print(f"   - Total contacts: {stats['total_contacts']}")
    print(f"   - Contacts with issues: {stats['contacts_with_issues']}")
    print(f"   - Review queue size: {stats['review_queue_size']}")
    
    print("\n   Issue breakdown:")
    for issue_type, count in stats['issue_types'].items():
        print(f"     • {issue_type}: {count}")
    
    print("\n   Email distribution:")
    for email_count in sorted(stats['email_distribution'].keys()):
        count = stats['email_distribution'][email_count]
        print(f"     • {email_count} emails: {count} contacts")
    
    # Get detailed statistics
    detailed_stats = analyzer.get_statistics()
    print(f"\n   Contacts with 4+ emails: {detailed_stats['emails']['contacts_with_4plus_emails']}")
    print(f"   Maximum emails per contact: {detailed_stats['emails']['max_emails_per_contact']}")
    
    # Save review queue
    print("\n5. Saving review queue...")
    analyzer.save_review_queue()
    print(f"   ✓ Saved to: {config.REVIEW_QUEUE_FILE}")
    
    # Save statistics
    stats_file = os.path.join(config.DATA_DIR, 'analysis_stats.json')
    with open(stats_file, 'w') as f:
        json.dump(detailed_stats, f, indent=2)
    print(f"   ✓ Statistics saved to: {stats_file}")
    
    print("\n✅ Analysis complete! Ready for web review.")
    
    # Show sample of review items
    if analyzer.review_queue:
        print("\nSample review items:")
        for item in analyzer.review_queue[:3]:
            print(f"\n   • {item['formatted_name']}")
            print(f"     Organizations: {', '.join(item['organizations']) if item['organizations'] else 'None'}")
            print(f"     Emails: {item['email_count']}")
            print(f"     Issues: {', '.join(issue['type'] for issue in item['issues'])}")

if __name__ == "__main__":
    main()