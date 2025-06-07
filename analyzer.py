"""Contact Analysis Module - Issue Detection and Review Queue Creation

This module analyzes parsed vCard data to identify contacts that need
manual review based on business logic rules (soft compliance).

Note: This operates on already-validated vCard data from parser.py
"""

import json
import logging
from typing import List, Dict, Any
from collections import Counter
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContactAnalyzer:
    """Analyze contacts and create review queue for manual intervention
    
    Identifies contacts with:
    - Excessive emails (4+ addresses)
    - Invalid/missing names
    - Mixed email domains (potential incorrectly merged contacts)
    - Other data quality issues requiring human review
    """
    
    def __init__(self, contacts: List[Dict[str, Any]]):
        self.contacts = contacts
        self.review_queue = []
        
    def analyze(self) -> Dict[str, Any]:
        """Perform full analysis of contacts"""
        stats = {
            'total_contacts': len(self.contacts),
            'contacts_with_issues': 0,
            'issue_types': Counter(),
            'email_distribution': Counter(),
            'review_queue': []
        }
        
        # Analyze each contact
        for contact in self.contacts:
            email_count = len(contact['emails'])
            stats['email_distribution'][email_count] += 1
            
            if contact.get('issues'):
                stats['contacts_with_issues'] += 1
                for issue in contact['issues']:
                    stats['issue_types'][issue['type']] += 1
                
                # Add to review queue if meets criteria
                if self._needs_review(contact):
                    review_item = self._create_review_item(contact)
                    self.review_queue.append(review_item)
        
        stats['review_queue_size'] = len(self.review_queue)
        return stats
    
    def _needs_review(self, contact: Dict[str, Any]) -> bool:
        """Determine if contact needs manual review"""
        # Review if too many emails
        if len(contact['emails']) >= config.MAX_EMAILS_THRESHOLD:
            return True
        
        # Review if name issues
        for issue in contact.get('issues', []):
            if issue['type'] == 'invalid_name' and issue['severity'] == 'high':
                return True
            if issue['type'] == 'mixed_domains' and issue['severity'] == 'high':
                return True
        
        return False
    
    def _create_review_item(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """Create a review queue item"""
        return {
            'id': contact['id'],
            'formatted_name': contact['formatted_name'],
            'organizations': contact['organizations'],
            'emails': contact['emails'],
            'email_count': len(contact['emails']),
            'phones': contact['phones'],
            'issues': contact['issues'],
            'review_status': 'pending',
            'original_vcard': contact['original_vcard']
        }
    
    def save_review_queue(self):
        """Save review queue to JSON file"""
        logger.info(f"Saving review queue with {len(self.review_queue)} items")
        
        with open(config.REVIEW_QUEUE_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'version': '1.0',
                'total_items': len(self.review_queue),
                'items': self.review_queue
            }, f, indent=2, ensure_ascii=False)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detailed statistics about the contacts"""
        stats = {
            'total_contacts': len(self.contacts),
            'emails': {
                'total': sum(len(c['emails']) for c in self.contacts),
                'contacts_with_email': sum(1 for c in self.contacts if c['emails']),
                'max_emails_per_contact': max(len(c['emails']) for c in self.contacts) if self.contacts else 0,
                'contacts_with_4plus_emails': sum(1 for c in self.contacts if len(c['emails']) >= 4)
            },
            'phones': {
                'total': sum(len(c['phones']) for c in self.contacts),
                'contacts_with_phone': sum(1 for c in self.contacts if c['phones'])
            },
            'organizations': {
                'contacts_with_org': sum(1 for c in self.contacts if c['organizations'])
            },
            'photos': {
                'contacts_with_photo': sum(1 for c in self.contacts if c['photo'])
            }
        }
        
        # Add domain statistics
        all_domains = []
        for contact in self.contacts:
            for email in contact['emails']:
                if '@' in email['address']:
                    domain = email['address'].split('@')[1].lower()
                    all_domains.append(domain)
        
        domain_counts = Counter(all_domains)
        stats['top_domains'] = domain_counts.most_common(10)
        
        return stats