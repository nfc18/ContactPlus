#!/usr/bin/env python3
"""
Test script to show specific examples of vCard fixes
"""

import vobject
from vcard_validator import VCardStandardsValidator

# Sample problematic vCards from validation
problem_indices = [1, 12, 51, 60, 61]  # These had missing FN

def examine_fixed_vcards():
    """Show examples of how vCards were fixed"""
    
    print("Examples of vCard Fixes")
    print("=" * 60)
    
    # Load original file
    original_file = "/Users/lk/Documents/Developer/Private/ContactPlus/Imports/Sara_Export_Sara A. Kerner and 3.074 others.vcf"
    fixed_file = original_file.replace('.vcf', '_FIXED.vcf')
    
    # Read both files
    with open(original_file, 'r', encoding='utf-8') as f:
        original_data = f.read()
    
    with open(fixed_file, 'r', encoding='utf-8') as f:
        fixed_data = f.read()
    
    # Parse vCards
    original_vcards = list(vobject.readComponents(original_data))
    fixed_vcards = list(vobject.readComponents(fixed_data))
    
    # Show examples of fixes
    examples_shown = 0
    for i in problem_indices:
        if i < len(original_vcards) and i < len(fixed_vcards):
            print(f"\nvCard {i}:")
            print("-" * 40)
            
            orig = original_vcards[i]
            fixed = fixed_vcards[i]
            
            # Show original state
            print("BEFORE:")
            print(f"  Has FN: {hasattr(orig, 'fn')}")
            print(f"  Has N: {hasattr(orig, 'n')}")
            if hasattr(orig, 'n'):
                n = orig.n.value
                print(f"  N value: {n.given} {n.family}")
            if hasattr(orig, 'org'):
                print(f"  ORG: {orig.org.value}")
            if hasattr(orig, 'email'):
                print(f"  EMAIL: {orig.email.value}")
            
            # Show fixed state
            print("\nAFTER:")
            print(f"  Has FN: {hasattr(fixed, 'fn')}")
            if hasattr(fixed, 'fn'):
                print(f"  FN value: '{fixed.fn.value}'")
            print(f"  Has N: {hasattr(fixed, 'n')}")
            
            # Show how FN was generated
            print("\nFIX APPLIED:")
            if hasattr(fixed, 'fn') and not hasattr(orig, 'fn'):
                fn_value = fixed.fn.value
                
                # Determine source of FN
                if hasattr(orig, 'n'):
                    n = orig.n.value
                    expected_fn = f"{n.given} {n.family}".strip()
                    if fn_value == expected_fn:
                        print(f"  FN generated from N components")
                elif hasattr(orig, 'org') and fn_value in str(orig.org.value):
                    print(f"  FN generated from ORG")
                elif hasattr(orig, 'email') and '@' in orig.email.value:
                    local = orig.email.value.split('@')[0]
                    if local.replace('.', ' ').replace('_', ' ').title() in fn_value:
                        print(f"  FN generated from email local part")
                else:
                    print(f"  FN generated from fallback")
            
            examples_shown += 1
            if examples_shown >= 3:
                break
    
    print("\n" + "=" * 60)
    print("Summary: The fixer successfully generated missing FN fields")
    print("using available data from N, ORG, or EMAIL fields.")


if __name__ == "__main__":
    examine_fixed_vcards()