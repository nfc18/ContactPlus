#!/usr/bin/env python3
"""
AI-Powered Contact Intelligence Engine

This module combines rule-based intelligence with OpenAI API to provide
sophisticated contact analysis, name recognition, duplicate detection,
and merge conflict resolution.

The hybrid approach ensures reliability while leveraging AI for complex patterns.
"""

import os
import json
import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import vobject
from difflib import SequenceMatcher

# OpenAI integration for advanced analysis
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
    openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')) if os.getenv('OPENAI_API_KEY') else None
except ImportError:
    OPENAI_AVAILABLE = False
    openai_client = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfidenceLevel(Enum):
    """Confidence levels for AI analysis"""
    VERY_HIGH = 0.95  # Nearly certain, safe for auto-apply
    HIGH = 0.85       # Very confident, present to user as default
    MEDIUM = 0.70     # Somewhat confident, needs user review
    LOW = 0.50        # Uncertain, flag for careful review
    VERY_LOW = 0.30   # Likely incorrect, but worth mentioning


@dataclass
class IntelligenceInsight:
    """A single insight about a contact"""
    issue_type: str
    current_value: str
    suggested_value: str
    confidence: float
    reasoning: str
    evidence: List[str]
    auto_apply_safe: bool = False


@dataclass
class ContactAnalysis:
    """Complete AI analysis of a contact"""
    contact_id: str
    name_quality_score: float
    overall_quality_score: float
    insights: List[IntelligenceInsight]
    duplicate_candidates: List[Dict[str, Any]]
    risk_flags: List[str]
    improvement_potential: str


class ContactIntelligenceEngine:
    """
    Hybrid AI-powered contact analysis engine that combines:
    - Rule-based pattern recognition for fast, reliable detection
    - OpenAI API for complex contextual analysis
    - Learning from user feedback and patterns
    """
    
    def __init__(self, use_openai: bool = True, model: str = "gpt-4o-mini"):
        self.use_openai = use_openai and OPENAI_AVAILABLE and openai_client is not None
        self.model = model
        self.analysis_cache = {}  # Cache AI responses to save costs
        
        # Load rule-based patterns
        self.name_patterns = self._load_name_patterns()
        self.cultural_patterns = self._load_cultural_patterns()
        self.email_patterns = self._load_email_patterns()
        
        logger.info(f"Contact Intelligence Engine initialized (OpenAI: {self.use_openai})")
        
    def analyze_contact(self, vcard: vobject.vCard, context: Dict[str, Any] = None) -> ContactAnalysis:
        """
        Perform comprehensive intelligent analysis of a contact using hybrid approach.
        
        Args:
            vcard: The vCard object to analyze
            context: Additional context (other contacts, user preferences, etc.)
        """
        contact_id = self._extract_contact_id(vcard)
        
        # Check cache first
        cache_key = self._generate_cache_key(vcard)
        if cache_key in self.analysis_cache:
            logger.debug(f"Using cached analysis for contact {contact_id}")
            return self.analysis_cache[cache_key]
        
        logger.info(f"Analyzing contact {contact_id} with hybrid AI intelligence...")
        
        insights = []
        risk_flags = []
        
        # Phase 1: Rule-based analysis (fast, reliable)
        rule_insights = self._rule_based_analysis(vcard)
        insights.extend(rule_insights)
        
        # Phase 2: AI-enhanced analysis (for complex patterns)
        if self.use_openai and self._should_use_ai_analysis(vcard, rule_insights):
            ai_insights = self._ai_enhanced_analysis(vcard, rule_insights)
            insights.extend(ai_insights)
        
        # Calculate quality scores
        name_quality = self._calculate_name_quality(vcard)
        overall_quality = self._calculate_overall_quality(vcard, insights)
        
        # Identify potential duplicates (if context provided)
        duplicate_candidates = []
        if context and 'other_contacts' in context:
            duplicate_candidates = self._find_intelligent_duplicates(vcard, context['other_contacts'])
        
        # Assess improvement potential
        improvement_potential = self._assess_improvement_potential(insights)
        
        analysis = ContactAnalysis(
            contact_id=contact_id,
            name_quality_score=name_quality,
            overall_quality_score=overall_quality,
            insights=insights,
            duplicate_candidates=duplicate_candidates,
            risk_flags=risk_flags,
            improvement_potential=improvement_potential
        )
        
        # Cache the result
        self.analysis_cache[cache_key] = analysis
        
        return analysis
    
    def _generate_cache_key(self, vcard: vobject.vCard) -> str:
        """Generate cache key for contact analysis"""
        key_parts = []
        if hasattr(vcard, 'fn'):
            key_parts.append(vcard.fn.value)
        if hasattr(vcard, 'email_list'):
            key_parts.append(str([e.value for e in vcard.email_list]))
        return str(hash(''.join(key_parts)))
    
    def _should_use_ai_analysis(self, vcard: vobject.vCard, rule_insights: List[IntelligenceInsight]) -> bool:
        """Determine if AI analysis would be beneficial"""
        # Use AI for complex cases or when rule-based analysis is uncertain
        return (
            len(rule_insights) == 0 or  # No rule-based insights found
            any(insight.confidence < 0.8 for insight in rule_insights) or  # Low confidence
            self._has_complex_patterns(vcard)  # Complex patterns detected
        )
    
    def _has_complex_patterns(self, vcard: vobject.vCard) -> bool:
        """Check if contact has patterns that need AI analysis"""
        if hasattr(vcard, 'fn'):
            name = vcard.fn.value
            # Complex name patterns that benefit from AI
            return (
                len(name.split()) > 3 or  # Multiple names
                any(char in name for char in ['ü', 'ö', 'ä', 'ß']) or  # Non-ASCII chars
                'dr.' in name.lower() or 'prof.' in name.lower()  # Titles
            )
        return False
    
    def _rule_based_analysis(self, vcard: vobject.vCard) -> List[IntelligenceInsight]:
        """Fast rule-based analysis using existing patterns"""
        insights = []
        
        # Use existing methods
        insights.extend(self._analyze_name_intelligence(vcard))
        insights.extend(self._analyze_email_intelligence(vcard))
        insights.extend(self._analyze_phone_intelligence(vcard))
        
        return insights
    
    def _ai_enhanced_analysis(self, vcard: vobject.vCard, rule_insights: List[IntelligenceInsight]) -> List[IntelligenceInsight]:
        """AI-enhanced analysis using OpenAI API"""
        if not openai_client:
            logger.warning("OpenAI client not available, skipping AI analysis")
            return []
        
        try:
            # Extract contact data for AI
            contact_data = self._extract_contact_data_for_ai(vcard)
            
            # Create AI prompt
            prompt = self._create_ai_analysis_prompt(contact_data, rule_insights)
            
            # Call OpenAI API
            response = openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_ai_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content
            ai_insights = self._parse_ai_insights(ai_response)
            
            logger.info(f"AI analysis found {len(ai_insights)} additional insights")
            return ai_insights
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return []
    
    def _extract_contact_data_for_ai(self, vcard: vobject.vCard) -> Dict[str, Any]:
        """Extract contact data for AI analysis"""
        data = {}
        
        if hasattr(vcard, 'fn'):
            data['name'] = vcard.fn.value
        
        if hasattr(vcard, 'email_list'):
            data['emails'] = [email.value for email in vcard.email_list]
        
        if hasattr(vcard, 'org'):
            org_values = vcard.org.value
            if isinstance(org_values, list):
                data['organization'] = ' '.join(str(v) for v in org_values)
            else:
                data['organization'] = str(org_values)
        
        if hasattr(vcard, 'note'):
            data['note'] = vcard.note.value[:200]  # Limit note length
        
        return data
    
    def _get_ai_system_prompt(self) -> str:
        """System prompt for AI contact analysis"""
        return """You are an expert contact data analyst specializing in contact quality and intelligent name recognition.

Your expertise includes:
- Recognizing email-derived names (e.g., "claudiaplatzer85" should be "Claudia Platzer")
- Understanding cultural naming patterns (German, Austrian, international)
- Detecting business vs personal contacts
- Identifying data quality issues

For each contact, provide specific insights with confidence scores. Focus on issues that would significantly improve data quality.

Respond in JSON format with an array of insights:
[
  {
    "issue_type": "email_derived_name",
    "current_value": "claudiaplatzer85",
    "suggested_value": "Claudia Platzer",
    "confidence": 0.95,
    "reasoning": "Name appears to be email username - first name + last name + numbers",
    "auto_apply_safe": true
  }
]

Be conservative with auto_apply_safe - only for high-confidence, low-risk changes."""
    
    def _create_ai_analysis_prompt(self, contact_data: Dict[str, Any], rule_insights: List[IntelligenceInsight]) -> str:
        """Create prompt for AI analysis"""
        prompt = f"""Analyze this contact for data quality improvements:

CONTACT DATA:
{json.dumps(contact_data, indent=2)}

RULE-BASED INSIGHTS ALREADY FOUND:
{[f"{i.issue_type}: {i.current_value} -> {i.suggested_value}" for i in rule_insights]}

FOCUS AREAS:
1. Name quality - is this a real name or derived from email/username?
2. Cultural patterns - proper German/Austrian name formatting
3. Business vs personal classification
4. Any patterns the rule-based system might have missed

Provide specific, actionable insights that would improve contact quality."""
        
        return prompt
    
    def _parse_ai_insights(self, ai_response: str) -> List[IntelligenceInsight]:
        """Parse AI response into IntelligenceInsight objects"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', ai_response, re.DOTALL)
            if not json_match:
                logger.warning("No JSON array found in AI response")
                return []
            
            insights_data = json.loads(json_match.group())
            insights = []
            
            for data in insights_data:
                insight = IntelligenceInsight(
                    issue_type=data.get('issue_type', 'unknown'),
                    current_value=data.get('current_value', ''),
                    suggested_value=data.get('suggested_value', ''),
                    confidence=data.get('confidence', 0.5),
                    reasoning=data.get('reasoning', ''),
                    evidence=[data.get('reasoning', '')],  # Use reasoning as evidence
                    auto_apply_safe=data.get('auto_apply_safe', False)
                )
                insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to parse AI insights: {e}")
            return []
    
    def _analyze_name_intelligence(self, vcard: vobject.vCard) -> List[IntelligenceInsight]:
        """Intelligent name analysis that recognizes human-obvious patterns"""
        insights = []
        
        if not hasattr(vcard, 'fn'):
            return insights
            
        current_name = vcard.fn.value
        
        # Pattern 1: Email-derived names (like "claudiaplatzer85")
        email_derived_insight = self._detect_email_derived_name(vcard, current_name)
        if email_derived_insight:
            insights.append(email_derived_insight)
        
        # Pattern 2: All caps or all lowercase names
        case_insight = self._detect_case_issues(current_name)
        if case_insight:
            insights.append(case_insight)
        
        # Pattern 3: Missing spaces in compound names
        # (This would be implemented for detecting compound names without spaces)
        
        # Pattern 4: Numbers in names (usually not legitimate)
        number_insight = self._detect_numbers_in_names(current_name)
        if number_insight:
            insights.append(number_insight)
        
        # Pattern 5: Username-like patterns
        username_insight = self._detect_username_patterns(current_name)
        if username_insight:
            insights.append(username_insight)
        
        return insights
    
    def _detect_email_derived_name(self, vcard: vobject.vCard, name: str) -> Optional[IntelligenceInsight]:
        """Detect names that were obviously derived from email addresses"""
        
        if not hasattr(vcard, 'email_list') or not vcard.email_list:
            return None
        
        # Get email prefix (part before @)
        email = vcard.email_list[0].value
        if '@' not in email:
            return None
            
        email_prefix = email.split('@')[0].lower()
        name_lower = name.lower().replace(' ', '')
        
        # Check if name matches email prefix exactly or closely
        similarity = SequenceMatcher(None, name_lower, email_prefix).ratio()
        
        if similarity > 0.85:  # Very similar
            # Attempt to parse real name from email prefix
            suggested_name = self._parse_name_from_email_prefix(email_prefix)
            
            confidence = 0.95 if similarity > 0.95 else 0.85
            
            return IntelligenceInsight(
                issue_type="email_derived_name",
                current_value=name,
                suggested_value=suggested_name,
                confidence=confidence,
                reasoning=f"Name '{name}' matches email prefix '{email_prefix}' too closely to be a real name",
                evidence=[
                    f"Email: {email}",
                    f"Similarity score: {similarity:.2f}",
                    f"Pattern: username-like structure"
                ],
                auto_apply_safe=(confidence > 0.90)
            )
        
        return None
    
    def _parse_name_from_email_prefix(self, email_prefix: str) -> str:
        """Intelligently parse a real name from an email prefix"""
        
        # Remove numbers (like "85" in "claudiaplatzer85")
        clean_prefix = re.sub(r'\d+', '', email_prefix)
        
        # Split on common separators
        separators = ['.', '_', '-']
        parts = [clean_prefix]
        
        for sep in separators:
            if sep in clean_prefix:
                parts = clean_prefix.split(sep)
                break
        
        if len(parts) == 1:
            # Single part - try to identify first/last name boundary
            part = parts[0]
            
            # Look for common name patterns
            # This is where cultural/linguistic knowledge helps
            parsed = self._parse_compound_name(part)
            if parsed:
                return parsed
            
            # Fallback: capitalize first letter
            return part.capitalize()
        
        elif len(parts) == 2:
            # Two parts - likely first and last name
            first, last = parts
            return f"{first.capitalize()} {last.capitalize()}"
        
        else:
            # Multiple parts - capitalize each
            return ' '.join(part.capitalize() for part in parts if part)
    
    def _parse_compound_name(self, compound: str) -> Optional[str]:
        """Parse compound names like 'claudiaplatzer' into 'Claudia Platzer'"""
        
        # Look for common first names at the beginning
        common_first_names = {
            'claudia': 'Claudia',
            'michael': 'Michael',
            'christian': 'Christian',
            'johannes': 'Johannes',
            'alexander': 'Alexander',
            'sebastian': 'Sebastian',
            'maximilian': 'Maximilian',
            'andreas': 'Andreas',
            'thomas': 'Thomas',
            'stefan': 'Stefan',
            'daniel': 'Daniel',
            'martin': 'Martin',
            'markus': 'Markus',
            'peter': 'Peter',
            'david': 'David',
            'robert': 'Robert',
            'wolfgang': 'Wolfgang',
            'gerald': 'Gerald',
            'harald': 'Harald',
            'werner': 'Werner'
        }
        
        compound_lower = compound.lower()
        
        for first_name_lower, first_name_proper in common_first_names.items():
            if compound_lower.startswith(first_name_lower):
                remainder = compound[len(first_name_lower):]
                if len(remainder) > 2:  # Must have substantial last name part
                    last_name = remainder.capitalize()
                    return f"{first_name_proper} {last_name}"
        
        return None
    
    def _detect_case_issues(self, name: str) -> Optional[IntelligenceInsight]:
        """Detect improper capitalization"""
        
        if name.isupper():
            suggested = self._proper_case_name(name)
            return IntelligenceInsight(
                issue_type="improper_case",
                current_value=name,
                suggested_value=suggested,
                confidence=0.95,
                reasoning="Name is in ALL CAPS, should use proper case",
                evidence=["All characters are uppercase"],
                auto_apply_safe=True
            )
        
        elif name.islower():
            suggested = self._proper_case_name(name)
            return IntelligenceInsight(
                issue_type="improper_case",
                current_value=name,
                suggested_value=suggested,
                confidence=0.95,
                reasoning="Name is in all lowercase, should use proper case",
                evidence=["All characters are lowercase"],
                auto_apply_safe=True
            )
        
        return None
    
    def _detect_numbers_in_names(self, name: str) -> Optional[IntelligenceInsight]:
        """Detect inappropriate numbers in names"""
        
        if re.search(r'\d', name):
            suggested = re.sub(r'\d+', '', name).strip()
            suggested = re.sub(r'\s+', ' ', suggested)  # Clean up extra spaces
            
            if suggested != name:
                return IntelligenceInsight(
                    issue_type="numbers_in_name",
                    current_value=name,
                    suggested_value=suggested,
                    confidence=0.90,
                    reasoning="Names rarely contain numbers - likely from username/email",
                    evidence=[f"Found digits: {re.findall(r'\\d+', name)}"],
                    auto_apply_safe=True
                )
        
        return None
    
    def _detect_username_patterns(self, name: str) -> Optional[IntelligenceInsight]:
        """Detect username-like patterns in names"""
        
        username_indicators = [
            (r'^[a-z]+\d+$', "lowercase + numbers pattern"),
            (r'^[a-z]+[._-][a-z]+\d*$', "lowercase with separators"),
            (r'^\w+@', "contains @ symbol"),
            (r'^user\d+', "generic user pattern"),
            (r'^contact\d+', "generic contact pattern")
        ]
        
        for pattern, description in username_indicators:
            if re.match(pattern, name.lower()):
                return IntelligenceInsight(
                    issue_type="username_pattern",
                    current_value=name,
                    suggested_value="[Manual Review Required]",
                    confidence=0.80,
                    reasoning=f"Name follows {description} - likely not a real name",
                    evidence=[f"Matches pattern: {pattern}"],
                    auto_apply_safe=False
                )
        
        return None
    
    def _analyze_email_intelligence(self, vcard: vobject.vCard) -> List[IntelligenceInsight]:
        """Intelligent email analysis"""
        insights = []
        
        if not hasattr(vcard, 'email_list') or not vcard.email_list:
            return insights
        
        emails = [email.value for email in vcard.email_list]
        
        # Detect duplicate emails (case variations)
        duplicates = self._find_email_duplicates(emails)
        if duplicates:
            insights.append(IntelligenceInsight(
                issue_type="duplicate_emails",
                current_value=str(duplicates),
                suggested_value="Remove duplicates",
                confidence=0.95,
                reasoning="Found case variations of same email",
                evidence=[f"Duplicates: {duplicates}"],
                auto_apply_safe=True
            ))
        
        return insights
    
    def _analyze_phone_intelligence(self, vcard: vobject.vCard) -> List[IntelligenceInsight]:
        """Intelligent phone analysis"""
        # Implement phone number intelligence
        return []
    
    def _analyze_data_consistency(self, vcard: vobject.vCard) -> List[IntelligenceInsight]:
        """Analyze data consistency across fields"""
        # Implement cross-field consistency checks
        return []
    
    def _find_intelligent_duplicates(self, vcard: vobject.vCard, other_contacts: List[vobject.vCard]) -> List[Dict[str, Any]]:
        """Find potential duplicates using intelligent matching"""
        # Implement smart duplicate detection
        return []
    
    def _proper_case_name(self, name: str) -> str:
        """Convert name to proper case with intelligence"""
        # Reuse the logic from soft compliance but enhanced
        parts = name.split()
        fixed_parts = []
        
        for part in parts:
            if part.upper() in ['II', 'III', 'IV', 'JR', 'SR', 'PHD', 'MD']:
                fixed_parts.append(part.upper())
            elif part.lower() in ['de', 'van', 'von', 'der', 'la', 'di']:
                fixed_parts.append(part.lower())
            elif '-' in part:
                subparts = part.split('-')
                fixed_parts.append('-'.join(p.capitalize() for p in subparts))
            elif "'" in part:
                subparts = part.split("'")
                fixed_parts.append("'".join(p.capitalize() for p in subparts))
            else:
                fixed_parts.append(part.capitalize())
        
        return ' '.join(fixed_parts)
    
    def _find_email_duplicates(self, emails: List[str]) -> List[str]:
        """Find duplicate emails with different cases"""
        seen = set()
        duplicates = []
        
        for email in emails:
            email_lower = email.lower()
            if email_lower in seen:
                duplicates.append(email)
            else:
                seen.add(email_lower)
        
        return duplicates
    
    def _calculate_name_quality(self, vcard: vobject.vCard) -> float:
        """Calculate name quality score"""
        if not hasattr(vcard, 'fn'):
            return 0.0
        
        name = vcard.fn.value
        score = 1.0
        
        # Deduct for obvious issues
        if name.isupper() or name.islower():
            score -= 0.3
        
        if re.search(r'\d', name):
            score -= 0.4
        
        if len(name.split()) < 2:
            score -= 0.2
        
        return max(0.0, score)
    
    def _calculate_overall_quality(self, vcard: vobject.vCard, insights: List[IntelligenceInsight]) -> float:
        """Calculate overall contact quality score"""
        base_score = 1.0
        
        # Deduct based on insights
        for insight in insights:
            if insight.confidence > 0.8:
                base_score -= 0.1
        
        return max(0.0, base_score)
    
    def _assess_improvement_potential(self, insights: List[IntelligenceInsight]) -> str:
        """Assess how much this contact could be improved"""
        high_confidence_insights = [i for i in insights if i.confidence > 0.8]
        
        if len(high_confidence_insights) == 0:
            return "minimal"
        elif len(high_confidence_insights) <= 2:
            return "moderate"
        else:
            return "significant"
    
    def _extract_contact_id(self, vcard: vobject.vCard) -> str:
        """Extract or generate contact ID"""
        if hasattr(vcard, 'uid'):
            return vcard.uid.value
        elif hasattr(vcard, 'fn'):
            return f"contact_{hash(vcard.fn.value)}"
        else:
            return f"contact_{hash(str(vcard))}"
    
    def _load_name_patterns(self) -> Dict[str, Any]:
        """Load name recognition patterns"""
        # This could be loaded from a file or database
        return {}
    
    def _load_cultural_patterns(self) -> Dict[str, Any]:
        """Load cultural naming patterns"""
        return {}
    
    def _load_email_patterns(self) -> Dict[str, Any]:
        """Load email pattern recognition"""
        return {}


# Convenience functions for integration
def analyze_contact_with_ai(vcard: vobject.vCard, context: Dict[str, Any] = None) -> ContactAnalysis:
    """Analyze a single contact with AI intelligence"""
    engine = ContactIntelligenceEngine()
    return engine.analyze_contact(vcard, context)


def get_high_confidence_fixes(analysis: ContactAnalysis) -> List[IntelligenceInsight]:
    """Get fixes that can be applied automatically with high confidence"""
    return [insight for insight in analysis.insights 
            if insight.confidence >= ConfidenceLevel.VERY_HIGH.value and insight.auto_apply_safe]


def get_user_review_items(analysis: ContactAnalysis) -> List[IntelligenceInsight]:
    """Get items that need user review"""
    return [insight for insight in analysis.insights 
            if insight.confidence < ConfidenceLevel.VERY_HIGH.value or not insight.auto_apply_safe]


if __name__ == "__main__":
    # Test with a problematic contact
    test_vcard_text = """BEGIN:VCARD
VERSION:3.0
FN:claudiaplatzer85
N:;claudiaplatzer85;;;
EMAIL:claudiaplatzer85@gmail.com
END:VCARD"""
    
    vcard = vobject.readOne(test_vcard_text)
    analysis = analyze_contact_with_ai(vcard)
    
    print("AI Contact Analysis")
    print("=" * 50)
    print(f"Name Quality Score: {analysis.name_quality_score:.2f}")
    print(f"Overall Quality Score: {analysis.overall_quality_score:.2f}")
    print(f"Improvement Potential: {analysis.improvement_potential}")
    
    print("\nInsights:")
    for insight in analysis.insights:
        print(f"\n- Issue: {insight.issue_type}")
        print(f"  Current: {insight.current_value}")
        print(f"  Suggested: {insight.suggested_value}")
        print(f"  Confidence: {insight.confidence:.2f}")
        print(f"  Reasoning: {insight.reasoning}")
        print(f"  Auto-apply safe: {insight.auto_apply_safe}")