#!/usr/bin/env python3
"""
AI-First Contact Processing Demo

This demonstrates the AI-powered approach to contact processing that solves
the "claudiaplatzer85" problem by applying intelligence BEFORE merging.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Any
import vobject

# Import our AI modules
from contact_intelligence import ContactIntelligenceEngine, analyze_contact_with_ai
from ai_first_pipeline import AIFirstPipeline, start_fresh_with_ai

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demo_ai_contact_analysis():
    """Demonstrate AI analysis on problematic contacts"""
    
    print("🧠 AI-First Contact Processing Demo")
    print("=" * 60)
    print("Solving the 'claudiaplatzer85' problem with AI intelligence")
    print("=" * 60)
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY not set - will use rule-based analysis only")
        print("To enable full AI features: export OPENAI_API_KEY='your-key'")
        print()
    
    # Create test contacts with typical issues
    test_contacts = [
        {
            'name': 'Demo: Email-derived name',
            'vcard_data': '''BEGIN:VCARD
VERSION:3.0
FN:claudiaplatzer85
EMAIL:claudia.platzer@gmail.com
ORG:Example Corp
END:VCARD'''
        },
        {
            'name': 'Demo: All caps name',
            'vcard_data': '''BEGIN:VCARD
VERSION:3.0
FN:CHRISTIAN MÜLLER
EMAIL:christian.mueller@company.at
ORG:Austrian Company GmbH
END:VCARD'''
        },
        {
            'name': 'Demo: Username pattern',
            'vcard_data': '''BEGIN:VCARD
VERSION:3.0
FN:user123
EMAIL:max.mustermann@example.com
TEL:+43123456789
END:VCARD'''
        },
        {
            'name': 'Demo: Professional titles',
            'vcard_data': '''BEGIN:VCARD
VERSION:3.0
FN:Dr. prof. werner schneider
EMAIL:w.schneider@university.ac.at
ORG:University of Vienna
END:VCARD'''
        }
    ]
    
    # Initialize AI engine
    engine = ContactIntelligenceEngine(use_openai=True)
    
    print(f"🔧 AI Engine Status:")
    print(f"   OpenAI Available: {engine.use_openai}")
    print(f"   Model: {engine.model}")
    print()
    
    # Analyze each test contact
    for i, test_contact in enumerate(test_contacts, 1):
        print(f"📊 Test {i}: {test_contact['name']}")
        print("-" * 40)
        
        # Parse vCard
        vcard = list(vobject.readComponents(test_contact['vcard_data']))[0]
        original_name = vcard.fn.value if hasattr(vcard, 'fn') else 'No name'
        
        print(f"Original Name: {original_name}")
        
        # AI Analysis
        analysis = engine.analyze_contact(vcard)
        
        print(f"Quality Score: {analysis.overall_quality_score:.3f}")
        print(f"Name Quality: {analysis.name_quality_score:.3f}")
        print(f"Improvement Potential: {analysis.improvement_potential}")
        
        if analysis.insights:
            print(f"\n🔍 AI Insights ({len(analysis.insights)} found):")
            for insight in analysis.insights:
                print(f"   • {insight.issue_type}")
                print(f"     Current: {insight.current_value}")
                print(f"     Suggested: {insight.suggested_value}")
                print(f"     Confidence: {insight.confidence:.2f}")
                print(f"     Safe to auto-apply: {insight.auto_apply_safe}")
                print(f"     Reasoning: {insight.reasoning}")
                print()
        else:
            print("   ✅ No issues found - contact looks good!")
        
        print("=" * 60)
        print()

def demo_database_preview():
    """Demo the database preview functionality"""
    
    print("📊 AI Database Quality Preview")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = AIFirstPipeline()
    
    # Preview all source databases
    try:
        preview_results = pipeline.preview_all_databases()
        
        print("📈 Source Database Quality Analysis:")
        print()
        
        for source_name, analysis in preview_results['database_previews'].items():
            print(f"🗂️  {source_name.upper()} DATABASE")
            print(f"   Total Contacts: {analysis['total_contacts']:,}")
            print(f"   Quality Score: {analysis['average_quality_score']:.3f} ({analysis['quality_grade']})")
            print(f"   Sample Size: {analysis['sample_size']} contacts analyzed")
            
            if analysis['issues_by_type']:
                print(f"   Top Issues:")
                for issue_type, count in list(analysis['issues_by_type'].items())[:3]:
                    print(f"     • {issue_type}: {count} occurrences")
            
            if analysis['sample_issues']:
                print(f"   Sample Problem:")
                issue = analysis['sample_issues'][0]
                print(f"     Contact: {issue['contact']}")
                print(f"     Issue: {issue['issue']}")
                print(f"     Current: {issue['current']}")
                print(f"     AI Suggestion: {issue['suggested']}")
                print(f"     Confidence: {issue['confidence']:.2f}")
            
            print()
        
        print(f"🎯 Recommendation: {preview_results['recommendation']}")
        
        return preview_results
        
    except Exception as e:
        print(f"❌ Preview failed: {e}")
        logger.error(f"Database preview error: {e}")
        return None

def demo_ai_cleaning_preview():
    """Demo what AI cleaning would do without actually modifying files"""
    
    print("🔧 AI Cleaning Preview (No Files Modified)")
    print("=" * 60)
    
    # Load a sample from Sara's database
    sara_file = "Imports/Sara_Export_Sara A. Kerner and 3.074 others.vcf"
    
    if not os.path.exists(sara_file):
        print(f"❌ Test file not found: {sara_file}")
        print("Please ensure the source databases are in the Imports/ directory")
        return
    
    print(f"📖 Loading sample from: {sara_file}")
    
    try:
        with open(sara_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        vcards = list(vobject.readComponents(content))
        sample_size = min(10, len(vcards))
        sample_contacts = vcards[:sample_size]
        
        print(f"🔍 Analyzing {sample_size} sample contacts...")
        
        engine = ContactIntelligenceEngine(use_openai=True)
        
        total_issues = 0
        auto_fixable = 0
        quality_scores = []
        
        for i, vcard in enumerate(sample_contacts):
            try:
                analysis = engine.analyze_contact(vcard)
                quality_scores.append(analysis.overall_quality_score)
                
                contact_name = vcard.fn.value if hasattr(vcard, 'fn') else f'Contact_{i}'
                
                if analysis.insights:
                    total_issues += len(analysis.insights)
                    contact_auto_fixable = sum(1 for insight in analysis.insights if insight.auto_apply_safe)
                    auto_fixable += contact_auto_fixable
                    
                    print(f"\n📱 {contact_name}")
                    print(f"   Quality: {analysis.overall_quality_score:.3f}")
                    print(f"   Issues: {len(analysis.insights)} found, {contact_auto_fixable} auto-fixable")
                    
                    # Show top issue
                    if analysis.insights:
                        top_issue = analysis.insights[0]
                        print(f"   Top Issue: {top_issue.issue_type}")
                        print(f"   Fix: {top_issue.current_value} → {top_issue.suggested_value}")
                        print(f"   Confidence: {top_issue.confidence:.2f}")
                
            except Exception as e:
                logger.error(f"Analysis failed for contact {i}: {e}")
        
        # Summary
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        print(f"\n📊 SAMPLE ANALYSIS SUMMARY")
        print(f"   Average Quality Score: {avg_quality:.3f}")
        print(f"   Total Issues Found: {total_issues}")
        print(f"   Auto-fixable Issues: {auto_fixable}")
        print(f"   Improvement Potential: {auto_fixable}/{total_issues} issues can be auto-fixed")
        
        # Projection to full database
        total_contacts = len(vcards)
        projected_issues = int(total_issues * total_contacts / sample_size)
        projected_fixes = int(auto_fixable * total_contacts / sample_size)
        
        print(f"\n🔮 FULL DATABASE PROJECTION ({total_contacts:,} contacts)")
        print(f"   Estimated Total Issues: ~{projected_issues:,}")
        print(f"   Estimated Auto-fixes: ~{projected_fixes:,}")
        print(f"   Quality Improvement: {projected_fixes/projected_issues*100:.1f}% auto-fixable")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        logger.error(f"Sample analysis error: {e}")

def main():
    """Main demo function"""
    
    while True:
        print("\n🧠 AI-First Contact Processing Demo")
        print("=" * 50)
        print("1. Demo AI Contact Analysis (test cases)")
        print("2. Preview Source Database Quality")
        print("3. Demo AI Cleaning Preview (sample)")
        print("4. Run Full AI-First Pipeline (PREVIEW ONLY)")
        print("5. Exit")
        print()
        
        choice = input("Select option (1-5): ").strip()
        
        if choice == '1':
            demo_ai_contact_analysis()
        elif choice == '2':
            demo_database_preview()
        elif choice == '3':
            demo_ai_cleaning_preview()
        elif choice == '4':
            print("\n🚀 Full AI-First Pipeline Preview")
            print("This would process all source databases with AI intelligence")
            print("(Not implemented in demo - would require processing ~7K contacts)")
            print("Use the actual AI-First pipeline for full processing.")
        elif choice == '5':
            print("👋 Demo complete!")
            break
        else:
            print("❌ Invalid choice. Please select 1-5.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()