#!/usr/bin/env python3
"""
Investigate where our email cleaning process failed
"""

import vobject
import os

def analyze_email_counts(filepath, description):
    """Analyze email counts in a file"""
    print(f"\n{description}")
    print("=" * 80)
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        vcards = list(vobject.readComponents(f.read()))
    
    email_distribution = {}
    problematic = []
    
    for vcard in vcards:
        email_count = 0
        if hasattr(vcard, 'email_list'):
            email_count = len(vcard.email_list)
        
        email_distribution[email_count] = email_distribution.get(email_count, 0) + 1
        
        if email_count > 4:
            name = vcard.fn.value if hasattr(vcard, 'fn') else "No name"
            emails = [e.value for e in vcard.email_list[:5]] if hasattr(vcard, 'email_list') else []
            problematic.append((name, email_count, emails))
    
    print(f"Total contacts: {len(vcards)}")
    print(f"Email distribution:")
    for count in sorted(email_distribution.keys()):
        print(f"  {count} emails: {email_distribution[count]} contacts")
    
    if problematic:
        print(f"\n⚠️  PROBLEMATIC CONTACTS ({len(problematic)} found):")
        for name, count, emails in problematic[:10]:  # Show first 10
            print(f"  - {name}: {count} emails")
            for email in emails:
                print(f"    • {email}")
            if count > 5:
                print(f"    • ... and {count - 5} more")
    else:
        print("✅ No contacts with >4 emails found")
    
    return len(problematic)

def main():
    """Investigate the failure step by step"""
    
    print("INVESTIGATING EMAIL CLEANING FAILURE")
    print("=" * 80)
    
    # Check each stage of our process
    stages = [
        ("Original iPhone Contacts", "Imports/iPhone_Contacts_Contacts.vcf"),
        ("After validation", "data/iPhone_Contacts_VALIDATED_20250606_120917.vcf"),
        ("After cleaning non-personal", "data/iPhone_Contacts_VALIDATED_20250606_120917_CLEANED.vcf"),
        ("After manual corrections", "data/iPhone_Contacts_VALIDATED_20250606_120917_CORRECTED.vcf"),
        ("After Daniel fix", "data/iPhone_Contacts_VALIDATED_20250606_120917_FIXED.vcf"),
        ("Final version", "data/iPhone_Contacts_VALIDATED_20250606_120917_FINAL.vcf"),
        ("After intelligent merge", "data/INTELLIGENTLY_MERGED_20250606_133625.vcf"),
        ("After final cleaning", "data/FINAL_CLEANED_MERGED_20250606_134153.vcf")
    ]
    
    problem_counts = []
    
    for description, filepath in stages:
        count = analyze_email_counts(filepath, description)
        problem_counts.append((description, count))
    
    print("\n" + "=" * 80)
    print("FAILURE ANALYSIS")
    print("=" * 80)
    
    for description, count in problem_counts:
        status = "✅" if count == 0 else f"⚠️  {count} problems"
        print(f"{status} {description}")
    
    # Check Sara and iPhone Suggested too
    print("\nChecking other databases:")
    analyze_email_counts("data/Sara_Export_VALIDATED_20250606_FINAL.vcf", "Sara's Final Database")
    analyze_email_counts("data/iPhone_Suggested_VALIDATED_20250606_120917_FINAL.vcf", "iPhone Suggested Final")

if __name__ == "__main__":
    main()