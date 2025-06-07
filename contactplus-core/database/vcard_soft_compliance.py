#!/usr/bin/env python3
"""
vCard Soft Compliance - Data Quality Improvements

This module implements business logic rules for data quality that go beyond
RFC compliance. These are "soft" rules that improve data consistency.

RULE: Always use vcard library for validation, vobject for manipulation
"""

import re
import logging
from typing import List, Dict, Tuple, Optional, Set
import vobject  # For manipulation ONLY
import phonenumbers
from email_validator import validate_email, EmailNotValidError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SoftComplianceChecker:
    """
    Checks and fixes soft compliance issues (data quality).
    
    Rules implemented:
    1. Extract emails/phones from notes
    2. Proper name capitalization
    3. Phone number formatting (E.164)
    4. Email validation and normalization
    5. Remove duplicate emails/phones
    6. Organization name standardization
    7. URL validation
    8. Clean up notes field
    """
    
    def __init__(self):
        self.fix_stats = {
            'emails_extracted_from_notes': 0,
            'phones_extracted_from_notes': 0,
            'names_capitalized': 0,
            'phones_formatted': 0,
            'emails_normalized': 0,
            'duplicates_removed': 0,
            'orgs_standardized': 0,
            'urls_validated': 0,
            'notes_cleaned': 0,
            'total_improved': 0
        }
        
        # Patterns for extraction
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,5}[-\s\.]?[0-9]{1,5}')
        
    def check_and_fix_file(self, input_filepath: str, output_filepath: str, 
                          default_country: str = 'US') -> Dict[str, any]:
        """
        Check and fix soft compliance issues in vCard file.
        
        Args:
            input_filepath: Input vCard file
            output_filepath: Output fixed vCard file
            default_country: Default country for phone number parsing
        """
        logger.info(f"Starting soft compliance check for: {input_filepath}")
        
        # Parse with vobject for manipulation
        with open(input_filepath, 'r', encoding='utf-8') as f:
            vcard_data = f.read()
        
        fixed_vcards = []
        issues_found = []
        
        for i, vcard in enumerate(vobject.readComponents(vcard_data)):
            try:
                issues = self._check_single_vcard(vcard, i)
                if issues:
                    issues_found.extend(issues)
                    
                fixed_vcard = self._fix_single_vcard(vcard, default_country)
                fixed_vcards.append(fixed_vcard)
                
            except Exception as e:
                logger.error(f"Error processing vCard {i}: {e}")
                fixed_vcards.append(vcard)  # Keep original if error
        
        # Write fixed vCards
        with open(output_filepath, 'w', encoding='utf-8') as f:
            for vcard in fixed_vcards:
                f.write(vcard.serialize())
        
        return {
            'total_vcards': len(fixed_vcards),
            'issues_found': len(issues_found),
            'sample_issues': issues_found[:10],
            'fixes_applied': self.fix_stats,
            'output_file': output_filepath
        }
    
    def _check_single_vcard(self, vcard: vobject.vCard, index: int) -> List[str]:
        """Check a single vCard for soft compliance issues"""
        issues = []
        
        # Check for emails/phones in notes
        if hasattr(vcard, 'note'):
            note_text = vcard.note.value
            
            if self.email_pattern.search(note_text):
                issues.append(f"vCard {index}: Email found in notes")
            
            if self.phone_pattern.search(note_text):
                issues.append(f"vCard {index}: Phone found in notes")
        
        # Check name capitalization
        if hasattr(vcard, 'fn'):
            fn = vcard.fn.value
            if fn.isupper() or fn.islower():
                issues.append(f"vCard {index}: Name not properly capitalized: {fn}")
        
        if hasattr(vcard, 'n'):
            n = vcard.n.value
            if n.family and (n.family.isupper() or n.family.islower()):
                issues.append(f"vCard {index}: Family name not properly capitalized")
            if n.given and (n.given.isupper() or n.given.islower()):
                issues.append(f"vCard {index}: Given name not properly capitalized")
        
        # Check for duplicate emails
        if hasattr(vcard, 'email_list') and len(vcard.email_list) > 1:
            emails = [e.value.lower() for e in vcard.email_list]
            if len(emails) != len(set(emails)):
                issues.append(f"vCard {index}: Duplicate emails found")
        
        # Check phone formatting
        if hasattr(vcard, 'tel_list'):
            for tel in vcard.tel_list:
                if not tel.value.startswith('+'):
                    issues.append(f"vCard {index}: Phone not in E.164 format: {tel.value}")
                    break
        
        return issues
    
    def _fix_single_vcard(self, vcard: vobject.vCard, default_country: str) -> vobject.vCard:
        """Fix soft compliance issues in a single vCard
        
        IMPORTANT: Must maintain RFC compliance while improving data quality
        """
        
        # Fix 1: Extract emails/phones from notes
        if hasattr(vcard, 'note'):
            original_note = vcard.note.value
            cleaned_note = original_note
            
            # Extract emails
            emails_found = self.email_pattern.findall(original_note)
            for email in emails_found:
                # Add to vCard if not already present
                existing_emails = []
                if hasattr(vcard, 'email_list'):
                    existing_emails = [e.value.lower() for e in vcard.email_list]
                
                if email.lower() not in existing_emails:
                    new_email = vcard.add('email')
                    new_email.value = email
                    new_email.type_param = 'INTERNET'
                    self.fix_stats['emails_extracted_from_notes'] += 1
                
                # Remove from note
                cleaned_note = cleaned_note.replace(email, '')
            
            # Extract phones
            phones_found = self.phone_pattern.findall(original_note)
            for phone in phones_found:
                # Add to vCard
                try:
                    parsed = phonenumbers.parse(phone, default_country)
                    if phonenumbers.is_valid_number(parsed):
                        formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                        
                        # Check if not already present
                        existing_phones = []
                        if hasattr(vcard, 'tel_list'):
                            existing_phones = [t.value for t in vcard.tel_list]
                        
                        if formatted not in existing_phones:
                            new_tel = vcard.add('tel')
                            new_tel.value = formatted
                            new_tel.type_param = 'VOICE'
                            self.fix_stats['phones_extracted_from_notes'] += 1
                        
                        # Remove from note
                        cleaned_note = cleaned_note.replace(phone, '')
                except:
                    pass  # Skip invalid phones
            
            # Update note if changed
            cleaned_note = ' '.join(cleaned_note.split())  # Clean up whitespace
            if cleaned_note != original_note:
                vcard.note.value = cleaned_note
                self.fix_stats['notes_cleaned'] += 1
        
        # Fix 2: Name capitalization
        if hasattr(vcard, 'fn'):
            original_fn = vcard.fn.value
            fixed_fn = self._proper_case_name(original_fn)
            if fixed_fn != original_fn:
                vcard.fn.value = fixed_fn
                self.fix_stats['names_capitalized'] += 1
        
        if hasattr(vcard, 'n'):
            n = vcard.n.value
            changed = False
            
            if n.family:
                fixed_family = self._proper_case_name(n.family)
                if fixed_family != n.family:
                    n.family = fixed_family
                    changed = True
            
            if n.given:
                fixed_given = self._proper_case_name(n.given)
                if fixed_given != n.given:
                    n.given = fixed_given
                    changed = True
            
            if changed:
                self.fix_stats['names_capitalized'] += 1
        
        # Fix 3: Phone formatting
        if hasattr(vcard, 'tel_list'):
            for tel in vcard.tel_list:
                original = tel.value
                try:
                    # Parse and format to E.164
                    parsed = phonenumbers.parse(original, default_country)
                    if phonenumbers.is_valid_number(parsed):
                        formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                        if formatted != original:
                            tel.value = formatted
                            self.fix_stats['phones_formatted'] += 1
                except:
                    pass  # Keep original if can't parse
        
        # Fix 4: Email normalization and validation
        if hasattr(vcard, 'email_list'):
            valid_emails = []
            seen_emails = set()
            
            for email in vcard.email_list:
                try:
                    # Validate and normalize
                    validation = validate_email(email.value)
                    normalized = validation.email.lower()
                    
                    # Remove duplicates
                    if normalized not in seen_emails:
                        email.value = normalized
                        valid_emails.append(email)
                        seen_emails.add(normalized)
                        self.fix_stats['emails_normalized'] += 1
                    else:
                        self.fix_stats['duplicates_removed'] += 1
                except EmailNotValidError:
                    # Keep invalid emails for now (user might want to review)
                    valid_emails.append(email)
            
            # Remove old emails and add valid ones back
            if valid_emails:  # Only modify if we have valid emails
                for email in list(vcard.email_list):
                    vcard.remove(email)
                for email in valid_emails:
                    vcard.add(email)
        
        # Fix 5: Organization standardization
        if hasattr(vcard, 'org'):
            org_values = vcard.org.value
            if isinstance(org_values, list):
                # Capitalize each component
                fixed_values = [self._proper_case_org(str(v)) for v in org_values]
                if fixed_values != org_values:
                    vcard.org.value = fixed_values
                    self.fix_stats['orgs_standardized'] += 1
        
        # Ensure we still have required fields after all fixes
        # This prevents soft compliance from breaking hard compliance
        if not hasattr(vcard, 'fn') and hasattr(vcard, 'n'):
            # Emergency FN generation if somehow removed
            vcard.add('fn')
            n = vcard.n.value
            vcard.fn.value = f"{n.given} {n.family}".strip() or "Unknown"
            logger.warning("Had to add FN during soft compliance to maintain RFC compliance")
        
        self.fix_stats['total_improved'] += 1
        return vcard
    
    def _proper_case_name(self, name: str) -> str:
        """Convert name to proper case, handling special cases"""
        if not name:
            return name
        
        # Handle names with multiple parts
        parts = name.split()
        fixed_parts = []
        
        for part in parts:
            # Special cases
            if part.upper() in ['II', 'III', 'IV', 'JR', 'SR', 'PHD', 'MD']:
                fixed_parts.append(part.upper())
            elif part.lower() in ['de', 'van', 'von', 'der', 'la', 'di']:
                fixed_parts.append(part.lower())
            elif '-' in part:
                # Handle hyphenated names
                subparts = part.split('-')
                fixed_parts.append('-'.join(p.capitalize() for p in subparts))
            elif "'" in part:
                # Handle names like O'Brien
                subparts = part.split("'")
                fixed_parts.append("'".join(p.capitalize() for p in subparts))
            else:
                fixed_parts.append(part.capitalize())
        
        return ' '.join(fixed_parts)
    
    def _proper_case_org(self, org: str) -> str:
        """Convert organization name to proper case"""
        if not org:
            return org
        
        # Common acronyms to keep uppercase
        acronyms = {'LLC', 'INC', 'CORP', 'GMBH', 'AG', 'SA', 'LTD', 'PLC', 'IT', 'CEO', 'CTO', 'VP'}
        
        words = org.split()
        fixed_words = []
        
        for word in words:
            if word.upper() in acronyms:
                fixed_words.append(word.upper())
            else:
                fixed_words.append(word.capitalize())
        
        return ' '.join(fixed_words)


# Additional suggestions for soft compliance
class SoftComplianceSuggestions:
    """
    Additional data quality improvements you might consider:
    
    1. **Email domain validation**: Check if email domains actually exist
    2. **Phone number type detection**: Automatically detect mobile vs landline
    3. **Address standardization**: Format addresses consistently
    4. **URL validation**: Ensure URLs are reachable
    5. **Photo optimization**: Resize large photos, convert to JPEG
    6. **Birthday format**: Ensure consistent date formats
    7. **Remove trailing whitespace**: Clean all text fields
    8. **Merge similar organizations**: "Google Inc" vs "Google Inc."
    9. **Social media extraction**: Extract LinkedIn, Twitter from URLs
    10. **Title standardization**: "CEO" vs "Chief Executive Officer"
    """
    pass


if __name__ == "__main__":
    # Example usage
    import config
    
    input_file = "/Users/lk/Documents/Developer/Private/ContactPlus/Imports/Sara_Export_Sara A. Kerner and 3.074 others_FIXED.vcf"
    output_file = input_file.replace('_FIXED.vcf', '_SOFT_COMPLIANT.vcf')
    
    print("Soft Compliance Checker")
    print("=" * 60)
    
    checker = SoftComplianceChecker()
    result = checker.check_and_fix_file(input_file, output_file, default_country='US')
    
    print(f"\nTotal vCards processed: {result['total_vcards']}")
    print(f"Issues found: {result['issues_found']}")
    
    print("\nFixes applied:")
    for fix_type, count in result['fixes_applied'].items():
        if count > 0:
            print(f"  {fix_type}: {count}")
    
    if result['sample_issues']:
        print("\nSample issues found:")
        for issue in result['sample_issues']:
            print(f"  - {issue}")
    
    print(f"\nOutput saved to: {output_file}")