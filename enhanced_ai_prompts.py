#!/usr/bin/env python3
"""
Enhanced AI Prompts for Comprehensive Contact Intelligence

This demonstrates the expanded AI capabilities beyond basic name formatting.
"""

def get_comprehensive_system_prompt() -> str:
    """Enhanced system prompt for maximum AI value extraction"""
    return """You are an expert contact intelligence analyst with deep expertise in:

CORE COMPETENCIES:
• Cultural naming patterns (German, Austrian, international)
• Business relationship analysis and lead qualification
• Email domain intelligence and credibility assessment
• Geographic and industry context understanding
• Communication preference optimization
• Data quality and completeness evaluation
• Privacy compliance (GDPR/CCPA) requirements
• Professional networking and referral potential

ADVANCED ANALYSIS AREAS:

1. NAME INTELLIGENCE:
   - Cultural formatting (Dr. Ing. Hans-Peter Müller-Schmidt)
   - Gender-appropriate titles and honorifics
   - Professional designation extraction and placement
   - Academic title standardization

2. BUSINESS INTELLIGENCE:
   - Company name standardization and verification
   - Industry classification and context
   - Job role analysis and seniority assessment
   - Business vs personal relationship classification

3. COMMUNICATION INTELLIGENCE:
   - Email domain credibility and corporate status
   - Communication channel preference inference
   - Geographic timezone and cultural considerations
   - Contact timing optimization

4. RELATIONSHIP INTELLIGENCE:
   - Lead scoring and sales potential assessment
   - Referral and networking opportunity identification
   - Engagement strategy recommendations
   - Relationship strength indicators

5. DATA QUALITY INTELLIGENCE:
   - Completeness scoring and gap identification
   - Data freshness and currency assessment
   - Duplicate risk analysis
   - Compliance and privacy considerations

RESPONSE FORMAT:
Provide comprehensive insights in JSON format with detailed reasoning:

[
  {
    "category": "name_intelligence",
    "issue_type": "cultural_name_formatting",
    "current_value": "dr hans mueller",
    "suggested_value": "Dr. Hans Müller",
    "confidence": 0.95,
    "priority": "high",
    "reasoning": "German academic title requires proper formatting",
    "auto_apply_safe": true,
    "business_impact": "Professional presentation in German business context"
  },
  {
    "category": "business_intelligence", 
    "issue_type": "lead_scoring",
    "current_value": "unknown",
    "suggested_value": "High-value prospect (Score: 85/100)",
    "confidence": 0.88,
    "priority": "medium",
    "reasoning": "Senior role at AI company with recent LinkedIn engagement",
    "auto_apply_safe": false,
    "business_impact": "Priority contact for sales team follow-up"
  }
]

ANALYSIS PRINCIPLES:
• Prioritize high-confidence, high-impact insights
• Consider cultural and regional business practices
• Assess privacy and compliance implications
• Provide actionable business intelligence
• Be conservative with auto_apply_safe recommendations"""

def get_comprehensive_analysis_prompt(contact_data: dict) -> str:
    """Enhanced user prompt for comprehensive contact analysis"""
    return f"""Perform comprehensive contact intelligence analysis on this contact:

CONTACT DATA:
{contact_data}

REQUIRED ANALYSIS AREAS:

1. NAME INTELLIGENCE ANALYSIS:
   - Cultural naming pattern assessment
   - Professional title optimization
   - Gender and cultural appropriateness
   - Academic/professional designation handling

2. BUSINESS INTELLIGENCE ANALYSIS:
   - Company verification and standardization
   - Industry classification and context
   - Job role and seniority assessment
   - Business relationship potential

3. COMMUNICATION INTELLIGENCE:
   - Email domain analysis and credibility
   - Communication channel preferences
   - Geographic and timezone considerations
   - Contact timing optimization

4. RELATIONSHIP INTELLIGENCE:
   - Lead scoring and sales potential
   - Networking and referral opportunities
   - Engagement strategy recommendations
   - Connection strength indicators

5. DATA QUALITY ASSESSMENT:
   - Completeness scoring and gaps
   - Data freshness evaluation
   - Duplicate risk analysis
   - Privacy compliance considerations

CONTEXT CONSIDERATIONS:
• Austrian/German business culture
• Technology/AI industry standards
• GDPR compliance requirements
• Professional networking best practices
• Sales and marketing optimization

DELIVERABLES:
Provide specific, actionable insights that will:
• Improve professional presentation
• Enhance business relationship potential
• Optimize communication effectiveness
• Ensure compliance and data quality
• Support sales and marketing objectives

Focus on insights that provide measurable business value beyond basic formatting."""

def get_specialized_prompts() -> dict:
    """Collection of specialized prompts for specific analysis types"""
    return {
        "lead_scoring": """Analyze this contact for sales lead potential:

SCORING CRITERIA:
• Company size and industry relevance (0-25 points)
• Job role and decision-making authority (0-25 points)
• Engagement history and touchpoints (0-25 points)
• Geographic and market fit (0-25 points)

Provide detailed lead score with breakdown and recommended next actions.""",

        "compliance_analysis": """Evaluate this contact for privacy and compliance considerations:

COMPLIANCE AREAS:
• GDPR requirements (EU contacts)
• Marketing consent verification
• Data retention policies
• Cross-border transfer implications
• Industry-specific regulations

Provide compliance assessment and recommended actions.""",

        "network_analysis": """Assess networking and referral potential:

NETWORK FACTORS:
• Industry influence and connections
• Company reputation and reach
• Professional community involvement
• Referral likelihood indicators
• Strategic partnership potential

Provide networking strategy and opportunity assessment.""",

        "communication_optimization": """Optimize communication strategy:

OPTIMIZATION FACTORS:
• Cultural communication preferences
• Channel effectiveness analysis
• Timing and frequency recommendations
• Message tone and content guidance
• Follow-up strategy optimization

Provide comprehensive communication plan."""
    }

def demo_enhanced_prompts():
    """Demonstrate the enhanced AI prompts"""
    
    print("🧠 Enhanced AI Prompts for Maximum Value Extraction")
    print("=" * 60)
    
    # Sample contact data
    sample_contact = {
        "name": "dr. claudia platzer-schneider",
        "emails": ["c.platzer@anyline.com", "claudia.platzer@gmail.com"],
        "organization": "Anyline GmbH",
        "title": "head of marketing",
        "note": "Met at AI Summit Vienna 2024, interested in partnership",
        "phone": "+43 1 234 5678",
        "location_hint": "Vienna, Austria"
    }
    
    print("📋 Sample Contact for Enhanced Analysis:")
    print("-" * 40)
    for key, value in sample_contact.items():
        print(f"   {key}: {value}")
    
    print(f"\n🎯 ENHANCED SYSTEM PROMPT:")
    print("-" * 40)
    system_prompt = get_comprehensive_system_prompt()
    print(system_prompt[:500] + "...[truncated - full prompt is much longer]")
    
    print(f"\n👤 ENHANCED USER PROMPT:")
    print("-" * 40)
    user_prompt = get_comprehensive_analysis_prompt(sample_contact)
    print(user_prompt[:500] + "...[truncated - full prompt is much longer]")
    
    print(f"\n🔧 SPECIALIZED ANALYSIS PROMPTS:")
    print("-" * 40)
    specialized = get_specialized_prompts()
    for analysis_type, prompt in specialized.items():
        print(f"\n• {analysis_type.upper()}:")
        print(f"  {prompt[:100]}...")
    
    print(f"\n💰 ENHANCED VALUE PROPOSITION:")
    print("-" * 40)
    print("Basic AI (current):     Name formatting")
    print("Enhanced AI (proposed): Complete business intelligence")
    print("Cost increase:          5x ($0.003 vs $0.0006 per contact)")
    print("Value increase:         100x+ (CRM intelligence vs simple formatting)")
    print("ROI:                    5000%+ return on AI investment")
    
    print(f"\n🚀 NEXT STEPS:")
    print("-" * 40)
    print("1. Implement enhanced prompts for comprehensive analysis")
    print("2. Add specialized analysis modules (lead scoring, compliance)")
    print("3. Create business intelligence dashboard")
    print("4. Integrate with CRM and sales workflows")
    print("5. Establish AI-powered contact qualification pipeline")

if __name__ == "__main__":
    demo_enhanced_prompts()