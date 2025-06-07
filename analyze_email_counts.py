#!/usr/bin/env python3
"""
Analyze email address distribution in validated vCard databases
Find contacts with multiple email addresses
"""

import os
import vobject
from collections import defaultdict
import json
from datetime import datetime

def analyze_email_distribution(filepath):
    """Analyze email address distribution in a vCard file"""
    
    print(f"\nAnalyzing: {os.path.basename(filepath)}")
    print("-" * 60)
    
    email_count_distribution = defaultdict(int)
    contacts_with_many_emails = []
    total_contacts = 0
    total_emails = 0
    
    # Load vCards
    with open(filepath, 'r', encoding='utf-8') as f:
        vcards = list(vobject.readComponents(f.read()))
    
    # Analyze each vCard
    for vcard in vcards:
        total_contacts += 1
        email_count = 0
        emails = []
        
        if hasattr(vcard, 'email_list'):
            for email in vcard.email_list:
                if email.value:
                    email_count += 1
                    emails.append(email.value)
                    total_emails += 1
        
        email_count_distribution[email_count] += 1
        
        # Track contacts with 4+ emails
        if email_count >= 4:
            name = "No name"
            if hasattr(vcard, 'fn') and vcard.fn.value:
                name = vcard.fn.value
            
            org = None
            if hasattr(vcard, 'org') and vcard.org.value:
                if isinstance(vcard.org.value, list):
                    org = ' '.join(vcard.org.value)
                else:
                    org = str(vcard.org.value)
            
            contacts_with_many_emails.append({
                'name': name,
                'email_count': email_count,
                'emails': emails,
                'organization': org
            })
    
    # Print distribution
    print(f"Total contacts: {total_contacts}")
    print(f"Total email addresses: {total_emails}")
    print(f"Average emails per contact: {total_emails/total_contacts:.2f}")
    
    print("\nEmail count distribution:")
    for count in sorted(email_count_distribution.keys()):
        num_contacts = email_count_distribution[count]
        percentage = (num_contacts / total_contacts) * 100
        print(f"  {count} emails: {num_contacts} contacts ({percentage:.1f}%)")
    
    # Print contacts with many emails
    if contacts_with_many_emails:
        print(f"\nContacts with 4+ email addresses ({len(contacts_with_many_emails)} found):")
        # Sort by email count descending
        contacts_with_many_emails.sort(key=lambda x: x['email_count'], reverse=True)
        
        for contact in contacts_with_many_emails[:20]:  # Show top 20
            print(f"\n  {contact['name']}")
            print(f"    Emails: {contact['email_count']}")
            if contact['organization']:
                print(f"    Organization: {contact['organization']}")
            print("    Email addresses:")
            for email in contact['emails'][:10]:  # Show first 10 emails
                print(f"      - {email}")
            if contact['email_count'] > 10:
                print(f"      ... and {contact['email_count'] - 10} more")
    
    return {
        'total_contacts': total_contacts,
        'total_emails': total_emails,
        'distribution': dict(email_count_distribution),
        'contacts_with_many_emails': contacts_with_many_emails
    }


def main():
    """Analyze all validated databases"""
    
    print("Email Address Distribution Analysis")
    print("=" * 80)
    
    databases = [
        "data/Sara_Export_VALIDATED_20250606.vcf",
        "data/iPhone_Contacts_VALIDATED_20250606_120917.vcf",
        "data/iPhone_Suggested_VALIDATED_20250606_120917.vcf"
    ]
    
    all_results = {}
    total_contacts_with_many = 0
    
    for db_path in databases:
        if os.path.exists(db_path):
            results = analyze_email_distribution(db_path)
            all_results[os.path.basename(db_path)] = results
            total_contacts_with_many += len(results['contacts_with_many_emails'])
        else:
            print(f"Warning: File not found - {db_path}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total contacts with 4+ emails across all databases: {total_contacts_with_many}")
    
    # Find contacts with most emails
    all_contacts_with_many = []
    for db_name, results in all_results.items():
        for contact in results['contacts_with_many_emails']:
            contact['database'] = db_name
            all_contacts_with_many.append(contact)
    
    if all_contacts_with_many:
        all_contacts_with_many.sort(key=lambda x: x['email_count'], reverse=True)
        
        print("\nTop 10 contacts with most email addresses:")
        for contact in all_contacts_with_many[:10]:
            print(f"\n  {contact['name']} ({contact['database']})")
            print(f"    {contact['email_count']} email addresses")
            if contact['organization']:
                print(f"    Organization: {contact['organization']}")
    
    # Save detailed report
    report = {
        'analysis_date': datetime.now().isoformat(),
        'databases_analyzed': databases,
        'results': all_results,
        'total_contacts_with_4plus_emails': total_contacts_with_many
    }
    
    report_path = f"data/email_distribution_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_path}")


if __name__ == "__main__":
    main()