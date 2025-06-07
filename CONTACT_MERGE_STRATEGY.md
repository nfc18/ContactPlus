# Contact Database Merge Strategy

## Executive Summary
This document outlines a comprehensive strategy for merging three contact databases while maintaining data integrity, preventing incorrect merges, and preserving all valuable information.

## 1. Contact Matching Strategy

### 1.1 Primary Matching Criteria (High Confidence)
**These indicate the same person with high confidence:**

1. **Email Match** (Confidence: 95%)
   - Exact email address match
   - Case-insensitive comparison
   - Trim whitespace

2. **Phone Match** (Confidence: 90%)
   - Normalized phone number match (E.164 format)
   - Match last 10 digits for international variations
   - Consider numbers identical if they differ only by country code

3. **Combined Criteria** (Confidence: 98%)
   - Name similarity >80% AND (same email domain OR same organization)
   - Name similarity >70% AND (same phone area code OR same city)

### 1.2 Secondary Matching (Medium Confidence)
**These require additional verification:**

1. **Name + Organization** (Confidence: 85%)
   - Exact name match AND exact organization match
   - Handles cases like "John Smith at Apple"

2. **Name + Location** (Confidence: 75%)
   - Exact name match AND same city/region
   - Useful for local contacts

### 1.3 Non-Matching Criteria
**Never merge contacts when:**
- Only name matches (too many false positives)
- Different organizations for common names
- Email domains suggest different people (e.g., @company1.com vs @company2.com)

### 1.4 Special Cases
**Known duplicate names (keep separate):**
- Bernhard Reiterer (Anyline) vs Bernhard Reiterer (signd.id)
- Christian Pichler (Anyline) vs Christian Pichler (Tyrolit)

## 2. Database Priority Rules

### 2.1 Source Hierarchy
When merging, prioritize data based on source reliability:

1. **Sara's Database** (Primary)
   - Most curated and maintained
   - Likely contains most accurate business contacts
   - Priority weight: 100

2. **iPhone Contacts** (Secondary)
   - Actively used, regularly updated
   - Mix of personal and business
   - Priority weight: 80

3. **iPhone Suggested** (Tertiary)
   - Auto-captured, less verified
   - May contain outdated information
   - Priority weight: 60

### 2.2 Field-Level Priority
Different fields may have different priority rules:

| Field | Priority Rule | Rationale |
|-------|--------------|-----------|
| Name | Longest/most complete | "John Smith Jr." > "John Smith" |
| Organization | Most recent/specific | "Apple Inc." > "Apple" |
| Phone | Most formatted | "+1-555-123-4567" > "5551234567" |
| Email | All unique kept | Preserve all valid emails |
| Address | Most complete | Full address > partial |
| Notes | Concatenate all | Preserve all information |
| Photo | Highest quality | Largest file size/newest |

## 3. Data Preservation Rules

### 3.1 Additive Fields (Keep All Unique)
- **Emails**: Keep all unique email addresses
- **Phone Numbers**: Keep all unique phone numbers
- **URLs**: Keep all unique URLs
- **Addresses**: Keep all unique addresses

### 3.2 Selective Fields (Choose Best)
- **Name**: Select most complete version
- **Organization**: Select most specific/recent
- **Title**: Select most recent/specific
- **Birthday**: Verify consistency, flag conflicts

### 3.3 Merged Fields
- **Notes**: Concatenate with timestamps
  ```
  [From Sara DB]: Original note
  [From iPhone, 2024]: Additional note
  ```

### 3.4 Conflict Resolution
When data conflicts:
1. Flag for manual review if critical (e.g., different birthdays)
2. Use priority rules for non-critical fields
3. Preserve both in notes if important

## 4. Merge Process Workflow

### Phase 1: Preparation
1. **Backup all databases**
2. **Validate each database** (RFC compliance)
3. **Normalize data** (phone numbers, emails, names)
4. **Create merge audit log**

### Phase 2: Matching
1. **Build match groups** using criteria above
2. **Score each match** (0-100 confidence)
3. **Separate into buckets:**
   - Auto-merge (95%+ confidence)
   - Review recommended (70-94% confidence)
   - Keep separate (<70% confidence)

### Phase 3: Merging
1. **Process auto-merge group**
   - Apply priority rules
   - Preserve all unique data
   - Log all decisions

2. **Generate review list**
   - Medium confidence matches
   - Conflicts in critical fields
   - Special cases (duplicate names)

3. **Manual review** (estimated 20-30 contacts)
   - Present clear comparison
   - Allow merge/keep separate decision
   - Document reasoning

### Phase 4: Post-Processing
1. **Validate merged database**
2. **Check for data loss**
3. **Generate merge report**
4. **Final soft compliance check**

## 5. Implementation Example

### Example 1: Simple Email Match
```
Sara DB:     John Smith (john@email.com, Apple Inc.)
iPhone:      John Smith (john@email.com, 555-1234)
Result:      John Smith (john@email.com, Apple Inc., 555-1234)
```

### Example 2: Conflicting Organizations
```
Sara DB:     Jane Doe (jane@email.com, Microsoft)
iPhone:      Jane Doe (jane@email.com, Google)
Action:      Flag for review - possible job change
```

### Example 3: Duplicate Names
```
Contact 1:   Christian Pichler (christian@anyline.com)
Contact 2:   Christian Pichler (cpichler@tyrolit.com)
Action:      Keep separate - different people
```

## 6. Quality Metrics

### Success Metrics
- **Correct Merges**: >99% accuracy
- **False Positives**: <0.1% (incorrect merges)
- **Data Preservation**: 100% of unique data retained
- **Review Burden**: <50 contacts requiring manual review

### Validation Checks
1. No contacts lost (sum of originals = merged + kept separate)
2. No data fields lost (all emails, phones preserved)
3. No RFC compliance issues introduced
4. Audit trail for every merge decision

## 7. Manual Review Interface

For contacts requiring review, present:
```
POTENTIAL MATCH (Confidence: 85%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Source 1 (Sara DB):
  Name: John Smith
  Org:  Apple Inc.
  Email: jsmith@apple.com
  Phone: +1-408-555-1234

Source 2 (iPhone):
  Name: John R. Smith  
  Org:  Apple
  Email: john.smith@apple.com
  Phone: +1-408-555-1234

Matching Factors:
  ✓ Same phone number
  ✓ Similar name (90%)
  ✓ Same organization
  ⚠️ Different email format

[MERGE] [KEEP SEPARATE] [SKIP]
```

## 8. Special Handling Rules

### 8.1 Company Contacts
- Preserve all email variations (john@company, j.smith@company)
- Keep work and personal phones
- Maintain history in notes

### 8.2 Evolved Contacts
- Job changes: Keep org history in notes
- Email changes: Preserve old emails as secondary
- Name changes: Note previous names

### 8.3 Shared Contacts
- Family members with shared emails
- Assistants with boss's contact info
- Company general contacts (info@, support@)

## 9. Final Recommendations

1. **Start Conservative**: Better to keep contacts separate than merge incorrectly
2. **Audit Everything**: Every decision should be logged and reversible
3. **Preserve Data**: Never delete data, only reorganize
4. **Manual Review**: Budget 30-60 minutes for reviewing 50 contacts
5. **Test First**: Run on small subset before full merge

## 10. Expected Outcomes

From your three databases:
- **Input**: ~7,076 total contacts
- **Expected after merge**: ~3,500-4,000 unique contacts
- **Requiring review**: 30-50 contacts
- **Processing time**: 2-3 minutes automated + 30-60 minutes review