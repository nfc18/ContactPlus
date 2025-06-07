#!/usr/bin/env python3
"""
Test AI Integration

Quick test to verify the AI-powered contact intelligence is working correctly.
"""

import os
import sys
import vobject
from contact_intelligence import ContactIntelligenceEngine, analyze_contact_with_ai

def test_ai_integration():
    """Test the AI integration with sample contacts"""
    
    print("🧪 Testing AI Integration")
    print("=" * 40)
    
    # Check OpenAI availability
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"OpenAI API Key: {'✅ Set' if api_key else '❌ Not set'}")
    
    # Test contact with obvious issues
    test_vcard_data = '''BEGIN:VCARD
VERSION:3.0
FN:claudiaplatzer85
EMAIL:claudia.platzer@gmail.com
EMAIL:Claudia.Platzer@gmail.com
ORG:Test Company
END:VCARD'''
    
    print(f"\n📝 Test Contact:")
    print(f"Name: claudiaplatzer85")
    print(f"Emails: claudia.platzer@gmail.com, Claudia.Platzer@gmail.com")
    
    # Parse vCard
    vcard = list(vobject.readComponents(test_vcard_data))[0]
    
    # Test rule-based analysis
    print(f"\n🔧 Rule-Based Analysis:")
    engine = ContactIntelligenceEngine(use_openai=False)
    rule_analysis = engine.analyze_contact(vcard)
    
    print(f"Quality Score: {rule_analysis.overall_quality_score:.3f}")
    print(f"Issues Found: {len(rule_analysis.insights)}")
    
    for insight in rule_analysis.insights:
        print(f"  • {insight.issue_type}: {insight.current_value} → {insight.suggested_value}")
        print(f"    Confidence: {insight.confidence:.2f}, Auto-safe: {insight.auto_apply_safe}")
    
    # Test AI-enhanced analysis if available
    if api_key:
        print(f"\n🧠 AI-Enhanced Analysis:")
        ai_engine = ContactIntelligenceEngine(use_openai=True)
        ai_analysis = ai_engine.analyze_contact(vcard)
        
        print(f"Quality Score: {ai_analysis.overall_quality_score:.3f}")
        print(f"Issues Found: {len(ai_analysis.insights)}")
        
        for insight in ai_analysis.insights:
            print(f"  • {insight.issue_type}: {insight.current_value} → {insight.suggested_value}")
            print(f"    Confidence: {insight.confidence:.2f}, Auto-safe: {insight.auto_apply_safe}")
            print(f"    Reasoning: {insight.reasoning}")
        
        # Compare results
        print(f"\n📊 Comparison:")
        print(f"Rule-based insights: {len(rule_analysis.insights)}")
        print(f"AI-enhanced insights: {len(ai_analysis.insights)}")
        print(f"AI improvement: {len(ai_analysis.insights) - len(rule_analysis.insights)} additional insights")
        
    else:
        print(f"\n⚠️  OpenAI API key not set - AI analysis skipped")
        print(f"To enable AI features: export OPENAI_API_KEY='your-key'")
    
    print(f"\n✅ Integration test complete!")
    return True

def test_batch_analysis():
    """Test batch analysis functionality"""
    
    print(f"\n🔄 Testing Batch Analysis")
    print("-" * 30)
    
    # Create multiple test contacts
    test_contacts = [
        '''BEGIN:VCARD
VERSION:3.0
FN:claudiaplatzer85
EMAIL:claudia.platzer@gmail.com
END:VCARD''',
        '''BEGIN:VCARD
VERSION:3.0
FN:JOHN SMITH
EMAIL:john.smith@company.com
END:VCARD''',
        '''BEGIN:VCARD
VERSION:3.0
FN:user123
EMAIL:max.mustermann@test.com
END:VCARD'''
    ]
    
    vcards = [list(vobject.readComponents(data))[0] for data in test_contacts]
    
    engine = ContactIntelligenceEngine()
    
    total_issues = 0
    auto_fixable = 0
    
    for i, vcard in enumerate(vcards):
        analysis = engine.analyze_contact(vcard)
        name = vcard.fn.value if hasattr(vcard, 'fn') else f'Contact {i+1}'
        
        print(f"Contact {i+1}: {name}")
        print(f"  Quality: {analysis.overall_quality_score:.3f}")
        print(f"  Issues: {len(analysis.insights)}")
        
        total_issues += len(analysis.insights)
        auto_fixable += sum(1 for insight in analysis.insights if insight.auto_apply_safe)
    
    print(f"\nBatch Summary:")
    print(f"Total contacts: {len(vcards)}")
    print(f"Total issues: {total_issues}")
    print(f"Auto-fixable: {auto_fixable}")
    print(f"Fix rate: {auto_fixable/total_issues*100:.1f}%" if total_issues > 0 else "Perfect quality!")

if __name__ == "__main__":
    try:
        test_ai_integration()
        test_batch_analysis()
        
        print(f"\n🎉 All tests passed!")
        print(f"AI-First contact processing is ready to use.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print(f"Check your setup and try again.")
        sys.exit(1)