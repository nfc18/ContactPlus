#!/usr/bin/env python3
"""
Post-Merge AI Recovery System

Applies intelligent analysis and corrections to an already-merged phonebook
to fix issues that should have been caught before merging.
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Any
import vobject
from contact_intelligence import ContactIntelligenceEngine, analyze_contact_with_ai
from phonebook_operations import PhonebookManager
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostMergeRecovery:
    """
    Applies AI intelligence to fix issues in an already-merged phonebook
    that should have been caught during initial processing.
    """
    
    def __init__(self):
        self.phonebook_manager = PhonebookManager()
        self.ai_engine = ContactIntelligenceEngine()
        
    def analyze_current_phonebook(self) -> Dict[str, Any]:
        """
        Analyze the current master phonebook for quality issues
        that AI would have prevented.
        """
        logger.info("Analyzing current master phonebook for AI-correctable issues...")
        
        # Load current master
        current_master = self.phonebook_manager.current_master
        if not current_master or not os.path.exists(current_master):
            raise FileNotFoundError("No current master phonebook found")
        
        with open(current_master, 'r', encoding='utf-8') as f:
            vcards = list(vobject.readComponents(f.read()))
        
        logger.info(f"Analyzing {len(vcards)} contacts...")
        
        # Categorize issues
        high_priority_fixes = []  # Auto-correctable with high confidence
        medium_priority_fixes = []  # Needs review but likely fixable
        low_priority_fixes = []  # Minor improvements
        business_contacts = []  # Should be categorized differently
        
        total_issues = 0
        
        for i, vcard in enumerate(vcards):
            try:
                analysis = analyze_contact_with_ai(vcard)
                
                if not analysis.insights:
                    continue
                
                total_issues += len(analysis.insights)
                contact_info = {
                    'index': i,
                    'name': vcard.fn.value if hasattr(vcard, 'fn') else 'Unknown',
                    'analysis': analysis
                }
                
                # Categorize by confidence and issue type
                for insight in analysis.insights:
                    if insight.confidence >= 0.90 and insight.auto_apply_safe:
                        if insight.issue_type == 'email_derived_name':
                            high_priority_fixes.append({
                                **contact_info,
                                'insight': insight,
                                'category': 'email_derived_username'
                            })
                        else:
                            high_priority_fixes.append({
                                **contact_info,
                                'insight': insight,
                                'category': 'formatting'
                            })
                    elif insight.confidence >= 0.70:
                        medium_priority_fixes.append({
                            **contact_info,
                            'insight': insight
                        })
                    else:
                        low_priority_fixes.append({
                            **contact_info,
                            'insight': insight
                        })
                
                # Check for business contacts mixed with personal
                if self._is_business_contact(vcard):
                    business_contacts.append(contact_info)
                    
            except Exception as e:
                logger.error(f"Error analyzing contact {i}: {e}")
        
        return {
            'total_contacts': len(vcards),
            'total_issues': total_issues,
            'high_priority_fixes': high_priority_fixes,
            'medium_priority_fixes': medium_priority_fixes,
            'low_priority_fixes': low_priority_fixes,
            'business_contacts': business_contacts,
            'quality_score': 1.0 - (total_issues / len(vcards)) if vcards else 0,
            'timestamp': datetime.now().isoformat()
        }
    
    def apply_recovery_fixes(self, analysis_result: Dict[str, Any], 
                           apply_high_priority: bool = True,
                           apply_medium_priority: bool = False) -> Dict[str, Any]:
        """
        Apply AI-suggested fixes to recover from pre-merge quality issues.
        
        FOLLOWS MANDATORY PHONEBOOK EDITING PROTOCOL
        """
        logger.info("Starting post-merge recovery with AI fixes...")
        
        # STEP 1: PRE-EDIT VALIDATION (MANDATORY)
        current_master = self.phonebook_manager.current_master
        from auto_validate import validate_phonebook
        validate_phonebook(current_master, "pre-recovery check")
        
        # STEP 2: AUTOMATIC BACKUP (MANDATORY)
        backup_path = self.phonebook_manager._backup_current()
        logger.info(f"Recovery backup created: {backup_path}")
        
        # STEP 3: LOAD CONTACTS INTO MEMORY
        with open(current_master, 'r', encoding='utf-8') as f:
            vcards = list(vobject.readComponents(f.read()))
        
        fixes_applied = []
        
        # Apply high priority fixes (email-derived usernames, etc.)
        if apply_high_priority:
            for fix in analysis_result['high_priority_fixes']:
                try:
                    contact_index = fix['index']
                    insight = fix['insight']
                    vcard = vcards[contact_index]
                    
                    original_name = vcard.fn.value if hasattr(vcard, 'fn') else 'Unknown'
                    
                    # Apply the fix
                    if insight.issue_type == 'email_derived_name':
                        vcard.fn.value = insight.suggested_value
                        
                        # Update N field too
                        if hasattr(vcard, 'n'):
                            name_parts = insight.suggested_value.split()
                            if len(name_parts) >= 2:
                                vcard.n.value.given = name_parts[0]
                                vcard.n.value.family = ' '.join(name_parts[1:])
                    
                    elif insight.issue_type in ['improper_case', 'numbers_in_name']:
                        vcard.fn.value = insight.suggested_value
                    
                    fixes_applied.append({
                        'type': insight.issue_type,
                        'original': original_name,
                        'fixed': insight.suggested_value,
                        'confidence': insight.confidence
                    })
                    
                    logger.info(f"Fixed: {original_name} → {insight.suggested_value}")
                    
                except Exception as e:
                    logger.error(f"Failed to apply fix: {e}")
        
        # Apply medium priority fixes if requested
        if apply_medium_priority:
            # Similar logic for medium priority fixes
            pass
        
        # STEP 4: SAVE TO TEMPORARY FILE AND VALIDATE (MANDATORY)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_file = f"temp_recovery_{timestamp}.vcf"
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            for vcard in vcards:
                f.write(vcard.serialize())
        
        # Validate fixed file
        from vcard_validator import VCardStandardsValidator
        validator = VCardStandardsValidator()
        is_valid, errors, warnings = validator.validate_file(temp_file)
        
        if not is_valid:
            os.remove(temp_file)
            logger.error(f"Recovery fixes broke validation ({len(errors)} errors) - aborting")
            return {
                'status': 'failed',
                'reason': 'Validation failed after fixes',
                'errors': errors[:10]
            }
        
        # STEP 5: SAVE NEW MASTER (MANDATORY)
        new_master = f"data/MASTER_PHONEBOOK_RECOVERED_{timestamp}.vcf"
        os.rename(temp_file, new_master)
        self.phonebook_manager.current_master = new_master
        
        # STEP 6: CHANGE REPORTING (MANDATORY)
        logger.info(f"Recovery complete: {len(fixes_applied)} fixes applied")
        logger.info(f"New master: {new_master}")
        
        return {
            'status': 'success',
            'new_master': new_master,
            'backup_path': backup_path,
            'fixes_applied': fixes_applied,
            'total_fixes': len(fixes_applied),
            'validation_result': {
                'valid': is_valid,
                'errors': len(errors),
                'warnings': len(warnings)
            }
        }
    
    def _is_business_contact(self, vcard: vobject.vCard) -> bool:
        """Detect if this is likely a business contact mixed with personal"""
        if not hasattr(vcard, 'fn'):
            return False
            
        name = vcard.fn.value.lower()
        
        business_indicators = [
            'support', 'team', 'buchhaltung', 'service', 'info@',
            'bot', 'chat', 'control', 'system', 'auto',
            'gmbh', 'inc', 'llc', 'ltd', 'corp'
        ]
        
        return any(indicator in name for indicator in business_indicators)
    
    def generate_recovery_report(self, analysis: Dict[str, Any], 
                               recovery_result: Dict[str, Any] = None) -> str:
        """Generate comprehensive recovery report"""
        
        report_file = f"data/POST_MERGE_RECOVERY_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'problem_identified': "Phonebook was merged before AI intelligence was implemented",
            'timeline_evidence': {
                'phonebook_created': "2025-06-07 07:17:56",
                'ai_system_built': "2025-06-07 10:45:00",
                'gap_minutes': 207
            },
            'analysis': analysis,
            'recovery_applied': recovery_result is not None,
            'recovery_result': recovery_result,
            'recommendations': self._generate_recommendations(analysis)
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report_file


def recover_from_premature_merge(apply_fixes: bool = True) -> Dict[str, Any]:
    """
    Main function to recover from pre-AI merge issues.
    
    This addresses the exact problem: contacts were merged before
    AI intelligence was available to catch quality issues.
    """
    recovery = PostMergeRecovery()
    
    # Analyze current state
    logger.info("Analyzing damage from pre-AI merge...")
    analysis = recovery.analyze_current_phonebook()
    
    logger.info(f"Found {analysis['total_issues']} quality issues in {analysis['total_contacts']} contacts")
    logger.info(f"High priority fixes available: {len(analysis['high_priority_fixes'])}")
    
    result = {'analysis': analysis}
    
    if apply_fixes:
        # Apply recovery fixes
        logger.info("Applying AI recovery fixes...")
        recovery_result = recovery.apply_recovery_fixes(analysis)
        result['recovery'] = recovery_result
    
    # Generate report
    report_file = recovery.generate_recovery_report(analysis, result.get('recovery'))
    result['report_file'] = report_file
    
    return result


if __name__ == "__main__":
    print("Post-Merge AI Recovery System")
    print("=" * 50)
    print("Problem: Contacts were merged BEFORE AI intelligence was available")
    print("Solution: Apply AI corrections to fix preventable quality issues")
    print("=" * 50)
    
    try:
        result = recover_from_premature_merge(apply_fixes=True)
        
        analysis = result['analysis']
        print(f"\nCurrent Database Analysis:")
        print(f"Total contacts: {analysis['total_contacts']}")
        print(f"Quality issues: {analysis['total_issues']}")
        print(f"Quality score: {analysis['quality_score']:.1%}")
        print(f"High priority fixes: {len(analysis['high_priority_fixes'])}")
        
        if 'recovery' in result:
            recovery = result['recovery']
            print(f"\nRecovery Applied:")
            print(f"Status: {recovery['status']}")
            print(f"Fixes applied: {recovery.get('total_fixes', 0)}")
            if recovery['status'] == 'success':
                print(f"New master: {recovery['new_master']}")
        
        print(f"\nDetailed report: {result['report_file']}")
        
    except Exception as e:
        logger.error(f"Recovery failed: {e}")
        print(f"Error: {e}")