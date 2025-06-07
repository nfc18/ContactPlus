"""
Database connector wrapper for FastAPI integration
"""
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
import vobject

from .vcard_database import VCardConnector as BaseConnector, ContactRecord
from models.schemas import Contact, SourceInfo


class APIConnector:
    """API-friendly wrapper for VCardConnector"""
    
    def __init__(self, database_path: str = None):
        if database_path is None:
            database_path = os.environ.get('DATABASE_PATH', 'data/master_database')
        self.connector = BaseConnector(database_path)
    
    def _record_to_model(self, record: ContactRecord) -> Contact:
        """Convert internal ContactRecord to API Contact model"""
        # Parse vCard data to extract fields
        try:
            vcard = list(vobject.readComponents(record.vcard_data))[0]
            
            # Extract emails
            emails = []
            if hasattr(vcard, 'email_list'):
                emails = [email.value for email in vcard.email_list]
            
            # Extract phones
            phones = []
            if hasattr(vcard, 'tel_list'):
                phones = [tel.value for tel in vcard.tel_list]
            
            # Extract other fields
            organization = None
            if hasattr(vcard, 'org') and vcard.org.value:
                organization = str(vcard.org.value[0]) if isinstance(vcard.org.value, list) else str(vcard.org.value)
            
            title = None
            if hasattr(vcard, 'title') and vcard.title.value:
                title = vcard.title.value
            
            notes = None
            if hasattr(vcard, 'note') and vcard.note.value:
                notes = vcard.note.value
            
            # Convert source info
            source_info = SourceInfo(
                database_name=record.source_info.database_name,
                source_file=record.source_info.source_file,
                original_index=record.source_info.original_index,
                import_timestamp=record.source_info.import_timestamp,
                import_session_id=record.source_info.import_session_id
            )
            
            return Contact(
                contact_id=record.contact_id,
                fn=vcard.fn.value if hasattr(vcard, 'fn') else "Unknown",
                emails=emails,
                phones=phones,
                organization=organization,
                title=title,
                notes=notes,
                source_info=source_info,
                created_at=datetime.fromisoformat(record.created_at),
                updated_at=datetime.fromisoformat(record.updated_at),
                version=record.version,
                is_active=record.is_active
            )
        except Exception as e:
            # Fallback if parsing fails
            raise ValueError(f"Failed to parse contact {record.contact_id}: {str(e)}")
    
    def get_contact(self, contact_id: str) -> Optional[Contact]:
        """Get a single contact by ID"""
        record = self.connector.get_contact(contact_id)
        if record:
            return self._record_to_model(record)
        return None
    
    def get_all_contacts(self, 
                        page: int = 1, 
                        page_size: int = 50,
                        active_only: bool = True) -> Dict[str, Any]:
        """Get paginated contacts"""
        all_records = self.connector.get_all_contacts(active_only=active_only)
        
        # Calculate pagination
        total = len(all_records)
        start = (page - 1) * page_size
        end = start + page_size
        
        # Get page of records
        page_records = all_records[start:end]
        contacts = [self._record_to_model(record) for record in page_records]
        
        return {
            "contacts": contacts,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    def search_contacts(self, 
                       query: str,
                       search_fields: List[str],
                       page: int = 1,
                       page_size: int = 50) -> Dict[str, Any]:
        """Search contacts by query"""
        all_records = self.connector.get_all_contacts(active_only=True)
        
        # Filter records based on search
        matching_records = []
        query_lower = query.lower()
        
        for record in all_records:
            try:
                vcard = list(vobject.readComponents(record.vcard_data))[0]
                
                # Check each search field
                match = False
                for field in search_fields:
                    if field == "fn" and hasattr(vcard, 'fn'):
                        if query_lower in vcard.fn.value.lower():
                            match = True
                            break
                    elif field == "email" and hasattr(vcard, 'email_list'):
                        for email in vcard.email_list:
                            if query_lower in email.value.lower():
                                match = True
                                break
                    elif field == "phone" and hasattr(vcard, 'tel_list'):
                        for tel in vcard.tel_list:
                            if query in tel.value.replace("-", "").replace(" ", ""):
                                match = True
                                break
                    elif field == "organization" and hasattr(vcard, 'org'):
                        org_value = str(vcard.org.value[0]) if isinstance(vcard.org.value, list) else str(vcard.org.value)
                        if query_lower in org_value.lower():
                            match = True
                            break
                
                if match:
                    matching_records.append(record)
                    
            except Exception:
                continue
        
        # Apply pagination
        total = len(matching_records)
        start = (page - 1) * page_size
        end = start + page_size
        page_records = matching_records[start:end]
        
        contacts = [self._record_to_model(record) for record in page_records]
        
        return {
            "contacts": contacts,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    def update_contact(self, contact_id: str, update_data: dict) -> bool:
        """Update a contact with new data"""
        # Get existing contact
        record = self.connector.get_contact(contact_id)
        if not record:
            return False
        
        # Parse existing vCard
        vcard = list(vobject.readComponents(record.vcard_data))[0]
        
        # Update fields
        if 'fn' in update_data and update_data['fn']:
            vcard.fn.value = update_data['fn']
        
        if 'emails' in update_data:
            # Remove existing emails
            if hasattr(vcard, 'email_list'):
                for email in vcard.email_list:
                    vcard.remove(email)
            # Add new emails
            for email in update_data['emails']:
                vcard.add('email').value = email
        
        if 'phones' in update_data:
            # Remove existing phones
            if hasattr(vcard, 'tel_list'):
                for tel in vcard.tel_list:
                    vcard.remove(tel)
            # Add new phones
            for phone in update_data['phones']:
                vcard.add('tel').value = phone
        
        if 'organization' in update_data:
            if hasattr(vcard, 'org'):
                vcard.org.value = [update_data['organization']]
            else:
                vcard.add('org').value = [update_data['organization']]
        
        if 'title' in update_data:
            if hasattr(vcard, 'title'):
                vcard.title.value = update_data['title']
            else:
                vcard.add('title').value = update_data['title']
        
        if 'notes' in update_data:
            if hasattr(vcard, 'note'):
                vcard.note.value = update_data['notes']
            else:
                vcard.add('note').value = update_data['notes']
        
        # Update in database
        return self.connector.update_contact(contact_id, vcard.serialize())
    
    def delete_contact(self, contact_id: str) -> bool:
        """Delete (soft delete) a contact"""
        return self.connector.delete_contact(contact_id)
    
    def import_database(self, source_file: str, database_name: str) -> Dict[str, Any]:
        """Import a vCard database"""
        return self.connector.import_database(source_file, database_name)
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return self.connector.get_database_stats()
    
    def export_database(self, active_only: bool = True) -> str:
        """Export database as vCard file"""
        contacts = self.connector.get_all_contacts(active_only=active_only)
        
        # Combine all vCards
        vcf_content = ""
        for contact in contacts:
            vcf_content += contact.vcard_data
            if not contact.vcard_data.endswith('\n'):
                vcf_content += '\n'
        
        return vcf_content