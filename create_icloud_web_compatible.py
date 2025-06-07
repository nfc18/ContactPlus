#!/usr/bin/env python3
"""Create iCloud.com web-compatible vCard file using parser"""
import vobject
from PIL import Image
from io import BytesIO
import base64

class ICloudWebProcessor:
    def __init__(self):
        self.stats = {
            'total': 0,
            'processed': 0,
            'item_prefixes_removed': 0,
            'x_fields_removed': 0,
            'empty_n_fixed': 0,
            'photos_resized': 0
        }
    
    def fix_empty_n_field(self, vcard):
        """Fix empty N fields by deriving from FN"""
        if hasattr(vcard, 'n'):
            n_value = vcard.n.value
            # Check if N field is essentially empty
            if not any([n_value.family, n_value.given, n_value.additional]):
                if hasattr(vcard, 'fn'):
                    # Parse FN to create proper N field
                    fn_parts = vcard.fn.value.strip().split()
                    if len(fn_parts) >= 2:
                        # Assume last part is family name
                        n_value.family = fn_parts[-1]
                        n_value.given = ' '.join(fn_parts[:-1])
                    elif len(fn_parts) == 1:
                        # Single word - use as given name
                        n_value.given = fn_parts[0]
                    self.stats['empty_n_fixed'] += 1
    
    def process_vcard_for_icloud_web(self, vcard):
        """Process a single vCard for iCloud.com compatibility"""
        # Create a new clean vCard
        new_vcard = vobject.vCard()
        
        # Add VERSION first (required)
        new_vcard.add('version')
        new_vcard.version.value = '3.0'
        
        # Add PRODID
        new_vcard.add('prodid')
        new_vcard.prodid.value = '-//Apple Inc.//macOS 15.5//EN'
        
        # Copy essential fields without item prefixes
        fields_to_copy = ['fn', 'n', 'org', 'title', 'tel', 'email', 'adr', 'note', 'bday', 'photo']
        
        for field_name in fields_to_copy:
            # Get all instances of this field
            for child in vcard.getChildren():
                if child.name.lower() == field_name:
                    # Skip if it has an item prefix
                    if hasattr(child, 'group') and child.group:
                        self.stats['item_prefixes_removed'] += 1
                        # Still copy the field, just without the group
                        new_child = new_vcard.add(field_name)
                        new_child.value = child.value
                        # Copy parameters except group
                        for param in child.params:
                            if param != 'GROUP':
                                setattr(new_child, param.lower() + '_param', 
                                       getattr(child, param.lower() + '_param'))
                    else:
                        # Direct copy
                        new_child = new_vcard.add(field_name)
                        new_child.value = child.value
                        # Copy all parameters
                        for param in child.params:
                            setattr(new_child, param.lower() + '_param', 
                                   getattr(child, param.lower() + '_param'))
        
        # URL fields need special handling (often have item prefixes)
        url_count = 0
        for child in vcard.getChildren():
            if child.name == 'URL':
                if url_count < 3:  # Limit URLs to avoid complexity
                    new_url = new_vcard.add('url')
                    new_url.value = child.value
                    if hasattr(child, 'type_param'):
                        new_url.type_param = child.type_param
                    url_count += 1
                    if hasattr(child, 'group') and child.group:
                        self.stats['item_prefixes_removed'] += 1
        
        # Skip all X- fields for iCloud.com compatibility
        x_field_count = 0
        for child in vcard.getChildren():
            if child.name.startswith('X-'):
                x_field_count += 1
        if x_field_count > 0:
            self.stats['x_fields_removed'] += x_field_count
        
        # Fix empty N field
        self.fix_empty_n_field(new_vcard)
        
        # Check photo size
        if hasattr(new_vcard, 'photo'):
            serialized = new_vcard.serialize()
            if len(serialized.encode('utf-8')) > 256 * 1024:
                self.resize_photo(new_vcard)
        
        return new_vcard
    
    def resize_photo(self, vcard):
        """Resize photo to fit within limits"""
        try:
            photo_data = vcard.photo.value
            if isinstance(photo_data, str):
                photo_bytes = base64.b64decode(photo_data)
            else:
                photo_bytes = photo_data
            
            img = Image.open(BytesIO(photo_bytes))
            
            # More aggressive resizing for iCloud.com
            max_dimension = 600
            quality = 75
            
            img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            
            output = BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            
            vcard.photo.value = output.getvalue()
            vcard.photo.encoding_param = 'b'
            vcard.photo.type_param = 'JPEG'
            
            self.stats['photos_resized'] += 1
        except:
            # If photo processing fails, remove it
            del vcard.photo
    
    def process_file(self, input_path, output_path):
        """Process entire vCard file for iCloud.com web compatibility"""
        print("Creating iCloud.com web-compatible vCard file...")
        print("=" * 80)
        
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        output_vcards = []
        
        for vcard in vobject.readComponents(content):
            self.stats['total'] += 1
            
            try:
                # Process for iCloud.com compatibility
                new_vcard = self.process_vcard_for_icloud_web(vcard)
                output_vcards.append(new_vcard)
                self.stats['processed'] += 1
                
                if self.stats['processed'] % 100 == 0:
                    print(f"Processed {self.stats['processed']} contacts...")
                
            except Exception as e:
                print(f"Error processing vCard: {e}")
                # Skip problematic vCards for now
        
        # Write output
        print(f"\nWriting {len(output_vcards)} contacts to output file...")
        with open(output_path, 'w', encoding='utf-8') as f:
            for vcard in output_vcards:
                f.write(vcard.serialize())
                f.write('\n')
        
        # Print summary
        print("\n" + "=" * 80)
        print("Processing Summary:")
        print(f"Total vCards: {self.stats['total']}")
        print(f"Successfully processed: {self.stats['processed']}")
        print(f"Item prefixes removed: {self.stats['item_prefixes_removed']}")
        print(f"X- fields removed: {self.stats['x_fields_removed']}")
        print(f"Empty N fields fixed: {self.stats['empty_n_fixed']}")
        print(f"Photos resized: {self.stats['photos_resized']}")
        
        # Quick validation
        self.validate_output(output_path)
    
    def validate_output(self, output_path):
        """Quick validation of output file"""
        print("\nValidating output file...")
        
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        vcard_count = 0
        has_item_prefix = False
        has_x_fields = False
        
        for line in content.split('\n'):
            if line.startswith('BEGIN:VCARD'):
                vcard_count += 1
            elif line.startswith('item'):
                has_item_prefix = True
            elif line.startswith('X-'):
                has_x_fields = True
        
        print(f"Output has {vcard_count} vCards")
        print(f"Has item prefixes: {has_item_prefix}")
        print(f"Has X- fields: {has_x_fields}")
        
        if not has_item_prefix and not has_x_fields:
            print("\n✅ File should be compatible with iCloud.com web import!")
        else:
            print("\n⚠️  File may still have compatibility issues")

def main():
    processor = ICloudWebProcessor()
    
    input_file = "data/Sara_Export_iCloud_Ready.vcf"
    output_file = "data/Sara_Export_iCloud_Web.vcf"
    
    processor.process_file(input_file, output_file)
    
    print(f"\n✅ iCloud.com compatible file saved to: {output_file}")
    print("\nTry importing this file at iCloud.com")

if __name__ == "__main__":
    main()