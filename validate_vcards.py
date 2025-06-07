#!/usr/bin/env python3
"""
vCard Standards Validation Script
Validates vCard files against RFC 2426 (vCard 3.0) standards
"""

import os
import sys
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
import vobject
import config

class VCardValidator:
    """Validate vCard files for RFC 2426 compliance"""
    
    def __init__(self, strict=True):
        self.strict = strict
        self.errors = []
        self.warnings = []
        self.stats = defaultdict(int)
        
    def validate_file(self, filepath):
        """Validate an entire vCard file"""
        print(f"\n{'='*60}")
        print(f"Validating: {os.path.basename(filepath)}")
        print(f"File size: {os.path.getsize(filepath) / 1024 / 1024:.2f} MB")
        print(f"{'='*60}\n")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into individual vCards
        vcards = self._split_vcards(content)
        print(f"Found {len(vcards)} vCard entries\n")
        
        # Validate each vCard
        valid_count = 0
        for i, vcard_text in enumerate(vcards):
            if i % 100 == 0 and i > 0:
                print(f"Progress: {i}/{len(vcards)} validated...")
            
            is_valid = self._validate_single_vcard(vcard_text, i)
            if is_valid:
                valid_count += 1
        
        # Print summary
        self._print_summary(len(vcards), valid_count)
        
        return {
            'total_vcards': len(vcards),
            'valid_vcards': valid_count,
            'errors': self.errors[:100],  # Limit to first 100 errors
            'warnings': self.warnings[:100],
            'stats': dict(self.stats)
        }
    
    def _split_vcards(self, content):
        """Split file content into individual vCard blocks"""
        vcards = []
        current_vcard = []
        in_vcard = False
        
        for line in content.split('\n'):
            line = line.rstrip('\r\n')
            
            if line == 'BEGIN:VCARD':
                in_vcard = True
                current_vcard = [line]
            elif line == 'END:VCARD' and in_vcard:
                current_vcard.append(line)
                vcards.append('\n'.join(current_vcard))
                current_vcard = []
                in_vcard = False
            elif in_vcard:
                current_vcard.append(line)
        
        return vcards
    
    def _validate_single_vcard(self, vcard_text, index):
        """Validate a single vCard entry"""
        errors = []
        warnings = []
        
        # 1. Check BEGIN/END structure
        if not vcard_text.startswith('BEGIN:VCARD'):
            errors.append(f"vCard {index}: Missing BEGIN:VCARD")
        if not vcard_text.endswith('END:VCARD'):
            errors.append(f"vCard {index}: Missing END:VCARD")
        
        lines = vcard_text.split('\n')
        properties = {}
        
        # Parse properties
        for line in lines[1:-1]:  # Skip BEGIN and END
            if ':' in line:
                prop = line.split(':', 1)[0].split(';')[0].upper()
                properties[prop] = properties.get(prop, 0) + 1
                
                # Check for common issues
                if line.startswith(' ') or line.startswith('\t'):
                    self.stats['folded_lines'] += 1
                
                # Check encoding
                if 'ENCODING=QUOTED-PRINTABLE' in line.upper():
                    self.stats['quoted_printable'] += 1
                elif 'ENCODING=BASE64' in line.upper():
                    self.stats['base64_encoded'] += 1
        
        # 2. Check required properties (RFC 2426)
        if 'VERSION' not in properties:
            errors.append(f"vCard {index}: Missing required VERSION property")
        else:
            # Check version number
            version_line = next((l for l in lines if l.startswith('VERSION:')), None)
            if version_line and '3.0' not in version_line:
                warnings.append(f"vCard {index}: Not version 3.0 ({version_line})")
        
        if 'FN' not in properties:
            errors.append(f"vCard {index}: Missing required FN (formatted name) property")
            self.stats['missing_fn'] += 1
        
        if 'N' not in properties:
            warnings.append(f"vCard {index}: Missing N (structured name) property")
            self.stats['missing_n'] += 1
        
        # 3. Check for duplicate properties that should be unique
        for prop in ['VERSION', 'FN', 'N', 'BDAY']:
            if properties.get(prop, 0) > 1:
                warnings.append(f"vCard {index}: Multiple {prop} properties ({properties[prop]})")
        
        # 4. Check for common issues
        if 'EMAIL' in properties and properties['EMAIL'] >= 4:
            self.stats['excessive_emails'] += 1
            warnings.append(f"vCard {index}: Excessive emails ({properties['EMAIL']})")
        
        if 'PHOTO' in properties:
            self.stats['has_photo'] += 1
            # Check for large photos
            photo_lines = [l for l in lines if l.startswith('PHOTO')]
            for photo_line in photo_lines:
                if len(photo_line) > 75:  # RFC recommends line folding at 75 chars
                    self.stats['unfolded_photos'] += 1
        
        # 5. Check for non-standard properties
        standard_props = {
            'BEGIN', 'END', 'VERSION', 'FN', 'N', 'NICKNAME', 'PHOTO', 'BDAY',
            'ADR', 'LABEL', 'TEL', 'EMAIL', 'MAILER', 'TZ', 'GEO', 'TITLE',
            'ROLE', 'LOGO', 'AGENT', 'ORG', 'CATEGORIES', 'NOTE', 'PRODID',
            'REV', 'SORT-STRING', 'SOUND', 'UID', 'URL', 'CLASS', 'KEY'
        }
        
        for prop in properties:
            if prop not in standard_props and not prop.startswith('X-'):
                warnings.append(f"vCard {index}: Non-standard property: {prop}")
                self.stats[f'non_standard_{prop}'] += 1
        
        # 6. Try parsing with vobject to catch additional issues
        try:
            vobj = vobject.readOne(vcard_text)
            # Successfully parsed
            if hasattr(vobj, 'contents'):
                self.stats['vobject_parseable'] += 1
        except Exception as e:
            errors.append(f"vCard {index}: vobject parsing failed: {str(e)[:50]}")
            self.stats['vobject_parse_errors'] += 1
        
        # Store errors and warnings
        if errors:
            self.errors.extend(errors)
            for error in errors:
                if self.strict:
                    print(f"❌ {error}")
        
        if warnings:
            self.warnings.extend(warnings)
        
        return len(errors) == 0
    
    def _print_summary(self, total, valid):
        """Print validation summary"""
        print(f"\n{'='*60}")
        print("VALIDATION SUMMARY")
        print(f"{'='*60}")
        print(f"Total vCards: {total}")
        print(f"Valid vCards: {valid} ({valid/total*100:.1f}%)")
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")
        
        print(f"\nKEY STATISTICS:")
        for key, value in sorted(self.stats.items()):
            print(f"  {key}: {value}")
        
        if self.errors:
            print(f"\nSAMPLE ERRORS (first 10):")
            for error in self.errors[:10]:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\nSAMPLE WARNINGS (first 10):")
            for warning in self.warnings[:10]:
                print(f"  • {warning}")


def validate_with_vobject(filepath):
    """Additional validation using vobject's parsing"""
    print(f"\n{'='*60}")
    print("VOBJECT PARSING ANALYSIS")
    print(f"{'='*60}\n")
    
    parse_errors = []
    successful_parses = 0
    total_vcards = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            for vcard in vobject.readComponents(f.read()):
                total_vcards += 1
                try:
                    # Try to access common properties
                    _ = vcard.serialize()
                    if hasattr(vcard, 'fn'):
                        _ = vcard.fn.value
                    if hasattr(vcard, 'n'):
                        _ = vcard.n.value
                    successful_parses += 1
                except Exception as e:
                    parse_errors.append({
                        'index': total_vcards,
                        'error': str(e)[:100]
                    })
        except Exception as e:
            print(f"Fatal parsing error: {e}")
    
    print(f"vobject successfully parsed: {successful_parses}/{total_vcards}")
    print(f"Parse errors: {len(parse_errors)}")
    
    if parse_errors:
        print("\nSample parse errors:")
        for error in parse_errors[:5]:
            print(f"  vCard {error['index']}: {error['error']}")
    
    return {
        'total': total_vcards,
        'successful': successful_parses,
        'errors': parse_errors
    }


def main():
    """Main validation routine"""
    # Create data directory if it doesn't exist
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    print("vCard Standards Validation")
    print("=" * 60)
    print(f"Target: {config.SARA_VCARD_FILE}")
    print(f"Standard: RFC 2426 (vCard 3.0)")
    
    # Initialize validator
    validator = VCardValidator(strict=False)  # Set to True for all errors
    
    # Run validation
    results = validator.validate_file(config.SARA_VCARD_FILE)
    
    # Run vobject parsing analysis
    vobject_results = validate_with_vobject(config.SARA_VCARD_FILE)
    
    # Save results
    report = {
        'timestamp': datetime.now().isoformat(),
        'file': config.SARA_VCARD_FILE,
        'validation_results': results,
        'vobject_results': vobject_results
    }
    
    report_file = os.path.join(config.DATA_DIR, 'validation_report.json')
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Validation complete! Report saved to: {report_file}")
    
    # Determine if the file is generally compliant
    compliance_rate = results['valid_vcards'] / results['total_vcards'] * 100
    if compliance_rate >= 95:
        print(f"\n✅ File is generally RFC 2426 compliant ({compliance_rate:.1f}%)")
    elif compliance_rate >= 80:
        print(f"\n⚠️  File has some compliance issues ({compliance_rate:.1f}%)")
    else:
        print(f"\n❌ File has significant compliance issues ({compliance_rate:.1f}%)")


if __name__ == "__main__":
    main()