#!/usr/bin/env python3
"""Diagnose why iCloud.com import fails while Contacts app succeeds"""
import vobject
import re

def diagnose_icloud_issues():
    """Check for potential iCloud.com specific issues"""
    print("Diagnosing potential iCloud.com import issues...")
    print("=" * 80)
    
    with open("data/Sara_Export_iCloud_Ready.vcf", 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = {
        'special_chars': [],
        'long_fields': [],
        'multiple_types': [],
        'x_fields': [],
        'item_prefixes': [],
        'encoding_params': [],
        'line_lengths': [],
        'empty_n_fields': []
    }
    
    # Parse with vobject
    vcards = list(vobject.readComponents(content))
    print(f"\nTotal vCards: {len(vcards)}")
    
    for i, vcard in enumerate(vcards):
        # Check for special characters in FN
        if hasattr(vcard, 'fn'):
            fn_value = vcard.fn.value
            if any(ord(c) > 127 for c in fn_value):
                issues['special_chars'].append((i, fn_value))
            if len(fn_value) > 100:
                issues['long_fields'].append((i, f"FN: {len(fn_value)} chars"))
        
        # Check N field structure
        if hasattr(vcard, 'n'):
            n_value = vcard.n.value
            if not any([n_value.family, n_value.given]):
                issues['empty_n_fields'].append((i, str(n_value)))
        
        # Check for X- fields
        for child in vcard.getChildren():
            if child.name.startswith('X-'):
                issues['x_fields'].append((i, child.name))
            
            # Check for item prefixes (like item1.EMAIL)
            if hasattr(child, 'group') and child.group:
                issues['item_prefixes'].append((i, f"{child.group}.{child.name}"))
            
            # Check encoding parameters
            if hasattr(child, 'encoding_param'):
                issues['encoding_params'].append((i, f"{child.name}: {child.encoding_param}"))
    
    # Check raw content for line length issues
    for i, line in enumerate(content.split('\n')):
        if len(line) > 75 and not line.startswith(' '):  # vCard line folding
            if not any(line.startswith(x) for x in ['PHOTO:', 'NOTE:', 'KEY:']):
                issues['line_lengths'].append((i, f"Line {i}: {len(line)} chars"))
    
    # Print findings
    print("\nPotential iCloud.com compatibility issues found:")
    print("-" * 80)
    
    if issues['special_chars']:
        print(f"\n1. Special/Unicode characters in FN fields: {len(issues['special_chars'])}")
        for idx, fn in issues['special_chars'][:5]:
            print(f"   vCard #{idx}: {fn}")
    
    if issues['empty_n_fields']:
        print(f"\n2. Empty or minimal N fields: {len(issues['empty_n_fields'])}")
        for idx, n in issues['empty_n_fields'][:5]:
            print(f"   vCard #{idx}: {n}")
    
    if issues['item_prefixes']:
        print(f"\n3. Item prefixes (item1., item2., etc): {len(set(issues['item_prefixes']))}")
        unique_prefixes = list(set([x[1] for x in issues['item_prefixes']]))[:10]
        for prefix in unique_prefixes:
            print(f"   {prefix}")
    
    if issues['x_fields']:
        print(f"\n4. X- extension fields: {len(set(issues['x_fields']))}")
        unique_x = list(set([x[1] for x in issues['x_fields']]))[:10]
        for x_field in unique_x:
            print(f"   {x_field}")
    
    if issues['long_fields']:
        print(f"\n5. Very long field values: {len(issues['long_fields'])}")
        for idx, field in issues['long_fields'][:5]:
            print(f"   vCard #{idx}: {field}")
    
    # Check VERSION distribution
    versions = {}
    for vcard in vcards:
        if hasattr(vcard, 'version'):
            v = vcard.version.value
            versions[v] = versions.get(v, 0) + 1
    
    print(f"\n6. VERSION distribution:")
    for v, count in versions.items():
        print(f"   VERSION:{v} - {count} vCards")
    
    # Suggestions
    print("\n" + "=" * 80)
    print("Suggestions for iCloud.com compatibility:")
    print("1. Remove item prefixes (item1.EMAIL → EMAIL)")
    print("2. Remove X- extension fields that iCloud might not understand")
    print("3. Ensure N fields have at least family or given name")
    print("4. Consider normalizing special characters in names")
    print("5. Keep all fields simple and standard")

if __name__ == "__main__":
    diagnose_icloud_issues()