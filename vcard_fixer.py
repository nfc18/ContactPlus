#!/usr/bin/env python3
"""
vCard Fixer - Remediate validation errors to ensure RFC compliance

RULE: Always use vcard library for validation, vobject for manipulation
This module fixes common vCard issues to ensure all contacts can be imported.
"""

import re
import logging
from typing import List, Dict, Tuple, Optional
import vobject  # For manipulation ONLY
from vcard_validator import VCardStandardsValidator  # For validation ONLY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VCardFixer:
    """
    Fixes common vCard compliance issues.
    
    Common fixes:
    - Missing FN (Formatted Name)
    - Missing N (Name components)
    - Missing VERSION
    - Apple ITEM property normalization
    - Character encoding issues
    """
    
    def __init__(self):
        self.validator = VCardStandardsValidator(strict=True)
        self.fix_stats = {
            'missing_fn_fixed': 0,
            'missing_n_fixed': 0,
            'missing_version_fixed': 0,
            'item_properties_normalized': 0,
            'total_fixed': 0
        }
    
    def fix_file(self, input_filepath: str, output_filepath: str) -> Dict[str, any]:
        """
        Fix all vCards in a file to ensure compliance.
        
        Workflow:
        1. Validate with vcard library
        2. Parse with vobject
        3. Fix issues
        4. Re-validate
        5. Save fixed version
        """
        logger.info(f"Starting vCard fix process for: {input_filepath}")
        
        # Step 1: Initial validation with vcard library
        logger.info("Step 1: Initial validation...")
        is_valid, errors, warnings = self.validator.validate_file(input_filepath)
        
        initial_report = {
            'initial_valid': is_valid,
            'initial_errors': len(errors),
            'initial_warnings': len(warnings),
            'sample_errors': errors[:5]
        }
        
        if is_valid:
            logger.info("File is already valid, no fixes needed")
            return {
                'status': 'already_valid',
                'initial_report': initial_report,
                'fixes_applied': self.fix_stats
            }
        
        # Step 2: Parse with vobject for manipulation
        logger.info("Step 2: Parsing with vobject for fixes...")
        with open(input_filepath, 'r', encoding='utf-8') as f:
            vcard_data = f.read()
        
        # Process each vCard
        fixed_vcards = []
        
        for vcard in vobject.readComponents(vcard_data):
            try:
                fixed_vcard = self._fix_single_vcard(vcard)
                fixed_vcards.append(fixed_vcard)
            except Exception as e:
                logger.error(f"Error fixing vCard: {e}")
                # Keep original if fix fails
                fixed_vcards.append(vcard)
        
        # Step 3: Write fixed vCards
        logger.info(f"Step 3: Writing {len(fixed_vcards)} fixed vCards...")
        with open(output_filepath, 'w', encoding='utf-8') as f:
            for vcard in fixed_vcards:
                f.write(vcard.serialize())
        
        # Step 4: Re-validate fixed file
        logger.info("Step 4: Re-validating fixed file...")
        final_valid, final_errors, final_warnings = self.validator.validate_file(output_filepath)
        
        final_report = {
            'final_valid': final_valid,
            'final_errors': len(final_errors),
            'final_warnings': len(final_warnings),
            'remaining_errors': final_errors[:5]
        }
        
        # Return comprehensive report
        return {
            'status': 'fixed',
            'initial_report': initial_report,
            'final_report': final_report,
            'fixes_applied': self.fix_stats,
            'improvement': {
                'errors_fixed': initial_report['initial_errors'] - final_report['final_errors'],
                'warnings_reduced': initial_report['initial_warnings'] - final_report['final_warnings']
            }
        }
    
    def _fix_single_vcard(self, vcard: vobject.vCard) -> vobject.vCard:
        """Fix a single vCard object"""
        
        # Fix 1: Ensure VERSION is present
        if not hasattr(vcard, 'version'):
            vcard.add('version')
            vcard.version.value = '3.0'
            self.fix_stats['missing_version_fixed'] += 1
            logger.debug("Added missing VERSION")
        
        # Fix 2: Ensure FN (Formatted Name) is present
        if not hasattr(vcard, 'fn'):
            fn_value = self._generate_fn(vcard)
            if fn_value:
                vcard.add('fn')
                vcard.fn.value = fn_value
                self.fix_stats['missing_fn_fixed'] += 1
                logger.debug(f"Added missing FN: {fn_value}")
        
        # Fix 3: Ensure N (Name components) is present
        if not hasattr(vcard, 'n'):
            n_value = self._generate_n(vcard)
            if n_value:
                vcard.add('n')
                vcard.n.value = n_value
                self.fix_stats['missing_n_fixed'] += 1
                logger.debug("Added missing N")
        
        # Fix 4: Normalize Apple ITEM properties
        self._normalize_item_properties(vcard)
        
        self.fix_stats['total_fixed'] += 1
        return vcard
    
    def _generate_fn(self, vcard: vobject.vCard) -> Optional[str]:
        """Generate FN from available data"""
        
        # Try 1: From N components
        if hasattr(vcard, 'n'):
            n = vcard.n.value
            parts = []
            if n.given:
                parts.append(n.given)
            if n.family:
                parts.append(n.family)
            if parts:
                return ' '.join(parts)
        
        # Try 2: From ORG
        if hasattr(vcard, 'org'):
            org_values = vcard.org.value
            if isinstance(org_values, list) and org_values:
                return str(org_values[0])
            elif org_values:
                return str(org_values)
        
        # Try 3: From EMAIL (extract name part)
        if hasattr(vcard, 'email'):
            email = vcard.email.value
            if '@' in email:
                local_part = email.split('@')[0]
                # Convert dots/underscores to spaces and title case
                name = local_part.replace('.', ' ').replace('_', ' ').title()
                return name
        
        # Try 4: From TEL (last resort)
        if hasattr(vcard, 'tel'):
            return f"Contact {vcard.tel.value}"
        
        # Default fallback
        return "Unknown Contact"
    
    def _generate_n(self, vcard: vobject.vCard) -> Optional[vobject.vcard.Name]:
        """Generate N from available data"""
        
        # Create Name object
        n = vobject.vcard.Name()
        
        # Try to parse from FN
        if hasattr(vcard, 'fn'):
            fn_value = vcard.fn.value
            parts = fn_value.split()
            
            if len(parts) >= 2:
                # Assume first name(s) and last name
                n.given = ' '.join(parts[:-1])
                n.family = parts[-1]
            elif len(parts) == 1:
                # Single name - could be first or last
                n.family = parts[0]
                n.given = ''
            
            n.additional = ''
            n.prefix = ''
            n.suffix = ''
            
            return n
        
        # Default empty name structure
        n.family = ''
        n.given = ''
        n.additional = ''
        n.prefix = ''
        n.suffix = ''
        
        return n
    
    def _normalize_item_properties(self, vcard: vobject.vCard):
        """Convert Apple ITEM properties to standard format"""
        
        # Find all ITEM properties
        items_to_process = {}
        
        for child in list(vcard.getChildren()):
            name = child.name
            
            # Check for ITEM pattern (e.g., ITEM1.EMAIL, ITEM1.X-ABLABEL)
            if '.' in name and name.split('.')[0].startswith('ITEM'):
                item_num = name.split('.')[0]
                prop_name = name.split('.', 1)[1]
                
                if item_num not in items_to_process:
                    items_to_process[item_num] = {}
                
                items_to_process[item_num][prop_name] = child
        
        # Process each ITEM group
        for item_num, props in items_to_process.items():
            # Handle common patterns
            if 'EMAIL' in props and 'X-ABLABEL' in props:
                # Email with label - add as type parameter
                email_prop = props['EMAIL']
                label = props['X-ABLABEL'].value
                
                # Create new email property with proper type
                new_email = vcard.add('email')
                new_email.value = email_prop.value
                
                # Map common labels to types
                if label.lower() in ['work', 'business']:
                    new_email.type_param = 'WORK'
                elif label.lower() in ['home', 'personal']:
                    new_email.type_param = 'HOME'
                else:
                    new_email.type_param = label.upper()
                
                # Remove old properties
                vcard.remove(email_prop)
                vcard.remove(props['X-ABLABEL'])
                
                self.fix_stats['item_properties_normalized'] += 1
            
            elif 'URL' in props and 'X-ABLABEL' in props:
                # URL with label
                url_prop = props['URL']
                label = props['X-ABLABEL'].value
                
                # Create new URL property
                new_url = vcard.add('url')
                new_url.value = url_prop.value
                
                # Remove old properties
                vcard.remove(url_prop)
                vcard.remove(props['X-ABLABEL'])
                
                self.fix_stats['item_properties_normalized'] += 1


def fix_vcards_workflow(input_file: str, output_file: str) -> Dict[str, any]:
    """
    Complete workflow to fix vCard files.
    
    This is the recommended function to use for fixing vCards.
    Follows the pattern: validate -> fix -> re-validate
    """
    fixer = VCardFixer()
    return fixer.fix_file(input_file, output_file)


if __name__ == "__main__":
    # Example usage
    import config
    
    input_file = config.SARA_VCARD_FILE
    output_file = input_file.replace('.vcf', '_FIXED.vcf')
    
    print("vCard Fixer")
    print("=" * 60)
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    
    result = fix_vcards_workflow(input_file, output_file)
    
    print("\nFix Report:")
    print("-" * 40)
    print(f"Initial errors: {result['initial_report']['initial_errors']}")
    print(f"Final errors: {result['final_report']['final_errors']}")
    print(f"Errors fixed: {result['improvement']['errors_fixed']}")
    
    print("\nFixes applied:")
    for fix_type, count in result['fixes_applied'].items():
        if count > 0:
            print(f"  {fix_type}: {count}")
    
    print(f"\nFixed file saved to: {output_file}")