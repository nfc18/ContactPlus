#!/usr/bin/env python3
"""Create a web-compatible vCard file for iCloud.com import"""

import vobject
import config

def create_web_compatible_vcf():
    """Create a simplified vCard file that works with iCloud.com"""
    
    print("Creating web-compatible vCard file...")
    
    # Read the cleaned file
    with open(config.PROCESSED_VCARD_FILE, 'r', encoding='utf-8') as f:
        vcard_data = f.read()
    
    output_vcards = []
    count = 0
    errors = 0
    
    for vcard in vobject.readComponents(vcard_data):
        try:
            # Create a new minimal vCard
            new_vcard = vobject.vCard()
            
            # Add essential fields only
            # FN is required
            if hasattr(vcard, 'fn'):
                new_vcard.add('fn')
                new_vcard.fn.value = vcard.fn.value
            else:
                continue  # Skip if no FN
            
            # N is required
            if hasattr(vcard, 'n'):
                new_vcard.add('n')
                new_vcard.n.value = vcard.n.value
            else:
                # Create N from FN
                new_vcard.add('n')
                parts = vcard.fn.value.split(' ', 1)
                if len(parts) == 2:
                    new_vcard.n.value = vobject.vcard.Name(family=parts[1], given=parts[0])
                else:
                    new_vcard.n.value = vobject.vcard.Name(family=vcard.fn.value, given='')
            
            # Add emails
            if hasattr(vcard, 'email_list'):
                for email in vcard.email_list:
                    new_email = new_vcard.add('email')
                    new_email.value = email.value
                    new_email.type_param = 'INTERNET'
            
            # Add phone numbers
            if hasattr(vcard, 'tel_list'):
                for tel in vcard.tel_list:
                    new_tel = new_vcard.add('tel')
                    new_tel.value = tel.value
                    if hasattr(tel, 'type_param'):
                        new_tel.type_param = tel.type_param
            
            # Add organization
            if hasattr(vcard, 'org'):
                new_vcard.add('org')
                new_vcard.org.value = vcard.org.value
            
            # Add title
            if hasattr(vcard, 'title'):
                new_vcard.add('title')
                new_vcard.title.value = vcard.title.value
            
            output_vcards.append(new_vcard)
            count += 1
            
        except Exception as e:
            errors += 1
            print(f"Error processing contact: {e}")
    
    # Write single file
    output_file = config.PROCESSED_VCARD_FILE.replace('.vcf', '_web.vcf')
    with open(output_file, 'w', encoding='utf-8') as f:
        for vcard in output_vcards:
            f.write(vcard.serialize())
    
    print(f"\nCreated web-compatible file: {output_file}")
    print(f"Contacts: {count}")
    print(f"Errors: {errors}")
    
    # Also create smaller chunks for easier import
    chunk_size = 500
    total_chunks = (count + chunk_size - 1) // chunk_size
    
    print(f"\nCreating {total_chunks} smaller files for easier import...")
    
    for i in range(total_chunks):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, len(output_vcards))
        
        chunk_file = config.PROCESSED_VCARD_FILE.replace('.vcf', f'_web_chunk{i+1}.vcf')
        with open(chunk_file, 'w', encoding='utf-8') as f:
            for vcard in output_vcards[start:end]:
                f.write(vcard.serialize())
        
        print(f"Created: {chunk_file} ({end - start} contacts)")

if __name__ == "__main__":
    create_web_compatible_vcf()