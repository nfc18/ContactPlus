# CLAUDE.md - ContactPlus Project Context

## 🔒 CRITICAL: PHONEBOOK EDITING PROTOCOL
**MANDATORY REQUIREMENT: ALL phonebook modifications MUST follow the exact 6-step process defined in `PHONEBOOK_EDITING_PROTOCOL.md`**

**NO EXCEPTIONS - NO DEVIATIONS - NO SHORTCUTS**

This protocol ensures:
- Data integrity and RFC compliance
- Automatic backups before all changes
- Validation after every modification
- No possibility of data corruption
- Complete audit trail

**⚠️ VIOLATION OF THIS PROTOCOL IS PROHIBITED ⚠️**

---

## Project Overview

ContactPlus is a comprehensive vCard processing system that validates, fixes, and enhances contact databases. It implements a strict validation workflow with both RFC compliance (hard rules) and data quality improvements (soft rules).

## Core Architecture Rule

**MANDATORY**: Always use `vcard` library for validation + `vobject` for manipulation

This separation of concerns ensures:
- Strict RFC 2426 validation with the `vcard` library
- Flexible manipulation with `vobject` 
- Clear boundaries between validation and processing

## Complete Validation Workflow

```
1. Initial Validation (vcard library) - Check RFC compliance
   ↓
2. Hard Compliance Fixes - Add missing FN, VERSION, etc.
   ↓
3. Re-validation (vcard library) - Ensure fixes worked
   ↓
4. Soft Compliance Fixes - Extract emails, fix capitalization, format phones
   ↓
5. Final Validation (vcard library) - Ensure still RFC compliant
```

## Key Modules

### Core Processing
- `vcard_validator.py` - RFC validation using vcard library
- `vcard_fixer.py` - Fix hard compliance issues (missing fields)
- `vcard_soft_compliance.py` - Data quality improvements
- `vcard_workflow.py` - Complete pipeline orchestration

### Web Interface
- `app.py` - Flask application for manual review
- `analyzer.py` - Contact analysis and issue detection
- `parser.py` - Enhanced vCard parser with validation

## Validation Rules

### Hard Compliance (RFC 2426)
- Missing FN (formatted name) - MUST be fixed
- Missing VERSION - MUST be 3.0
- Missing N (structured name) - Should be fixed
- Proper BEGIN/END structure

### Soft Compliance (Data Quality)
- Extract emails/phones from NOTE fields
- Fix name capitalization (JOHN SMITH → John Smith)
- Format phone numbers to E.164 (+15551234567)
- Normalize emails to lowercase
- Remove duplicate emails (case-insensitive)
- Standardize organization names

## Key Commands

### Process vCard file with full workflow
```bash
python vcard_workflow.py
```

### Run web interface for manual review
```bash
python analyze_contacts.py  # First analyze
python app.py              # Then review
```

### Test the validation chain
```bash
python test_validation_chain.py
```

## Important Files to Check

When working on vCard processing:
1. Always check `VCARD_PROCESSING_STANDARD.md` for the mandatory rules
2. Review `vcard_workflow.py` for the complete pipeline
3. Check test files for examples of proper usage

## Testing Guidelines

Always test changes with:
1. Valid vCards - Should pass unchanged
2. Missing FN - Should be fixed and validated
3. Soft issues - Should be improved without breaking compliance
4. Edge cases - Empty fields, special characters, etc.

## Common Pitfalls to Avoid

1. **Never** use vobject for validation - it's too permissive
2. **Never** skip the final validation after soft fixes
3. **Always** create backups before processing
4. **Always** validate at each transformation stage

## Project Status

- ✅ Hard compliance validation and fixing
- ✅ Soft compliance rules implementation  
- ✅ Complete validation chain with safety checks
- ✅ Web interface for manual review
- 🔄 Ready for production use on contact databases

## Next Features Planned

1. Deduplication across contacts
2. LinkedIn data integration
3. Enhanced phone number type detection
4. Photo optimization
5. Social media profile extraction

## Performance Notes

- Sara's database: 3,075 contacts
- Processing time: ~5-10 seconds for full workflow
- Memory usage: Minimal (streaming processing)
- Success rate: 100% importability after fixes