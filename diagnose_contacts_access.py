#!/usr/bin/env python3
"""
Diagnose macOS Contacts access and permissions
"""

import Contacts
from Foundation import NSString

def diagnose_contacts_access():
    """Diagnose contacts access and show detailed information"""
    
    print("🔍 CONTACTS ACCESS DIAGNOSIS")
    print("=" * 60)
    
    # Check authorization status
    auth_status = Contacts.CNContactStore.authorizationStatusForEntityType_(Contacts.CNEntityTypeContacts)
    
    status_names = {
        0: "Not Determined",
        1: "Restricted", 
        2: "Denied",
        3: "Authorized"
    }
    
    print(f"📱 Authorization Status: {status_names.get(auth_status, 'Unknown')} ({auth_status})")
    
    if auth_status != Contacts.CNAuthorizationStatusAuthorized:
        print("❌ Access not fully authorized")
        if auth_status == Contacts.CNAuthorizationStatusDenied:
            print("💡 Enable access in: System Preferences > Privacy & Security > Contacts")
        return
    
    # Create contact store
    store = Contacts.CNContactStore.alloc().init()
    
    try:
        # Test with minimal keys first
        basic_keys = [Contacts.CNContactGivenNameKey, Contacts.CNContactFamilyNameKey]
        fetch_request = Contacts.CNContactFetchRequest.alloc().initWithKeysToFetch_(basic_keys)
        
        contact_count = 0
        sample_contacts = []
        
        def count_handler(contact, stop):
            nonlocal contact_count
            contact_count += 1
            
            if contact_count <= 5:  # Collect first 5 as samples
                given_name = str(contact.givenName()) if contact.givenName() else ''
                family_name = str(contact.familyName()) if contact.familyName() else ''
                full_name = f"{given_name} {family_name}".strip() or "No Name"
                sample_contacts.append(full_name)
            
            return True
        
        # Count all contacts
        success = store.enumerateContactsWithFetchRequest_error_usingBlock_(
            fetch_request, None, count_handler
        )
        
        if success:
            print(f"✅ Successfully accessed {contact_count} contacts")
            print(f"📝 Sample contacts:")
            for i, name in enumerate(sample_contacts, 1):
                print(f"   {i}. {name}")
                
            if contact_count > 5:
                print(f"   ... and {contact_count - 5} more")
                
        else:
            print("❌ Failed to enumerate contacts")
            
    except Exception as e:
        print(f"❌ Error accessing contacts: {e}")
        print(f"   Error type: {type(e)}")
    
    # Check container access
    try:
        print(f"\n📦 Checking containers...")
        containers = store.containersMatchingPredicate_error_(None, None)
        print(f"   Found {len(containers)} containers")
        
        for i, container in enumerate(containers):
            name = str(container.name()) if container.name() else 'Unnamed'
            container_type = container.type()
            print(f"   {i+1}. {name} (type: {container_type})")
            
    except Exception as e:
        print(f"⚠️  Could not check containers: {e}")
    
    # Check groups
    try:
        print(f"\n👥 Checking groups...")
        groups = store.groupsMatchingPredicate_error_(None, None)
        print(f"   Found {len(groups)} groups")
        
        for i, group in enumerate(groups[:3]):  # Show first 3
            name = str(group.name()) if group.name() else 'Unnamed'
            print(f"   {i+1}. {name}")
            
    except Exception as e:
        print(f"⚠️  Could not check groups: {e}")

if __name__ == "__main__":
    diagnose_contacts_access()