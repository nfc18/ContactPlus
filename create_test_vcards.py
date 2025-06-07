#!/usr/bin/env python3
"""Create test vCards to identify iCloud.com requirements"""
import vobject

def create_minimal_test():
    """Create absolutely minimal test vCards"""
    
    # Test 1: Absolute minimum vCard
    test1 = vobject.vCard()
    test1.add('version')
    test1.version.value = '3.0'
    test1.add('fn')
    test1.fn.value = 'Test Contact One'
    test1.add('n')
    test1.n.value = vobject.vcard.Name(family='One', given='Test Contact')
    
    with open('data/test1_minimal.vcf', 'w') as f:
        f.write(test1.serialize())
    print("Created test1_minimal.vcf - Absolute minimum vCard")
    
    # Test 2: With email
    test2 = vobject.vCard()
    test2.add('version')
    test2.version.value = '3.0'
    test2.add('fn')
    test2.fn.value = 'Test Contact Two'
    test2.add('n')
    test2.n.value = vobject.vcard.Name(family='Two', given='Test Contact')
    test2.add('email')
    test2.email.value = 'test2@example.com'
    test2.email.type_param = 'INTERNET'
    
    with open('data/test2_with_email.vcf', 'w') as f:
        f.write(test2.serialize())
    print("Created test2_with_email.vcf - With email")
    
    # Test 3: Multiple contacts in one file
    with open('data/test3_multiple.vcf', 'w') as f:
        for i in range(3):
            test = vobject.vCard()
            test.add('version')
            test.version.value = '3.0'
            test.add('fn')
            test.fn.value = f'Test Contact {i+1}'
            test.add('n')
            test.n.value = vobject.vcard.Name(family=f'Contact{i+1}', given='Test')
            f.write(test.serialize())
            f.write('\n')
    print("Created test3_multiple.vcf - Three contacts")
    
    # Test 4: Extract first 5 contacts from Sara's file with minimal fields
    print("\nExtracting first 5 contacts from Sara's database...")
    with open('data/Sara_Export_iCloud_Web.vcf', 'r') as f:
        content = f.read()
    
    output_vcards = []
    for i, vcard in enumerate(vobject.readComponents(content)):
        if i >= 5:
            break
        
        # Create minimal version
        minimal = vobject.vCard()
        minimal.add('version')
        minimal.version.value = '3.0'
        
        # Copy only FN and N
        if hasattr(vcard, 'fn'):
            minimal.add('fn')
            minimal.fn.value = vcard.fn.value
        else:
            minimal.add('fn')
            minimal.fn.value = f'Contact {i+1}'
        
        if hasattr(vcard, 'n'):
            minimal.add('n')
            minimal.n.value = vcard.n.value
        else:
            minimal.add('n')
            minimal.n.value = vobject.vcard.Name(family='Unknown', given='Contact')
        
        output_vcards.append(minimal)
    
    with open('data/test4_sara_minimal.vcf', 'w') as f:
        for vcard in output_vcards:
            f.write(vcard.serialize())
            f.write('\n')
    print("Created test4_sara_minimal.vcf - First 5 contacts from Sara (minimal)")
    
    print("\n" + "="*80)
    print("Test files created. Try importing these to iCloud.com:")
    print("1. test1_minimal.vcf - If this fails, it's a basic format issue")
    print("2. test2_with_email.vcf - If this fails, it's an email field issue")
    print("3. test3_multiple.vcf - If this fails, it's a multi-contact issue")
    print("4. test4_sara_minimal.vcf - If this fails, it's specific to Sara's data")
    print("\nThis will help us identify exactly what iCloud.com is rejecting.")

def check_raw_format():
    """Check the raw format of our generated files"""
    print("\n" + "="*80)
    print("Raw format of test1_minimal.vcf:")
    print("-"*40)
    with open('data/test1_minimal.vcf', 'r') as f:
        content = f.read()
        print(content)
        print(f"\nHex of first 100 chars: {content[:100].encode('utf-8').hex()}")

if __name__ == "__main__":
    create_minimal_test()
    check_raw_format()