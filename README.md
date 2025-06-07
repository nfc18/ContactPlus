# ContactPlus - Professional vCard Processing System

A comprehensive system for validating, cleaning, and enhancing vCard contact databases with both RFC compliance (hard rules) and data quality improvements (soft rules).

## Key Features

- **🔍 Dual Validation**: RFC 2426 compliance + data quality checks
- **🔧 Automatic Fixing**: Repairs missing fields and formatting issues
- **✅ Safety First**: Validates after each transformation
- **📊 Web Interface**: Review and manage contacts easily
- **🔄 Complete Workflow**: Validate → Fix → Soft Compliance → Final Check

## Quick Start

### 1. Set up environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Process vCard files (Complete Workflow)
```bash
# Run the complete validation and fixing workflow
python vcard_workflow.py

# Or use the simple one-liner
python -c "from vcard_workflow import ensure_valid_vcards; ensure_valid_vcards('contacts.vcf')"
```

This will:
1. **Validate** with vcard library (RFC compliance)
2. **Fix** hard compliance issues (missing FN, VERSION)
3. **Re-validate** to ensure fixes worked
4. **Apply** soft compliance (extract emails from notes, fix names)
5. **Final validation** to ensure still RFC compliant
6. **Output** clean, validated vCard file

### 3. Manual review (Web Interface)
```bash
# First analyze contacts
python analyze_contacts.py

# Then start web interface
python app.py
```

Then open http://localhost:5000 in your browser for manual review of complex cases.

## Validation Workflow

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│ 1. Validate │ → │ 2. Hard Fix  │ → │ 3. Validate │ → │ 4. Soft Fix │ → │ 5. Validate │
│   (vcard)   │    │ (RFC comply) │    │   (vcard)   │    │ (quality)   │    │   (vcard)   │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘    └──────────────┘
```

## Project Structure
```
ContactPlus/
├── Core Modules
│   ├── vcard_validator.py      # RFC validation using vcard library
│   ├── vcard_fixer.py         # Fix RFC compliance issues
│   ├── vcard_soft_compliance.py # Data quality improvements
│   └── vcard_workflow.py      # Complete processing pipeline
├── Web Interface
│   ├── app.py                 # Flask web application
│   ├── templates/             # HTML templates
│   └── static/                # CSS/JS files
├── Analysis Tools
│   ├── parser.py              # vCard parser with validation
│   ├── analyzer.py            # Contact analysis module
│   └── analyze_contacts.py    # CLI analysis script
├── Documentation
│   ├── VCARD_PROCESSING_STANDARD.md  # Mandatory rules
│   ├── COMPLETE_VCARD_WORKFLOW.md    # Full workflow guide
│   ├── SOFT_COMPLIANCE_RULES.md      # Data quality rules
│   └── VALIDATION_SAFETY.md          # Why we validate multiple times
└── Configuration
    ├── config.py              # Configuration settings
    └── requirements.txt       # Python dependencies
```

## Validation Rules

### Hard Compliance (RFC 2426)
- **Required Fields**: FN (formatted name), VERSION
- **Structure**: Proper BEGIN/END vCard blocks
- **Encoding**: Valid character encoding

### Soft Compliance (Data Quality)
- **Extract contacts from notes**: Move emails/phones to proper fields
- **Name capitalization**: John SMITH → John Smith
- **Phone formatting**: (555) 123-4567 → +15551234567
- **Email normalization**: John@EXAMPLE.com → john@example.com
- **Remove duplicates**: Case-insensitive deduplication

## Architecture Rule

**MANDATORY**: Always use `vcard` library for validation + `vobject` for manipulation

```python
# CORRECT approach
validator = VCardStandardsValidator()  # vcard library
is_valid, errors, warnings = validator.validate_file(filepath)

if is_valid:
    vcards = vobject.readComponents(data)  # vobject for manipulation
```

## Data Safety

- Original vCard files are never modified
- Automatic backups before processing
- Validation at every stage ensures no data corruption
- Complete audit trail of all changes
- Ability to revert to any previous state

## Usage Examples

### Process a vCard file with full workflow
```python
from vcard_workflow import VCardWorkflow

workflow = VCardWorkflow(auto_fix=True, backup=True, soft_compliance=True)
result = workflow.process_file("contacts.vcf")

print(f"Processed {result['vcards_parsed']} contacts")
print(f"Fixed {result['fix_report']['fixes_applied']['missing_fn_fixed']} missing names")
```

### Apply only soft compliance fixes
```python
from vcard_soft_compliance import SoftComplianceChecker

checker = SoftComplianceChecker()
result = checker.check_and_fix_file("input.vcf", "output.vcf")
```

## Results on Test Data

- **Sara's Database**: 3,075 contacts
- **Initial Errors**: 96 (missing FN fields)
- **After Hard Fix**: 0 errors
- **After Soft Fix**: 0 errors (maintained compliance!)
- **Success Rate**: 100%# Runner setup completed Sat Jun  7 21:40:48 CEST 2025
# Testing GitHub Actions with active runner Sat Jun  7 21:41:37 CEST 2025
