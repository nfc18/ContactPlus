# 🔒 MANDATORY PHONEBOOK EDITING PROTOCOL

## ⚠️ CRITICAL REQUIREMENT
**THIS PROCESS MUST BE FOLLOWED EXACTLY FOR ALL PHONEBOOK MODIFICATIONS**
**NO EXCEPTIONS - NO DEVIATIONS - NO SHORTCUTS**

---

## 📋 MANDATORY 6-STEP PROCESS

### **STEP 1: PRE-EDIT VALIDATION** ✅ REQUIRED
```python
# MUST load through PhonebookManager
phonebook_manager = PhonebookManager()
# This automatically validates current file - DO NOT BYPASS

# MUST verify file integrity before any changes
validate_phonebook(current_master, "pre-edit check")
```
**❌ NEVER edit files directly without this step**

### **STEP 2: AUTOMATIC BACKUP** ✅ REQUIRED  
```python
# MUST create timestamped backup before ANY changes
backup_path = self._backup_current()
# Creates: backup/backup_MASTER_PHONEBOOK_timestamp.vcf
```
**❌ NEVER skip backup creation**
**❌ NEVER modify files without backup**

### **STEP 3: PERFORM EDIT OPERATION** ✅ REQUIRED
```python
# MUST load contacts into memory first
contacts = list(vobject.readComponents(f.read()))

# Apply changes in memory only
modified_contacts = apply_changes(contacts)
```
**❌ NEVER edit files in-place**
**❌ NEVER modify original master directly**

### **STEP 4: POST-EDIT VALIDATION** ✅ REQUIRED
```python
# MUST save to temporary file first
temp_file = f"temp_phonebook_{timestamp}.vcf"
save_contacts(modified_contacts, temp_file)

# MANDATORY vcard library validation
is_valid, errors, warnings = validator.validate_file(temp_file)

if not is_valid:
    os.remove(temp_file)  # MUST delete invalid file
    return False          # MUST abort operation
```
**❌ NEVER save without validation**
**❌ NEVER keep invalid files**
**❌ NEVER bypass RFC compliance checking**

### **STEP 5: SAVE NEW MASTER** ✅ REQUIRED
```python
if validation_passes:
    # MUST create new timestamped master
    new_master = f"data/MASTER_PHONEBOOK_{timestamp}.vcf"
    os.rename(temp_file, new_master)
    self.current_master = new_master
else:
    # MUST preserve original on failure
    print("🚫 Changes rejected, original master preserved")
```
**❌ NEVER overwrite original master**
**❌ NEVER save if validation fails**

### **STEP 6: CHANGE REPORTING** ✅ REQUIRED
```python
# MUST report what changed
print(f"Contacts before: {original_count}")
print(f"Contacts after: {new_count}")
print(f"Net change: {new_count - original_count}")
```

---

## 🛡️ MANDATORY SAFETY GUARANTEES

### ✅ **ALWAYS REQUIRED**
- Pre-edit validation
- Automatic backup creation  
- RFC compliance validation
- Atomic operations (all-or-nothing)
- Change logging
- Timestamped versions

### ❌ **NEVER ALLOWED**
- Direct file editing
- Skipping validation
- Bypassing backups
- Overwriting original files
- Saving invalid vCards
- Partial operations

---

## 🚨 VIOLATION CONSEQUENCES

**ANY deviation from this process will result in:**
- Data corruption risk
- Loss of RFC compliance
- Inability to import contacts
- Potential data loss
- Breaking of phonebook integrity

---

## 📁 REQUIRED FILE STRUCTURE

```
data/
├── MASTER_PHONEBOOK_YYYYMMDD_HHMMSS.vcf  # Current master (NEVER modify)
├── MASTER_PHONEBOOK_YYYYMMDD_HHMMSS.vcf  # New master (after edits)

backup/
├── backup_MASTER_PHONEBOOK_YYYYMMDD_HHMMSS_timestamp.vcf  # Pre-edit backups
└── decision_processing_YYYYMMDD_HHMMSS/                   # Operation backups

temp/                                      # Temporary files (auto-cleaned)
├── temp_phonebook_timestamp.vcf           # Validation staging
```

---

## 🔧 APPROVED EDITING TOOLS

### ✅ **MUST USE THESE CLASSES**
- `PhonebookManager` - For all phonebook operations
- `VCardStandardsValidator` - For validation
- `auto_validate.py` - For validation functions

### ❌ **NEVER USE DIRECTLY**
- Raw file I/O for phonebook files
- Manual vCard manipulation
- External vCard tools
- Direct file overwrites

---

## 📋 IMPLEMENTATION CHECKLIST

For every phonebook edit operation, verify:

- [ ] Used PhonebookManager class
- [ ] Pre-edit validation completed
- [ ] Backup created automatically  
- [ ] Edit performed in memory only
- [ ] Post-edit validation passed
- [ ] New master created (not overwritten)
- [ ] Change report generated
- [ ] Original master preserved
- [ ] All temporary files cleaned

---

## 🔒 PROTOCOL ENFORCEMENT

**This protocol is IMMUTABLE and MANDATORY**

- No shortcuts allowed
- No "quick fixes" permitted  
- No bypassing for "simple" changes
- No exceptions for any reason

**EVERY phonebook modification MUST follow this exact process**

---

*Last Updated: 2025-06-07*
*Protocol Version: 1.0 (FINAL)*