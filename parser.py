"""vCard Parser Module - Enhanced with Validation

This module implements the standard vCard processing pattern:
1. Validate with vcard library (RFC compliance)
2. Parse/manipulate with vobject only if valid

RULE: Always use vcard library for validation, vobject for manipulation

The parser now includes validation reports to ensure data integrity
throughout the processing pipeline.
"""

import vobject  # For manipulation ONLY
import json
import uuid
from typing import List, Dict, Any, Tuple
import re
import logging
from vcard_validator import VCardStandardsValidator  # For validation ONLY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VCardParser:
    """Parse and analyze vCard files with integrated validation
    
    Implements the mandatory workflow:
    1. Validate with vcard library for RFC 2426 compliance
    2. Parse/manipulate with vobject only if reasonably valid
    3. Include validation report in results
    
    This ensures all parsed data meets standards before processing.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.contacts = []
        self.validator = VCardStandardsValidator(strict=False)  # Allow some real-world issues
        self.validation_report = None
        
    def parse(self) -> List[Dict[str, Any]]:
        """Parse vCard file and return list of contact dictionaries
        
        Standard workflow:
        1. Validate with vcard library first
        2. Parse with vobject only if reasonably valid
        """
        logger.info(f"Starting vCard processing: {self.filepath}")
        
        # STEP 1: Always validate first with vcard library
        logger.info("Step 1: Validating with vcard library...")
        is_valid, errors, warnings = self.validator.validate_file(self.filepath)
        
        self.validation_report = {
            'is_valid': is_valid,
            'error_count': len(errors),
            'warning_count': len(warnings),
            'sample_errors': errors[:5],
            'sample_warnings': warnings[:5]
        }
        
        logger.info(f"Validation complete: {len(errors)} errors, {len(warnings)} warnings")
        
        # Only proceed if file is reasonably valid
        if not is_valid and len(errors) > 100:
            logger.error(f"File has too many validation errors ({len(errors)}), aborting parse")
            raise ValueError(f"vCard file has {len(errors)} validation errors. Please fix before parsing.")
        
        # STEP 2: Parse with vobject for manipulation
        logger.info("Step 2: Parsing with vobject for manipulation...")
        
        with open(self.filepath, 'r', encoding='utf-8') as f:
            vcard_data = f.read()
            
        # Parse all vCards in the file using vobject (manipulation only)
        for vcard in vobject.readComponents(vcard_data):
            try:
                contact = self._parse_single_vcard(vcard)
                self.contacts.append(contact)
            except Exception as e:
                logger.error(f"Error parsing vCard: {e}")
                continue
                
        logger.info(f"Parsed {len(self.contacts)} contacts")
        return self.contacts
    
    def _parse_single_vcard(self, vcard) -> Dict[str, Any]:
        """Parse a single vCard component"""
        contact = {
            'id': str(uuid.uuid4()),
            'emails': [],
            'phones': [],
            'addresses': [],
            'urls': [],
            'organizations': [],
            'titles': [],
            'notes': [],
            'photo': None,
            'issues': [],
            'original_vcard': vcard.serialize()
        }
        
        # Parse name
        if hasattr(vcard, 'n'):
            name_parts = vcard.n.value
            contact['family_name'] = name_parts.family or ''
            contact['given_name'] = name_parts.given or ''
            contact['additional_name'] = name_parts.additional or ''
            contact['prefix'] = name_parts.prefix or ''
            contact['suffix'] = name_parts.suffix or ''
        
        # Parse formatted name
        if hasattr(vcard, 'fn'):
            contact['formatted_name'] = vcard.fn.value
        else:
            contact['formatted_name'] = f"{contact.get('given_name', '')} {contact.get('family_name', '')}".strip()
        
        # Parse emails
        if hasattr(vcard, 'email_list'):
            for email in vcard.email_list:
                email_data = {
                    'address': email.value,
                    'type': []
                }
                if hasattr(email, 'type_param'):
                    email_data['type'] = email.type_param if isinstance(email.type_param, list) else [email.type_param]
                contact['emails'].append(email_data)
        
        # Parse phone numbers
        if hasattr(vcard, 'tel_list'):
            for tel in vcard.tel_list:
                phone_data = {
                    'number': tel.value,
                    'type': []
                }
                if hasattr(tel, 'type_param'):
                    phone_data['type'] = tel.type_param if isinstance(tel.type_param, list) else [tel.type_param]
                contact['phones'].append(phone_data)
        
        # Parse organizations
        if hasattr(vcard, 'org'):
            org_values = vcard.org.value
            if isinstance(org_values, list):
                contact['organizations'] = [str(v) for v in org_values if v]
            else:
                contact['organizations'] = [str(org_values)] if org_values else []
        
        # Parse title
        if hasattr(vcard, 'title'):
            contact['titles'] = [vcard.title.value]
        
        # Parse addresses
        if hasattr(vcard, 'adr_list'):
            for adr in vcard.adr_list:
                addr_data = {
                    'street': str(adr.value.street or ''),
                    'city': str(adr.value.city or ''),
                    'region': str(adr.value.region or ''),
                    'code': str(adr.value.code or ''),
                    'country': str(adr.value.country or ''),
                    'type': []
                }
                if hasattr(adr, 'type_param'):
                    addr_data['type'] = adr.type_param if isinstance(adr.type_param, list) else [adr.type_param]
                contact['addresses'].append(addr_data)
        
        # Parse URLs
        if hasattr(vcard, 'url_list'):
            for url in vcard.url_list:
                contact['urls'].append(url.value)
        
        # Parse notes
        if hasattr(vcard, 'note'):
            contact['notes'] = [vcard.note.value]
        
        # Check for photo
        if hasattr(vcard, 'photo'):
            contact['photo'] = True  # Just flag presence, don't store data
        
        return contact
    
    def find_issues(self) -> List[Dict[str, Any]]:
        """Find contacts with potential issues"""
        contacts_with_issues = []
        
        for contact in self.contacts:
            issues = []
            
            # Check for too many emails
            if len(contact['emails']) >= 4:
                issues.append({
                    'type': 'too_many_emails',
                    'count': len(contact['emails']),
                    'severity': 'high' if len(contact['emails']) > 6 else 'medium'
                })
            
            # Check for empty or short names
            if not contact['formatted_name'] or len(contact['formatted_name']) < 2:
                issues.append({
                    'type': 'invalid_name',
                    'severity': 'high'
                })
            
            # Check for mixed email domains (potential merged contacts)
            if len(contact['emails']) > 2:
                domains = [email['address'].split('@')[1] for email in contact['emails'] if '@' in email['address']]
                if len(set(domains)) > 3:
                    issues.append({
                        'type': 'mixed_domains',
                        'domain_count': len(set(domains)),
                        'severity': 'medium'
                    })
            
            if issues:
                contact['issues'] = issues
                contacts_with_issues.append(contact)
        
        return contacts_with_issues