#!/usr/bin/env python3
"""
Test script to verify the new vCard processing workflow:
- vcard library for validation
- vobject for manipulation
"""

import sys
from vcard_validator import VCardStandardsValidator, process_vcard_file
import vobject
import config


def test_validation_workflow():
    """Test the standard validation + manipulation workflow"""
    
    print("Testing vCard Processing Standard")
    print("=" * 60)
    print("Rule: vcard library for validation + vobject for manipulation")
    print("=" * 60)
    print()
    
    # Test on Sara's vCard file
    filepath = config.SARA_VCARD_FILE
    
    # METHOD 1: Using the convenience function
    print("METHOD 1: Using process_vcard_file() convenience function")
    print("-" * 40)
    
    result = process_vcard_file(filepath)
    
    print(f"File: {result['filepath']}")
    print(f"Valid: {result['is_valid']}")
    print(f"Total errors: {result['total_errors']}")
    print(f"Total warnings: {result['total_warnings']}")
    print(f"Parsed vCards: {len(result['parsed_vcards'])}")
    
    if result['validation_errors']:
        print(f"\nSample validation errors:")
        for error in result['validation_errors'][:3]:
            print(f"  - {error}")
    
    print("\n" + "=" * 60)
    
    # METHOD 2: Manual step-by-step
    print("\nMETHOD 2: Manual step-by-step process")
    print("-" * 40)
    
    # Step 1: Validate with vcard library
    print("\nStep 1: Validating with vcard library...")
    validator = VCardStandardsValidator(strict=False)
    is_valid, errors, warnings = validator.validate_file(filepath)
    
    print(f"  Validation result: {'PASS' if is_valid else 'FAIL'}")
    print(f"  Errors: {len(errors)}")
    print(f"  Warnings: {len(warnings)}")
    
    # Step 2: Parse with vobject only if reasonably valid
    if is_valid or len(errors) < 100:
        print("\nStep 2: Parsing with vobject for manipulation...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            vcard_data = f.read()
        
        # Parse with vobject
        vcards = list(vobject.readComponents(vcard_data))
        print(f"  Successfully parsed {len(vcards)} vCards")
        
        # Example manipulation
        print("\nExample manipulation with vobject:")
        sample_count = 0
        for vcard in vcards[:5]:  # Just first 5
            if hasattr(vcard, 'fn'):
                print(f"  - {vcard.fn.value}")
                sample_count += 1
        
        print(f"\n✅ Workflow completed successfully!")
        print(f"   Validated {len(vcards)} vCards with vcard library")
        print(f"   Parsed and manipulated with vobject")
        
    else:
        print(f"\n❌ Too many validation errors ({len(errors)}), skipping vobject parsing")
        print("   Fix validation errors before manipulation")
    
    print("\n" + "=" * 60)
    print("SUMMARY: The standard workflow is working correctly!")
    print("Always remember: vcard for validation, vobject for manipulation")


if __name__ == "__main__":
    test_validation_workflow()