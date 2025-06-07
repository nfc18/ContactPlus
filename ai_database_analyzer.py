#!/usr/bin/env python3
"""
AI Database Analyzer - Start Fresh with Intelligence

This analyzes your original 3 source databases with AI intelligence
to show you exactly what quality issues exist BEFORE merging.
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Any
import vobject
import json
from contact_intelligence import ContactIntelligenceEngine, analyze_contact_with_ai, get_high_confidence_fixes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AISourceDatabaseAnalyzer:
    """
    Analyzes the original source databases with AI intelligence
    to identify quality issues that should be fixed BEFORE merging.
    """
    
    def __init__(self):
        self.ai_engine = ContactIntelligenceEngine()
        self.source_databases = {
            'sara': 'Imports/Sara_Export_Sara A. Kerner and 3.074 others.vcf',
            'iphone_contacts': 'Imports/iPhone_Contacts_Contacts.vcf',
            'iphone_suggested': 'Imports/iPhone_Suggested_Suggested Contacts.vcf'
        }
    
    def analyze_all_source_databases(self) -> Dict[str, Any]:
        """
        Analyze all original source databases with AI intelligence.
        This shows you what you would have caught if AI was used first.
        """
        
        print("🧠 AI Analysis of Original Source Databases")
        print("=" * 60)
        print("Goal: Show quality issues that AI would catch BEFORE merging")
        print("=" * 60)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'analysis_purpose': 'Identify quality issues in source databases before merging',
            'databases': {}
        }
        
        total_contacts = 0
        total_issues = 0
        
        for db_name, db_path in self.source_databases.items():
            if not os.path.exists(db_path):
                print(f"❌ Database not found: {db_path}")
                continue
            
            print(f"\n📱 Analyzing {db_name.upper()} Database")
            print("-" * 40)
            
            analysis = self._analyze_single_database(db_name, db_path)
            results['databases'][db_name] = analysis
            
            total_contacts += analysis['contact_count']
            total_issues += analysis['total_issues']
            
            # Show summary
            print(f"Contacts: {analysis['contact_count']:,}")
            print(f"Quality Score: {analysis['average_quality']:.1%}")
            print(f"AI-Detectable Issues: {analysis['total_issues']}")
            print(f"Auto-fixable: {analysis['auto_fixable_issues']}")
            
            # Show top issues
            if analysis['issue_breakdown']:
                print("Top Issue Types:")
                for issue_type, count in list(analysis['issue_breakdown'].items())[:3]:
                    print(f"  • {issue_type}: {count}")
        
        # Overall summary
        print(f"\n🎯 OVERALL ANALYSIS")
        print("-" * 40)
        print(f"Total Contacts: {total_contacts:,}")
        print(f"Total AI-Detectable Issues: {total_issues}")
        print(f"Issue Rate: {total_issues/total_contacts:.1%}")
        
        results['summary'] = {
            'total_contacts': total_contacts,
            'total_issues': total_issues,
            'issue_rate': total_issues/total_contacts if total_contacts > 0 else 0,
            'conclusion': self._generate_conclusion(total_issues, total_contacts)
        }
        
        # Save detailed report
        report_file = f"data/SOURCE_DATABASE_AI_ANALYSIS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs('data', exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        results['report_file'] = report_file
        print(f"\nDetailed report saved: {report_file}")
        
        return results
    
    def _analyze_single_database(self, db_name: str, db_path: str) -> Dict[str, Any]:
        """Analyze a single database with AI intelligence"""
        
        # Load contacts
        with open(db_path, 'r', encoding='utf-8') as f:
            vcards = list(vobject.readComponents(f.read()))
        
        logger.info(f"Analyzing {len(vcards)} contacts in {db_name}")
        
        all_issues = []
        quality_scores = []
        auto_fixable_count = 0
        issue_breakdown = {}
        
        # Analyze each contact (sample first 500 for speed)
        sample_size = min(500, len(vcards))
        
        for i, vcard in enumerate(vcards[:sample_size]):
            try:
                analysis = analyze_contact_with_ai(vcard)
                quality_scores.append(analysis.overall_quality_score)
                
                for insight in analysis.insights:
                    all_issues.append({
                        'contact_index': i,
                        'contact_name': vcard.fn.value if hasattr(vcard, 'fn') else f'Contact_{i}',
                        'issue_type': insight.issue_type,
                        'current_value': insight.current_value,
                        'suggested_value': insight.suggested_value,
                        'confidence': insight.confidence,
                        'auto_apply_safe': insight.auto_apply_safe
                    })
                    
                    # Count by type
                    issue_type = insight.issue_type
                    issue_breakdown[issue_type] = issue_breakdown.get(issue_type, 0) + 1
                    
                    if insight.auto_apply_safe and insight.confidence >= 0.90:
                        auto_fixable_count += 1
                
            except Exception as e:
                logger.error(f"Error analyzing contact {i}: {e}")
        
        # Calculate statistics
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Find interesting examples
        examples = self._find_interesting_examples(all_issues)
        
        return {
            'database_name': db_name,
            'database_path': db_path,
            'contact_count': len(vcards),
            'sample_analyzed': sample_size,
            'average_quality': avg_quality,
            'total_issues': len(all_issues),
            'auto_fixable_issues': auto_fixable_count,
            'issue_breakdown': dict(sorted(issue_breakdown.items(), key=lambda x: x[1], reverse=True)),
            'interesting_examples': examples,
            'quality_grade': self._quality_grade(avg_quality)
        }
    
    def _find_interesting_examples(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find the most interesting examples to show the user"""
        
        # Prioritize email-derived names (like Claudia Platzer case)
        email_derived = [i for i in issues if i['issue_type'] == 'email_derived_name']
        
        # High-confidence issues
        high_confidence = [i for i in issues if i['confidence'] >= 0.90]
        
        # Combine and deduplicate
        interesting = []
        seen_names = set()
        
        # Start with email-derived (highest priority)
        for issue in email_derived[:5]:
            if issue['contact_name'] not in seen_names:
                interesting.append(issue)
                seen_names.add(issue['contact_name'])
        
        # Add other high-confidence issues
        for issue in high_confidence[:10]:
            if len(interesting) >= 10:
                break
            if issue['contact_name'] not in seen_names:
                interesting.append(issue)
                seen_names.add(issue['contact_name'])
        
        return interesting
    
    def _quality_grade(self, score: float) -> str:
        """Convert quality score to letter grade"""
        if score >= 0.95: return "A+"
        elif score >= 0.90: return "A"
        elif score >= 0.85: return "B+"
        elif score >= 0.80: return "B"
        elif score >= 0.75: return "C+"
        elif score >= 0.70: return "C"
        else: return "D"
    
    def _generate_conclusion(self, total_issues: int, total_contacts: int) -> str:
        """Generate conclusion about whether AI processing is needed"""
        
        issue_rate = total_issues / total_contacts if total_contacts > 0 else 0
        
        if issue_rate > 0.15:
            return "HIGH_PRIORITY: Significant quality issues detected - AI processing essential before merging"
        elif issue_rate > 0.05:
            return "RECOMMENDED: Moderate quality issues - AI processing would prevent merge problems"
        else:
            return "OPTIONAL: Good quality overall - minimal AI processing needed"
    
    def show_claudia_platzer_equivalents(self, results: Dict[str, Any]) -> None:
        """Show examples similar to the Claudia Platzer case across all databases"""
        
        print(f"\n🔍 'Claudia Platzer' Equivalents Found:")
        print("-" * 50)
        print("These are email-derived usernames that AI would fix:")
        
        found_examples = False
        
        for db_name, db_analysis in results['databases'].items():
            examples = db_analysis.get('interesting_examples', [])
            email_derived = [e for e in examples if e['issue_type'] == 'email_derived_name']
            
            if email_derived:
                found_examples = True
                print(f"\n{db_name.upper()}:")
                for example in email_derived:
                    print(f"  ❌ {example['current_value']}")
                    print(f"  ✅ AI suggests: {example['suggested_value']} ({example['confidence']:.0%} confident)")
                    print()
        
        if not found_examples:
            print("No obvious email-derived usernames found in sample.")
            print("(Note: This analyzes only first 500 contacts per database)")


def analyze_source_databases_with_ai():
    """
    Main function: Analyze original source databases to show what
    AI would have caught before merging.
    """
    
    analyzer = AISourceDatabaseAnalyzer()
    results = analyzer.analyze_all_source_databases()
    
    # Show Claudia Platzer equivalents
    analyzer.show_claudia_platzer_equivalents(results)
    
    # Show recommendation
    print(f"\n💡 RECOMMENDATION:")
    print("-" * 30)
    print(results['summary']['conclusion'])
    
    if results['summary']['issue_rate'] > 0.05:
        print(f"\n🚀 NEXT STEPS:")
        print("1. Use ai_first_pipeline.py to clean each database individually")
        print("2. Apply AI fixes to prevent quality issues")  
        print("3. Then proceed with intelligent merging")
        print("4. This prevents the 'Claudia Platzer' problem entirely!")
    
    return results


if __name__ == "__main__":
    try:
        result = analyze_source_databases_with_ai()
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        print(f"Error: {e}")