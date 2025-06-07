#!/usr/bin/env python3
"""
AI-Powered Cross-Database Duplicate Detection

This module uses AI intelligence to detect duplicates ACROSS multiple databases
after they've been individually cleaned. Focuses on data quality and consolidation.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import vobject
from difflib import SequenceMatcher
from contact_intelligence import ContactIntelligenceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DuplicateMatch:
    """Represents a potential duplicate match between contacts"""
    contact1_id: str
    contact2_id: str
    contact1_source: str
    contact2_source: str
    match_type: str  # 'exact', 'fuzzy', 'conflict'
    confidence: float
    matching_fields: List[str]
    conflicting_fields: List[str]
    recommended_action: str
    reasoning: str

@dataclass
class MergeDecision:
    """Represents a decision on how to merge duplicate contacts"""
    primary_contact_id: str
    secondary_contact_ids: List[str]
    field_preferences: Dict[str, str]  # field -> source preference
    merge_strategy: str
    confidence: float
    requires_review: bool

class CrossDatabaseDuplicateDetector:
    """
    AI-powered duplicate detection across multiple cleaned databases.
    
    Uses multiple strategies:
    1. Exact matching (same name + email/phone)
    2. Fuzzy matching (similar names + overlapping info)
    3. AI analysis for complex cases
    """
    
    def __init__(self, use_ai: bool = True):
        self.use_ai = use_ai
        self.ai_engine = ContactIntelligenceEngine(use_openai=use_ai) if use_ai else None
        self.contacts_by_database = {}
        self.all_contacts = []
        
    def analyze_across_databases(self, database_files: List[str]) -> Dict[str, Any]:
        """
        Analyze duplicates across multiple cleaned databases.
        
        Args:
            database_files: List of cleaned vCard files to analyze
            
        Returns:
            Comprehensive duplicate analysis report
        """
        logger.info(f"🔍 Analyzing duplicates across {len(database_files)} databases")
        
        # Load all contacts from databases
        self._load_all_databases(database_files)
        
        # Find potential duplicates
        potential_duplicates = self._find_potential_duplicates()
        
        # Classify matches
        exact_matches = []
        fuzzy_matches = []
        conflicts = []
        
        for match in potential_duplicates:
            if match.match_type == 'exact':
                exact_matches.append(match)
            elif match.match_type == 'fuzzy':
                fuzzy_matches.append(match)
            else:
                conflicts.append(match)
        
        # Generate merge recommendations
        merge_recommendations = self._generate_merge_recommendations(potential_duplicates)
        
        # Calculate statistics
        total_contacts = len(self.all_contacts)
        duplicate_contacts = len(exact_matches) + len(fuzzy_matches)
        unique_contacts = total_contacts - duplicate_contacts
        
        analysis_report = {
            'timestamp': datetime.now().isoformat(),
            'databases_analyzed': database_files,
            'total_contacts': total_contacts,
            'contacts_by_database': {db: len(contacts) for db, contacts in self.contacts_by_database.items()},
            'duplicate_analysis': {
                'exact_matches': len(exact_matches),
                'fuzzy_matches': len(fuzzy_matches),
                'conflicts_requiring_review': len(conflicts),
                'estimated_unique_contacts': unique_contacts,
                'deduplication_potential': f"{duplicate_contacts}/{total_contacts} contacts can be merged"
            },
            'exact_matches': [self._match_to_dict(m) for m in exact_matches[:20]],  # Sample
            'fuzzy_matches': [self._match_to_dict(m) for m in fuzzy_matches[:20]],  # Sample
            'conflicts': [self._match_to_dict(m) for m in conflicts[:10]],  # Sample
            'merge_recommendations': [self._recommendation_to_dict(r) for r in merge_recommendations[:20]]
        }
        
        # Save detailed report
        report_file = f"data/DUPLICATE_ANALYSIS_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(analysis_report, f, indent=2)
        
        analysis_report['report_file'] = report_file
        
        logger.info(f"✅ Duplicate analysis complete: {duplicate_contacts} duplicates found in {total_contacts} contacts")
        return analysis_report
    
    def _load_all_databases(self, database_files: List[str]):
        """Load contacts from all database files"""
        self.contacts_by_database = {}
        self.all_contacts = []
        
        for db_file in database_files:
            db_name = os.path.basename(db_file).replace('.vcf', '')
            
            logger.info(f"Loading {db_name}...")
            
            try:
                with open(db_file, 'r', encoding='utf-8') as f:
                    vcards = list(vobject.readComponents(f.read()))
                
                contacts = []
                for i, vcard in enumerate(vcards):
                    contact = {
                        'id': f"{db_name}_{i}",
                        'source_database': db_name,
                        'source_file': db_file,
                        'index_in_source': i,
                        'vcard': vcard,
                        'data': self._extract_contact_data(vcard)
                    }
                    contacts.append(contact)
                    self.all_contacts.append(contact)
                
                self.contacts_by_database[db_name] = contacts
                logger.info(f"  Loaded {len(contacts)} contacts from {db_name}")
                
            except Exception as e:
                logger.error(f"Failed to load {db_file}: {e}")
    
    def _extract_contact_data(self, vcard: vobject.vCard) -> Dict[str, Any]:
        """Extract searchable data from vCard"""
        data = {
            'name': vcard.fn.value if hasattr(vcard, 'fn') else '',
            'emails': [],
            'phones': [],
            'organizations': [],
            'note': ''
        }
        
        # Extract emails
        if hasattr(vcard, 'email_list'):
            data['emails'] = [email.value.lower() for email in vcard.email_list]
        
        # Extract phones
        if hasattr(vcard, 'tel_list'):
            data['phones'] = [tel.value for tel in vcard.tel_list]
        
        # Extract organizations
        if hasattr(vcard, 'org'):
            org_values = vcard.org.value
            if isinstance(org_values, list):
                data['organizations'] = [str(v) for v in org_values]
            else:
                data['organizations'] = [str(org_values)]
        
        # Extract note
        if hasattr(vcard, 'note'):
            data['note'] = vcard.note.value
        
        return data
    
    def _find_potential_duplicates(self) -> List[DuplicateMatch]:
        """Find potential duplicates using multiple strategies"""
        logger.info("🔍 Finding potential duplicates...")
        
        potential_duplicates = []
        
        # Compare each contact with all others
        for i, contact1 in enumerate(self.all_contacts):
            for j, contact2 in enumerate(self.all_contacts[i+1:], i+1):
                # Skip same database comparisons for now (focus on cross-database)
                if contact1['source_database'] == contact2['source_database']:
                    continue
                
                match = self._compare_contacts(contact1, contact2)
                if match:
                    potential_duplicates.append(match)
        
        logger.info(f"Found {len(potential_duplicates)} potential duplicate pairs")
        return potential_duplicates
    
    def _compare_contacts(self, contact1: Dict, contact2: Dict) -> Optional[DuplicateMatch]:
        """Compare two contacts for potential duplication"""
        
        data1 = contact1['data']
        data2 = contact2['data']
        
        matching_fields = []
        conflicting_fields = []
        
        # Check name similarity
        name_similarity = SequenceMatcher(None, data1['name'].lower(), data2['name'].lower()).ratio()
        
        # Check email overlap
        email_overlap = set(data1['emails']) & set(data2['emails'])
        
        # Check phone overlap
        phone_overlap = set(data1['phones']) & set(data2['phones'])
        
        # Determine match type and confidence
        if email_overlap and name_similarity > 0.8:
            # Strong match - same email and similar name
            match_type = 'exact'
            confidence = 0.95
            matching_fields = ['email', 'name']
        elif phone_overlap and name_similarity > 0.8:
            # Strong match - same phone and similar name
            match_type = 'exact'
            confidence = 0.90
            matching_fields = ['phone', 'name']
        elif name_similarity > 0.9 and (email_overlap or phone_overlap):
            # Very similar names with some contact overlap
            match_type = 'fuzzy'
            confidence = 0.85
            matching_fields = ['name']
            if email_overlap:
                matching_fields.append('email')
            if phone_overlap:
                matching_fields.append('phone')
        elif name_similarity > 0.95:
            # Very similar names but no contact overlap - potential conflict
            match_type = 'conflict'
            confidence = 0.75
            matching_fields = ['name']
            conflicting_fields = ['contact_info']
        else:
            # No significant match
            return None
        
        # Determine recommended action
        if match_type == 'exact':
            recommended_action = 'auto_merge'
        elif match_type == 'fuzzy':
            recommended_action = 'review_merge'
        else:
            recommended_action = 'manual_review'
        
        reasoning = f"Name similarity: {name_similarity:.2f}, Email overlap: {len(email_overlap)}, Phone overlap: {len(phone_overlap)}"
        
        return DuplicateMatch(
            contact1_id=contact1['id'],
            contact2_id=contact2['id'],
            contact1_source=contact1['source_database'],
            contact2_source=contact2['source_database'],
            match_type=match_type,
            confidence=confidence,
            matching_fields=matching_fields,
            conflicting_fields=conflicting_fields,
            recommended_action=recommended_action,
            reasoning=reasoning
        )
    
    def _generate_merge_recommendations(self, potential_duplicates: List[DuplicateMatch]) -> List[MergeDecision]:
        """Generate intelligent merge recommendations"""
        logger.info("🎯 Generating merge recommendations...")
        
        recommendations = []
        
        # Group duplicates by primary contact
        duplicate_groups = {}
        for match in potential_duplicates:
            if match.recommended_action == 'auto_merge':
                primary_id = match.contact1_id
                if primary_id not in duplicate_groups:
                    duplicate_groups[primary_id] = []
                duplicate_groups[primary_id].append(match.contact2_id)
        
        # Create merge decisions
        for primary_id, duplicate_ids in duplicate_groups.items():
            # Determine field preferences based on source reliability
            field_preferences = {
                'name': 'most_complete',
                'emails': 'merge_all',
                'phones': 'merge_all',
                'organizations': 'most_recent',
                'photo': 'highest_quality'
            }
            
            recommendation = MergeDecision(
                primary_contact_id=primary_id,
                secondary_contact_ids=duplicate_ids,
                field_preferences=field_preferences,
                merge_strategy='intelligent_merge',
                confidence=0.90,
                requires_review=False
            )
            recommendations.append(recommendation)
        
        logger.info(f"Generated {len(recommendations)} merge recommendations")
        return recommendations
    
    def _match_to_dict(self, match: DuplicateMatch) -> Dict[str, Any]:
        """Convert DuplicateMatch to dictionary for JSON serialization"""
        return {
            'contact1_id': match.contact1_id,
            'contact2_id': match.contact2_id,
            'contact1_source': match.contact1_source,
            'contact2_source': match.contact2_source,
            'match_type': match.match_type,
            'confidence': match.confidence,
            'matching_fields': match.matching_fields,
            'conflicting_fields': match.conflicting_fields,
            'recommended_action': match.recommended_action,
            'reasoning': match.reasoning
        }
    
    def _recommendation_to_dict(self, recommendation: MergeDecision) -> Dict[str, Any]:
        """Convert MergeDecision to dictionary for JSON serialization"""
        return {
            'primary_contact_id': recommendation.primary_contact_id,
            'secondary_contact_ids': recommendation.secondary_contact_ids,
            'field_preferences': recommendation.field_preferences,
            'merge_strategy': recommendation.merge_strategy,
            'confidence': recommendation.confidence,
            'requires_review': recommendation.requires_review
        }

def analyze_database_duplicates(database_files: List[str]) -> Dict[str, Any]:
    """
    Convenience function to analyze duplicates across databases.
    
    Args:
        database_files: List of cleaned vCard database files
        
    Returns:
        Comprehensive duplicate analysis report
    """
    detector = CrossDatabaseDuplicateDetector(use_ai=True)
    return detector.analyze_across_databases(database_files)

if __name__ == "__main__":
    # Demo the duplicate detection
    print("🔍 Cross-Database Duplicate Detection Demo")
    print("=" * 50)
    
    # Test with available databases
    available_databases = []
    
    # Check for cleaned databases first
    cleaned_files = [
        'Sara_Export_Sara A. Kerner and 3.074 others_AI_CLEANED.vcf',
        'iPhone_Contacts_Contacts_AI_CLEANED.vcf',
        'iPhone_Suggested_Suggested Contacts_AI_CLEANED.vcf'
    ]
    
    for file in cleaned_files:
        if os.path.exists(file):
            available_databases.append(file)
    
    # Fallback to original files for demo
    if not available_databases:
        original_files = [
            'Imports/Sara_Export_Sara A. Kerner and 3.074 others.vcf',
            'Imports/iPhone_Contacts_Contacts.vcf',
            'Imports/iPhone_Suggested_Suggested Contacts.vcf'
        ]
        
        for file in original_files:
            if os.path.exists(file):
                available_databases.append(file)
    
    if available_databases:
        print(f"📊 Analyzing {len(available_databases)} databases:")
        for db in available_databases:
            print(f"   • {db}")
        
        try:
            # Run duplicate analysis
            analysis = analyze_database_duplicates(available_databases)
            
            print(f"\n🎯 DUPLICATE ANALYSIS RESULTS:")
            print(f"   Total contacts: {analysis['total_contacts']:,}")
            print(f"   Exact matches: {analysis['duplicate_analysis']['exact_matches']}")
            print(f"   Fuzzy matches: {analysis['duplicate_analysis']['fuzzy_matches']}")
            print(f"   Conflicts: {analysis['duplicate_analysis']['conflicts_requiring_review']}")
            print(f"   Estimated unique: {analysis['duplicate_analysis']['estimated_unique_contacts']:,}")
            
            print(f"\n📄 Detailed report: {analysis['report_file']}")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            logger.error(f"Duplicate analysis error: {e}")
    else:
        print("❌ No database files found for analysis")
        print("Please run AI-First cleaning first or check file paths")