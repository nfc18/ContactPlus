#!/usr/bin/env python3
"""
Intelligent Workflow - AI-Enhanced Contact Processing

This module integrates the AI intelligence engine with the existing
contact processing workflow to leverage smart analysis and suggestions.
"""

import os
import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime
import vobject
from vcard_workflow import VCardWorkflow
from contact_intelligence import ContactIntelligenceEngine, analyze_contact_with_ai, get_high_confidence_fixes, get_user_review_items
from vcard_validator import VCardStandardsValidator
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntelligentContactWorkflow:
    """
    Enhanced workflow that combines rule-based processing with AI intelligence.
    
    Process:
    1. Standard validation and fixing (existing workflow)
    2. AI analysis of each contact
    3. Apply high-confidence AI fixes automatically
    4. Queue uncertain cases for human review with AI insights
    5. Generate comprehensive improvement report
    """
    
    def __init__(self, auto_apply_ai_fixes=True, ai_confidence_threshold=0.95):
        self.standard_workflow = VCardWorkflow(auto_fix=True, backup=True, soft_compliance=True)
        self.ai_engine = ContactIntelligenceEngine()
        self.auto_apply_ai_fixes = auto_apply_ai_fixes
        self.ai_confidence_threshold = ai_confidence_threshold
        
    def process_file_with_intelligence(self, filepath: str) -> Dict[str, Any]:
        """
        Process vCard file with both standard rules and AI intelligence.
        
        Returns comprehensive report including AI analysis and suggestions.
        """
        logger.info(f"Starting intelligent processing of: {filepath}")
        
        # Step 1: Run standard workflow first
        logger.info("Step 1: Running standard validation and fixes...")
        standard_result = self.standard_workflow.process_file(filepath)
        
        if not standard_result.get('final_valid', False):
            logger.error("Standard workflow failed - cannot proceed with AI analysis")
            return {
                'status': 'failed',
                'reason': 'Standard validation failed',
                'standard_result': standard_result
            }
        
        working_file = standard_result.get('working_file', filepath)
        
        # Step 2: Load contacts for AI analysis
        logger.info("Step 2: Loading contacts for AI analysis...")
        with open(working_file, 'r', encoding='utf-8') as f:
            vcards = list(vobject.readComponents(f.read()))
        
        # Step 3: AI analysis of each contact
        logger.info(f"Step 3: Analyzing {len(vcards)} contacts with AI...")
        ai_analyses = []
        high_confidence_fixes = []
        review_queue = []
        
        for i, vcard in enumerate(vcards):
            try:
                analysis = analyze_contact_with_ai(vcard)
                ai_analyses.append(analysis)
                
                # Categorize fixes
                high_conf_fixes = get_high_confidence_fixes(analysis)
                review_items = get_user_review_items(analysis)
                
                if high_conf_fixes:
                    high_confidence_fixes.append({
                        'contact_index': i,
                        'contact_id': analysis.contact_id,
                        'fixes': high_conf_fixes
                    })
                
                if review_items:
                    review_queue.append({
                        'contact_index': i,
                        'contact_id': analysis.contact_id,
                        'analysis': analysis,
                        'review_items': review_items
                    })
                    
            except Exception as e:
                logger.error(f"AI analysis failed for contact {i}: {e}")
        
        # Step 4: Apply high-confidence AI fixes
        logger.info(f"Step 4: Applying {len(high_confidence_fixes)} high-confidence AI fixes...")
        if self.auto_apply_ai_fixes and high_confidence_fixes:
            vcards = self._apply_ai_fixes(vcards, high_confidence_fixes)
            
            # Save improved version
            ai_improved_file = working_file.replace('.vcf', '_AI_IMPROVED.vcf')
            with open(ai_improved_file, 'w', encoding='utf-8') as f:
                for vcard in vcards:
                    f.write(vcard.serialize())
            
            # Validate AI improvements didn't break anything
            validator = VCardStandardsValidator()
            is_valid, errors, warnings = validator.validate_file(ai_improved_file)
            
            if is_valid:
                working_file = ai_improved_file
                logger.info("AI improvements applied and validated successfully")
            else:
                logger.warning(f"AI improvements broke validation ({len(errors)} errors) - reverting")
        
        # Step 5: Generate comprehensive report
        report = self._generate_intelligence_report(
            standard_result=standard_result,
            ai_analyses=ai_analyses,
            high_confidence_fixes=high_confidence_fixes,
            review_queue=review_queue,
            final_file=working_file
        )
        
        return report
    
    def _apply_ai_fixes(self, vcards: List[vobject.vCard], fixes_list: List[Dict[str, Any]]) -> List[vobject.vCard]:
        """Apply high-confidence AI fixes to vCards"""
        
        for fix_group in fixes_list:
            contact_index = fix_group['contact_index']
            vcard = vcards[contact_index]
            
            for insight in fix_group['fixes']:
                try:
                    if insight.issue_type == 'email_derived_name':
                        # Fix name
                        if hasattr(vcard, 'fn'):
                            vcard.fn.value = insight.suggested_value
                        
                        # Update N field if it exists
                        if hasattr(vcard, 'n'):
                            name_parts = insight.suggested_value.split()
                            if len(name_parts) >= 2:
                                vcard.n.value.given = name_parts[0]
                                vcard.n.value.family = ' '.join(name_parts[1:])
                    
                    elif insight.issue_type == 'improper_case':
                        if hasattr(vcard, 'fn'):
                            vcard.fn.value = insight.suggested_value
                    
                    elif insight.issue_type == 'numbers_in_name':
                        if hasattr(vcard, 'fn'):
                            vcard.fn.value = insight.suggested_value
                    
                    elif insight.issue_type == 'duplicate_emails':
                        # Remove duplicate emails
                        if hasattr(vcard, 'email_list'):
                            unique_emails = []
                            seen = set()
                            for email in vcard.email_list:
                                email_lower = email.value.lower()
                                if email_lower not in seen:
                                    unique_emails.append(email)
                                    seen.add(email_lower)
                                else:
                                    vcard.remove(email)
                    
                    logger.info(f"Applied AI fix: {insight.issue_type} -> {insight.suggested_value}")
                
                except Exception as e:
                    logger.error(f"Failed to apply AI fix {insight.issue_type}: {e}")
        
        return vcards
    
    def _generate_intelligence_report(self, standard_result: Dict[str, Any], 
                                    ai_analyses: List, high_confidence_fixes: List[Dict[str, Any]],
                                    review_queue: List[Dict[str, Any]], final_file: str) -> Dict[str, Any]:
        """Generate comprehensive intelligence report"""
        
        # Calculate AI statistics
        total_contacts = len(ai_analyses)
        contacts_with_issues = len([a for a in ai_analyses if a.insights])
        total_insights = sum(len(a.insights) for a in ai_analyses)
        high_conf_insights = sum(len(f['fixes']) for f in high_confidence_fixes)
        review_needed = len(review_queue)
        
        # Quality score distribution
        quality_scores = [a.overall_quality_score for a in ai_analyses]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Issue type breakdown
        issue_types = {}
        for analysis in ai_analyses:
            for insight in analysis.insights:
                issue_types[insight.issue_type] = issue_types.get(insight.issue_type, 0) + 1
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'input_file': standard_result['input_file'],
            'final_file': final_file,
            'status': 'completed',
            
            # Standard workflow results
            'standard_workflow': {
                'initial_errors': standard_result['initial_validation']['error_count'],
                'final_valid': standard_result['final_valid'],
                'vcards_processed': standard_result['vcards_parsed']
            },
            
            # AI analysis results
            'ai_analysis': {
                'total_contacts': total_contacts,
                'contacts_with_issues': contacts_with_issues,
                'total_insights': total_insights,
                'average_quality_score': round(avg_quality, 3),
                'issue_type_breakdown': issue_types
            },
            
            # AI improvements
            'ai_improvements': {
                'high_confidence_fixes_applied': high_conf_insights,
                'contacts_improved_automatically': len(high_confidence_fixes),
                'contacts_needing_review': review_needed
            },
            
            # Review queue for human attention
            'review_queue': review_queue[:10],  # First 10 for preview
            'total_review_items': len(review_queue),
            
            # Quality improvement summary
            'improvement_summary': self._generate_improvement_summary(ai_analyses, high_confidence_fixes)
        }
        
        return report
    
    def _generate_improvement_summary(self, ai_analyses: List, applied_fixes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of potential and applied improvements"""
        
        potential_improvements = {
            'name_quality': 0,
            'email_cleanup': 0,
            'data_consistency': 0,
            'duplicate_removal': 0
        }
        
        applied_improvements = {
            'name_quality': 0,
            'email_cleanup': 0,
            'data_consistency': 0,
            'duplicate_removal': 0
        }
        
        # Count potential improvements
        for analysis in ai_analyses:
            for insight in analysis.insights:
                if insight.issue_type in ['email_derived_name', 'improper_case', 'numbers_in_name']:
                    potential_improvements['name_quality'] += 1
                elif insight.issue_type == 'duplicate_emails':
                    potential_improvements['email_cleanup'] += 1
        
        # Count applied improvements
        for fix_group in applied_fixes:
            for insight in fix_group['fixes']:
                if insight.issue_type in ['email_derived_name', 'improper_case', 'numbers_in_name']:
                    applied_improvements['name_quality'] += 1
                elif insight.issue_type == 'duplicate_emails':
                    applied_improvements['email_cleanup'] += 1
        
        return {
            'potential': potential_improvements,
            'applied': applied_improvements,
            'improvement_rate': {
                category: applied_improvements[category] / max(potential_improvements[category], 1)
                for category in potential_improvements
            }
        }


def process_contacts_intelligently(filepath: str, output_dir: str = None) -> Dict[str, Any]:
    """
    Convenience function to process contacts with full AI intelligence.
    
    This is the main entry point for intelligent contact processing.
    """
    if output_dir is None:
        output_dir = os.path.dirname(filepath)
    
    workflow = IntelligentContactWorkflow(auto_apply_ai_fixes=True)
    result = workflow.process_file_with_intelligence(filepath)
    
    # Save detailed report
    report_file = os.path.join(output_dir, f'intelligence_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    with open(report_file, 'w') as f:
        # Clean result for JSON serialization
        clean_result = {}
        for key, value in result.items():
            if key != 'review_queue':  # Skip complex objects
                clean_result[key] = value
        json.dump(clean_result, f, indent=2)
    
    result['report_file'] = report_file
    return result


if __name__ == "__main__":
    # Test with a sample file
    test_file = "Imports/Sara_Export_Sara A. Kerner and 3.074 others.vcf"
    
    if os.path.exists(test_file):
        print("Intelligent Contact Processing Demo")
        print("=" * 60)
        
        result = process_contacts_intelligently(test_file)
        
        print(f"\nProcessing Results:")
        print(f"Status: {result['status']}")
        print(f"Contacts analyzed: {result['ai_analysis']['total_contacts']}")
        print(f"Issues detected: {result['ai_analysis']['total_insights']}")
        print(f"Auto-fixes applied: {result['ai_improvements']['high_confidence_fixes_applied']}")
        print(f"Contacts needing review: {result['ai_improvements']['contacts_needing_review']}")
        print(f"Average quality score: {result['ai_analysis']['average_quality_score']}")
        
        print(f"\nIssue types found:")
        for issue_type, count in result['ai_analysis']['issue_type_breakdown'].items():
            print(f"  {issue_type}: {count}")
        
        print(f"\nReport saved to: {result['report_file']}")
    else:
        print(f"Test file not found: {test_file}")
        print("Please provide a valid vCard file path")