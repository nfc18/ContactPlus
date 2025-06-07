#!/usr/bin/env python3
"""
User Preferences Configuration for AI Contact Processing

This module stores user preferences and domain knowledge to make
AI decisions aligned with user expectations and minimize manual intervention.
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class UserPreferences:
    """
    User preferences for AI contact processing decisions.
    These will be populated based on the preference capture session.
    """
    
    # Source reliability ranking (1 = most reliable)
    source_trust_ranking: List[str] = None
    
    # Name formatting preferences
    compound_name_style: str = "hyphenated"  # or "spaced"
    professional_title_handling: str = "separate_field"  # or "keep_in_name" or "remove"
    informal_vs_formal_names: str = "prefer_formal"  # or "prefer_informal" or "context_dependent"
    
    # Email preferences
    email_domain_trust: Dict[str, int] = None  # domain -> trust_score (1-5)
    email_conflict_resolution: str = "prefer_personal"  # or "prefer_work" or "most_recent"
    
    # Phone number preferences
    phone_priority: str = "prefer_mobile"  # or "prefer_landline" or "most_recent"
    international_format: str = "include_country_code"  # or "local_format" or "mixed"
    
    # Duplicate merge strategy
    auto_merge_confidence_threshold: float = 0.95
    photo_selection_strategy: str = "highest_resolution"  # or "most_recent" or "reliable_source"
    note_combination_strategy: str = "preserve_all"  # or "keep_longest" or "reliable_source"
    
    # Business contact handling
    auto_detect_business_contacts: bool = True
    business_contact_separation: str = "mixed"  # or "separate" or "remove"
    
    # Quality and confidence settings
    auto_fix_confidence_threshold: float = 0.90
    never_auto_modify_fields: List[str] = None
    
    # Austrian/German specific
    umlaut_handling: str = "preserve"  # or "convert" or "mixed"
    austrian_address_format: bool = True
    professional_title_preservation: str = "preserve_in_name"
    
    # Special cases
    family_member_merge_policy: str = "never_auto_merge"
    nickname_expansion_policy: str = "prefer_formal"
    work_colleague_handling: str = "consistent_company_names"


class PreferenceBasedDecisionMaker:
    """
    Makes AI decisions based on user preferences to minimize manual intervention.
    """
    
    def __init__(self, preferences: UserPreferences):
        self.prefs = preferences
    
    def should_auto_apply_fix(self, confidence: float, fix_type: str, field: str) -> bool:
        """
        Determine if an AI fix should be applied automatically based on user preferences.
        """
        # Check if field is in never-auto-modify list
        if self.prefs.never_auto_modify_fields and field in self.prefs.never_auto_modify_fields:
            return False
        
        # Check confidence threshold
        if confidence < self.prefs.auto_fix_confidence_threshold:
            return False
        
        # Special handling for different fix types
        if fix_type == "email_derived_name":
            # User typically wants these fixed as they're obvious issues
            return confidence >= 0.90  # Slightly more aggressive for obvious cases
        
        elif fix_type == "professional_title":
            return confidence >= self.prefs.auto_fix_confidence_threshold
        
        return True
    
    def resolve_email_conflict(self, emails: List[Dict[str, Any]]) -> str:
        """
        Choose primary email based on user preferences.
        """
        if not emails:
            return None
        
        if len(emails) == 1:
            return emails[0]['address']
        
        # Apply user preference strategy
        if self.prefs.email_conflict_resolution == "prefer_personal":
            # Prioritize personal domains
            personal_domains = ['gmail.com', 'gmx.net', 'icloud.com', 'yahoo.com']
            for email in emails:
                domain = email['address'].split('@')[1].lower()
                if domain in personal_domains:
                    return email['address']
        
        elif self.prefs.email_conflict_resolution == "prefer_work":
            # Prioritize work domains (non-personal)
            personal_domains = ['gmail.com', 'gmx.net', 'icloud.com', 'yahoo.com']
            for email in emails:
                domain = email['address'].split('@')[1].lower()
                if domain not in personal_domains:
                    return email['address']
        
        # Fallback to first email
        return emails[0]['address']
    
    def resolve_phone_conflict(self, phones: List[Dict[str, Any]]) -> str:
        """
        Choose primary phone based on user preferences.
        """
        if not phones:
            return None
        
        if len(phones) == 1:
            return phones[0]['number']
        
        # Apply user preference
        if self.prefs.phone_priority == "prefer_mobile":
            for phone in phones:
                if phone.get('type', '').lower() in ['mobile', 'cell', 'handy']:
                    return phone['number']
        
        elif self.prefs.phone_priority == "prefer_landline":
            for phone in phones:
                if phone.get('type', '').lower() in ['home', 'work', 'landline']:
                    return phone['number']
        
        # Fallback to first phone
        return phones[0]['number']
    
    def format_name_according_to_preference(self, name_parts: Dict[str, str]) -> str:
        """
        Format name according to user preferences.
        """
        first = name_parts.get('given', '')
        last = name_parts.get('family', '')
        
        # Handle compound names
        if '-' in last and self.prefs.compound_name_style == "spaced":
            last = last.replace('-', ' ')
        elif ' ' in last and self.prefs.compound_name_style == "hyphenated":
            last = last.replace(' ', '-')
        
        return f"{first} {last}".strip()
    
    def should_auto_merge_duplicates(self, confidence: float) -> bool:
        """
        Determine if duplicates should be auto-merged based on confidence.
        """
        return confidence >= self.prefs.auto_merge_confidence_threshold
    
    def is_business_contact(self, contact_name: str, organization: str = None) -> bool:
        """
        Determine if contact should be classified as business.
        """
        if not self.prefs.auto_detect_business_contacts:
            return False
        
        business_indicators = [
            'support', 'team', 'service', 'info', 'help',
            'gmbh', 'ag', 'inc', 'corp', 'ltd', 'llc',
            'buchhaltung', 'verwaltung', 'sekretariat'
        ]
        
        name_lower = contact_name.lower()
        for indicator in business_indicators:
            if indicator in name_lower:
                return True
        
        if organization:
            org_lower = organization.lower()
            for indicator in business_indicators:
                if indicator in org_lower:
                    return True
        
        return False
    
    def get_source_priority_score(self, source_name: str) -> int:
        """
        Get priority score for source (lower number = higher priority).
        """
        if not self.prefs.source_trust_ranking:
            return 99  # Default low priority
        
        try:
            return self.prefs.source_trust_ranking.index(source_name) + 1
        except ValueError:
            return 99  # Unknown source gets low priority


# Default conservative preferences (safe starting point)
DEFAULT_PREFERENCES = UserPreferences(
    source_trust_ranking=['iphone_contacts', 'sara_export', 'iphone_suggested'],
    compound_name_style="hyphenated",
    professional_title_handling="separate_field",
    informal_vs_formal_names="prefer_formal",
    email_domain_trust={
        'gmail.com': 5,
        'gmx.net': 5,
        'icloud.com': 4,
        'yahoo.com': 3
    },
    email_conflict_resolution="prefer_personal",
    phone_priority="prefer_mobile",
    international_format="include_country_code",
    auto_merge_confidence_threshold=0.95,
    photo_selection_strategy="highest_resolution",
    note_combination_strategy="preserve_all",
    auto_detect_business_contacts=True,
    business_contact_separation="mixed",
    auto_fix_confidence_threshold=0.90,
    never_auto_modify_fields=[],  # Empty = allow all fields to be modified
    umlaut_handling="preserve",
    austrian_address_format=True,
    professional_title_preservation="preserve_in_name",
    family_member_merge_policy="never_auto_merge",
    nickname_expansion_policy="prefer_formal",
    work_colleague_handling="consistent_company_names"
)


def load_user_preferences(config_file: str = "user_preferences.json") -> UserPreferences:
    """
    Load user preferences from configuration file.
    Falls back to defaults if file doesn't exist.
    """
    import json
    import os
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Create UserPreferences object from config
            # This would need to be implemented based on the actual structure
            return DEFAULT_PREFERENCES  # For now, return defaults
        except Exception as e:
            print(f"Error loading preferences: {e}")
            return DEFAULT_PREFERENCES
    else:
        return DEFAULT_PREFERENCES


def save_user_preferences(preferences: UserPreferences, config_file: str = "user_preferences.json"):
    """
    Save user preferences to configuration file.
    """
    import json
    from dataclasses import asdict
    
    try:
        with open(config_file, 'w') as f:
            json.dump(asdict(preferences), f, indent=2)
        print(f"Preferences saved to {config_file}")
    except Exception as e:
        print(f"Error saving preferences: {e}")


if __name__ == "__main__":
    # Example usage
    prefs = load_user_preferences()
    decision_maker = PreferenceBasedDecisionMaker(prefs)
    
    # Example decision making
    print("Auto-apply name fix with 95% confidence?", 
          decision_maker.should_auto_apply_fix(0.95, "email_derived_name", "name"))
    
    print("Auto-merge duplicates with 90% confidence?",
          decision_maker.should_auto_merge_duplicates(0.90))
    
    print("Is 'Anyline Support' a business contact?",
          decision_maker.is_business_contact("Anyline Support"))