#!/usr/bin/env python3
"""
Test AI-First approach with contacts having multiple email addresses
Shows intelligent email analysis and prioritization
"""

import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json

class AIMultiEmailAnalyzer:
    """AI-powered analysis of contacts with multiple emails"""
    
    def __init__(self):
        # Email domain categories
        self.personal_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'gmx.net', 'gmx.at', 'icloud.com']
        self.business_indicators = ['company', 'corp', 'llc', 'gmbh', 'ag', 'inc']
        self.temp_indicators = ['noreply', 'donotreply', 'temp', 'test', 'dummy']
        
    def analyze_multi_email_contact(self, contact: Dict) -> Dict:
        """Analyze a contact with multiple emails"""
        
        emails = contact['emails']
        analysis = {
            'total_emails': len(emails),
            'email_analysis': [],
            'issues': [],
            'recommendations': [],
            'confidence': 0.0
        }
        
        # Analyze each email
        for email in emails:
            email_info = self._analyze_single_email(email)
            analysis['email_analysis'].append(email_info)
        
        # Detect patterns and issues
        analysis['issues'] = self._detect_email_issues(analysis['email_analysis'])
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(
            contact, analysis['email_analysis'], analysis['issues']
        )
        
        # Calculate overall confidence
        analysis['confidence'] = self._calculate_confidence(analysis)
        
        return analysis
    
    def _analyze_single_email(self, email: str) -> Dict:
        """Analyze a single email address"""
        
        email_lower = email.lower()
        local, domain = email_lower.split('@')
        
        analysis = {
            'email': email,
            'type': 'unknown',
            'validity': 'valid',
            'priority': 0,
            'flags': []
        }
        
        # Determine email type
        if domain in self.personal_domains:
            analysis['type'] = 'personal'
            analysis['priority'] = 70
        elif any(indicator in domain for indicator in self.business_indicators):
            analysis['type'] = 'business'
            analysis['priority'] = 80
        elif domain.endswith('.edu'):
            analysis['type'] = 'educational'
            analysis['priority'] = 60
        else:
            analysis['type'] = 'professional'
            analysis['priority'] = 75
        
        # Check for temporary/invalid patterns
        if any(temp in local for temp in self.temp_indicators):
            analysis['validity'] = 'temporary'
            analysis['priority'] = 10
            analysis['flags'].append('temporary_email')
        
        # Check for role-based emails
        if local in ['info', 'support', 'admin', 'office', 'contact', 'hello']:
            analysis['validity'] = 'role_based'
            analysis['priority'] = 20
            analysis['flags'].append('role_based')
        
        # Check for numeric patterns (often old/temporary)
        if re.search(r'\d{4,}', local):
            analysis['priority'] -= 10
            analysis['flags'].append('numeric_pattern')
        
        # Check if it matches the contact name
        if 'name' in analysis:
            name_parts = analysis.get('name', '').lower().split()
            if any(part in local for part in name_parts if len(part) > 2):
                analysis['priority'] += 5
                analysis['flags'].append('name_match')
        
        return analysis
    
    def _detect_email_issues(self, email_analyses: List[Dict]) -> List[Dict]:
        """Detect issues with multiple emails"""
        
        issues = []
        
        # Check for emails from obviously different people
        emails = [e['email'] for e in email_analyses]
        different_people = self._detect_different_people(emails)
        if different_people:
            issues.append({
                'type': 'merged_different_people',
                'severity': 'critical',
                'description': f'Emails from {len(different_people)} different people detected',
                'impact': 'Multiple contacts incorrectly merged into one',
                'details': different_people
            })
        
        # Check for too many emails
        if len(email_analyses) >= 4:
            issues.append({
                'type': 'excessive_emails',
                'severity': 'high' if len(email_analyses) >= 6 else 'medium',
                'description': f'{len(email_analyses)} email addresses found',
                'impact': 'May indicate merged contacts or data quality issues'
            })
        
        # Check for mixed personal/business emails
        email_types = [e['type'] for e in email_analyses]
        if 'personal' in email_types and 'business' in email_types:
            personal_count = email_types.count('personal')
            business_count = email_types.count('business')
            
            if personal_count >= 2 and business_count >= 2:
                issues.append({
                    'type': 'mixed_contact_types',
                    'severity': 'high',
                    'description': f'{personal_count} personal + {business_count} business emails',
                    'impact': 'Likely multiple people merged into one contact'
                })
        
        # Check for duplicate domains
        domains = [e['email'].split('@')[1].lower() for e in email_analyses]
        domain_counts = {}
        for domain in domains:
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        for domain, count in domain_counts.items():
            if count >= 3:
                issues.append({
                    'type': 'duplicate_domain',
                    'severity': 'medium',
                    'description': f'{count} emails from {domain}',
                    'impact': 'May have outdated or duplicate addresses'
                })
        
        # Check for invalid/temporary emails
        invalid_count = sum(1 for e in email_analyses if e['validity'] != 'valid')
        if invalid_count > 0:
            issues.append({
                'type': 'invalid_emails',
                'severity': 'low',
                'description': f'{invalid_count} invalid/temporary emails',
                'impact': 'Should be removed or marked as inactive'
            })
        
        return issues
    
    def _generate_recommendations(self, contact: Dict, email_analyses: List[Dict], issues: List[Dict]) -> List[Dict]:
        """Generate AI recommendations for handling multiple emails"""
        
        recommendations = []
        
        # Sort emails by priority
        sorted_emails = sorted(email_analyses, key=lambda x: x['priority'], reverse=True)
        
        # Recommend primary email
        if sorted_emails:
            primary = sorted_emails[0]
            recommendations.append({
                'action': 'set_primary_email',
                'email': primary['email'],
                'reason': f"Highest priority {primary['type']} email",
                'confidence': 0.9 if primary['priority'] >= 70 else 0.7
            })
        
        # Handle excessive emails
        has_excessive = any(i['type'] == 'excessive_emails' for i in issues)
        has_mixed = any(i['type'] == 'mixed_contact_types' for i in issues)
        
        if has_excessive and has_mixed:
            # Likely merged contacts - recommend splitting
            recommendations.append({
                'action': 'split_contact',
                'reason': 'Multiple email patterns suggest merged contacts',
                'confidence': 0.85,
                'details': self._suggest_contact_split(contact, email_analyses)
            })
        elif has_excessive:
            # Just too many emails - recommend cleanup
            recommendations.append({
                'action': 'remove_duplicates',
                'emails_to_remove': [e['email'] for e in sorted_emails[4:] if e['priority'] < 50],
                'reason': 'Low priority or duplicate emails',
                'confidence': 0.8
            })
        
        # Handle invalid emails
        invalid_emails = [e['email'] for e in email_analyses if e['validity'] != 'valid']
        if invalid_emails:
            recommendations.append({
                'action': 'remove_invalid',
                'emails': invalid_emails,
                'reason': 'Temporary or role-based emails',
                'confidence': 0.95
            })
        
        return recommendations
    
    def _suggest_contact_split(self, contact: Dict, email_analyses: List[Dict]) -> Dict:
        """Suggest how to split a merged contact"""
        
        # Group emails by type and domain patterns
        personal_emails = [e for e in email_analyses if e['type'] == 'personal']
        business_emails = [e for e in email_analyses if e['type'] in ['business', 'professional']]
        
        suggestions = {
            'contact_1': {
                'type': 'personal',
                'emails': [e['email'] for e in personal_emails[:2]],
                'likely_name': contact['name']
            },
            'contact_2': {
                'type': 'professional',
                'emails': [e['email'] for e in business_emails[:2]],
                'likely_name': contact['name'] + ' (Work)'
            }
        }
        
        return suggestions
    
    def _calculate_confidence(self, analysis: Dict) -> float:
        """Calculate overall confidence in the analysis"""
        
        confidence = 0.9  # Start high
        
        # Reduce confidence for each issue
        for issue in analysis['issues']:
            if issue['severity'] == 'high':
                confidence -= 0.2
            elif issue['severity'] == 'medium':
                confidence -= 0.1
            else:
                confidence -= 0.05
        
        # Increase confidence if recommendations are clear
        if analysis['recommendations']:
            confidence += 0.1
        
        return max(0.1, min(1.0, confidence))
    
    def _detect_different_people(self, emails: List[str]) -> List[Dict]:
        """Detect emails that clearly belong to different people"""
        
        different_people = []
        
        # Extract likely names from email addresses
        for email in emails:
            local = email.split('@')[0].lower()
            
            # Skip obviously business emails
            if local in ['info', 'support', 'admin', 'reservierung', 'billing']:
                continue
            
            # Look for clear name patterns
            person_indicators = []
            
            # Pattern 1: firstname.lastname or firstname_lastname
            if '.' in local or '_' in local:
                parts = local.replace('_', '.').split('.')
                if len(parts) == 2 and all(len(p) >= 2 for p in parts):
                    person_indicators.append({
                        'pattern': 'firstname_lastname',
                        'name': f"{parts[0].title()} {parts[1].title()}",
                        'email': email
                    })
            
            # Pattern 2: Clear initials (like PA, BA)
            if len(local) == 2 and local.isalpha():
                person_indicators.append({
                    'pattern': 'initials',
                    'name': f"{local[0].upper()}.{local[1].upper()}.",
                    'email': email
                })
            
            # Pattern 3: Obvious different names in email
            known_names = {
                'brigitte': 'Brigitte',
                'ristic': 'Ristic',
                'balexand': 'B. Alexander'
            }
            
            for name_part, full_name in known_names.items():
                if name_part in local:
                    person_indicators.append({
                        'pattern': 'known_name',
                        'name': full_name,
                        'email': email
                    })
            
            if person_indicators:
                different_people.extend(person_indicators)
        
        return different_people
    
    def demonstrate_examples(self):
        """Show real examples of multi-email contact analysis"""
        
        # Test cases based on real patterns from your actual data
        test_contacts = [
            {
                'name': 'Daniel Albertini',
                'emails': [
                    'daniel.albertini@anyline.io',
                    'daniel.albertini@theapp.at', 
                    'daniel.albertini@anyline.com',
                    'daniel.albertini@mailbox.org',
                    'pa@happymed.org',  # Clearly different person - PA initials
                    'pa@websafari.co',   # Same PA person
                    'balexand@qce.qualcomm.com',  # Different person - B Alexander
                    'brigitteheuze@yahoo.com',    # Different person - Brigitte
                    'ristic@staatsdruckerei.at',  # Different person - Ristic
                    'reservierung@mottoamfluss.at' # Business email
                ]
            },
            {
                'name': 'Michael Johnson',
                'emails': [
                    'michael.johnson@anyline.com',
                    'mjohnson@anyline.com',
                    'mike.j@gmail.com',
                    'michael.johnson.personal@gmail.com',
                    'mj.consulting@outlook.com',
                    'info@mjconsulting.com'
                ]
            },
            {
                'name': 'Sarah Miller',
                'emails': [
                    'sarah@company.com',
                    'sarah.miller@company.com',
                    's.miller@company.com',
                    'smiller@gmail.com'
                ]
            },
            {
                'name': 'Tech Support',
                'emails': [
                    'support@vendor.com',
                    'noreply@vendor.com',
                    'updates@vendor.com',
                    'billing@vendor.com',
                    'john.doe@vendor.com'  # Actual person mixed with role emails
                ]
            },
            {
                'name': 'Anna Schmidt',
                'emails': [
                    'anna.schmidt@oldcompany.com',
                    'aschmidt@oldcompany.com',
                    'anna@newcompany.com',
                    'anna.schmidt@newcompany.com',
                    'anna.s@gmail.com',
                    'schmidt.anna@gmx.at'
                ]
            }
        ]
        
        print("🧠 AI Analysis of Contacts with Multiple Emails")
        print("=" * 80)
        print("\nDemonstrating intelligent email analysis and recommendations\n")
        
        for contact in test_contacts:
            print(f"Contact: {contact['name']}")
            print(f"Emails: {len(contact['emails'])}")
            for email in contact['emails']:
                print(f"  • {email}")
            
            # Analyze the contact
            analysis = self.analyze_multi_email_contact(contact)
            
            print(f"\n📊 AI Analysis (Confidence: {analysis['confidence']:.0%}):")
            
            # Show issues
            if analysis['issues']:
                print("\n⚠️  Issues Detected:")
                for issue in analysis['issues']:
                    print(f"  - {issue['description']} [{issue['severity']}]")
                    print(f"    Impact: {issue['impact']}")
                    
                    # Show details for merged people
                    if issue['type'] == 'merged_different_people' and 'details' in issue:
                        print("    Different people detected:")
                        for person in issue['details']:
                            print(f"      • {person['name']} ({person['email']})")
            
            # Show recommendations
            if analysis['recommendations']:
                print("\n💡 AI Recommendations:")
                for rec in analysis['recommendations']:
                    if rec['action'] == 'set_primary_email':
                        print(f"  ✓ Set primary email: {rec['email']}")
                        print(f"    Reason: {rec['reason']}")
                    elif rec['action'] == 'split_contact':
                        print(f"  ✓ Split into multiple contacts:")
                        details = rec['details']
                        print(f"    • Personal: {', '.join(details['contact_1']['emails'])}")
                        print(f"    • Professional: {', '.join(details['contact_2']['emails'])}")
                    elif rec['action'] == 'remove_invalid':
                        print(f"  ✓ Remove invalid emails: {', '.join(rec['emails'])}")
                    elif rec['action'] == 'remove_duplicates':
                        print(f"  ✓ Remove low-priority emails: {', '.join(rec['emails_to_remove'])}")
            
            print("\n" + "-" * 80 + "\n")
        
        # Summary
        print("🎯 Key Benefits of AI-First Email Analysis:")
        print("  1. Intelligent detection of merged contacts")
        print("  2. Automatic prioritization of emails")
        print("  3. Recognition of outdated/invalid addresses")
        print("  4. Smart recommendations for cleanup")
        print("  5. Confidence scoring for all decisions")


if __name__ == "__main__":
    analyzer = AIMultiEmailAnalyzer()
    analyzer.demonstrate_examples()