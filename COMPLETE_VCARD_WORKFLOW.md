# Complete vCard Processing Workflow

## Overview

Our vCard processing system implements a comprehensive 3-stage workflow that ensures both **RFC compliance** (hard rules) and **data quality** (soft rules).

## The Complete Validation Chain

```
┌─────────────────┐     ┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ 1. VALIDATION   │ --> │ 2. HARD FIXES   │ --> │ 3. RE-VALIDATE  │ --> │ 4. SOFT FIXES   │
│ (vcard library) │     │ (RFC compliance)│     │ (vcard library) │     │ (Data quality)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                        │                        │
         ▼                       ▼                        ▼                        ▼
   Identify errors          Fix violations          Verify fixes OK         Improve quality
   - Missing FN            - Add FN from data      - Check compliance      - Extract contacts
   - Missing VERSION       - Add N structure       - Confirm valid         - Fix names  
   - Invalid structure     - Add VERSION 3.0       - Ready for soft        - Format phones
                                                                                     │
                                                                                     ▼
                                                                           ┌─────────────────┐
                                                                           │ 5. FINAL CHECK  │
                                                                           │ (vcard library) │
                                                                           └─────────────────┘
                                                                                     │
                                                                                     ▼
                                                                            Ensure RFC compliant
```

## Stage 1: Validation (vcard library)

**Purpose**: Identify RFC 2426 violations

Checks for:
- Required fields (FN, VERSION)
- Proper vCard structure (BEGIN/END)
- Valid property syntax
- Standards compliance

## Stage 2: Hard Compliance Fixes

**Purpose**: Fix RFC violations to ensure importability

Fixes:
- **Missing FN**: Generate from N, ORG, email, or phone
- **Missing N**: Parse from FN or create empty structure
- **Missing VERSION**: Add VERSION:3.0
- **Structure issues**: Ensure proper BEGIN/END

## Stage 3: Re-Validation

**Purpose**: Ensure hard fixes worked correctly

Checks:
- All required fields now present
- vCard structure is valid
- Ready for soft compliance improvements

## Stage 4: Soft Compliance Fixes

**Purpose**: Improve data quality and consistency

Fixes:
- **Extract contact info from notes**: Move emails/phones to proper fields
- **Name capitalization**: 
  - JOHN SMITH → John Smith
  - jane doe → Jane Doe
  - O'BRIEN → O'Brien
- **Phone formatting**: Convert to E.164 (+12125551234)
- **Email normalization**: Lowercase and validate
- **Remove duplicates**: Case-insensitive deduplication
- **Organization standardization**: Proper capitalization with acronyms

## Stage 5: Final Validation

**Purpose**: Ensure soft fixes didn't break RFC compliance

Verifies:
- Still has all required fields (FN, VERSION)
- No structural damage from data extraction
- Maintains importability
- Catches any regression issues

**Key Safety**: If soft compliance introduces errors, they are logged and can be reviewed

## Usage

### Simple One-Line Processing
```python
from vcard_workflow import ensure_valid_vcards

# Ensures file is valid and clean
clean_file = ensure_valid_vcards("contacts.vcf")
```

### Full Workflow Control
```python
from vcard_workflow import VCardWorkflow

workflow = VCardWorkflow(
    auto_fix=True,         # Apply hard fixes
    backup=True,           # Create backup first
    soft_compliance=True   # Apply soft fixes
)

result = workflow.process_file("contacts.vcf")
```

### Custom Processing
```python
# 1. Validate only
from vcard_validator import VCardStandardsValidator
validator = VCardStandardsValidator()
is_valid, errors, warnings = validator.validate_file("contacts.vcf")

# 2. Fix hard compliance only
from vcard_fixer import VCardFixer
fixer = VCardFixer()
fixer.fix_file("contacts.vcf", "fixed.vcf")

# 3. Apply soft compliance only
from vcard_soft_compliance import SoftComplianceChecker
soft_checker = SoftComplianceChecker()
soft_checker.check_and_fix_file("fixed.vcf", "clean.vcf")
```

## Example Results

### Input vCard (with issues):
```vcard
BEGIN:VCARD
VERSION:3.0
N:SMITH;JOHN;;;
TEL:(212) 555-1234
EMAIL:JOHN@COMPANY.COM
NOTE:Alternative email: john.smith@gmail.com
END:VCARD
```

### After Stage 2 (RFC compliant):
```vcard
BEGIN:VCARD
VERSION:3.0
FN:John Smith
N:SMITH;JOHN;;;
TEL:(212) 555-1234
EMAIL:JOHN@COMPANY.COM
NOTE:Alternative email: john.smith@gmail.com
END:VCARD
```

### After Stage 4 & 5 (Clean, consistent & validated):
```vcard
BEGIN:VCARD
VERSION:3.0
FN:John Smith
N:Smith;John;;;
TEL:+12125551234
EMAIL:john@company.com
EMAIL:john.smith@gmail.com
NOTE:Alternative email: 
END:VCARD
```

## Configuration

### Default Settings
- Phone country: US
- Name particles: de, van, von, la, etc.
- Org acronyms: LLC, INC, CORP, IT, CEO, etc.

### Custom Configuration
```python
workflow = VCardWorkflow()
result = workflow.process_file(
    "contacts.vcf",
    default_country="GB",  # UK phone parsing
    strict=False          # Allow some violations
)
```

## File Outputs

For input file `contacts.vcf`, the workflow creates:
- `backup/workflow/contacts.vcf_TIMESTAMP.backup` - Original backup
- `contacts_FIXED.vcf` - After hard compliance fixes
- `contacts_FIXED_SOFT.vcf` - After soft compliance fixes

## Monitoring & Reporting

The workflow provides detailed reporting at each validation point:
```json
{
  "initial_validation": {
    "valid": false,
    "error_count": 96
  },
  "post_fix_validation": {
    "valid": true,
    "error_count": 0
  },
  "soft_compliance_report": {
    "issues_found": 150,
    "fixes_applied": {
      "emails_extracted_from_notes": 15,
      "names_capitalized": 234,
      "phones_formatted": 567
    }
  },
  "post_soft_validation": {
    "valid": true,
    "error_count": 0
  },
  "validation_summary": "1 → 0 → 0 errors"
}
```

## Best Practices

1. **Always backup first** - The workflow creates automatic backups
2. **Review soft fixes** - Some may need manual verification
3. **Test on samples** - Process a few contacts first
4. **Check logs** - Detailed logging helps troubleshoot issues
5. **Validate output** - Ensure compatibility with target systems

## Next Steps

With clean, compliant vCards you can:
1. Import to any contact management system
2. Proceed with deduplication
3. Enhance with external data
4. Apply business logic rules
5. Export to specific platforms

The workflow ensures a solid foundation of standardized contact data for all downstream processing.