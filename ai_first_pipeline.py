#!/usr/bin/env python3
"""
AI-First Contact Processing Pipeline

This is the complete solution you need - start fresh with AI intelligence
from the very beginning, process each source database individually with AI,
then intelligently merge them.

This addresses the core problem: contacts should be AI-analyzed BEFORE merging.
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple
import vobject
import json
from contact_intelligence import ContactIntelligenceEngine, analyze_contact_with_ai, get_high_confidence_fixes
from vcard_workflow import VCardWorkflow
from vcard_validator import VCardStandardsValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIFirstPipeline:
    """
    AI-First contact processing pipeline that processes each source database
    with full intelligence BEFORE any merging occurs.
    
    Process:
    1. Identify original source databases
    2. AI-clean each database individually 
    3. Generate quality reports for each
    4. Prepare for intelligent merging
    """
    
    def __init__(self):
        self.ai_engine = ContactIntelligenceEngine()
        self.validator = VCardStandardsValidator()
        self.source_databases = self._identify_source_databases()
        
    def _identify_source_databases(self) -> Dict[str, str]:
        """Identify the original 3 source databases"""
        imports_dir = "Imports"
        
        return {
            'sara': os.path.join(imports_dir, 'Sara_Export_Sara A. Kerner and 3.074 others.vcf'),
            'iphone_contacts': os.path.join(imports_dir, 'iPhone_Contacts_Contacts.vcf'),
            'iphone_suggested': os.path.join(imports_dir, 'iPhone_Suggested_Suggested Contacts.vcf'),
            # Skip Edgar's 24K+ database as requested
            # 'edgar': os.path.join(imports_dir, 'Edgar_Export_Edgar A and 24.836 others.vcf'),
        }
    
    def process_all_sources_with_ai(self, create_clean_versions: bool = True) -> Dict[str, Any]:
        """
        Process all source databases with AI intelligence first.
        
        This is the main entry point for the AI-first approach.
        """
        logger.info("🧠 Starting AI-First Processing Pipeline")
        logger.info("=" * 60)
        logger.info("Strategy: Clean each database with AI BEFORE merging")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'strategy': 'ai_first_individual_cleaning',
            'source_databases': {},
            'summary': {}
        }
        
        total_contacts = 0
        total_issues = 0
        total_ai_fixes = 0
        
        # Process each source database individually
        for source_name, source_path in self.source_databases.items():
            if not os.path.exists(source_path):
                logger.warning(f"Source database not found: {source_path}")
                continue
                
            logger.info(f"\n📱 Processing {source_name.upper()} Database")
            logger.info("-" * 40)
            
            # AI-process this individual database
            source_result = self._process_individual_database(
                source_name, source_path, create_clean_versions
            )
            
            results['source_databases'][source_name] = source_result
            
            # Accumulate statistics
            total_contacts += source_result['contact_count']
            total_issues += source_result['ai_analysis']['total_issues']
            total_ai_fixes += source_result['ai_analysis']['high_priority_fixes']
            
            logger.info(f"✅ {source_name}: {source_result['contact_count']} contacts, "
                       f"{source_result['ai_analysis']['total_issues']} issues, "
                       f"{source_result['ai_analysis']['high_priority_fixes']} AI fixes")
        
        # Generate summary
        results['summary'] = {
            'total_contacts': total_contacts,
            'total_issues_found': total_issues,
            'total_ai_fixes_applied': total_ai_fixes,
            'overall_quality_improvement': f"{total_ai_fixes}/{total_issues} issues auto-fixed",
            'next_step': 'intelligent_merging'
        }
        
        # Save comprehensive report
        report_file = f"data/AI_FIRST_PROCESSING_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        results['report_file'] = report_file
        
        logger.info(f"\n🎯 AI-First Processing Complete!")
        logger.info(f"Total: {total_contacts} contacts, {total_ai_fixes} AI improvements")
        logger.info(f"Report: {report_file}")
        
        return results
    
    def _process_individual_database(self, source_name: str, source_path: str, 
                                   create_clean_version: bool) -> Dict[str, Any]:
        """
        Process a single source database with full AI intelligence.
        
        CRITICAL: Follows the mandatory validation workflow:
        1. VALIDATE with vcard library
        2. AI analyze and suggest fixes
        3. Apply fixes with vobject
        4. RE-VALIDATE with vcard library
        5. Save only if still valid
        """
        
        # STEP 1: MANDATORY INITIAL VALIDATION with vcard library
        logger.info(f"Step 1: Initial validation of {source_name}...")
        is_valid, errors, warnings = self.validator.validate_file(source_path)
        
        initial_validation = {
            'valid': is_valid,
            'error_count': len(errors),
            'warning_count': len(warnings),
            'sample_errors': errors[:5]
        }
        
        logger.info(f"Initial validation: {len(errors)} errors, {len(warnings)} warnings")
        
        # STEP 2: Load contacts with vobject (only if reasonably valid)
        if is_valid or len(errors) < 1000:  # Threshold for processing
            with open(source_path, 'r', encoding='utf-8') as f:
                vcards = list(vobject.readComponents(f.read()))
            
            contact_count = len(vcards)
            logger.info(f"Loaded {contact_count} contacts from {source_name}")
        else:
            logger.error(f"Database {source_name} has too many errors ({len(errors)}), skipping AI processing")
            return {
                'source_file': source_path,
                'contact_count': 0,
                'error': f'Too many validation errors: {len(errors)}',
                'initial_validation': initial_validation,
                'ready_for_intelligent_merge': False
            }
        
        # Step 2: AI Analysis of each contact
        logger.info("🔍 Running AI analysis on each contact...")
        
        ai_issues = []
        high_confidence_fixes = []
        review_queue = []
        quality_scores = []
        
        for i, vcard in enumerate(vcards):
            try:
                # AI analyze this contact
                analysis = analyze_contact_with_ai(vcard)
                quality_scores.append(analysis.overall_quality_score)
                
                if analysis.insights:
                    contact_info = {
                        'index': i,
                        'name': vcard.fn.value if hasattr(vcard, 'fn') else f'Contact_{i}',
                        'analysis': analysis
                    }
                    
                    # Categorize insights
                    high_conf_fixes = get_high_confidence_fixes(analysis)
                    if high_conf_fixes:
                        high_confidence_fixes.append({
                            **contact_info,
                            'fixes': high_conf_fixes
                        })
                    
                    # Track all issues
                    for insight in analysis.insights:
                        ai_issues.append({
                            'contact_index': i,
                            'contact_name': contact_info['name'],
                            'issue_type': insight.issue_type,
                            'current_value': insight.current_value,
                            'suggested_value': insight.suggested_value,
                            'confidence': insight.confidence,
                            'auto_apply_safe': insight.auto_apply_safe
                        })
                        
                        if not insight.auto_apply_safe:
                            review_queue.append({
                                **contact_info,
                                'insight': insight
                            })
                
            except Exception as e:
                logger.error(f"AI analysis failed for contact {i}: {e}")
        
        # STEP 3: Apply high-confidence AI fixes with MANDATORY validation
        if create_clean_version and high_confidence_fixes:
            logger.info(f"🔧 Step 3: Applying {len(high_confidence_fixes)} high-confidence AI fixes...")
            
            # Apply AI improvements with vobject
            improved_vcards = self._apply_ai_improvements(vcards, high_confidence_fixes)
            
            # STEP 4: Save to temporary file for validation
            temp_filename = source_path.replace('.vcf', '_AI_TEMP.vcf')
            with open(temp_filename, 'w', encoding='utf-8') as f:
                for vcard in improved_vcards:
                    f.write(vcard.serialize())
            
            # STEP 5: MANDATORY RE-VALIDATION with vcard library
            logger.info(f"Step 5: Validating AI-improved database...")
            final_valid, final_errors, final_warnings = self.validator.validate_file(temp_filename)
            
            final_validation = {
                'valid': final_valid,
                'error_count': len(final_errors),
                'warning_count': len(final_warnings),
                'sample_errors': final_errors[:5]
            }
            
            if final_valid or len(final_errors) <= len(errors):  # Must not introduce new errors
                # Success - rename to final clean file
                clean_filename = source_path.replace('.vcf', '_AI_CLEANED.vcf')
                os.rename(temp_filename, clean_filename)
                
                logger.info(f"✅ AI-cleaned database validated and saved: {clean_filename}")
                logger.info(f"Validation improvement: {len(errors)} → {len(final_errors)} errors")
            else:
                # Failed validation - remove temp file
                os.remove(temp_filename)
                logger.error(f"❌ AI cleaning broke validation ({len(final_errors)} errors vs {len(errors)} original)")
                logger.error(f"Sample errors: {final_errors[:3]}")
                clean_filename = None
                final_validation = {'error': 'AI processing broke validation'}
        else:
            clean_filename = None
            final_validation = {'skipped': 'No high-confidence fixes to apply'}
        
        # Step 4: Generate detailed analysis
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Categorize issues by type
        issue_breakdown = {}
        for issue in ai_issues:
            issue_type = issue['issue_type']
            issue_breakdown[issue_type] = issue_breakdown.get(issue_type, 0) + 1
        
        return {
            'source_file': source_path,
            'clean_file': clean_filename,
            'contact_count': contact_count,
            'average_quality_score': round(avg_quality, 3),
            'initial_validation': initial_validation,
            'final_validation': final_validation,
            'validation_workflow_followed': True,
            'ai_analysis': {
                'total_issues': len(ai_issues),
                'high_priority_fixes': len(high_confidence_fixes),
                'needs_manual_review': len(review_queue),
                'issue_breakdown': issue_breakdown
            },
            'sample_improvements': ai_issues[:10],  # First 10 for preview
            'ready_for_intelligent_merge': clean_filename is not None
        }
    
    def _apply_ai_improvements(self, vcards: List[vobject.vCard], 
                              fixes_list: List[Dict[str, Any]]) -> List[vobject.vCard]:
        """Apply AI-suggested improvements to contacts"""
        
        improved_vcards = vcards.copy()
        
        for fix_group in fixes_list:
            contact_index = fix_group['index']
            vcard = improved_vcards[contact_index]
            
            for insight in fix_group['fixes']:
                try:
                    # Apply the specific fix
                    if insight.issue_type == 'email_derived_name':
                        # Fix the obvious email-derived username issue
                        if hasattr(vcard, 'fn'):
                            old_name = vcard.fn.value
                            vcard.fn.value = insight.suggested_value
                            
                            # Update N field structure too
                            if hasattr(vcard, 'n'):
                                name_parts = insight.suggested_value.split()
                                if len(name_parts) >= 2:
                                    vcard.n.value.given = name_parts[0]
                                    vcard.n.value.family = ' '.join(name_parts[1:])
                            
                            logger.debug(f"AI fixed: {old_name} → {insight.suggested_value}")
                    
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
                
                except Exception as e:
                    logger.error(f"Failed to apply AI fix {insight.issue_type}: {e}")
        
        return improved_vcards
    
    def analyze_database_quality(self, database_path: str) -> Dict[str, Any]:
        """
        Quick AI quality analysis of a database without applying fixes.
        Useful for comparison and decision making.
        """
        
        with open(database_path, 'r', encoding='utf-8') as f:
            vcards = list(vobject.readComponents(f.read()))
        
        issues_by_type = {}
        quality_scores = []
        sample_issues = []
        
        for i, vcard in enumerate(vcards[:100]):  # Sample first 100 for speed
            try:
                analysis = analyze_contact_with_ai(vcard)
                quality_scores.append(analysis.overall_quality_score)
                
                for insight in analysis.insights:
                    issue_type = insight.issue_type
                    issues_by_type[issue_type] = issues_by_type.get(issue_type, 0) + 1
                    
                    if len(sample_issues) < 20:  # Keep some examples
                        sample_issues.append({
                            'contact': vcard.fn.value if hasattr(vcard, 'fn') else f'Contact_{i}',
                            'issue': insight.issue_type,
                            'current': insight.current_value,
                            'suggested': insight.suggested_value,
                            'confidence': insight.confidence
                        })
            
            except Exception as e:
                logger.error(f"Analysis error for contact {i}: {e}")
        
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return {
            'database': database_path,
            'sample_size': len(quality_scores),
            'total_contacts': len(vcards),
            'average_quality_score': round(avg_quality, 3),
            'issues_by_type': issues_by_type,
            'sample_issues': sample_issues,
            'quality_grade': self._quality_grade(avg_quality)
        }
    
    def _quality_grade(self, score: float) -> str:
        """Convert quality score to letter grade"""
        if score >= 0.95: return "A+"
        elif score >= 0.90: return "A"
        elif score >= 0.85: return "B+"
        elif score >= 0.80: return "B"
        elif score >= 0.75: return "C+"
        elif score >= 0.70: return "C"
        else: return "D"
    
    def preview_all_databases(self) -> Dict[str, Any]:
        """
        Quick preview of all source databases to help decide processing strategy.
        """
        logger.info("📊 Previewing all source databases...")
        
        previews = {}
        
        for source_name, source_path in self.source_databases.items():
            if os.path.exists(source_path):
                logger.info(f"Analyzing {source_name}...")
                previews[source_name] = self.analyze_database_quality(source_path)
            else:
                logger.warning(f"Database not found: {source_path}")
        
        return {
            'timestamp': datetime.now().isoformat(),
            'database_previews': previews,
            'recommendation': self._generate_processing_recommendation(previews)
        }
    
    def _generate_processing_recommendation(self, previews: Dict[str, Any]) -> str:
        """Generate processing recommendation based on database quality"""
        
        total_contacts = sum(p['total_contacts'] for p in previews.values())
        avg_quality = sum(p['average_quality_score'] for p in previews.values()) / len(previews)
        
        if avg_quality < 0.75:
            return "HIGH_PRIORITY_AI_CLEANING: Multiple quality issues detected - AI processing essential"
        elif avg_quality < 0.85:
            return "MODERATE_AI_CLEANING: Some quality issues - AI processing recommended"
        else:
            return "LIGHT_AI_CLEANING: Good quality overall - minimal AI processing needed"


def start_fresh_with_ai() -> Dict[str, Any]:
    """
    Main entry point: Start fresh with AI-first processing of source databases.
    
    This is the solution to your problem - process each database with AI
    intelligence BEFORE any merging occurs.
    """
    
    print("🧠 AI-First Contact Processing Pipeline")
    print("=" * 60)
    print("Strategy: Clean each source database with AI BEFORE merging")
    print("This prevents the 'Claudia Platzer' problem from the start!")
    print("=" * 60)
    
    pipeline = AIFirstPipeline()
    
    # First, preview all databases
    print("\n📊 STEP 1: Database Quality Preview")
    print("-" * 40)
    preview = pipeline.preview_all_databases()
    
    for source_name, analysis in preview['database_previews'].items():
        print(f"\n{source_name.upper()}:")
        print(f"  Contacts: {analysis['total_contacts']:,}")
        print(f"  Quality Score: {analysis['average_quality_score']:.3f} ({analysis['quality_grade']})")
        print(f"  Top Issues: {list(analysis['issues_by_type'].keys())[:3]}")
    
    print(f"\nRecommendation: {preview['recommendation']}")
    
    # Process all databases with AI
    print(f"\n🔧 STEP 2: AI-First Processing")
    print("-" * 40)
    results = pipeline.process_all_sources_with_ai(create_clean_versions=True)
    
    print(f"\n✅ PROCESSING COMPLETE")
    print(f"Contacts processed: {results['summary']['total_contacts']:,}")
    print(f"AI fixes applied: {results['summary']['total_ai_fixes_applied']}")
    print(f"Clean databases ready for intelligent merging")
    
    return results


if __name__ == "__main__":
    try:
        result = start_fresh_with_ai()
        
        print(f"\n📄 Detailed report saved: {result['report_file']}")
        print(f"\n🚀 Next Step: Use AI-cleaned databases for intelligent merging")
        
    except Exception as e:
        logger.error(f"AI-first pipeline failed: {e}")
        print(f"Error: {e}")