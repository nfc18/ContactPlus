#!/usr/bin/env python3
"""
Auto-validation wrapper for phonebook operations
"""

from vcard_validator import VCardStandardsValidator
import os

def validate_phonebook(filepath, operation_name="operation"):
    """Validate phonebook and report results"""
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    validator = VCardStandardsValidator()
    is_valid, errors, warnings = validator.validate_file(filepath)
    
    print(f"\n📋 Validation after {operation_name}:")
    print(f"   File: {os.path.basename(filepath)}")
    print(f"   Valid: {'✅ YES' if is_valid else '❌ NO'}")
    print(f"   Errors: {len(errors)}")
    print(f"   Warnings: {len(warnings)} (mostly Apple properties)")
    
    if errors:
        print("\n❌ ERRORS found:")
        for i, error in enumerate(errors[:5]):
            print(f"   {i+1}. {error}")
        if len(errors) > 5:
            print(f"   ... and {len(errors)-5} more errors")
        return False
    
    if warnings and len(warnings) > 250:  # Only warn if too many warnings
        print(f"\n⚠️  Unusual number of warnings: {len(warnings)}")
    
    return True

def validate_current_master():
    """Validate the current master phonebook"""
    # Find latest master
    import glob
    masters = glob.glob("data/MASTER_PHONEBOOK_*.vcf")
    if masters:
        latest = sorted(masters)[-1]
        return validate_phonebook(latest, "current master")
    else:
        print("❌ No master phonebook found")
        return False

if __name__ == "__main__":
    validate_current_master()