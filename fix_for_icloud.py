#!/usr/bin/env python3
"""Create a fully iCloud-compatible vCard file"""
import re

def fix_for_icloud():
    """Fix all issues for iCloud import"""
    print("Creating iCloud-compatible vCard file...\n")
    
    with open("data/Sara_Export_ICLOUD_FINAL.vcf", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Process each vCard
    fixed_vcards = []
    current_vcard = []
    in_vcard = False
    
    for line in content.split('\n'):
        if line.strip() == 'BEGIN:VCARD':
            in_vcard = True
            current_vcard = [line]
        elif line.strip() == 'END:VCARD':
            current_vcard.append(line)
            
            # Fix vCard if needed
            vcard_text = '\n'.join(current_vcard)
            
            # Check if FN exists
            if 'FN:' not in vcard_text:
                # Try to create FN from N field
                n_match = re.search(r'N:([^;]*);([^;]*);([^;]*);([^;]*);([^;]*)', vcard_text)
                if n_match:
                    last = n_match.group(1).strip()
                    first = n_match.group(2).strip()
                    middle = n_match.group(3).strip()
                    
                    # Build formatted name
                    fn_parts = []
                    if first:
                        fn_parts.append(first)
                    if middle:
                        fn_parts.append(middle)
                    if last:
                        fn_parts.append(last)
                    
                    if fn_parts:
                        fn = ' '.join(fn_parts)
                    else:
                        # Use organization or email as fallback
                        org_match = re.search(r'ORG:([^;]+)', vcard_text)
                        email_match = re.search(r'EMAIL[^:]*:([^\r\n]+)', vcard_text)
                        
                        if org_match:
                            fn = org_match.group(1).strip()
                        elif email_match:
                            fn = email_match.group(1).strip()
                        else:
                            fn = "Unknown Contact"
                    
                    # Insert FN after N field
                    fixed_lines = []
                    for vline in current_vcard:
                        fixed_lines.append(vline)
                        if vline.startswith('N:'):
                            fixed_lines.append(f'FN:{fn}')
                    
                    fixed_vcards.append('\n'.join(fixed_lines))
                else:
                    # No N field either - create minimal contact
                    fixed_lines = ['BEGIN:VCARD', 'VERSION:3.0']
                    
                    # Try to find any identifying info
                    email_match = re.search(r'EMAIL[^:]*:([^\r\n]+)', vcard_text)
                    tel_match = re.search(r'TEL[^:]*:([^\r\n]+)', vcard_text)
                    
                    if email_match:
                        email = email_match.group(1).strip()
                        fixed_lines.append(f'N:{email};;;;')
                        fixed_lines.append(f'FN:{email}')
                    elif tel_match:
                        tel = tel_match.group(1).strip()
                        fixed_lines.append(f'N:{tel};;;;')
                        fixed_lines.append(f'FN:{tel}')
                    else:
                        fixed_lines.append('N:Unknown;;;;')
                        fixed_lines.append('FN:Unknown Contact')
                    
                    # Add other fields from original
                    for vline in current_vcard[2:-1]:  # Skip BEGIN, VERSION, END
                        if not vline.startswith('N:') and not vline.startswith('FN:'):
                            fixed_lines.append(vline)
                    
                    fixed_lines.append('END:VCARD')
                    fixed_vcards.append('\n'.join(fixed_lines))
            else:
                # vCard is OK
                fixed_vcards.append(vcard_text)
            
            current_vcard = []
            in_vcard = False
        elif in_vcard:
            current_vcard.append(line)
    
    # Write final file
    output_file = "data/Sara_Export_READY_FOR_ICLOUD.vcf"
    with open(output_file, 'w', encoding='utf-8') as f:
        # Join with double newline for better compatibility
        f.write('\n\n'.join(fixed_vcards))
    
    print(f"✅ Created: {output_file}")
    
    # Verify
    with open(output_file, 'r', encoding='utf-8') as f:
        verify_content = f.read()
    
    vcards = re.findall(r'BEGIN:VCARD.*?END:VCARD', verify_content, re.DOTALL)
    missing_fn = sum(1 for v in vcards if 'FN:' not in v)
    oversized = sum(1 for v in vcards if len(v.encode('utf-8')) > 256 * 1024)
    
    print(f"\nVerification:")
    print(f"  Total vCards: {len(vcards)}")
    print(f"  Missing FN: {missing_fn}")
    print(f"  Oversized: {oversized}")
    
    if missing_fn == 0 and oversized == 0:
        print("\n🎉 File is fully iCloud compatible!")

if __name__ == "__main__":
    fix_for_icloud()