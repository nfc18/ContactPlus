#!/usr/bin/env python3
"""
Demo: Show Exact OpenAI API Prompts

This demonstrates the exact prompts sent to OpenAI API during AI-First processing.
"""

import os
import json
import vobject
from contact_intelligence import ContactIntelligenceEngine

def show_api_prompts():
    """Show the exact prompts sent to OpenAI API"""
    
    print("🤖 OpenAI API Prompts Used in AI-First Processing")
    print("=" * 60)
    
    # Create test contact
    test_vcard_data = '''BEGIN:VCARD
VERSION:3.0
FN:claudiaplatzer85
EMAIL:claudia.platzer@gmail.com
EMAIL:CLAUDIA.PLATZER@GMAIL.COM
ORG:Anyline GmbH
TEL:+43123456789
NOTE:Marketing contact from LinkedIn event
END:VCARD'''
    
    vcard = list(vobject.readComponents(test_vcard_data))[0]
    
    print("📋 Input Contact:")
    print(f"   Name: {vcard.fn.value}")
    print(f"   Emails: {[e.value for e in vcard.email_list]}")
    print(f"   Organization: {vcard.org.value}")
    print(f"   Note: {vcard.note.value}")
    
    # Create engine and extract data as AI would see it
    engine = ContactIntelligenceEngine(use_openai=True)
    contact_data = engine._extract_contact_data_for_ai(vcard)
    
    print(f"\n📊 Contact Data Sent to AI:")
    print("-" * 40)
    print(json.dumps(contact_data, indent=2))
    
    # Show system prompt
    system_prompt = engine._get_ai_system_prompt()
    print(f"\n🧠 SYSTEM PROMPT (Defines AI Role):")
    print("-" * 40)
    print(system_prompt)
    
    # First get rule-based insights
    rule_insights = engine._rule_based_analysis(vcard)
    
    # Show user prompt
    user_prompt = engine._create_ai_analysis_prompt(contact_data, rule_insights)
    print(f"\n👤 USER PROMPT (Specific Analysis Request):")
    print("-" * 40)
    print(user_prompt)
    
    # Show the complete API call structure
    print(f"\n🔗 COMPLETE OPENAI API CALL STRUCTURE:")
    print("-" * 40)
    api_call_example = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": system_prompt[:200] + "...[truncated for display]"
            },
            {
                "role": "user", 
                "content": user_prompt[:300] + "...[truncated for display]"
            }
        ],
        "temperature": 0.1,
        "max_tokens": 1000
    }
    
    print(json.dumps(api_call_example, indent=2))
    
    print(f"\n📏 API CALL STATISTICS:")
    print("-" * 40)
    system_tokens = len(system_prompt.split())
    user_tokens = len(user_prompt.split())
    total_input_tokens = system_tokens + user_tokens
    
    print(f"   System prompt tokens: ~{system_tokens}")
    print(f"   User prompt tokens: ~{user_tokens}")
    print(f"   Total input tokens: ~{total_input_tokens}")
    print(f"   Max response tokens: 1000")
    print(f"   Model: gpt-4o-mini")
    print(f"   Temperature: 0.1 (deterministic)")
    
    # Estimate cost
    # gpt-4o-mini pricing: $0.15/1M input tokens, $0.60/1M output tokens
    input_cost = (total_input_tokens / 1_000_000) * 0.15
    output_cost = (1000 / 1_000_000) * 0.60  # Assume full response
    total_cost = input_cost + output_cost
    
    print(f"\n💰 ESTIMATED COST PER CONTACT:")
    print("-" * 40)
    print(f"   Input cost: ${input_cost:.6f}")
    print(f"   Output cost: ${output_cost:.6f}")
    print(f"   Total per contact: ${total_cost:.6f}")
    print(f"   Cost for 1000 contacts: ${total_cost * 1000:.2f}")
    print(f"   Cost for 7000 contacts: ${total_cost * 7000:.2f}")

def show_actual_api_response():
    """Show what an actual API response looks like"""
    
    print(f"\n🎯 EXAMPLE API RESPONSE:")
    print("-" * 40)
    
    example_response = """[
  {
    "issue_type": "email_derived_name",
    "current_value": "claudiaplatzer85",
    "suggested_value": "Claudia Platzer",
    "confidence": 0.95,
    "reasoning": "Name appears to be email username - first name + last name + numbers",
    "auto_apply_safe": true
  },
  {
    "issue_type": "duplicate_emails",
    "current_value": "CLAUDIA.PLATZER@GMAIL.COM",
    "suggested_value": "Remove case duplicate",
    "confidence": 0.99,
    "reasoning": "Found case variation of same email address",
    "auto_apply_safe": true
  },
  {
    "issue_type": "business_classification",
    "current_value": "Unknown",
    "suggested_value": "Business",
    "confidence": 0.85,
    "reasoning": "Organization 'Anyline GmbH' indicates business contact",
    "auto_apply_safe": false
  }
]"""
    
    print(example_response)
    
    print(f"\n🔄 HOW AI RESPONSE IS PROCESSED:")
    print("-" * 40)
    print("1. Extract JSON array from AI response")
    print("2. Parse each insight object")
    print("3. Create IntelligenceInsight objects")
    print("4. Filter by confidence and safety")
    print("5. Apply only high-confidence, safe changes")
    print("6. Flag others for human review")

def show_privacy_and_data_handling():
    """Show how data is handled for privacy"""
    
    print(f"\n🔒 DATA PRIVACY & HANDLING:")
    print("-" * 40)
    print("✅ NO sensitive data sent to OpenAI:")
    print("   • Only name, email domains, organization names")
    print("   • NO full email addresses")
    print("   • NO phone numbers")
    print("   • NO addresses or personal details")
    print("   • Notes truncated to 200 characters max")
    print()
    print("✅ Data minimization:")
    print("   • Only quality-relevant fields analyzed")
    print("   • Caching prevents duplicate API calls")
    print("   • Temp files cleaned automatically")
    print()
    print("✅ API security:")
    print("   • HTTPS encrypted communication")
    print("   • No data stored by OpenAI (per their policy)")
    print("   • Rate limiting and error handling")

if __name__ == "__main__":
    try:
        if not os.getenv('OPENAI_API_KEY'):
            print("⚠️  Note: OPENAI_API_KEY not set - showing prompts only")
            print("Set API key to see actual API responses")
            print()
        
        show_api_prompts()
        show_actual_api_response()
        show_privacy_and_data_handling()
        
        print(f"\n✅ PROMPT TRANSPARENCY COMPLETE")
        print("You now see exactly what's sent to OpenAI API")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("Check your environment setup")