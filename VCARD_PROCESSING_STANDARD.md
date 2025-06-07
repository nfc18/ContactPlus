# vCard Processing Standard - ContactPlus

## 🚨 MANDATORY RULE

**ALWAYS use vcard library for validation + vobject for manipulation**

This is the required pattern for ALL vCard operations in this project.

## Standard Workflow

```python
# 1. VALIDATE with vcard library
from vcard_validator import VCardStandardsValidator

validator = VCardStandardsValidator()
is_valid, errors, warnings = validator.validate_file(filepath)

# 2. MANIPULATE with vobject (only if valid)
if is_valid or len(errors) < threshold:
    import vobject
    vcards = list(vobject.readComponents(vcard_data))
    # Now manipulate...
```

## Required Pattern Implementation

### ✅ CORRECT Implementation
```python
from vcard_validator import VCardStandardsValidator
import vobject

class MyVCardProcessor:
    def __init__(self):
        # Use vcard library for validation
        self.validator = VCardStandardsValidator()
    
    def process(self, filepath):
        # STEP 1: Validate with vcard library
        is_valid, errors, warnings = self.validator.validate_file(filepath)
        
        # STEP 2: Parse with vobject only if valid
        if is_valid or len(errors) < 100:
            with open(filepath, 'r') as f:
                vcards = list(vobject.readComponents(f.read()))
            # Manipulate with vobject...
```

### ❌ INCORRECT Implementation
```python
# WRONG: Using only vobject
import vobject
vcards = vobject.readComponents(data)  # NO validation!

# WRONG: Using vcard for manipulation
import vcard
vcard.modify_contact()  # vcard is for validation ONLY!
```

## Library Responsibilities

### vcard Library (Validation ONLY)
- RFC 2426 compliance checking
- Structure validation
- Required fields verification
- Standards conformance
- Error/warning reporting

### vobject Library (Manipulation ONLY)
- Parsing vCard data
- Creating new vCards
- Modifying properties
- Serializing to string
- Data extraction

## Implementation Checklist

When creating ANY vCard processing script:

- [ ] Import `VCardStandardsValidator` from `vcard_validator.py`
- [ ] Create validator instance
- [ ] Validate file FIRST with vcard library
- [ ] Check validation results
- [ ] Only proceed to vobject if validation passes (or errors are acceptable)
- [ ] Use vobject for all data manipulation
- [ ] Document that the script follows the standard pattern

## Example Scripts Following the Standard

1. **parser.py** - Updated to validate before parsing
2. **vcard_validator.py** - Reference implementation
3. **apply_changes.py** - Must be updated to follow pattern
4. **analyze_contacts.py** - Must be updated to follow pattern

## Error Handling

```python
# Standard error handling pattern
validator = VCardStandardsValidator()
is_valid, errors, warnings = validator.validate_file(filepath)

if not is_valid:
    if len(errors) > 100:
        # Too many errors - abort
        raise ValueError(f"File has {len(errors)} validation errors")
    else:
        # Some errors but proceed with caution
        logger.warning(f"Processing file with {len(errors)} errors")
        
# Safe to use vobject now
vcards = parse_with_vobject(filepath)
```

## Migration Guide

To update existing scripts:

1. Add import: `from vcard_validator import VCardStandardsValidator`
2. Before any vobject usage, add validation:
   ```python
   validator = VCardStandardsValidator()
   is_valid, errors, warnings = validator.validate_file(filepath)
   ```
3. Wrap vobject code in validation check
4. Add logging for validation results

## Enforcement

- All PRs must follow this pattern
- Code reviews will check for compliance
- Automated tests will verify the pattern is followed
- Non-compliant code will be rejected

Remember: **vcard for validation, vobject for manipulation** - ALWAYS!