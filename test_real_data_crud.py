#!/usr/bin/env python3
"""
Comprehensive Real Data CRUD Testing

Tests the VCard Database with real data from the 3 source databases:
1. Import 50 contacts from each database (150 total)
2. Verify reading consistency 
3. Edit 25 contacts with various field modifications
4. Verify edits are persisted correctly
5. Delete 25 contacts and verify deletion
6. Test restore functionality

This validates the database works perfectly with real contact data.
"""

import os
import json
import shutil
import tempfile
from datetime import datetime
from typing import List, Dict, Any
import vobject
from vcard_database import VCardConnector, VCardDatabase

def extract_random_n_contacts(source_file: str, n: int = 50) -> List[str]:
    """Extract N random contacts from a vCard file"""
    import random
    
    if not os.path.exists(source_file):
        return []
    
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into individual vCards
    all_vcards = []
    current_vcard = []
    for line in content.split('\n'):
        if line.strip() == 'BEGIN:VCARD':
            current_vcard = [line]
        elif line.strip() == 'END:VCARD':
            current_vcard.append(line)
            all_vcards.append('\n'.join(current_vcard))
            current_vcard = []
        elif current_vcard:
            current_vcard.append(line)
    
    # Return random selection
    if len(all_vcards) <= n:
        return all_vcards
    
    # Use fixed seed for reproducible tests
    random.seed(42)
    return random.sample(all_vcards, n)

def modify_vcard_fields(vcard_data: str, modifications: Dict[str, str]) -> str:
    """Modify various fields in a vCard"""
    try:
        vcard = list(vobject.readComponents(vcard_data))[0]
        
        # Apply modifications
        for field, new_value in modifications.items():
            if field == 'fn':
                if hasattr(vcard, 'fn'):
                    vcard.fn.value = new_value
                else:
                    vcard.add('fn').value = new_value
            elif field == 'email':
                # Add new email or modify existing
                vcard.add('email').value = new_value
            elif field == 'tel':
                # Add new phone or modify existing
                vcard.add('tel').value = new_value
            elif field == 'org':
                if hasattr(vcard, 'org'):
                    vcard.org.value = new_value
                else:
                    vcard.add('org').value = new_value
            elif field == 'title':
                if hasattr(vcard, 'title'):
                    vcard.title.value = new_value
                else:
                    vcard.add('title').value = new_value
            elif field == 'note':
                if hasattr(vcard, 'note'):
                    vcard.note.value = new_value
                else:
                    vcard.add('note').value = new_value
        
        return vcard.serialize()
    except Exception as e:
        print(f"Error modifying vCard: {e}")
        return vcard_data

def run_comprehensive_real_data_test():
    """Run comprehensive testing with real data from all 3 databases"""
    
    print("🧪 COMPREHENSIVE REAL DATA CRUD TESTING - RANDOM SAMPLING")
    print("=" * 70)
    print("Testing with 50 RANDOM contacts from each source database")
    print("Testing: Import → Read → Update → Delete → Restore")
    print("Random seed: 42 (for reproducible results)")
    print()
    
    # Create temporary database for testing
    test_dir = tempfile.mkdtemp()
    connector = VCardConnector(test_dir)
    
    try:
        # Source database files
        source_databases = {
            'sara_export': 'Imports/Sara_Export_Sara A. Kerner and 3.074 others.vcf',
            'iphone_contacts': 'Imports/iPhone_Contacts_Contacts.vcf',
            'iphone_suggested': 'Imports/iPhone_Suggested_Suggested Contacts.vcf'
        }
        
        # PHASE 1: Extract and Import Real Data
        print("📥 PHASE 1: Extracting and Importing Real Data")
        print("-" * 50)
        
        total_imported = 0
        imported_contact_ids = []
        
        for db_name, db_file in source_databases.items():
            if not os.path.exists(db_file):
                print(f"⚠️  {db_name}: File not found - {db_file}")
                continue
            
            print(f"\n🔍 Extracting 50 random contacts from {db_name}...")
            
            # Extract 50 random contacts
            extracted_vcards = extract_random_n_contacts(db_file, 50)
            print(f"   Extracted: {len(extracted_vcards)} contacts")
            
            if not extracted_vcards:
                continue
            
            # Create temporary file for import
            temp_file = os.path.join(test_dir, f"{db_name}_sample.vcf")
            with open(temp_file, 'w', encoding='utf-8') as f:
                for vcard in extracted_vcards:
                    f.write(vcard + '\n')
            
            # Import using connector
            print(f"📥 Importing {db_name} sample...")
            result = connector.import_database(temp_file, db_name)
            
            print(f"   ✅ Imported: {result['imported_contacts']}/{result['total_contacts']}")
            print(f"   🔧 Compliance fixes: {result['compliance_fixes']}")
            
            if result['errors']:
                print(f"   ⚠️  Errors: {len(result['errors'])}")
                for error in result['errors'][:3]:  # Show first 3 errors
                    print(f"      • {error}")
            
            total_imported += result['imported_contacts']
            imported_contact_ids.extend(result['contact_ids'])
        
        print(f"\n📊 Phase 1 Results:")
        print(f"   Total contacts imported: {total_imported}")
        print(f"   Contact IDs generated: {len(imported_contact_ids)}")
        
        # PHASE 2: Verify Reading Consistency
        print(f"\n📖 PHASE 2: Verifying Reading Consistency")
        print("-" * 50)
        
        # Test getting individual contacts
        print("🔍 Testing individual contact retrieval...")
        read_success_count = 0
        read_errors = []
        
        for i, contact_id in enumerate(imported_contact_ids[:10]):  # Test first 10
            contact = connector.get_contact(contact_id)
            if contact:
                read_success_count += 1
                # Verify source tracking
                if not all([
                    contact.source_info.database_name,
                    contact.source_info.source_file,
                    contact.source_info.import_timestamp
                ]):
                    read_errors.append(f"Missing source info for {contact_id}")
            else:
                read_errors.append(f"Could not retrieve {contact_id}")
        
        print(f"   Individual reads: {read_success_count}/10 successful")
        
        # Test getting all contacts
        print("📚 Testing bulk contact retrieval...")
        all_contacts = connector.get_all_contacts()
        print(f"   Retrieved all contacts: {len(all_contacts)}")
        
        # Verify database statistics
        print("📊 Testing database statistics...")
        stats = connector.get_database_stats()
        print(f"   Active contacts: {stats['active_contacts']}")
        print(f"   Total operations: {stats['total_operations']}")
        print(f"   Sources: {list(stats['contacts_by_source'].keys())}")
        
        # Verify vCard data integrity
        print("🔍 Testing vCard data integrity...")
        integrity_issues = 0
        for contact in all_contacts[:20]:  # Check first 20
            try:
                # Parse vCard to verify it's valid
                vcard = list(vobject.readComponents(contact.vcard_data))[0]
                
                # Check required fields
                if not hasattr(vcard, 'fn') or not vcard.fn.value:
                    integrity_issues += 1
                if not hasattr(vcard, 'version'):
                    integrity_issues += 1
                    
                # Check source tracking
                required_x_fields = ['x_source_database', 'x_source_file', 'x_source_index']
                for field in required_x_fields:
                    if not hasattr(vcard, field):
                        integrity_issues += 1
                        
            except Exception as e:
                integrity_issues += 1
                read_errors.append(f"vCard parsing error for {contact.contact_id}: {e}")
        
        print(f"   Integrity issues: {integrity_issues}")
        
        if read_errors:
            print(f"   ⚠️  Read errors ({len(read_errors)}):")
            for error in read_errors[:5]:
                print(f"      • {error}")
        
        # PHASE 3: Update/Edit Testing
        print(f"\n✏️  PHASE 3: Update/Edit Testing")
        print("-" * 50)
        
        # Select 25 contacts for editing
        contacts_to_edit = imported_contact_ids[:25]
        edit_success_count = 0
        edit_errors = []
        
        print(f"🎯 Editing {len(contacts_to_edit)} contacts with various field modifications...")
        
        for i, contact_id in enumerate(contacts_to_edit):
            try:
                # Get original contact
                original_contact = connector.get_contact(contact_id)
                if not original_contact:
                    edit_errors.append(f"Could not find contact {contact_id} for editing")
                    continue
                
                # Define various modifications based on index
                modifications = {}
                
                if i % 5 == 0:  # Every 5th contact - update name
                    modifications['fn'] = f"Updated Name {i}"
                if i % 3 == 0:  # Every 3rd contact - add email
                    modifications['email'] = f"updated{i}@example.com"
                if i % 4 == 0:  # Every 4th contact - add phone
                    modifications['tel'] = f"+1555123{i:04d}"
                if i % 6 == 0:  # Every 6th contact - update organization
                    modifications['org'] = f"Updated Company {i}"
                if i % 7 == 0:  # Every 7th contact - add title
                    modifications['title'] = f"Updated Title {i}"
                if i % 8 == 0:  # Every 8th contact - add note
                    modifications['note'] = f"Updated via CRUD test on {datetime.now().strftime('%Y-%m-%d')}"
                
                if not modifications:  # Ensure every contact gets at least one modification
                    modifications['note'] = f"Test modification {i}"
                
                # Apply modifications
                modified_vcard = modify_vcard_fields(original_contact.vcard_data, modifications)
                
                # Update in database
                success = connector.update_contact(contact_id, modified_vcard)
                
                if success:
                    edit_success_count += 1
                    print(f"   ✅ Updated {contact_id}: {list(modifications.keys())}")
                else:
                    edit_errors.append(f"Failed to update {contact_id}")
                    
            except Exception as e:
                edit_errors.append(f"Error updating {contact_id}: {e}")
        
        print(f"\n📊 Edit Results:")
        print(f"   Successful edits: {edit_success_count}/{len(contacts_to_edit)}")
        
        if edit_errors:
            print(f"   ⚠️  Edit errors ({len(edit_errors)}):")
            for error in edit_errors[:5]:
                print(f"      • {error}")
        
        # Verify edits persisted
        print("🔍 Verifying edits persisted after database reload...")
        
        # Create new connector instance to test persistence
        new_connector = VCardConnector(test_dir)
        persistence_issues = 0
        
        for contact_id in contacts_to_edit[:10]:  # Check first 10 edited contacts
            original_contact = connector.get_contact(contact_id)
            reloaded_contact = new_connector.get_contact(contact_id)
            
            if not reloaded_contact:
                persistence_issues += 1
            elif reloaded_contact.version != original_contact.version:
                persistence_issues += 1
            elif reloaded_contact.vcard_data != original_contact.vcard_data:
                persistence_issues += 1
        
        print(f"   Persistence issues: {persistence_issues}/10")
        
        # PHASE 4: Delete Testing
        print(f"\n🗑️  PHASE 4: Delete Testing")
        print("-" * 50)
        
        # Select 25 contacts for deletion (different from edited ones)
        contacts_to_delete = imported_contact_ids[25:50]
        delete_success_count = 0
        delete_errors = []
        
        print(f"🎯 Soft-deleting {len(contacts_to_delete)} contacts...")
        
        for contact_id in contacts_to_delete:
            try:
                success = connector.delete_contact(contact_id)
                if success:
                    delete_success_count += 1
                    print(f"   ✅ Deleted {contact_id}")
                    
                    # Verify deletion
                    deleted_contact = connector.get_contact(contact_id)
                    if deleted_contact and deleted_contact.is_active:
                        delete_errors.append(f"Contact {contact_id} still active after deletion")
                else:
                    delete_errors.append(f"Failed to delete {contact_id}")
                    
            except Exception as e:
                delete_errors.append(f"Error deleting {contact_id}: {e}")
        
        print(f"\n📊 Delete Results:")
        print(f"   Successful deletes: {delete_success_count}/{len(contacts_to_delete)}")
        
        # Verify active contact count decreased
        updated_stats = connector.get_database_stats()
        expected_active = total_imported - delete_success_count
        actual_active = updated_stats['active_contacts']
        
        print(f"   Expected active contacts: {expected_active}")
        print(f"   Actual active contacts: {actual_active}")
        
        if actual_active != expected_active:
            delete_errors.append(f"Active contact count mismatch: expected {expected_active}, got {actual_active}")
        
        if delete_errors:
            print(f"   ⚠️  Delete errors ({len(delete_errors)}):")
            for error in delete_errors[:5]:
                print(f"      • {error}")
        
        # PHASE 5: Restore Testing
        print(f"\n🔄 PHASE 5: Restore Testing")
        print("-" * 50)
        
        # Restore 10 deleted contacts
        contacts_to_restore = contacts_to_delete[:10]
        restore_success_count = 0
        restore_errors = []
        
        print(f"🎯 Restoring {len(contacts_to_restore)} deleted contacts...")
        
        for contact_id in contacts_to_restore:
            try:
                success = connector.restore_contact(contact_id)
                if success:
                    restore_success_count += 1
                    print(f"   ✅ Restored {contact_id}")
                    
                    # Verify restoration
                    restored_contact = connector.get_contact(contact_id)
                    if not restored_contact or not restored_contact.is_active:
                        restore_errors.append(f"Contact {contact_id} not active after restoration")
                else:
                    restore_errors.append(f"Failed to restore {contact_id}")
                    
            except Exception as e:
                restore_errors.append(f"Error restoring {contact_id}: {e}")
        
        print(f"\n📊 Restore Results:")
        print(f"   Successful restores: {restore_success_count}/{len(contacts_to_restore)}")
        
        if restore_errors:
            print(f"   ⚠️  Restore errors ({len(restore_errors)}):")
            for error in restore_errors[:3]:
                print(f"      • {error}")
        
        # FINAL SUMMARY
        print(f"\n🎉 COMPREHENSIVE REAL DATA TEST COMPLETE!")
        print("=" * 60)
        
        final_stats = connector.get_database_stats()
        
        summary = {
            'phase1_import': {
                'total_imported': total_imported,
                'databases_processed': len([db for db in source_databases.values() if os.path.exists(db)]),
                'contact_ids_generated': len(imported_contact_ids)
            },
            'phase2_reading': {
                'individual_reads_successful': f"{read_success_count}/10",
                'bulk_retrieval_count': len(all_contacts),
                'integrity_issues': integrity_issues,
                'read_errors': len(read_errors)
            },
            'phase3_updates': {
                'contacts_edited': len(contacts_to_edit),
                'successful_edits': edit_success_count,
                'edit_errors': len(edit_errors),
                'persistence_issues': persistence_issues
            },
            'phase4_deletes': {
                'contacts_deleted': len(contacts_to_delete),
                'successful_deletes': delete_success_count,
                'delete_errors': len(delete_errors)
            },
            'phase5_restores': {
                'contacts_restored': len(contacts_to_restore),
                'successful_restores': restore_success_count,
                'restore_errors': len(restore_errors)
            },
            'final_state': {
                'total_contacts_in_db': final_stats['total_contacts'],
                'active_contacts': final_stats['active_contacts'],
                'total_operations_logged': final_stats['total_operations'],
                'database_file_size': os.path.getsize(final_stats['database_file']) if os.path.exists(final_stats['database_file']) else 0
            }
        }
        
        print(f"📊 FINAL RESULTS:")
        print(f"   Import: {summary['phase1_import']['total_imported']} contacts from {summary['phase1_import']['databases_processed']} databases")
        print(f"   Reading: {summary['phase2_reading']['individual_reads_successful']} individual reads, {summary['phase2_reading']['integrity_issues']} integrity issues")
        print(f"   Updates: {summary['phase3_updates']['successful_edits']}/{summary['phase3_updates']['contacts_edited']} successful edits")
        print(f"   Deletes: {summary['phase4_deletes']['successful_deletes']}/{summary['phase4_deletes']['contacts_deleted']} successful deletes")
        print(f"   Restores: {summary['phase5_restores']['successful_restores']}/{summary['phase5_restores']['contacts_restored']} successful restores")
        print(f"   Final state: {summary['final_state']['active_contacts']} active contacts, {summary['final_state']['total_operations_logged']} operations logged")
        
        # Determine overall success
        total_errors = (len(read_errors) + len(edit_errors) + len(delete_errors) + len(restore_errors) + 
                       integrity_issues + persistence_issues)
        
        if total_errors == 0:
            print(f"\n✅ ALL TESTS PASSED! Database is 100% ready for production.")
            print(f"🎯 Real data CRUD operations work flawlessly.")
            return True
        else:
            print(f"\n⚠️  ISSUES FOUND: {total_errors} total errors across all phases")
            print(f"🔧 Review errors before proceeding to full data import")
            return False
        
    finally:
        # Cleanup
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir, ignore_errors=True)
        print(f"\n🧹 Test environment cleaned up")

if __name__ == "__main__":
    success = run_comprehensive_real_data_test()
    
    if success:
        print(f"\n🚀 READY FOR PRODUCTION DATA IMPORT!")
        print(f"The database architecture handles real data perfectly.")
        print(f"You can now proceed with importing all 7,000+ contacts.")
    else:
        print(f"\n🛠️ ISSUES NEED ATTENTION")
        print(f"Fix the identified problems before full data import.")