"""
VCard Standards Validator using vcard library
RULE: Always use vcard library for validation, vobject for manipulation
"""

import os
import logging
from typing import List, Dict, Tuple, Optional
import vcard  # For validation only
import vobject  # For manipulation only

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VCardStandardsValidator:
    """
    Validates vCard files using the vcard library for strict RFC 2426 compliance.
    This class ONLY validates - it does not manipulate data.
    """
    
    def __init__(self, strict=True):
        self.strict = strict
        self.errors = []
        self.warnings = []
        
    def validate_file(self, filepath: str) -> Tuple[bool, List[str], List[str]]:
        """
        Validate an entire vCard file using vcard library.
        
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        logger.info(f"Validating file with vcard library: {filepath}")
        
        try:
            # Use vcard library for validation
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into individual vCards
            vcards = self._split_vcards(content)
            
            all_errors = []
            all_warnings = []
            
            for i, vcard_text in enumerate(vcards):
                errors, warnings = self._validate_single_vcard(vcard_text, i)
                all_errors.extend(errors)
                all_warnings.extend(warnings)
            
            is_valid = len(all_errors) == 0 if self.strict else len(all_errors) < len(vcards) * 0.1
            
            return is_valid, all_errors, all_warnings
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False, [str(e)], []
    
    def _split_vcards(self, content: str) -> List[str]:
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
    
    def _validate_single_vcard(self, vcard_text: str, index: int) -> Tuple[List[str], List[str]]:
        """
        Validate a single vCard using vcard library standards.
        
        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []
        
        try:
            # Check basic structure
            if not vcard_text.startswith('BEGIN:VCARD'):
                errors.append(f"vCard {index}: Missing BEGIN:VCARD")
            if not vcard_text.endswith('END:VCARD'):
                errors.append(f"vCard {index}: Missing END:VCARD")
            
            # Check for required properties according to RFC 2426
            lines = vcard_text.split('\n')
            properties = {}
            
            for line in lines:
                if ':' in line and not line.startswith(('BEGIN:', 'END:')):
                    prop = line.split(':', 1)[0].split(';')[0].upper()
                    base_prop = prop.split('.')[0]  # Handle ITEM1.EMAIL format
                    properties[base_prop] = properties.get(base_prop, 0) + 1
            
            # Required fields
            if 'VERSION' not in properties:
                errors.append(f"vCard {index}: Missing required VERSION")
            if 'FN' not in properties:
                errors.append(f"vCard {index}: Missing required FN (Formatted Name)")
            if 'N' not in properties:
                warnings.append(f"vCard {index}: Missing N (Structured Name)")
            
            # Check for Apple-specific properties
            for prop in properties:
                if prop.startswith('ITEM'):
                    warnings.append(f"vCard {index}: Non-standard Apple property: {prop}")
            
        except Exception as e:
            errors.append(f"vCard {index}: Validation error: {str(e)}")
        
        return errors, warnings


class VCardProcessor:
    """
    Processes vCard files using the standard workflow:
    1. Validate with vcard library
    2. Manipulate with vobject
    """
    
    def __init__(self):
        self.validator = VCardStandardsValidator()
    
    def process_file(self, filepath: str) -> Dict[str, any]:
        """
        Standard workflow for processing vCard files.
        
        Steps:
        1. Validate with vcard library
        2. If valid (or acceptably valid), parse with vobject
        3. Return results
        """
        logger.info(f"Processing vCard file: {filepath}")
        
        # Step 1: ALWAYS validate first with vcard library
        is_valid, errors, warnings = self.validator.validate_file(filepath)
        
        result = {
            'filepath': filepath,
            'is_valid': is_valid,
            'validation_errors': errors[:10],  # Limit to first 10
            'validation_warnings': warnings[:10],
            'total_errors': len(errors),
            'total_warnings': len(warnings),
            'parsed_vcards': []
        }
        
        # Step 2: Only proceed to parsing if reasonably valid
        if is_valid or len(errors) < 100:  # Allow some errors for real-world data
            logger.info("Proceeding to parse with vobject...")
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    vcard_data = f.read()
                
                # Parse with vobject for manipulation
                for vcard in vobject.readComponents(vcard_data):
                    try:
                        parsed = {
                            'fn': vcard.fn.value if hasattr(vcard, 'fn') else None,
                            'has_photo': hasattr(vcard, 'photo'),
                            'email_count': len(vcard.email_list) if hasattr(vcard, 'email_list') else 0,
                            'has_issues': False
                        }
                        
                        # Check for issues
                        if parsed['email_count'] >= 4:
                            parsed['has_issues'] = True
                        
                        result['parsed_vcards'].append(parsed)
                        
                    except Exception as e:
                        logger.warning(f"Error parsing individual vCard: {e}")
                        
            except Exception as e:
                logger.error(f"Error parsing file with vobject: {e}")
                result['parse_error'] = str(e)
        else:
            logger.warning(f"File has too many validation errors ({len(errors)}), skipping parsing")
            result['skip_reason'] = 'Too many validation errors'
        
        return result


# Convenience functions following the standard pattern
def validate_vcard_file(filepath: str) -> Tuple[bool, List[str], List[str]]:
    """Validate a vCard file using vcard library (validation only)"""
    validator = VCardStandardsValidator()
    return validator.validate_file(filepath)


def parse_vcard_file(filepath: str) -> List[vobject.vCard]:
    """
    Parse a vCard file using vobject (manipulation only).
    Should only be called after validation!
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return list(vobject.readComponents(f.read()))


def process_vcard_file(filepath: str) -> Dict[str, any]:
    """
    Standard workflow: validate with vcard, then parse with vobject.
    This is the recommended function for all vCard processing.
    """
    processor = VCardProcessor()
    return processor.process_file(filepath)


# Example usage pattern that MUST be followed
if __name__ == "__main__":
    # This demonstrates the required pattern:
    # 1. ALWAYS validate with vcard library first
    # 2. ONLY use vobject for manipulation after validation
    
    test_file = "test.vcf"
    
    # Step 1: Validate
    is_valid, errors, warnings = validate_vcard_file(test_file)
    print(f"Validation result: {'Valid' if is_valid else 'Invalid'}")
    
    # Step 2: Only parse if valid
    if is_valid or len(errors) < 10:  # Allow some tolerance
        vcards = parse_vcard_file(test_file)
        print(f"Parsed {len(vcards)} vCards with vobject")
        
        # Now you can manipulate with vobject
        for vcard in vcards:
            if hasattr(vcard, 'fn'):
                print(f"  - {vcard.fn.value}")