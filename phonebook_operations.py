#!/usr/bin/env python3
"""
Phonebook operations with automatic validation

🔒 CRITICAL: This module implements the MANDATORY phonebook editing protocol
defined in PHONEBOOK_EDITING_PROTOCOL.md. This process MUST be followed
exactly for ALL phonebook modifications. NO EXCEPTIONS.
"""

import vobject
import os
from datetime import datetime
from auto_validate import validate_phonebook
import shutil

class PhonebookManager:
    """Manage phonebook operations with automatic validation"""
    
    def __init__(self):
        self.current_master = self._find_latest_master()
        if self.current_master:
            print(f"📱 Current master: {os.path.basename(self.current_master)}")
            self._validate_current()
        else:
            print("❌ No master phonebook found")
    
    def _find_latest_master(self):
        """Find the latest master phonebook"""
        import glob
        masters = glob.glob("data/MASTER_PHONEBOOK_*.vcf")
        if masters:
            return sorted(masters)[-1]
        
        # Fallback to final master
        final_masters = glob.glob("data/FINAL_MASTER_CONTACTS_*.vcf")
        if final_masters:
            return sorted(final_masters)[-1]
        
        return None
    
    def _validate_current(self):
        """Validate current master"""
        return validate_phonebook(self.current_master, "initialization")
    
    def _backup_current(self):
        """Create backup of current master"""
        if not self.current_master:
            return None
        
        backup_dir = "backup"
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_{os.path.basename(self.current_master)}_{timestamp}"
        backup_path = os.path.join(backup_dir, backup_name)
        
        shutil.copy2(self.current_master, backup_path)
        print(f"💾 Backup created: {backup_path}")
        return backup_path
    
    def _save_new_master(self, contacts, operation_name):
        """Save new master with validation"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_path = f"data/MASTER_PHONEBOOK_{timestamp}.vcf"
        
        with open(new_path, 'w', encoding='utf-8') as f:
            for contact in contacts:
                f.write(contact.serialize())
        
        # Validate immediately
        if validate_phonebook(new_path, operation_name):
            self.current_master = new_path
            print(f"✅ New master saved: {os.path.basename(new_path)}")
            return new_path
        else:
            print(f"❌ Validation failed! Removing invalid file: {new_path}")
            os.remove(new_path)
            return None
    
    def add_contact(self, contact_vcard, operation_name="add contact"):
        """Add a contact with validation"""
        if not self.current_master:
            print("❌ No current master to modify")
            return False
        
        # Backup current
        self._backup_current()
        
        # Load current contacts
        with open(self.current_master, 'r', encoding='utf-8') as f:
            contacts = list(vobject.readComponents(f.read()))
        
        print(f"Adding contact to {len(contacts)} existing contacts...")
        
        # Add new contact
        contacts.append(contact_vcard)
        
        # Save and validate
        new_path = self._save_new_master(contacts, operation_name)
        return new_path is not None
    
    def remove_contact(self, contact_name, operation_name="remove contact"):
        """Remove a contact by name with validation"""
        if not self.current_master:
            print("❌ No current master to modify")
            return False
        
        # Backup current
        self._backup_current()
        
        # Load current contacts
        with open(self.current_master, 'r', encoding='utf-8') as f:
            contacts = list(vobject.readComponents(f.read()))
        
        # Find and remove contact
        removed_count = 0
        remaining_contacts = []
        
        for contact in contacts:
            name = contact.fn.value if hasattr(contact, 'fn') else 'No name'
            if contact_name.lower() in name.lower():
                print(f"Removing: {name}")
                removed_count += 1
            else:
                remaining_contacts.append(contact)
        
        if removed_count == 0:
            print(f"❌ No contacts found matching '{contact_name}'")
            return False
        
        print(f"Removed {removed_count} contacts, {len(remaining_contacts)} remaining")
        
        # Save and validate
        new_path = self._save_new_master(remaining_contacts, f"{operation_name} (removed {removed_count})")
        return new_path is not None
    
    def get_stats(self):
        """Get phonebook statistics"""
        if not self.current_master:
            return None
        
        with open(self.current_master, 'r', encoding='utf-8') as f:
            contacts = list(vobject.readComponents(f.read()))
        
        stats = {
            'total_contacts': len(contacts),
            'with_email': 0,
            'with_phone': 0,
            'with_org': 0,
            'total_emails': 0,
            'total_phones': 0
        }
        
        for contact in contacts:
            if hasattr(contact, 'email_list') and contact.email_list:
                stats['with_email'] += 1
                stats['total_emails'] += len(contact.email_list)
            
            if hasattr(contact, 'tel_list') and contact.tel_list:
                stats['with_phone'] += 1
                stats['total_phones'] += len(contact.tel_list)
            
            if hasattr(contact, 'org') and contact.org.value:
                stats['with_org'] += 1
        
        return stats

def create_contact(name, emails=None, phones=None, org=None):
    """Helper to create a vCard contact"""
    contact = vobject.vCard()
    contact.add('version')
    contact.version.value = '3.0'
    
    # Name
    contact.add('fn')
    contact.fn.value = name
    
    # Parse name for N field
    name_parts = name.split()
    if len(name_parts) >= 2:
        contact.add('n')
        contact.n.value = vobject.vcard.Name(
            family=name_parts[-1],
            given=' '.join(name_parts[:-1])
        )
    else:
        contact.add('n')
        contact.n.value = vobject.vcard.Name(family='', given=name)
    
    # Emails
    if emails:
        for email in emails:
            contact.add('email')
            contact.email.value = email
    
    # Phones
    if phones:
        for phone in phones:
            contact.add('tel')
            contact.tel.value = phone
    
    # Organization
    if org:
        contact.add('org')
        contact.org.value = org
    
    return contact

if __name__ == "__main__":
    # Test the manager
    manager = PhonebookManager()
    if manager.current_master:
        stats = manager.get_stats()
        print(f"\n📊 Current phonebook stats:")
        for key, value in stats.items():
            print(f"   {key}: {value}")