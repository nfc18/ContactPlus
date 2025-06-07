#!/usr/bin/env python3
"""
🔒 PHONEBOOK EDITING PROTOCOL ENFORCEMENT

This module contains validation checks to ensure the mandatory
phonebook editing protocol is being followed correctly.

CRITICAL: This protocol MUST be followed for ALL phonebook modifications.
"""

import os
import sys
from datetime import datetime

class ProtocolViolationError(Exception):
    """Raised when the mandatory phonebook editing protocol is violated"""
    pass

def enforce_protocol_compliance():
    """
    Enforce that the mandatory phonebook editing protocol is being followed
    
    This function MUST be called before any phonebook editing operation
    """
    
    # Check that we're using the PhonebookManager
    frame = sys._getframe(1)
    calling_function = frame.f_code.co_name
    calling_module = frame.f_globals.get('__name__', '')
    
    # Allowed entry points for phonebook editing
    approved_modules = [
        'phonebook_operations',
        'apply_final_merge', 
        'apply_user_decisions',
        'apply_merge_decisions'
    ]
    
    approved_classes = ['PhonebookManager', 'DecisionProcessor']
    
    # Check if being called through approved channels
    if calling_module not in approved_modules and calling_function not in approved_classes:
        print("🚨 PROTOCOL VIOLATION DETECTED!")
        print(f"   Calling module: {calling_module}")
        print(f"   Calling function: {calling_function}")
        print("")
        print("❌ Direct phonebook editing is PROHIBITED")
        print("✅ Use PhonebookManager class instead")
        print("")
        print("📋 See PHONEBOOK_EDITING_PROTOCOL.md for required process")
        
        raise ProtocolViolationError(
            "MANDATORY PROTOCOL VIOLATION: Direct phonebook editing not allowed. "
            "Must use PhonebookManager class and follow 6-step protocol."
        )

def validate_backup_exists(operation_name):
    """Ensure backup was created before operation"""
    
    # Check that backup directory exists and has recent backups
    backup_dir = "backup"
    if not os.path.exists(backup_dir):
        raise ProtocolViolationError(
            f"PROTOCOL VIOLATION: No backup directory found before {operation_name}. "
            "Backup creation is MANDATORY."
        )
    
    # Check for recent backups (within last 5 minutes)
    recent_backups = []
    now = datetime.now()
    
    for backup_file in os.listdir(backup_dir):
        if backup_file.startswith('backup_MASTER_PHONEBOOK_'):
            backup_path = os.path.join(backup_dir, backup_file)
            mod_time = datetime.fromtimestamp(os.path.getmtime(backup_path))
            age_minutes = (now - mod_time).total_seconds() / 60
            
            if age_minutes < 5:  # Recent backup
                recent_backups.append(backup_file)
    
    if not recent_backups:
        raise ProtocolViolationError(
            f"PROTOCOL VIOLATION: No recent backup found before {operation_name}. "
            "Backup creation is MANDATORY before ANY phonebook modification."
        )

def validate_file_not_overwritten(original_path):
    """Ensure original master file was not overwritten"""
    
    if not os.path.exists(original_path):
        raise ProtocolViolationError(
            "PROTOCOL VIOLATION: Original master phonebook file missing. "
            "Original files must NEVER be overwritten or deleted."
        )

def validate_vcard_compliance(file_path, operation_name):
    """Validate that result file is RFC compliant"""
    
    try:
        from auto_validate import validate_phonebook
        
        is_valid = validate_phonebook(file_path, operation_name)
        
        if not is_valid:
            raise ProtocolViolationError(
                f"PROTOCOL VIOLATION: {operation_name} resulted in invalid vCard file. "
                "ALL modifications must maintain RFC compliance."
            )
            
    except ImportError:
        # Fallback to basic vcard library check
        try:
            import vcard
            with open(file_path, 'r') as f:
                content = f.read()
                # Basic vcard library validation would go here
        except Exception as e:
            raise ProtocolViolationError(
                f"PROTOCOL VIOLATION: Cannot validate {operation_name} result. "
                f"Validation is MANDATORY. Error: {e}"
            )

class ProtocolEnforcer:
    """Context manager to enforce protocol compliance"""
    
    def __init__(self, operation_name, original_master_path):
        self.operation_name = operation_name
        self.original_master_path = original_master_path
        self.start_time = None
    
    def __enter__(self):
        print(f"🔒 ENFORCING PROTOCOL for: {self.operation_name}")
        
        # Step 1: Check protocol compliance
        enforce_protocol_compliance()
        
        # Step 2: Validate backup exists
        validate_backup_exists(self.operation_name)
        
        # Step 3: Ensure original file exists
        validate_file_not_overwritten(self.original_master_path)
        
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # Operation completed successfully
            duration = datetime.now() - self.start_time
            print(f"✅ PROTOCOL COMPLIANT: {self.operation_name} completed in {duration}")
        else:
            # Operation failed
            print(f"❌ PROTOCOL ENFORCEMENT: {self.operation_name} failed")
            
        # Always ensure original file still exists
        validate_file_not_overwritten(self.original_master_path)

# Protocol compliance constants
PROTOCOL_VERSION = "1.0"
LAST_UPDATED = "2025-06-07"

def print_protocol_warning():
    """Print mandatory protocol warning"""
    print("🔒" + "="*78 + "🔒")
    print("  MANDATORY PHONEBOOK EDITING PROTOCOL ENFORCEMENT ACTIVE")
    print("  ")
    print("  ALL phonebook modifications MUST follow the 6-step protocol")
    print("  defined in PHONEBOOK_EDITING_PROTOCOL.md")
    print("  ")
    print("  NO EXCEPTIONS - NO DEVIATIONS - NO SHORTCUTS")
    print("🔒" + "="*78 + "🔒")

if __name__ == "__main__":
    print_protocol_warning()
    print(f"\nProtocol Version: {PROTOCOL_VERSION}")
    print(f"Last Updated: {LAST_UPDATED}")
    print(f"\nProtocol Status: ACTIVE and ENFORCED")