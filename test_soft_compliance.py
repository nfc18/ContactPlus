#!/usr/bin/env python3
"""
Test soft compliance with example vCards
"""

import vobject
from vcard_soft_compliance import SoftComplianceChecker


def create_test_vcards():
    """Create test vCards with soft compliance issues"""
    
    # Test 1: Email/phone in notes
    vcard1 = vobject.vCard()
    vcard1.add('fn')
    vcard1.fn.value = 'JOHN SMITH'  # Also tests capitalization
    vcard1.add('n')
    vcard1.n.value = vobject.vcard.Name(family='SMITH', given='JOHN')
    vcard1.add('note')
    vcard1.note.value = 'Call me at 555-123-4567 or email john@example.com for details'
    vcard1.add('version')
    vcard1.version.value = '3.0'
    
    # Test 2: Phone formatting
    vcard2 = vobject.vCard()
    vcard2.add('fn')
    vcard2.fn.value = 'jane doe'  # All lowercase
    vcard2.add('tel')
    vcard2.tel.value = '(212) 555-1234'  # US format, not E.164
    vcard2.add('tel')
    vcard2.tel.value = '44 20 7123 4567'  # UK format
    vcard2.add('version')
    vcard2.version.value = '3.0'
    
    # Test 3: Duplicate emails and improper org name
    vcard3 = vobject.vCard()
    vcard3.add('fn')
    vcard3.fn.value = "o'brien, patrick"  # Complex capitalization
    vcard3.add('email')
    vcard3.email.value = 'Patrick@Company.COM'
    vcard3.add('email')
    vcard3.email.value = 'PATRICK@COMPANY.COM'  # Duplicate
    vcard3.add('org')
    vcard3.org.value = ['acme corp', 'it department']  # Needs capitalization
    vcard3.add('version')
    vcard3.version.value = '3.0'
    
    return [vcard1, vcard2, vcard3]


def demonstrate_soft_compliance():
    """Show soft compliance fixes in action"""
    
    print("Soft Compliance Demonstration")
    print("=" * 60)
    
    # Create test vCards
    test_vcards = create_test_vcards()
    
    # Write test file
    test_input = 'test_soft_input.vcf'
    test_output = 'test_soft_output.vcf'
    
    with open(test_input, 'w') as f:
        for vcard in test_vcards:
            f.write(vcard.serialize())
    
    # Apply soft compliance
    checker = SoftComplianceChecker()
    
    # Show BEFORE state
    print("\n--- BEFORE SOFT COMPLIANCE ---\n")
    
    for i, vcard in enumerate(test_vcards):
        print(f"vCard {i + 1}:")
        print(f"  FN: {vcard.fn.value}")
        
        if hasattr(vcard, 'note'):
            print(f"  NOTE: {vcard.note.value}")
        
        if hasattr(vcard, 'tel_list'):
            for tel in vcard.tel_list:
                print(f"  TEL: {tel.value}")
        
        if hasattr(vcard, 'email_list'):
            for email in vcard.email_list:
                print(f"  EMAIL: {email.value}")
        
        if hasattr(vcard, 'org'):
            print(f"  ORG: {vcard.org.value}")
        
        print()
    
    # Apply fixes
    result = checker.check_and_fix_file(test_input, test_output, default_country='US')
    
    # Load fixed vCards
    with open(test_output, 'r') as f:
        fixed_vcards = list(vobject.readComponents(f.read()))
    
    # Show AFTER state
    print("\n--- AFTER SOFT COMPLIANCE ---\n")
    
    for i, vcard in enumerate(fixed_vcards):
        print(f"vCard {i + 1}:")
        print(f"  FN: {vcard.fn.value}")
        
        if hasattr(vcard, 'note'):
            print(f"  NOTE: {vcard.note.value}")
        
        if hasattr(vcard, 'tel_list'):
            for tel in vcard.tel_list:
                print(f"  TEL: {tel.value}")
        
        if hasattr(vcard, 'email_list'):
            for email in vcard.email_list:
                print(f"  EMAIL: {email.value}")
        
        if hasattr(vcard, 'org'):
            print(f"  ORG: {vcard.org.value}")
        
        print()
    
    # Show statistics
    print("\n--- FIXES APPLIED ---")
    for fix_type, count in result['fixes_applied'].items():
        if count > 0:
            print(f"  {fix_type}: {count}")
    
    # Clean up
    import os
    os.remove(test_input)
    os.remove(test_output)


if __name__ == "__main__":
    demonstrate_soft_compliance()