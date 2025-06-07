# Contact Cleaner Complete Workflow

## System Overview
The Contact Cleaner is a comprehensive system for importing, cleaning, merging, enhancing, and rating contacts from multiple sources. This document provides a complete workflow from start to finish.

## Workflow Stages

### Stage 1: Data Import and Normalization

#### 1.1 Import Sources
```python
# Import from multiple sources
sources = {
    'iphone': '/Imports/iPhone_Contacts_Contacts.vcf',
    'sara_export': '/Imports/Sara_Export_Sara A. Kerner and 3.074 others.vcf',
    'edgar_export': '/Imports/Edgar_Export_Edgar A and 24.836 others.vcf',
    'linkedin': '/Imports/Basic_LinkedInDataExport_06-03-2025.zip/Connections.csv',
    'suggested': '/Imports/iPhone_Suggested_Suggested Contacts.vcf'
}

# Process each source
all_contacts = []
for source_name, file_path in sources.items():
    contacts = import_contacts(file_path, source=source_name)
    all_contacts.extend(contacts)
    
    # Log import statistics
    log_import_stats(source_name, len(contacts))
```

#### 1.2 Initial Validation
- Validate vCard format compliance
- Check required fields (FN for vCard)
- Flag malformed entries for manual review
- Create import report

### Stage 2: Data Cleaning

#### 2.1 Field Standardization
```python
for contact in all_contacts:
    # Name cleaning
    contact.first_name = clean_name(contact.first_name)
    contact.last_name = clean_name(contact.last_name)
    
    # Email normalization
    contact.emails = [clean_email(e) for e in contact.emails if validate_email(e)]
    
    # Phone normalization
    contact.phones = [normalize_phone(p) for p in contact.phones if p]
    
    # Extract data from notes
    extracted = extract_from_notes(contact.notes)
    contact.emails.extend(extracted.get('emails', []))
    contact.phones.extend(extracted.get('phones', []))
    contact.notes = extracted.get('cleaned_notes', contact.notes)
```

#### 2.2 Data Quality Issues to Fix
- **Capitalization**: JOHN DOE → John Doe
- **Phone formats**: (555) 123-4567 → +15551234567
- **Email validation**: Remove invalid emails
- **Data in wrong fields**: Extract from notes
- **Remove duplicates within contact**: Unique emails/phones

### Stage 3: Deduplication and Merging

#### 3.1 Duplicate Detection
```python
# Generate candidate pairs using blocking
candidates = generate_candidate_pairs(all_contacts)

# Score each pair
duplicate_groups = []
for contact1, contact2 in candidates:
    score = calculate_match_score(contact1, contact2)
    
    if score > 0.9:
        # Automatic merge candidate
        duplicate_groups.append({
            'contacts': [contact1, contact2],
            'score': score,
            'action': 'auto_merge'
        })
    elif score > 0.7:
        # Manual review needed
        duplicate_groups.append({
            'contacts': [contact1, contact2],
            'score': score,
            'action': 'manual_review',
            'reason': identify_conflict_reason(contact1, contact2)
        })
```

#### 3.2 Merge Execution
```python
merged_contacts = []
for group in duplicate_groups:
    if group['action'] == 'auto_merge':
        primary = select_primary_contact(group['contacts'])
        merged = execute_merge(primary, group['contacts'])
        merged_contacts.append(merged)
    elif group['action'] == 'manual_review':
        # Queue for manual review
        queue_for_review(group)
```

#### 3.3 Special Cases
- **Same name, different people**: Flag with warning
- **Family members**: Keep separate
- **Multiple email addresses (>3)**: Manual review
- **Conflicting companies**: Manual review

### Stage 4: Data Enhancement

#### 4.1 LinkedIn Enhancement
```python
# Load LinkedIn data
linkedin_connections = load_linkedin_connections()

for contact in merged_contacts:
    # Try to match with LinkedIn
    linkedin_match = find_linkedin_match(contact, linkedin_connections)
    
    if linkedin_match and linkedin_match.confidence > 0.8:
        # Enhance with professional data
        contact.job_title = linkedin_match.position or contact.job_title
        contact.organization = linkedin_match.company or contact.organization
        contact.linkedin_url = linkedin_match.url
        contact.linkedin_connected = linkedin_match.connected_on
```

#### 4.2 Email Analysis Enhancement
```python
# Analyze email interactions
email_analyzer = EmailInteractionAnalyzer(mailbox_path)

for contact in merged_contacts:
    if contact.emails:
        # Get interaction statistics
        stats = email_analyzer.analyze_contact_interactions(contact)
        
        # Store enhancement data
        contact.interaction_count = stats['total_sent'] + stats['total_received']
        contact.last_interaction = stats['last_interaction']
        contact.interaction_frequency = stats['interaction_frequency']
        
        # Extract signature data from recent emails
        contact.enhance_from_signatures(stats['extracted_data'])
```

### Stage 5: Contact Rating

#### 5.1 Calculate Ratings
```python
rated_contacts = []

for contact in merged_contacts:
    # Calculate component scores
    interaction_score = calculate_interaction_score(contact)
    completeness_score = calculate_completeness_score(contact)
    relationship_score = calculate_relationship_score(contact)
    recency_score = calculate_recency_score(contact)
    quality_score = calculate_quality_score(contact)
    
    # Calculate total rating
    total_score = (
        interaction_score +
        completeness_score +
        relationship_score +
        recency_score +
        quality_score
    )
    
    # Apply overrides
    if contact.tags and 'family' in contact.tags:
        total_score = max(total_score, 85)
    
    # Categorize
    category = categorize_contact(total_score)
    
    rated_contacts.append({
        'contact': contact,
        'score': total_score,
        'category': category,
        'components': {
            'interaction': interaction_score,
            'completeness': completeness_score,
            'relationship': relationship_score,
            'recency': recency_score,
            'quality': quality_score
        }
    })
```

### Stage 6: Export Preparation

#### 6.1 Filter for Export
```python
# Separate contacts by category
export_groups = {
    'premium': [],      # Score 80-100
    'standard': [],     # Score 60-79
    'archive': [],      # Score 40-59
    'review': []        # Score 0-39
}

for rated in rated_contacts:
    export_groups[rated['category']].append(rated)

# Prepare export lists
premium_export = [r['contact'] for r in export_groups['premium']]
standard_export = [r['contact'] for r in export_groups['standard']]
```

#### 6.2 Final Validation
```python
# Validate all contacts before export
for contact in premium_export + standard_export:
    # Ensure vCard compliance
    validate_for_export(contact)
    
    # Generate unique UID if missing
    if not contact.uid:
        contact.uid = generate_uuid()
    
    # Final quality check
    issues = final_quality_check(contact)
    if issues:
        log_export_warning(contact, issues)
```

### Stage 7: Export and History

#### 7.1 Generate Export Files
```python
# Generate vCard exports
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Premium contacts - for primary address book
premium_vcf = generate_vcf(
    premium_export,
    filename=f'contacts_premium_{timestamp}.vcf',
    version='4.0'
)

# Standard contacts - for secondary storage
standard_vcf = generate_vcf(
    standard_export,
    filename=f'contacts_standard_{timestamp}.vcf',
    version='4.0'
)

# Archive - for backup only
archive_json = export_to_json(
    export_groups['archive'],
    filename=f'contacts_archive_{timestamp}.json'
)
```

#### 7.2 Create History Record
```python
# Document the entire operation
history = {
    'timestamp': datetime.now(),
    'sources': sources,
    'statistics': {
        'total_imported': len(all_contacts),
        'after_cleaning': len(cleaned_contacts),
        'after_merging': len(merged_contacts),
        'duplicates_found': len(duplicate_groups),
        'exported': {
            'premium': len(premium_export),
            'standard': len(standard_export),
            'archive': len(export_groups['archive']),
            'review': len(export_groups['review'])
        }
    },
    'operations': operation_log,
    'issues': quality_issues,
    'merge_history': merge_operations
}

save_history(history)
```

## Execution Flow

### Complete Pipeline Function
```python
def run_contact_cleaner(config):
    """Execute complete contact cleaning pipeline"""
    
    # Initialize
    setup_database()
    setup_logging()
    
    try:
        # Stage 1: Import
        print("Stage 1: Importing contacts...")
        contacts = import_all_sources(config['sources'])
        save_checkpoint('import_complete', contacts)
        
        # Stage 2: Clean
        print("Stage 2: Cleaning data...")
        cleaned = clean_all_contacts(contacts)
        save_checkpoint('cleaning_complete', cleaned)
        
        # Stage 3: Deduplicate
        print("Stage 3: Finding and merging duplicates...")
        merged = deduplicate_contacts(cleaned)
        save_checkpoint('deduplication_complete', merged)
        
        # Stage 4: Enhance
        print("Stage 4: Enhancing with external data...")
        enhanced = enhance_contacts(merged, config['enhancement_sources'])
        save_checkpoint('enhancement_complete', enhanced)
        
        # Stage 5: Rate
        print("Stage 5: Rating contacts...")
        rated = rate_all_contacts(enhanced)
        save_checkpoint('rating_complete', rated)
        
        # Stage 6: Export
        print("Stage 6: Preparing exports...")
        exports = prepare_exports(rated, config['export_thresholds'])
        
        # Stage 7: Finalize
        print("Stage 7: Generating files and history...")
        finalize_exports(exports)
        
        print("✅ Contact cleaning complete!")
        return generate_summary_report()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        rollback_to_checkpoint()
        raise
```

## Quality Assurance Checklist

### Pre-Processing
- [ ] Backup all original files
- [ ] Verify file formats
- [ ] Check available disk space
- [ ] Review configuration settings

### During Processing
- [ ] Monitor duplicate detection accuracy
- [ ] Review contacts flagged for manual review
- [ ] Verify enhancement data quality
- [ ] Check for data loss

### Post-Processing
- [ ] Validate all export files
- [ ] Test import in target applications
- [ ] Review summary statistics
- [ ] Archive original files
- [ ] Document any manual interventions

## Recovery Procedures

### Checkpoint Recovery
```python
def recover_from_checkpoint(checkpoint_name):
    """Recover from a saved checkpoint"""
    
    checkpoint = load_checkpoint(checkpoint_name)
    if checkpoint:
        print(f"Recovering from {checkpoint_name}")
        contacts = checkpoint['data']
        resume_from_stage(checkpoint['next_stage'], contacts)
    else:
        print("No valid checkpoint found")
```

### Rollback Procedures
1. **Individual Contact**: Restore from version history
2. **Batch Operation**: Undo entire batch
3. **Complete Reset**: Restore from initial backup

## Best Practices

### Data Safety
1. Never modify original files
2. Create backups before each stage
3. Validate after each operation
4. Keep detailed logs

### Performance
1. Process in batches for large datasets
2. Use database indices for lookups
3. Parallelize where possible
4. Monitor memory usage

### Quality
1. Manual review for uncertain matches
2. Preserve all original data
3. Document all decisions
4. Test exports before deletion

## Configuration Example
```python
config = {
    'sources': {
        'vcf_files': ['*.vcf'],
        'csv_files': ['linkedin_connections.csv'],
        'email_account': 'user@example.com'
    },
    'thresholds': {
        'auto_merge': 0.9,
        'manual_review': 0.7,
        'export_minimum': 60
    },
    'enhancement_sources': {
        'linkedin': True,
        'email_analysis': True,
        'external_apis': False
    },
    'export_formats': {
        'premium': 'vcard4',
        'standard': 'vcard3',
        'archive': 'json'
    }
}
```

## Summary
This workflow provides a systematic approach to cleaning and managing contacts:
1. **Import** from multiple sources
2. **Clean** and standardize data
3. **Merge** duplicates intelligently
4. **Enhance** with additional data
5. **Rate** based on importance
6. **Export** high-value contacts
7. **Archive** complete history

The system prioritizes data integrity, provides rollback capabilities, and ensures vCard standard compliance throughout the process.