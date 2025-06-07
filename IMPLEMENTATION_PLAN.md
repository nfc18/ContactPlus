# Contact Cleaner Implementation Plan - Phase 1

## Overview
Build a web-based contact review system for Sara's database (3,075 contacts) with focus on manual review of data quality issues.

## Development Phases

### Phase 1A: Project Setup (Day 1)
1. **Environment Setup**
   ```bash
   ContactPlus/
   ├── app.py              # Flask application
   ├── requirements.txt    # Dependencies
   ├── config.py          # Configuration
   ├── backup/            # Backup directory
   ├── data/              # Working data
   ├── static/            # CSS/JS
   └── templates/         # HTML templates
   ```

2. **Create Backup**
   - Copy Sara's vCard to `backup/` with timestamp
   - Never modify original file

3. **Install Dependencies**
   - Flask (web framework)
   - vobject (vCard parser)
   - Create virtual environment

### Phase 1B: vCard Analysis Engine (Day 1-2)
1. **Parser Module** (`parser.py`)
   - Load and parse vCard file
   - Extract all contact fields properly
   - Handle multi-line fields (photos, notes)

2. **Analysis Module** (`analyzer.py`)
   - Identify contacts with 4+ emails
   - Find empty/problematic names
   - Detect potential duplicates
   - Create review queue

3. **Data Structure**
   ```json
   {
     "review_queue": [
       {
         "id": "uuid-here",
         "name": "Alexander Schoenfeldt",
         "issues": ["too_many_emails"],
         "email_count": 5,
         "emails": [...],
         "original_vcard": "..."
       }
     ]
   }
   ```

### Phase 1C: Web Review Interface (Day 2-3)
1. **Backend Routes**
   - `/` - Dashboard with statistics
   - `/review` - Review interface
   - `/api/contact/<id>` - Get contact data
   - `/api/decision` - Save review decision

2. **Frontend Pages**
   - Simple Bootstrap UI
   - One contact at a time
   - Clear action buttons
   - Progress indicator

3. **Review Actions**
   - Keep all emails
   - Select primary email
   - Remove specific emails
   - Split into multiple contacts
   - Flag for later review

### Phase 1D: Decision Storage (Day 3)
1. **Decision Tracking**
   ```json
   {
     "decisions": {
       "contact-uuid": {
         "action": "select_primary",
         "primary_email": "work@company.com",
         "removed_emails": ["old@previous.com"],
         "timestamp": "2025-01-06T10:30:00",
         "notes": "Kept current work email only"
       }
     }
   }
   ```

2. **Session Management**
   - Save progress automatically
   - Allow resume from interruption
   - Track review statistics

### Phase 1E: Apply Changes (Day 4)
1. **Change Processor** (`processor.py`)
   - Read all decisions
   - Apply changes to create new vCard
   - Maintain data integrity
   - Generate change report

2. **Export Options**
   - Clean vCard file
   - CSV summary of changes
   - Statistics report

## Technical Stack

```txt
Python 3.9+
Flask 3.0.0
vobject 0.9.6
Bootstrap 5 (CDN)
No database needed (JSON files only)
```

## Review Priorities

1. **Contacts with 4+ emails** (46 contacts)
2. **Contacts with special characters in names** (182 contacts)
3. **Potential duplicates** (if time permits)

## Success Criteria

- ✓ No data loss from original file
- ✓ All decisions tracked and reversible
- ✓ Clean, simple UI for non-technical review
- ✓ Export produces valid vCard 3.0
- ✓ Complete review in < 1 hour

## Timeline

- **Day 1**: Setup + Parser
- **Day 2**: Analysis + Web UI
- **Day 3**: Review Interface + Testing
- **Day 4**: Apply changes + Export

## Next Steps After Approval

1. Create project structure
2. Set up virtual environment
3. Create backup of Sara's database
4. Begin parser implementation

---

**Ready to proceed?** This plan focuses on Sara's database only, with a simple but effective review system.