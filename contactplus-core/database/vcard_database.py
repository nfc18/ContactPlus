#!/usr/bin/env python3
"""
VCard Database - Core Database System for ContactPlus

This is the ONLY way to access contact data in ContactPlus.
All vCard operations must go through this database interface.

Features:
- Full version control and audit logging
- Compliance-only storage (all vCards must be RFC compliant)
- Source tracking for all contacts
- Rollback capabilities
- CRUD operations with validation

Architecture:
- VCardDatabase: Main database class
- VCardConnector: Interface for all operations
- Uses vcard library for validation + vobject for manipulation
"""

import os
import json
import logging
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import vcard  # For validation only
import vobject  # For manipulation only
from .vcard_validator import VCardStandardsValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SourceInfo:
    """Metadata about contact source"""
    database_name: str
    source_file: str
    original_index: int
    import_timestamp: str
    import_session_id: str

@dataclass
class ContactRecord:
    """Internal contact record with metadata"""
    contact_id: str
    vcard_data: str
    source_info: SourceInfo
    created_at: str
    updated_at: str
    version: int
    is_active: bool

@dataclass
class DatabaseOperation:
    """Audit log entry for database operations"""
    operation_id: str
    operation_type: str  # 'CREATE', 'UPDATE', 'DELETE', 'IMPORT'
    contact_id: str
    timestamp: str
    user_session: str
    changes: Dict[str, Any]
    rollback_data: Optional[str] = None

class VCardDatabase:
    """
    Core VCard Database with version control and audit logging.
    
    This class manages the master vCard database with:
    - Full compliance validation
    - Source tracking
    - Version control
    - Audit logging
    - Rollback capabilities
    """
    
    def __init__(self, database_path: str = "data/master_database"):
        self.database_path = database_path
        self.contacts_file = os.path.join(database_path, "contacts.vcf")
        self.metadata_file = os.path.join(database_path, "metadata.json")
        self.audit_log_file = os.path.join(database_path, "audit_log.json")
        self.backup_dir = os.path.join(database_path, "backups")
        
        self.validator = VCardStandardsValidator()
        self.contacts = {}  # contact_id -> ContactRecord
        self.audit_log = []
        
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database structure and load existing data"""
        os.makedirs(self.database_path, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Create initial files if they don't exist
        if not os.path.exists(self.metadata_file):
            initial_metadata = {'contacts': {}, 'last_updated': datetime.now().isoformat()}
            with open(self.metadata_file, 'w') as f:
                json.dump(initial_metadata, f, indent=2)
        
        if not os.path.exists(self.audit_log_file):
            initial_log = {'operations': [], 'last_updated': datetime.now().isoformat()}
            with open(self.audit_log_file, 'w') as f:
                json.dump(initial_log, f, indent=2)
        
        # Load existing metadata
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
                contacts_data = metadata.get('contacts', {})
                self.contacts = {}
                for cid, record_data in contacts_data.items():
                    # Convert source_info dict back to SourceInfo object
                    source_info_data = record_data['source_info']
                    source_info = SourceInfo(**source_info_data)
                    record_data['source_info'] = source_info
                    self.contacts[cid] = ContactRecord(**record_data)
        
        # Load existing audit log
        if os.path.exists(self.audit_log_file):
            with open(self.audit_log_file, 'r') as f:
                log_data = json.load(f)
                self.audit_log = [
                    DatabaseOperation(**op) 
                    for op in log_data.get('operations', [])
                ]
        
        logger.info(f"Database initialized: {len(self.contacts)} contacts, {len(self.audit_log)} operations")
    
    def _save_metadata(self):
        """Save metadata to disk"""
        metadata = {
            'contacts': {cid: asdict(record) for cid, record in self.contacts.items()},
            'last_updated': datetime.now().isoformat(),
            'total_contacts': len(self.contacts),
            'active_contacts': len([c for c in self.contacts.values() if c.is_active])
        }
        
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _save_audit_log(self):
        """Save audit log to disk"""
        audit_data = {
            'operations': [asdict(op) for op in self.audit_log],
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.audit_log_file, 'w') as f:
            json.dump(audit_data, f, indent=2)
    
    def _rebuild_contacts_file(self):
        """Rebuild the main contacts.vcf file from active contacts"""
        logger.info("Rebuilding contacts.vcf file...")
        
        # Create backup first
        if os.path.exists(self.contacts_file):
            backup_file = os.path.join(
                self.backup_dir, 
                f"contacts_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.vcf"
            )
            shutil.copy2(self.contacts_file, backup_file)
            logger.info(f"Backup created: {backup_file}")
        
        # Write all active contacts
        with open(self.contacts_file, 'w', encoding='utf-8') as f:
            for contact in self.contacts.values():
                if contact.is_active:
                    f.write(contact.vcard_data)
                    if not contact.vcard_data.endswith('\n'):
                        f.write('\n')
        
        logger.info(f"Contacts file rebuilt with {len([c for c in self.contacts.values() if c.is_active])} contacts")
    
    def _log_operation(self, operation_type: str, contact_id: str, changes: Dict[str, Any], 
                       user_session: str = "system", rollback_data: Optional[str] = None):
        """Log database operation for audit trail"""
        operation = DatabaseOperation(
            operation_id=f"op_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.audit_log)}",
            operation_type=operation_type,
            contact_id=contact_id,
            timestamp=datetime.now().isoformat(),
            user_session=user_session,
            changes=changes,
            rollback_data=rollback_data
        )
        
        self.audit_log.append(operation)
        self._save_audit_log()
        
        logger.info(f"Operation logged: {operation_type} on {contact_id}")
    
    def validate_vcard_compliance(self, vcard_data: str) -> Tuple[bool, List[str], List[str]]:
        """
        Validate vCard for RFC compliance.
        MANDATORY: Only compliant vCards can be stored.
        """
        # Write to temp file for validation
        temp_file = f"/tmp/vcard_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.vcf"
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(vcard_data)
            
            is_valid, errors, warnings = self.validator.validate_file(temp_file)
            return is_valid, errors, warnings
            
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def make_vcard_compliant(self, vcard_data: str, source_info: SourceInfo) -> str:
        """
        Make vCard RFC compliant and add source tracking.
        This is the ONLY modification allowed during import.
        """
        # Parse vCard
        try:
            vcard = list(vobject.readComponents(vcard_data))[0]
        except Exception as e:
            raise ValueError(f"Cannot parse vCard: {e}")
        
        # Add missing required fields
        if not hasattr(vcard, 'version'):
            vcard.add('version').value = '3.0'
        
        if not hasattr(vcard, 'fn') or not vcard.fn.value or not vcard.fn.value.strip():
            # Create FN from N or email
            if hasattr(vcard, 'n') and vcard.n.value:
                n = vcard.n.value
                fn_parts = []
                if hasattr(n, 'given') and n.given:
                    fn_parts.append(n.given)
                if hasattr(n, 'family') and n.family:
                    fn_parts.append(n.family)
                fn_value = ' '.join(fn_parts) if fn_parts else 'Unknown'
            elif hasattr(vcard, 'email_list') and vcard.email_list:
                # Use email username as fallback
                email = vcard.email_list[0].value
                username = email.split('@')[0]
                fn_value = username
            else:
                fn_value = 'Unknown Contact'
            
            # Add or update FN
            if hasattr(vcard, 'fn'):
                vcard.fn.value = fn_value
            else:
                vcard.add('fn').value = fn_value
        
        # Add source tracking (this is the KEY addition)
        vcard.add('x-source-database').value = source_info.database_name
        vcard.add('x-source-file').value = source_info.source_file
        vcard.add('x-source-index').value = str(source_info.original_index)
        vcard.add('x-import-timestamp').value = source_info.import_timestamp
        vcard.add('x-import-session-id').value = source_info.import_session_id
        
        # Serialize back to string
        compliant_vcard = vcard.serialize()
        
        # Final validation
        is_valid, errors, warnings = self.validate_vcard_compliance(compliant_vcard)
        if not is_valid:
            raise ValueError(f"Failed to make vCard compliant: {errors}")
        
        return compliant_vcard

class VCardConnector:
    """
    The ONLY interface for accessing the VCard Database.
    All ContactPlus operations must go through this connector.
    """
    
    def __init__(self, database_path: str = "data/master_database"):
        self.database = VCardDatabase(database_path)
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def import_database(self, source_file: str, database_name: str) -> Dict[str, Any]:
        """
        Import an entire vCard database with compliance validation.
        This is the main import method for the 3 source databases.
        """
        logger.info(f"Importing database: {database_name} from {source_file}")
        
        if not os.path.exists(source_file):
            raise FileNotFoundError(f"Source file not found: {source_file}")
        
        import_session_id = f"import_{database_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Read source file
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into individual vCards
        vcards = []
        current_vcard = []
        for line in content.split('\n'):
            if line.strip() == 'BEGIN:VCARD':
                current_vcard = [line]
            elif line.strip() == 'END:VCARD':
                current_vcard.append(line)
                vcards.append('\n'.join(current_vcard))
                current_vcard = []
            elif current_vcard:
                current_vcard.append(line)
        
        import_results = {
            'database_name': database_name,
            'source_file': source_file,
            'import_session_id': import_session_id,
            'total_contacts': len(vcards),
            'imported_contacts': 0,
            'compliance_fixes': 0,
            'errors': [],
            'contact_ids': []
        }
        
        # Handle malformed content - if no vCards found, treat as error
        if not vcards and content.strip():
            import_results['errors'].append(f"No valid vCard format found in file. Content appears to be malformed.")
        
        # Process each vCard
        for index, vcard_data in enumerate(vcards):
            try:
                # Create source info
                source_info = SourceInfo(
                    database_name=database_name,
                    source_file=source_file,
                    original_index=index,
                    import_timestamp=datetime.now().isoformat(),
                    import_session_id=import_session_id
                )
                
                # Check if compliance fixes needed
                is_valid, errors, warnings = self.database.validate_vcard_compliance(vcard_data)
                
                if not is_valid:
                    # Make compliant
                    compliant_vcard = self.database.make_vcard_compliant(vcard_data, source_info)
                    import_results['compliance_fixes'] += 1
                    logger.info(f"Fixed compliance issues for contact {index}: {errors}")
                else:
                    # Just add source tracking
                    compliant_vcard = self.database.make_vcard_compliant(vcard_data, source_info)
                
                # Generate contact ID
                contact_id = f"{database_name}_{index:06d}"
                
                # Create contact record
                contact_record = ContactRecord(
                    contact_id=contact_id,
                    vcard_data=compliant_vcard,
                    source_info=source_info,
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat(),
                    version=1,
                    is_active=True
                )
                
                # Store in database
                self.database.contacts[contact_id] = contact_record
                
                # Log operation
                self.database._log_operation(
                    operation_type='IMPORT',
                    contact_id=contact_id,
                    changes={'action': 'imported', 'source': database_name},
                    user_session=self.session_id
                )
                
                import_results['imported_contacts'] += 1
                import_results['contact_ids'].append(contact_id)
                
            except Exception as e:
                error_msg = f"Failed to import contact {index}: {e}"
                import_results['errors'].append(error_msg)
                logger.error(error_msg)
        
        # Save database state
        self.database._save_metadata()
        self.database._rebuild_contacts_file()
        
        logger.info(f"Import complete: {import_results['imported_contacts']}/{import_results['total_contacts']} contacts imported")
        return import_results
    
    def get_contact(self, contact_id: str) -> Optional[ContactRecord]:
        """Get a contact by ID"""
        return self.database.contacts.get(contact_id)
    
    def get_all_contacts(self, active_only: bool = True) -> List[ContactRecord]:
        """Get all contacts"""
        if active_only:
            return [c for c in self.database.contacts.values() if c.is_active]
        return list(self.database.contacts.values())
    
    def update_contact(self, contact_id: str, updated_vcard_data: str) -> bool:
        """
        Update an existing contact with new vCard data.
        Validates compliance and logs the operation.
        """
        if contact_id not in self.database.contacts:
            return False
        
        contact = self.database.contacts[contact_id]
        
        # Validate new vCard data
        is_valid, errors, warnings = self.database.validate_vcard_compliance(updated_vcard_data)
        if not is_valid:
            raise ValueError(f"Updated vCard is not compliant: {errors}")
        
        # Store old data for rollback
        old_vcard_data = contact.vcard_data
        
        # Update contact
        contact.vcard_data = updated_vcard_data
        contact.updated_at = datetime.now().isoformat()
        contact.version += 1
        
        # Log operation
        self.database._log_operation(
            operation_type='UPDATE',
            contact_id=contact_id,
            changes={'action': 'updated', 'version': contact.version},
            user_session=self.session_id,
            rollback_data=old_vcard_data
        )
        
        # Save changes
        self.database._save_metadata()
        self.database._rebuild_contacts_file()
        
        logger.info(f"Contact {contact_id} updated to version {contact.version}")
        return True
    
    def delete_contact(self, contact_id: str) -> bool:
        """
        Delete a contact (soft delete - marks as inactive).
        Maintains audit trail and allows recovery.
        """
        if contact_id not in self.database.contacts:
            return False
        
        contact = self.database.contacts[contact_id]
        if not contact.is_active:
            return False  # Already deleted
        
        # Store data for rollback
        rollback_data = contact.vcard_data
        
        # Soft delete
        contact.is_active = False
        contact.updated_at = datetime.now().isoformat()
        contact.version += 1
        
        # Log operation
        self.database._log_operation(
            operation_type='DELETE',
            contact_id=contact_id,
            changes={'action': 'soft_deleted', 'version': contact.version},
            user_session=self.session_id,
            rollback_data=rollback_data
        )
        
        # Save changes
        self.database._save_metadata()
        self.database._rebuild_contacts_file()
        
        logger.info(f"Contact {contact_id} deleted (soft delete)")
        return True
    
    def restore_contact(self, contact_id: str) -> bool:
        """
        Restore a soft-deleted contact.
        """
        if contact_id not in self.database.contacts:
            return False
        
        contact = self.database.contacts[contact_id]
        if contact.is_active:
            return False  # Not deleted
        
        # Restore
        contact.is_active = True
        contact.updated_at = datetime.now().isoformat()
        contact.version += 1
        
        # Log operation
        self.database._log_operation(
            operation_type='RESTORE',
            contact_id=contact_id,
            changes={'action': 'restored', 'version': contact.version},
            user_session=self.session_id
        )
        
        # Save changes
        self.database._save_metadata()
        self.database._rebuild_contacts_file()
        
        logger.info(f"Contact {contact_id} restored")
        return True

    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        active_contacts = [c for c in self.database.contacts.values() if c.is_active]
        
        # Group by source database
        by_source = {}
        for contact in active_contacts:
            source = contact.source_info.database_name
            by_source[source] = by_source.get(source, 0) + 1
        
        return {
            'total_contacts': len(self.database.contacts),
            'active_contacts': len(active_contacts),
            'contacts_by_source': by_source,
            'total_operations': len(self.database.audit_log),
            'database_file': self.database.contacts_file,
            'last_operation': self.database.audit_log[-1].timestamp if self.database.audit_log else None
        }

def create_master_database_from_sources():
    """
    Main function to create the master database from the 3 source files.
    This implements the exact architecture you described.
    """
    print("🗄️ CREATING MASTER VCARD DATABASE")
    print("=" * 50)
    
    # Initialize connector
    connector = VCardConnector()
    
    # Source databases to import
    source_databases = {
        'sara_export': 'Imports/Sara_Export_Sara A. Kerner and 3.074 others.vcf',
        'iphone_contacts': 'Imports/iPhone_Contacts_Contacts.vcf', 
        'iphone_suggested': 'Imports/iPhone_Suggested_Suggested Contacts.vcf'
    }
    
    total_imported = 0
    total_compliance_fixes = 0
    
    # Import each database
    for db_name, db_file in source_databases.items():
        if os.path.exists(db_file):
            print(f"\n📥 Importing {db_name}...")
            try:
                result = connector.import_database(db_file, db_name)
                
                print(f"   ✅ {result['imported_contacts']}/{result['total_contacts']} contacts imported")
                print(f"   🔧 {result['compliance_fixes']} compliance fixes applied")
                
                total_imported += result['imported_contacts']
                total_compliance_fixes += result['compliance_fixes']
                
                if result['errors']:
                    print(f"   ⚠️ {len(result['errors'])} errors occurred")
                
            except Exception as e:
                print(f"   ❌ Import failed: {e}")
        else:
            print(f"   ⚠️ File not found: {db_file}")
    
    # Final statistics
    stats = connector.get_database_stats()
    
    print(f"\n🎉 MASTER DATABASE CREATED!")
    print("-" * 30)
    print(f"Total contacts imported: {total_imported:,}")
    print(f"Compliance fixes applied: {total_compliance_fixes}")
    print(f"Active contacts: {stats['active_contacts']:,}")
    print(f"Database file: {stats['database_file']}")
    
    print(f"\n📊 Contacts by source:")
    for source, count in stats['contacts_by_source'].items():
        print(f"   {source}: {count:,} contacts")
    
    print(f"\n✅ Architecture implemented:")
    print(f"   • VCard Database with version control")
    print(f"   • VCardConnector as single access point") 
    print(f"   • Full compliance validation")
    print(f"   • Source tracking for all contacts")
    print(f"   • Audit logging for all operations")
    
    return connector

if __name__ == "__main__":
    # Create the master database
    connector = create_master_database_from_sources()