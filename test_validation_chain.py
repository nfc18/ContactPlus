#!/usr/bin/env python3
"""
Test the complete validation chain:
1. Initial validation
2. Hard compliance fixes
3. Re-validation
4. Soft compliance fixes
5. Final validation
"""

import vobject
from vcard_workflow import VCardWorkflow
import tempfile
import os


def create_test_vcards_with_issues():
    """Create test vCards with various compliance issues"""
    
    # Create as text to include violations
    vcards_text = []
    
    # vCard 1: Missing FN, phone in notes
    vcard1 = """BEGIN:VCARD
VERSION:3.0
N:SMITH;JOHN;;;
NOTE:Call me at 555-1234 or email john@example.com
END:VCARD"""
    
    # vCard 2: Has FN but bad capitalization and email format
    vcard2 = """BEGIN:VCARD
VERSION:3.0
FN:jane doe
N:doe;jane;;;
EMAIL:JANE@EXAMPLE.COM
TEL:(415) 555-1234
END:VCARD"""
    
    # vCard 3: Complex case - empty FN
    vcard3 = """BEGIN:VCARD
VERSION:3.0
FN:
EMAIL:test@example.com
EMAIL:TEST@EXAMPLE.COM
ORG:acme corp
END:VCARD"""
    
    return [vcard1, vcard2, vcard3]


def test_validation_chain():
    """Test that validation works at each stage"""
    
    print("Testing Complete Validation Chain")
    print("=" * 60)
    
    # Create test file
    test_vcards = create_test_vcards_with_issues()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.vcf', delete=False) as f:
        test_file = f.name
        for vcard_text in test_vcards:
            f.write(vcard_text + '\n')
    
    try:
        # Run complete workflow
        workflow = VCardWorkflow(
            auto_fix=True,
            backup=False,  # Skip backup for test
            soft_compliance=True
        )
        
        result = workflow.process_file(test_file)
        
        # Display validation results at each stage
        print("\n1. INITIAL VALIDATION:")
        print(f"   Valid: {result['initial_validation']['valid']}")
        print(f"   Errors: {result['initial_validation']['error_count']}")
        if result['initial_validation']['sample_errors']:
            print("   Sample errors:")
            for err in result['initial_validation']['sample_errors']:
                print(f"     - {err}")
        
        if 'post_fix_validation' in result:
            print("\n2. POST-HARD-FIX VALIDATION:")
            print(f"   Valid: {result['post_fix_validation']['valid']}")
            print(f"   Errors: {result['post_fix_validation']['error_count']}")
            if result['post_fix_validation'].get('remaining_errors'):
                print("   Remaining errors:")
                for err in result['post_fix_validation']['remaining_errors']:
                    print(f"     - {err}")
        
        if 'soft_compliance_report' in result:
            print("\n3. SOFT COMPLIANCE APPLIED:")
            soft_report = result['soft_compliance_report']
            print(f"   Issues found: {soft_report['issues_found']}")
            print("   Fixes applied:")
            for fix, count in soft_report['fixes_applied'].items():
                if count > 0:
                    print(f"     - {fix}: {count}")
        
        if 'post_soft_validation' in result:
            print("\n4. FINAL VALIDATION (POST-SOFT):")
            print(f"   Valid: {result['post_soft_validation']['valid']}")
            print(f"   Errors: {result['post_soft_validation']['error_count']}")
            if result['post_soft_validation'].get('sample_errors'):
                print("   Any new errors:")
                for err in result['post_soft_validation']['sample_errors']:
                    print(f"     - {err}")
        
        print(f"\n5. FINAL RESULT:")
        print(f"   All vCards valid: {result['final_valid']}")
        print(f"   vCards parsed: {result['vcards_parsed']}")
        
        # Verify soft compliance didn't break hard compliance
        if result.get('post_soft_validation'):
            initial_errors = result['initial_validation']['error_count']
            post_hard_errors = result.get('post_fix_validation', {}).get('error_count', 0)
            post_soft_errors = result['post_soft_validation']['error_count']
            
            print(f"\n6. VALIDATION SUMMARY:")
            print(f"   Errors: {initial_errors} → {post_hard_errors} → {post_soft_errors}")
            
            if post_soft_errors > post_hard_errors:
                print("   ⚠️  WARNING: Soft compliance introduced new errors!")
            else:
                print("   ✅ Soft compliance maintained RFC compliance!")
        
        # Load and check final vCards
        if result.get('working_file') and os.path.exists(result['working_file']):
            print(f"\n7. FINAL VCARD INSPECTION:")
            with open(result['working_file'], 'r') as f:
                final_vcards = list(vobject.readComponents(f.read()))
            
            for i, vcard in enumerate(final_vcards[:3]):
                print(f"\n   vCard {i+1}:")
                if hasattr(vcard, 'fn'):
                    print(f"     FN: {vcard.fn.value}")
                if hasattr(vcard, 'n'):
                    n = vcard.n.value
                    print(f"     N: {n.given} {n.family}")
                if hasattr(vcard, 'email_list'):
                    for email in vcard.email_list:
                        print(f"     EMAIL: {email.value}")
                if hasattr(vcard, 'note'):
                    print(f"     NOTE: {vcard.note.value[:50]}...")
        
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
        # Clean up any generated files
        for ext in ['_FIXED.vcf', '_FIXED_SOFT.vcf']:
            fixed_file = test_file.replace('.vcf', ext)
            if os.path.exists(fixed_file):
                os.remove(fixed_file)


if __name__ == "__main__":
    test_validation_chain()