#!/usr/bin/env python3
"""Process vCards using proper parser for iCloud compatibility"""
import vobject
import json
import os
from PIL import Image
from io import BytesIO
import base64

class VCardProcessor:
    def __init__(self):
        self.stats = {
            'total': 0,
            'processed': 0,
            'missing_fn': 0,
            'oversized': 0,
            'photos_resized': 0,
            'errors': 0
        }
    
    def load_review_decisions(self):
        """Load the review decisions from the CLI review"""
        try:
            with open('data/review_decisions.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("No review decisions found - processing without modifications")
            return {}
    
    def ensure_fn_field(self, vcard):
        """Ensure vCard has FN field, create from available data if missing"""
        if not hasattr(vcard, 'fn'):
            # Try to build FN from N field
            if hasattr(vcard, 'n'):
                n_value = vcard.n.value
                name_parts = []
                if n_value.given:
                    name_parts.append(n_value.given)
                if n_value.additional:
                    name_parts.append(n_value.additional)
                if n_value.family:
                    name_parts.append(n_value.family)
                
                if name_parts:
                    vcard.add('fn')
                    vcard.fn.value = ' '.join(name_parts)
                    self.stats['missing_fn'] += 1
                    return
            
            # Try ORG
            if hasattr(vcard, 'org'):
                vcard.add('fn')
                vcard.fn.value = str(vcard.org.value[0]) if vcard.org.value else 'Organization'
                self.stats['missing_fn'] += 1
                return
            
            # Try EMAIL
            if hasattr(vcard, 'email'):
                vcard.add('fn')
                vcard.fn.value = vcard.email.value
                self.stats['missing_fn'] += 1
                return
            
            # Try TEL
            if hasattr(vcard, 'tel'):
                vcard.add('fn')
                vcard.fn.value = vcard.tel.value
                self.stats['missing_fn'] += 1
                return
            
            # Default
            vcard.add('fn')
            vcard.fn.value = 'Unknown Contact'
            self.stats['missing_fn'] += 1
    
    def resize_photo_if_needed(self, vcard):
        """Resize photo if vCard exceeds size limit"""
        try:
            # Check if vCard is oversized
            serialized = vcard.serialize()
            if len(serialized.encode('utf-8')) <= 256 * 1024:
                return  # Within limits
            
            # Check if has photo
            if not hasattr(vcard, 'photo'):
                return
            
            # Get photo data
            photo_data = vcard.photo.value
            if isinstance(photo_data, str):
                # It's base64 encoded
                photo_bytes = base64.b64decode(photo_data)
            else:
                photo_bytes = photo_data
            
            # Open image
            img = Image.open(BytesIO(photo_bytes))
            
            # Calculate target size (aim for 200KB photo max)
            quality = 85
            max_dimension = 800
            
            # Resize if too large
            if img.width > max_dimension or img.height > max_dimension:
                img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            
            # Save with compression
            output = BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            
            # Update vCard photo
            vcard.photo.value = output.getvalue()
            vcard.photo.encoding_param = 'b'
            vcard.photo.type_param = 'JPEG'
            
            self.stats['photos_resized'] += 1
            self.stats['oversized'] += 1
            
        except Exception as e:
            # If photo processing fails, remove it
            if hasattr(vcard, 'photo'):
                del vcard.photo
                self.stats['oversized'] += 1
    
    def apply_review_decision(self, vcard, decision):
        """Apply review decision to vCard"""
        action = decision.get('action')
        
        if action == 'primary_only':
            # Keep only first email
            if hasattr(vcard, 'email_list') and len(vcard.email_list) > 1:
                first_email = vcard.email_list[0]
                # Remove all emails
                while hasattr(vcard, 'email'):
                    vcard.remove(vcard.email)
                # Add back first email
                vcard.add('email')
                vcard.email.value = first_email.value
                vcard.email.type_param = first_email.type_param if hasattr(first_email, 'type_param') else 'INTERNET'
        
        elif action == 'select_emails':
            # Keep only selected emails
            emails_to_keep = decision.get('emails_to_keep', [])
            if hasattr(vcard, 'email_list'):
                all_emails = [(e.value, e) for e in vcard.email_list]
                # Remove all emails
                while hasattr(vcard, 'email'):
                    vcard.remove(vcard.email)
                # Add back selected emails
                for email_value, email_obj in all_emails:
                    if email_value in emails_to_keep:
                        vcard.add('email')
                        vcard.email.value = email_value
                        if hasattr(email_obj, 'type_param'):
                            vcard.email.type_param = email_obj.type_param
    
    def process_file(self, input_path, output_path):
        """Process vCard file with proper parser"""
        print(f"Processing {input_path} with vCard parser...")
        
        # Load review decisions
        decisions = self.load_review_decisions()
        
        # Read the file
        with open(input_path, 'r', encoding='utf-8') as f:
            vcard_data = f.read()
        
        # Parse all vCards
        output_vcards = []
        
        for vcard in vobject.readComponents(vcard_data):
            self.stats['total'] += 1
            
            try:
                # Ensure FN field exists
                self.ensure_fn_field(vcard)
                
                # Apply review decisions if any
                if hasattr(vcard, 'email') and vcard.email.value in decisions:
                    self.apply_review_decision(vcard, decisions[vcard.email.value])
                
                # Check and resize photo if needed
                self.resize_photo_if_needed(vcard)
                
                # Add to output
                output_vcards.append(vcard)
                self.stats['processed'] += 1
                
            except Exception as e:
                print(f"Error processing vCard: {e}")
                self.stats['errors'] += 1
                # Still include the vCard even if there was an error
                output_vcards.append(vcard)
        
        # Write output file
        with open(output_path, 'w', encoding='utf-8') as f:
            for vcard in output_vcards:
                f.write(vcard.serialize())
                f.write('\n')  # Add newline between vCards
        
        # Print statistics
        print("\nProcessing complete!")
        print(f"Total vCards: {self.stats['total']}")
        print(f"Successfully processed: {self.stats['processed']}")
        print(f"Missing FN fixed: {self.stats['missing_fn']}")
        print(f"Oversized vCards fixed: {self.stats['oversized']}")
        print(f"Photos resized: {self.stats['photos_resized']}")
        print(f"Errors: {self.stats['errors']}")
        
        # Verify output
        self.verify_output(output_path)
    
    def verify_output(self, output_path):
        """Verify the output file meets requirements"""
        print("\nVerifying output file...")
        
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = {
            'missing_fn': 0,
            'oversized': 0,
            'total': 0
        }
        
        for vcard in vobject.readComponents(content):
            issues['total'] += 1
            
            # Check FN
            if not hasattr(vcard, 'fn'):
                issues['missing_fn'] += 1
            
            # Check size
            serialized = vcard.serialize()
            if len(serialized.encode('utf-8')) > 256 * 1024:
                issues['oversized'] += 1
        
        print(f"\nVerification Results:")
        print(f"Total vCards: {issues['total']}")
        print(f"Missing FN: {issues['missing_fn']}")
        print(f"Oversized: {issues['oversized']}")
        
        if issues['missing_fn'] == 0 and issues['oversized'] == 0:
            print("\n✅ File is ready for iCloud import!")
        else:
            print("\n⚠️  File has issues that need to be fixed")

def main():
    processor = VCardProcessor()
    
    # Use the backup file as source
    input_file = "backup/Sara_Export_BACKUP_2025-06-05_22-40-40.vcf"
    output_file = "data/Sara_Export_iCloud_Ready.vcf"
    
    processor.process_file(input_file, output_file)
    
    print(f"\n✅ Output saved to: {output_file}")

if __name__ == "__main__":
    main()