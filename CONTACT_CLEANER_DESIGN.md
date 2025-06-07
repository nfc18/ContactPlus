# Contact Cleaner System Design

## Overview
This document outlines the design for a comprehensive contact management system that imports, cleans, merges, enhances, and rates contacts from multiple sources.

## Architecture Components

### 1. Contact Import Module

#### Supported Formats
- **vCard 3.0/4.0** (.vcf files)
- **CSV exports** (LinkedIn, Gmail, Outlook)
- **JSON formats** (various CRM exports)

#### Import Workflow
1. **File Detection**: Identify file type and version
2. **Parsing**: Use `vobject` library for vCard files
3. **Normalization**: Convert all contacts to internal format
4. **Validation**: Check for required fields and data integrity
5. **Storage**: Save to database with import metadata

### 2. Data Cleaning Module

#### Cleaning Rules
1. **Name Normalization**
   - Title case for names (John Smith, not JOHN SMITH or john smith)
   - Detect and separate titles (Dr., Prof., etc.)
   - Handle special characters and diacritics properly

2. **Phone Number Standardization**
   - Convert to E.164 format (+1234567890)
   - Extract phone numbers from NOTE fields
   - Validate country codes
   - Remove duplicates

3. **Email Validation**
   - Lowercase all email addresses
   - Validate email format
   - Extract emails from NOTE fields
   - Remove invalid addresses

4. **Address Formatting**
   - Standardize country names
   - Format postal codes
   - Geocode when possible

5. **Data Migration from Notes**
   - Extract phone numbers from NOTE fields
   - Extract email addresses from NOTE fields
   - Extract social media URLs
   - Move to appropriate fields

6. **Organization Cleanup**
   - Standardize company names
   - Remove redundant suffixes (GmbH, Inc., etc. when appropriate)

### 3. Contact Merging Module

#### Duplicate Detection Strategy
1. **Exact Matching**
   - Same email address
   - Same phone number
   - Same full name + company

2. **Fuzzy Matching**
   - Similar names (using Levenshtein distance)
   - Nickname variations (Bob/Robert, etc.)
   - Company variations
   - Similar phone numbers (with/without country code)

#### Merge Rules
1. **Automatic Merge Criteria**
   - Same email OR phone number
   - Confidence score > 90%
   - Less than 3 email addresses total

2. **Manual Review Required**
   - Same name, different companies
   - More than 3 email addresses
   - Conflicting critical data
   - Confidence score 70-90%

3. **Photo Selection**
   - Prefer higher resolution
   - Prefer newer photos
   - Keep all photos with ALTID

4. **Field Priority**
   - Newer data generally preferred
   - LinkedIn data for professional info
   - Phone contacts for personal info
   - User can set custom priorities

### 4. Data Enhancement Module

#### LinkedIn Enhancement
- Match contacts by name + company
- Update job titles
- Add company information
- Add LinkedIn URLs
- Update professional email addresses

#### Email Analysis Enhancement
- Analyze Sent Mail folder
- Count interactions per contact
- Calculate last interaction date
- Determine relationship strength
- Extract email signatures for additional data

#### External APIs (Optional)
- Clearbit for company data
- FullContact for social profiles
- Google Places for address validation

### 5. Contact Rating System

#### Rating Factors (0-100 scale)
1. **Interaction Frequency** (30%)
   - Email count in last year
   - Email count in last 3 months
   - Two-way communication bonus

2. **Data Completeness** (20%)
   - Has phone number
   - Has email
   - Has address
   - Has company/title
   - Has photo

3. **Relationship Type** (25%)
   - Professional contact
   - Personal contact
   - Family member (from groups/tags)
   - VIP status

4. **Recency** (15%)
   - Last interaction date
   - Contact update date
   - Connection date (LinkedIn)

5. **Data Quality** (10%)
   - Verified email
   - Valid phone number
   - Complete address
   - No data in wrong fields

#### Export Thresholds
- **Premium** (80-100): Close contacts, frequent interaction
- **Standard** (60-79): Regular contacts
- **Archive** (40-59): Occasional contacts
- **Review** (0-39): Outdated or incomplete

### 6. History & Rollback System

#### Version Control
- Each contact maintains version history
- Track all changes with timestamps
- Store change reasons
- Link related changes (batch operations)

#### Rollback Capabilities
- Rollback individual contact changes
- Rollback batch operations
- Restore from specific date
- Preview before rollback

#### Audit Trail
- Import sources and dates
- Merge operations
- Manual edits
- Enhancement sources
- Export history

### 7. Export Module

#### Export Formats
- vCard 4.0 (recommended)
- vCard 3.0 (compatibility)
- CSV (Gmail format)
- CSV (Outlook format)
- JSON (for APIs)

#### Export Options
- Filter by rating threshold
- Include/exclude specific fields
- Group by categories
- Split large exports

### 8. Testing Strategy

#### Unit Tests
- vCard parsing/generation
- Field validation
- Merge logic
- Rating calculations

#### Integration Tests
- Import → Clean → Merge workflow
- Enhancement APIs
- Database operations
- Export validation

#### Compliance Tests
- vCard 3.0/4.0 standards
- Character encoding
- Photo handling
- Multi-value fields

## Technology Stack

### Recommended Libraries
- **vobject**: vCard parsing and generation
- **phonenumbers**: Phone number validation
- **email-validator**: Email validation
- **fuzzywuzzy**: Fuzzy string matching
- **SQLAlchemy**: Database ORM
- **pandas**: Data manipulation
- **Pillow**: Image processing

### Database Schema
```sql
-- Contacts table
CREATE TABLE contacts (
    id UUID PRIMARY KEY,
    version INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    source_file TEXT,
    data JSONB,
    rating FLOAT,
    status TEXT
);

-- Contact versions for history
CREATE TABLE contact_versions (
    id UUID PRIMARY KEY,
    contact_id UUID REFERENCES contacts(id),
    version INTEGER,
    changed_at TIMESTAMP,
    changed_by TEXT,
    data JSONB,
    change_reason TEXT
);

-- Merge history
CREATE TABLE merge_history (
    id UUID PRIMARY KEY,
    primary_contact_id UUID,
    merged_contact_id UUID,
    merge_date TIMESTAMP,
    confidence_score FLOAT,
    merge_data JSONB
);
```

## Implementation Phases

### Phase 1: Foundation
- Set up project structure
- Implement vCard parser
- Create database schema
- Basic import functionality

### Phase 2: Cleaning
- Implement cleaning rules
- Data validation
- Field standardization
- Notes field extraction

### Phase 3: Merging
- Duplicate detection
- Merge logic
- Conflict resolution
- Manual review interface

### Phase 4: Enhancement
- LinkedIn data integration
- Email analysis
- External API integration

### Phase 5: Rating & Export
- Rating algorithm
- Export functionality
- History tracking
- Rollback features

### Phase 6: Testing & Polish
- Comprehensive testing
- Performance optimization
- Documentation
- User interface

## Key Considerations

### Performance
- Batch processing for large datasets
- Indexed searching
- Caching for duplicate detection
- Parallel processing where possible

### Privacy
- Local processing by default
- Optional cloud features
- Secure API credentials
- Data encryption at rest

### User Experience
- Clear progress indicators
- Preview before apply
- Undo functionality
- Detailed logs
- Export reports

### Data Integrity
- Never delete source data
- Validate before commit
- Atomic operations
- Backup before major operations