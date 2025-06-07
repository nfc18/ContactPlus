#!/usr/bin/env python3
"""
Complete vCard Processing Workflow

This module provides the standard workflow for processing vCard files:
1. Validate with vcard library
2. Fix issues if needed
3. Re-validate
4. Process with vobject

RULE: Always use vcard library for validation, vobject for manipulation
"""

import os
import logging
import shutil
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from vcard_validator import VCardStandardsValidator
from vcard_fixer import VCardFixer
from vcard_soft_compliance import SoftComplianceChecker
import vobject
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VCardWorkflow:
    """
    Standard workflow for processing vCard files with automatic fixing.
    
    This ensures all vCards are compliant before processing.
    """
    
    def __init__(self, auto_fix=True, backup=True, soft_compliance=True):
        self.auto_fix = auto_fix
        self.backup = backup
        self.soft_compliance = soft_compliance
        self.validator = VCardStandardsValidator()
        self.fixer = VCardFixer()
        self.soft_checker = SoftComplianceChecker()
        
    def process_file(self, filepath: str) -> Dict[str, any]:
        """
        Complete workflow for processing a vCard file.
        
        Steps:
        1. Create backup (if enabled)
        2. Validate with vcard library (hard compliance)
        3. Fix if needed and auto_fix is True
        4. Re-validate after hard fixes
        5. Apply soft compliance fixes if enabled
        6. Final validation after soft fixes
        7. Parse with vobject for further processing
        
        Returns:
            Dict with complete processing report
        """
        logger.info(f"Starting vCard workflow for: {filepath}")
        
        result = {
            'input_file': filepath,
            'timestamp': datetime.now().isoformat(),
            'backup_created': False,
            'fixes_applied': False,
            'final_valid': False,
            'vcards_parsed': 0
        }
        
        # Step 1: Create backup if requested
        if self.backup:
            backup_path = self._create_backup(filepath)
            result['backup_created'] = True
            result['backup_path'] = backup_path
            logger.info(f"Backup created: {backup_path}")
        
        # Step 2: Initial validation
        logger.info("Validating vCard file...")
        is_valid, errors, warnings = self.validator.validate_file(filepath)
        
        result['initial_validation'] = {
            'valid': is_valid,
            'error_count': len(errors),
            'warning_count': len(warnings),
            'sample_errors': errors[:5]
        }
        
        working_file = filepath
        
        # Step 3: Fix if needed
        if not is_valid and self.auto_fix:
            logger.info(f"File has {len(errors)} errors. Applying fixes...")
            
            # Create fixed version
            fixed_file = filepath.replace('.vcf', '_FIXED.vcf')
            fix_report = self.fixer.fix_file(filepath, fixed_file)
            
            result['fixes_applied'] = True
            result['fix_report'] = fix_report
            working_file = fixed_file
            
            # Re-validate fixed file
            logger.info("Re-validating fixed file...")
            is_valid, errors, warnings = self.validator.validate_file(fixed_file)
            
            result['post_fix_validation'] = {
                'valid': is_valid,
                'error_count': len(errors),
                'warning_count': len(warnings),
                'remaining_errors': errors[:5]
            }
        
        result['final_valid'] = is_valid
        
        # Step 4: Apply soft compliance if enabled and file is valid
        if self.soft_compliance and (is_valid or len(errors) < 100):
            logger.info("Applying soft compliance checks...")
            
            soft_compliant_file = working_file.replace('.vcf', '_SOFT.vcf')
            soft_result = self.soft_checker.check_and_fix_file(
                working_file, 
                soft_compliant_file,
                default_country='US'
            )
            
            result['soft_compliance_applied'] = True
            result['soft_compliance_report'] = {
                'issues_found': soft_result['issues_found'],
                'fixes_applied': soft_result['fixes_applied']
            }
            working_file = soft_compliant_file
            
            # Step 5: Final validation after soft compliance
            logger.info("Final validation after soft compliance...")
            final_is_valid, final_errors, final_warnings = self.validator.validate_file(working_file)
            
            result['post_soft_validation'] = {
                'valid': final_is_valid,
                'error_count': len(final_errors),
                'warning_count': len(final_warnings),
                'sample_errors': final_errors[:5]
            }
            
            if not final_is_valid:
                logger.warning(f"Soft compliance introduced {len(final_errors)} validation errors!")
                # Log which soft fixes might have caused issues
                if len(final_errors) > 0:
                    logger.error("Soft compliance may have broken RFC compliance. Review the changes.")
            
            # Update final validity status
            result['final_valid'] = final_is_valid
            is_valid = final_is_valid
            errors = final_errors
        
        # Step 6: Parse with vobject if valid (or reasonably valid)
        if is_valid or len(errors) < 100:
            logger.info("Parsing vCards with vobject...")
            
            try:
                with open(working_file, 'r', encoding='utf-8') as f:
                    vcard_data = f.read()
                
                vcards = list(vobject.readComponents(vcard_data))
                result['vcards_parsed'] = len(vcards)
                result['parse_success'] = True
                result['working_file'] = working_file
                
                # Sample data from parsed vCards
                sample_data = []
                for vcard in vcards[:5]:  # First 5 as sample
                    sample = {
                        'has_fn': hasattr(vcard, 'fn'),
                        'has_n': hasattr(vcard, 'n'),
                        'has_version': hasattr(vcard, 'version')
                    }
                    if hasattr(vcard, 'fn'):
                        sample['fn'] = vcard.fn.value
                    sample_data.append(sample)
                
                result['sample_vcards'] = sample_data
                
            except Exception as e:
                logger.error(f"Error parsing vCards: {e}")
                result['parse_success'] = False
                result['parse_error'] = str(e)
        else:
            logger.error(f"File still has too many errors ({len(errors)}), cannot proceed")
            result['skip_reason'] = f"Too many validation errors: {len(errors)}"
        
        return result
    
    def _create_backup(self, filepath: str) -> str:
        """Create timestamped backup of vCard file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = os.path.join(config.BACKUP_DIR, 'workflow')
        os.makedirs(backup_dir, exist_ok=True)
        
        filename = os.path.basename(filepath)
        backup_path = os.path.join(backup_dir, f"{filename}_{timestamp}.backup")
        
        shutil.copy2(filepath, backup_path)
        return backup_path


def ensure_valid_vcards(filepath: str, output_path: Optional[str] = None) -> str:
    """
    Convenience function to ensure vCard file is valid.
    
    If the file is invalid, it will be fixed and saved to output_path.
    If output_path is not provided, the original file will be overwritten.
    
    Args:
        filepath: Path to vCard file
        output_path: Optional output path for fixed file
        
    Returns:
        Path to valid vCard file
    """
    validator = VCardStandardsValidator()
    is_valid, errors, warnings = validator.validate_file(filepath)
    
    if is_valid:
        logger.info("File is already valid")
        return filepath
    
    # Fix the file
    fixer = VCardFixer()
    if output_path is None:
        output_path = filepath
    
    logger.info(f"Fixing {len(errors)} validation errors...")
    fix_report = fixer.fix_file(filepath, output_path)
    
    # Verify fixed file is valid
    is_valid, errors, warnings = validator.validate_file(output_path)
    if not is_valid:
        logger.warning(f"File still has {len(errors)} errors after fixing")
    
    return output_path


# Example usage demonstrating the complete workflow
if __name__ == "__main__":
    import json
    
    print("vCard Complete Workflow Demo")
    print("=" * 60)
    
    # Process Sara's vCard file with full compliance
    workflow = VCardWorkflow(auto_fix=True, backup=True, soft_compliance=True)
    result = workflow.process_file(config.SARA_VCARD_FILE)
    
    print("\nWorkflow Report:")
    print("-" * 40)
    print(f"Input file: {result['input_file']}")
    print(f"Backup created: {result['backup_created']}")
    print(f"Initial validation: {result['initial_validation']['error_count']} errors")
    print(f"Fixes applied: {result['fixes_applied']}")
    
    if result['fixes_applied']:
        print(f"Post-fix validation: {result['post_fix_validation']['error_count']} errors")
    
    if result.get('soft_compliance_applied'):
        soft_report = result['soft_compliance_report']
        print(f"\nSoft compliance:")
        print(f"  Issues found: {soft_report['issues_found']}")
        for fix, count in soft_report['fixes_applied'].items():
            if count > 0:
                print(f"  {fix}: {count}")
    
    print(f"\nFinal valid: {result['final_valid']}")
    print(f"vCards parsed: {result['vcards_parsed']}")
    
    # Save detailed report
    report_path = os.path.join(config.DATA_DIR, 'workflow_report.json')
    with open(report_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_path}")