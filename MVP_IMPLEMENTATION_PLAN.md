# MVP Implementation Plan - Contact Cleaner

## Overview
Based on critical analysis, this simplified plan focuses on building a working contact cleaner in 2 weeks with just the essential features.

## Core Principle: KISS (Keep It Simple, Stupid)
- No over-engineering
- No speculative features  
- Security by default
- Test everything

## MVP Scope (What we WILL build)

### Week 1: Foundation
1. **Secure vCard Parser**
   - Handle vCard 3.0/4.0
   - Graceful error handling
   - Support your actual files (iPhone, LinkedIn exports)

2. **Simple Storage**
   - SQLite with encryption
   - Basic CRUD operations
   - Audit logging

3. **Exact Duplicate Detection**
   - Email matching (normalized)
   - Phone matching (E.164 format)
   - Name + Company matching

### Week 2: Core Features
4. **Conservative Merger**
   - Only merge high-confidence matches
   - Preserve all data (union, not replace)
   - Full rollback capability

5. **Basic Cleaner**
   - Fix capitalization (JOHN → John)
   - Normalize phones to E.164
   - Extract phones/emails from notes
   - Remove empty fields

6. **Simple CLI Interface**
   ```bash
   # Import
   contactplus import iPhone_Contacts.vcf
   contactplus import LinkedIn_Export.vcf
   
   # Analyze
   contactplus stats
   contactplus find-duplicates --threshold 0.95
   
   # Clean
   contactplus clean --fix-caps --normalize-phones
   contactplus merge-duplicates --review
   
   # Export  
   contactplus export cleaned_contacts.vcf
   ```

## What we WON'T build (yet)
- ❌ Web UI
- ❌ LinkedIn enrichment  
- ❌ Email analysis
- ❌ ML deduplication
- ❌ Contact rating system
- ❌ Complex merge UI

## Technical Stack (Minimal)

```python
# requirements.txt
vobject==0.9.6        # vCard parsing
phonenumbers==8.13    # Phone normalization  
python-Levenshtein==0.21  # Name matching
cryptography==41.0    # Encryption
click==8.1           # CLI framework
sqlalchemy==2.0      # Database ORM
pytest==7.4          # Testing
```

## Project Structure

```
contactplus/
├── src/
│   ├── __init__.py
│   ├── cli.py           # Command-line interface
│   ├── parser.py        # vCard parsing
│   ├── storage.py       # Encrypted SQLite storage
│   ├── cleaner.py       # Data cleaning rules
│   ├── deduplicator.py  # Duplicate detection
│   └── merger.py        # Contact merging logic
├── tests/
│   ├── test_parser.py
│   ├── test_cleaner.py
│   └── fixtures/        # Test vCard files
├── README.md
├── requirements.txt
└── setup.py
```

## Implementation Schedule

### Day 1-2: Parser & Storage
```python
# Goal: Import vCards without losing data
def import_vcf(file_path):
    contacts = []
    with open(file_path, 'r') as f:
        for vcard in vobject.readComponents(f):
            contact = parse_vcard_safely(vcard)
            contacts.append(contact)
    
    store_contacts_securely(contacts)
    return len(contacts)
```

### Day 3-4: Deduplication
```python
# Goal: Find obvious duplicates
def find_duplicates(contacts):
    duplicates = []
    
    # Index by email
    by_email = defaultdict(list)
    for c in contacts:
        for email in c.emails:
            by_email[normalize_email(email)].append(c)
    
    # Index by phone
    by_phone = defaultdict(list)
    for c in contacts:
        for phone in c.phones:
            by_phone[normalize_phone(phone)].append(c)
    
    # Find groups with multiple contacts
    for email, group in by_email.items():
        if len(group) > 1:
            duplicates.append(group)
    
    return duplicates
```

### Day 5-6: Cleaning
```python
# Goal: Fix common data issues
def clean_contact(contact):
    # Fix capitalization
    contact.name = fix_capitalization(contact.name)
    
    # Normalize phones
    contact.phones = [normalize_phone(p) for p in contact.phones]
    
    # Extract data from notes
    extracted = extract_from_notes(contact.notes)
    contact.emails.extend(extracted['emails'])
    contact.phones.extend(extracted['phones'])
    
    # Remove duplicates within contact
    contact.emails = list(set(contact.emails))
    contact.phones = list(set(contact.phones))
    
    return contact
```

### Day 7-8: Merging
```python
# Goal: Safely merge duplicates
def merge_contacts(group):
    merged = Contact()
    
    # Use most complete name
    merged.name = max(group, key=lambda c: len(c.name or '')).name
    
    # Union all emails/phones
    merged.emails = list(set(e for c in group for e in c.emails))
    merged.phones = list(set(p for c in group for p in c.phones))
    
    # Keep highest quality photo
    photos = [c.photo for c in group if c.photo]
    if photos:
        merged.photo = max(photos, key=lambda p: len(p.data))
    
    # Merge notes
    notes = [c.notes for c in group if c.notes]
    merged.notes = '\n---\n'.join(notes)
    
    return merged
```

### Day 9-10: Testing & Polish
- Test with real data
- Handle edge cases
- Performance optimization
- Documentation

## Security Implementation

### Encryption at Rest
```python
from cryptography.fernet import Fernet

class SecureStorage:
    def __init__(self):
        self.key = self.load_or_create_key()
        self.cipher = Fernet(self.key)
    
    def save_contact(self, contact):
        data = contact.to_json()
        encrypted = self.cipher.encrypt(data.encode())
        self.db.save(contact.id, encrypted)
    
    def load_contact(self, id):
        encrypted = self.db.load(id)
        data = self.cipher.decrypt(encrypted)
        return Contact.from_json(data.decode())
```

### Audit Logging
```python
import logging

audit = logging.getLogger('audit')

def log_operation(operation, contact_id, details):
    audit.info({
        'timestamp': datetime.now().isoformat(),
        'operation': operation,
        'contact_id': contact_id,
        'details': details
    })
```

## Testing Strategy

### Unit Tests (Required)
```python
def test_normalize_phone():
    assert normalize_phone('(555) 123-4567') == '+15551234567'
    assert normalize_phone('+1-555-123-4567') == '+15551234567'
    assert normalize_phone('555.123.4567') == '+15551234567'

def test_fix_capitalization():
    assert fix_capitalization('JOHN DOE') == 'John Doe'
    assert fix_capitalization('mcdonald') == 'McDonald'
    assert fix_capitalization('o\'brien') == "O'Brien"
```

### Integration Tests
```python
def test_import_export_cycle():
    # Import
    original_count = import_vcf('test_contacts.vcf')
    
    # Clean
    clean_all_contacts()
    
    # Export
    export_vcf('output.vcf')
    
    # Verify
    reimported = import_vcf('output.vcf')
    assert reimported == original_count
```

## Success Metrics

1. **Import Success**: 100% of vCards imported without data loss
2. **Deduplication**: Find 95%+ of exact duplicates
3. **Performance**: Process 10,000 contacts in < 60 seconds
4. **Quality**: Exported vCards work in iCloud/Google
5. **Safety**: Zero data loss, full rollback capability

## Next Steps After MVP

Only after MVP is working and tested:

1. **Phase 2**: Fuzzy matching (1 week)
2. **Phase 3**: Web UI (2 weeks)  
3. **Phase 4**: LinkedIn enhancement (1 week)
4. **Phase 5**: Email analysis (1 week)

## Alternative: The 1-Day Script

If 2 weeks is too much, here's a 1-day version:

```python
#!/usr/bin/env python3
"""Ultra-simple contact cleaner - 1 day implementation"""

import vobject
import phonenumbers
import click

@click.command()
@click.argument('input_file')
@click.argument('output_file')
def clean_contacts(input_file, output_file):
    """Clean contacts in one pass"""
    seen_emails = set()
    seen_phones = set()
    cleaned = []
    
    with open(input_file) as f:
        for vcard in vobject.readComponents(f):
            # Skip if duplicate email
            emails = [e.value.lower() for e in vcard.contents.get('email', [])]
            if any(e in seen_emails for e in emails):
                continue
            seen_emails.update(emails)
            
            # Skip if duplicate phone
            phones = []
            for tel in vcard.contents.get('tel', []):
                try:
                    parsed = phonenumbers.parse(tel.value, 'US')
                    phones.append(phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164))
                except:
                    phones.append(tel.value)
            
            if any(p in seen_phones for p in phones):
                continue
            seen_phones.update(phones)
            
            # Fix name capitalization
            if hasattr(vcard, 'fn'):
                vcard.fn.value = ' '.join(w.capitalize() for w in vcard.fn.value.split())
            
            cleaned.append(vcard)
    
    # Write output
    with open(output_file, 'w') as f:
        for vcard in cleaned:
            f.write(vcard.serialize())
    
    click.echo(f"Cleaned {len(cleaned)} contacts")

if __name__ == '__main__':
    clean_contacts()
```

## Conclusion

Start with the MVP. It's better to have a working simple solution than a complex system that never ships. The modular design allows you to add features later as needed.