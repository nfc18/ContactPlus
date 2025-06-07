# Contact Deduplication and Merging Algorithms

## Overview
This document details the algorithms and strategies for detecting duplicate contacts and merging them intelligently while preserving data integrity.

## Duplicate Detection Pipeline

### Stage 1: Blocking / Candidate Generation
Before comparing all contacts against each other (O(n²) complexity), we first create blocks of potential matches.

#### Blocking Keys
1. **Email Block**: First 3 characters of email username
2. **Phone Block**: Last 6 digits of phone number
3. **Name Block**: Soundex/Metaphone of last name
4. **Company Block**: First word of company name

```python
def generate_blocks(contact):
    blocks = []
    
    # Email blocking
    for email in contact.emails:
        username = email.split('@')[0]
        if len(username) >= 3:
            blocks.append(('email', username[:3].lower()))
    
    # Phone blocking
    for phone in contact.phones:
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) >= 6:
            blocks.append(('phone', digits[-6:]))
    
    # Name blocking
    if contact.last_name:
        blocks.append(('name', soundex(contact.last_name)))
    
    return blocks
```

### Stage 2: Similarity Scoring
For each pair of candidates, calculate similarity scores across multiple dimensions.

#### Name Similarity
```python
def name_similarity(contact1, contact2):
    scores = []
    
    # Exact match
    if contact1.full_name == contact2.full_name:
        return 1.0
    
    # Last name match with first name similarity
    if contact1.last_name == contact2.last_name:
        first_sim = fuzz.ratio(contact1.first_name, contact2.first_name) / 100
        scores.append(0.7 + 0.3 * first_sim)
    
    # Nickname handling
    if are_nicknames(contact1.first_name, contact2.first_name):
        scores.append(0.85)
    
    # Fuzzy full name match
    full_sim = fuzz.token_sort_ratio(contact1.full_name, contact2.full_name) / 100
    scores.append(full_sim * 0.9)
    
    return max(scores) if scores else 0
```

#### Contact Method Similarity
```python
def contact_method_similarity(contact1, contact2):
    # Exact email match = very high confidence
    if set(contact1.emails) & set(contact2.emails):
        return 1.0
    
    # Exact phone match = very high confidence
    if set(normalize_phones(contact1.phones)) & set(normalize_phones(contact2.phones)):
        return 0.95
    
    # Similar phone (off by 1-2 digits)
    for p1 in contact1.phones:
        for p2 in contact2.phones:
            if phone_distance(p1, p2) <= 2:
                return 0.7
    
    return 0
```

#### Company Similarity
```python
def company_similarity(contact1, contact2):
    if not contact1.company or not contact2.company:
        return 0
    
    # Exact match
    if contact1.company.lower() == contact2.company.lower():
        return 1.0
    
    # Remove common suffixes
    c1_clean = remove_company_suffixes(contact1.company)
    c2_clean = remove_company_suffixes(contact2.company)
    
    # Fuzzy match
    return fuzz.ratio(c1_clean, c2_clean) / 100
```

### Stage 3: Composite Scoring
Combine individual scores with weights to get final similarity score.

```python
def calculate_match_score(contact1, contact2):
    weights = {
        'name': 0.3,
        'contact_method': 0.4,
        'company': 0.2,
        'location': 0.1
    }
    
    scores = {
        'name': name_similarity(contact1, contact2),
        'contact_method': contact_method_similarity(contact1, contact2),
        'company': company_similarity(contact1, contact2),
        'location': location_similarity(contact1, contact2)
    }
    
    # Apply weights
    final_score = sum(scores[k] * weights[k] for k in weights)
    
    # Boost score for multiple matching fields
    matching_fields = sum(1 for s in scores.values() if s > 0.5)
    if matching_fields >= 3:
        final_score = min(1.0, final_score * 1.1)
    
    return final_score
```

## Merge Strategies

### Conflict Resolution Rules

#### 1. Field Selection Priority
```python
FIELD_PRIORITY = {
    'source_priority': ['linkedin', 'gmail', 'icloud', 'manual'],
    'recency_weight': 0.3,
    'completeness_weight': 0.4,
    'source_weight': 0.3
}

def select_field_value(values, field_type):
    """Select best value from conflicting fields"""
    scored_values = []
    
    for value in values:
        score = 0
        
        # Recency score
        age_days = (datetime.now() - value.updated_at).days
        recency_score = max(0, 1 - (age_days / 365))
        score += recency_score * FIELD_PRIORITY['recency_weight']
        
        # Source score
        source_rank = FIELD_PRIORITY['source_priority'].index(value.source)
        source_score = 1 - (source_rank / len(FIELD_PRIORITY['source_priority']))
        score += source_score * FIELD_PRIORITY['source_weight']
        
        # Completeness score (for structured fields)
        if field_type == 'address':
            completeness = calculate_address_completeness(value)
            score += completeness * FIELD_PRIORITY['completeness_weight']
        
        scored_values.append((score, value))
    
    return max(scored_values, key=lambda x: x[0])[1]
```

#### 2. Multi-Value Field Handling
```python
def merge_multi_value_fields(contacts, field_name):
    """Merge fields that can have multiple values (emails, phones, etc.)"""
    all_values = []
    
    for contact in contacts:
        for value in getattr(contact, field_name):
            normalized = normalize_value(value, field_name)
            all_values.append({
                'value': value,
                'normalized': normalized,
                'source': contact.source,
                'added_date': contact.created_at
            })
    
    # Deduplicate based on normalized value
    unique_values = {}
    for item in all_values:
        key = item['normalized']
        if key not in unique_values or item['added_date'] > unique_values[key]['added_date']:
            unique_values[key] = item
    
    # Sort by priority
    result = sorted(unique_values.values(), 
                   key=lambda x: (x['source'] == 'linkedin', x['added_date']), 
                   reverse=True)
    
    # Flag if too many values
    if len(result) > 3 and field_name == 'emails':
        raise MergeWarning(f"Contact has {len(result)} email addresses")
    
    return [item['value'] for item in result]
```

#### 3. Photo Selection Algorithm
```python
def select_best_photo(photos):
    """Select highest quality photo from multiple options"""
    scored_photos = []
    
    for photo in photos:
        score = 0
        
        # Resolution score
        if photo.width and photo.height:
            pixels = photo.width * photo.height
            score += min(pixels / 1000000, 1.0) * 0.4  # Max 1 point for 1MP+
        
        # Format score
        format_scores = {'jpeg': 0.9, 'png': 1.0, 'gif': 0.5}
        score += format_scores.get(photo.format, 0.5) * 0.2
        
        # Recency score
        if photo.added_date:
            age_days = (datetime.now() - photo.added_date).days
            score += max(0, 1 - (age_days / 730)) * 0.2  # 2 years = 0
        
        # File size score (prefer reasonable sizes)
        if photo.file_size:
            if 50000 < photo.file_size < 500000:  # 50KB-500KB ideal
                score += 0.2
            elif photo.file_size <= 50000:
                score += 0.1
        
        scored_photos.append((score, photo))
    
    return max(scored_photos, key=lambda x: x[0])[1] if scored_photos else None
```

### Merge Execution

#### Safe Merge Process
```python
def execute_merge(primary_contact, duplicate_contacts, confidence_scores):
    """Safely merge contacts with rollback capability"""
    
    # Create backup
    merge_transaction = MergeTransaction()
    merge_transaction.save_state(primary_contact, duplicate_contacts)
    
    try:
        # Merge simple fields
        for field in SIMPLE_FIELDS:
            if not getattr(primary_contact, field):
                for dup in duplicate_contacts:
                    if value := getattr(dup, field):
                        setattr(primary_contact, field, value)
                        break
        
        # Merge multi-value fields
        for field in MULTI_VALUE_FIELDS:
            merged_values = merge_multi_value_fields(
                [primary_contact] + duplicate_contacts, 
                field
            )
            setattr(primary_contact, field, merged_values)
        
        # Handle special cases
        primary_contact.photos = merge_photos([primary_contact] + duplicate_contacts)
        primary_contact.notes = merge_notes([primary_contact] + duplicate_contacts)
        
        # Update metadata
        primary_contact.merge_count += len(duplicate_contacts)
        primary_contact.last_merged = datetime.now()
        primary_contact.merged_ids = [d.id for d in duplicate_contacts]
        
        # Validate merged contact
        validate_contact(primary_contact)
        
        # Commit transaction
        merge_transaction.commit()
        
        # Mark duplicates as merged
        for dup in duplicate_contacts:
            dup.status = 'merged'
            dup.merged_into = primary_contact.id
        
        return primary_contact
        
    except Exception as e:
        merge_transaction.rollback()
        raise MergeError(f"Merge failed: {str(e)}")
```

## Special Cases

### 1. Same Name, Different People
```python
def detect_different_people_same_name(contact1, contact2):
    """Detect when two contacts with same name are different people"""
    
    indicators = []
    
    # Different companies in same time period
    if contact1.company and contact2.company:
        if contact1.company != contact2.company:
            if overlapping_employment_dates(contact1, contact2):
                indicators.append(('different_companies', 0.8))
    
    # Different locations
    if contact1.city and contact2.city:
        if distance_between_cities(contact1.city, contact2.city) > 500:
            indicators.append(('different_locations', 0.6))
    
    # No overlapping contacts
    if not (set(contact1.emails) & set(contact2.emails)):
        if not (set(contact1.phones) & set(contact2.phones)):
            indicators.append(('no_common_contacts', 0.4))
    
    # Different professional fields
    if contact1.title and contact2.title:
        if professional_field(contact1.title) != professional_field(contact2.title):
            indicators.append(('different_fields', 0.5))
    
    # Calculate probability they're different people
    if indicators:
        probability = 1 - prod(1 - score for _, score in indicators)
        return probability > 0.7
    
    return False
```

### 2. Family Members Detection
```python
def detect_family_members(contact1, contact2):
    """Detect potential family members to avoid merging"""
    
    # Same last name
    if contact1.last_name != contact2.last_name:
        return False
    
    # Check for family indicators
    indicators = []
    
    # Same address
    if addresses_match(contact1.address, contact2.address):
        indicators.append('same_address')
    
    # Family email patterns
    if family_email_pattern(contact1.emails, contact2.emails):
        indicators.append('family_email')
    
    # Age difference (if birthdays available)
    if contact1.birthday and contact2.birthday:
        age_diff = abs((contact1.birthday - contact2.birthday).days / 365)
        if age_diff > 15:  # Likely parent/child
            indicators.append('age_difference')
    
    return len(indicators) >= 2
```

## Performance Optimizations

### 1. Incremental Processing
```python
def incremental_deduplication(new_contacts, existing_contacts):
    """Process only new contacts against existing ones"""
    
    # Build index of existing contacts
    email_index = build_index(existing_contacts, 'email')
    phone_index = build_index(existing_contacts, 'phone')
    name_index = build_index(existing_contacts, 'name')
    
    duplicates = []
    
    for new_contact in new_contacts:
        candidates = set()
        
        # Quick lookup using indices
        for email in new_contact.emails:
            candidates.update(email_index.get(email, []))
        
        for phone in new_contact.phones:
            candidates.update(phone_index.get(normalize_phone(phone), []))
        
        # Score only candidates
        for candidate in candidates:
            score = calculate_match_score(new_contact, candidate)
            if score > DUPLICATE_THRESHOLD:
                duplicates.append((new_contact, candidate, score))
    
    return duplicates
```

### 2. Batch Processing
```python
def batch_deduplication(contacts, batch_size=1000):
    """Process large contact lists in batches"""
    
    all_duplicates = []
    
    # Sort contacts to increase likelihood of duplicates being in same batch
    sorted_contacts = sorted(contacts, key=lambda c: (c.last_name, c.first_name))
    
    for i in range(0, len(sorted_contacts), batch_size):
        batch = sorted_contacts[i:i + batch_size]
        
        # Include overlap with previous batch
        if i > 0:
            overlap = sorted_contacts[max(0, i - 100):i]
            batch = overlap + batch
        
        # Process batch
        batch_duplicates = find_duplicates_in_batch(batch)
        all_duplicates.extend(batch_duplicates)
    
    # Deduplicate results
    return deduplicate_results(all_duplicates)
```

## Testing Strategies

### Test Cases for Deduplication
1. **Exact Duplicates**: Same email/phone
2. **Name Variations**: Bob/Robert, international characters
3. **Company Variations**: IBM vs International Business Machines
4. **Family Members**: Same last name, same address
5. **Different People**: John Smith (Company A) vs John Smith (Company B)
6. **Partial Data**: Contacts with minimal information
7. **Data Quality Issues**: Typos, formatting differences
8. **Edge Cases**: Single name contacts, numbers as names