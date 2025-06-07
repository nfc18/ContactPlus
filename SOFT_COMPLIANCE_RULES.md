# Soft Compliance Rules - Data Quality Standards

## Overview

Soft compliance rules improve data quality beyond RFC standards. These are business logic rules that ensure consistent, clean, and usable contact data.

## Implemented Rules

### 1. 📧 Email/Phone Extraction from Notes
**Rule**: No contact information should be in notes fields
- **Detection**: Regex patterns find emails and phones in NOTE fields
- **Fix**: Extract and move to proper EMAIL/TEL properties
- **Example**: 
  - Before: `NOTE: Call 555-1234 or email john@example.com`
  - After: `NOTE: Call or email` + new EMAIL and TEL entries

### 2. 🔤 Name Capitalization
**Rule**: Names should use proper case (not ALL CAPS or all lowercase)
- **Fix**: Intelligent capitalization handling special cases
- **Special cases handled**:
  - Suffixes: Jr, Sr, II, III, MD, PhD → uppercase
  - Particles: de, van, von, la → lowercase
  - Irish names: O'Brien, O'Neill → proper apostrophe handling
  - Hyphenated: Smith-Jones → both parts capitalized
- **Example**:
  - `JOHN SMITH` → `John Smith`
  - `o'brien, patrick` → `O'Brien, Patrick`
  - `MARY ANNE DE LA CRUZ` → `Mary Anne de la Cruz`

### 3. 📱 Phone Number Formatting
**Rule**: All phone numbers should be in E.164 format (+1234567890)
- **Uses**: Google's libphonenumber for parsing
- **Fix**: Parse and reformat to international standard
- **Example**:
  - `(212) 555-1234` → `+12125551234`
  - `44 20 7123 4567` → `+442071234567`

### 4. ✉️ Email Normalization
**Rule**: Emails should be lowercase and validated
- **Fix**: Validate syntax, normalize to lowercase
- **Duplicate removal**: Case-insensitive deduplication
- **Example**:
  - `John@COMPANY.COM` → `john@company.com`
  - Removes duplicate `JOHN@company.com`

### 5. 🏢 Organization Standardization
**Rule**: Organization names should be properly capitalized
- **Preserves common acronyms**: LLC, INC, GMBH, AG, LTD, IT, CEO
- **Example**:
  - `acme corp` → `Acme CORP`
  - `it department` → `IT Department`

### 6. 🧹 Notes Field Cleanup
**Rule**: Remove extracted data and clean whitespace
- **Fix**: After extraction, clean up extra spaces
- **Preserves**: Important contextual information

## Additional Suggestions

### Currently Available:
1. **Duplicate Contact Detection** - Within single vCard
2. **Email Domain Validation** - Checks if domain exists
3. **URL Validation** - Ensures URLs are properly formatted

### Future Enhancements:
1. **Phone Type Detection** - Identify mobile vs landline
2. **Address Standardization** - Consistent formatting
3. **Photo Optimization** - Resize/compress large images
4. **Social Media Extraction** - Parse LinkedIn, Twitter from URLs
5. **Title Normalization** - CEO vs Chief Executive Officer
6. **Birthday Formatting** - Consistent date formats
7. **Time Zone Detection** - From phone numbers/addresses

## Workflow Integration

The soft compliance check is integrated into the standard workflow:

```
1. Hard Compliance (RFC validation) ✓
2. Fix RFC violations ✓
3. Soft Compliance (data quality) ✓  ← You are here
4. Parse and process
```

## Usage

### Standalone:
```python
from vcard_soft_compliance import SoftComplianceChecker

checker = SoftComplianceChecker()
result = checker.check_and_fix_file('input.vcf', 'output.vcf')
```

### In Workflow:
```python
workflow = VCardWorkflow(
    auto_fix=True,          # Fix RFC violations
    backup=True,            # Create backups
    soft_compliance=True    # Apply soft rules
)
result = workflow.process_file('contacts.vcf')
```

## Impact on Sara's Database

Expected improvements:
- ~100+ names properly capitalized
- Phone numbers standardized to E.164
- Emails normalized and deduplicated
- Any contact info in notes extracted
- Organization names standardized

## Configuration

Default settings:
- Phone country: US (for parsing ambiguous numbers)
- Name particles: de, van, von, der, la, di
- Org acronyms: LLC, INC, CORP, GMBH, AG, etc.

These can be customized based on your contact database demographics.