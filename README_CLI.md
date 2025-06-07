# Contact Cleaner - CLI Version

A command-line tool for reviewing and cleaning vCard contact databases.

## Quick Start

### 1. Set up environment
```bash
# Create virtual environment (if not already done)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Analyze contacts
```bash
python analyze_contacts.py
```

This will:
- Parse Sara's vCard file (3,075 contacts)
- Identify 49 contacts with issues (4+ emails)
- Create a review queue

### 3. Review contacts via CLI
```bash
python review_cli.py
```

The CLI tool will:
- Show one contact at a time
- Display all email addresses
- Show identified issues
- Let you choose an action

### 4. Apply changes
```bash
python apply_changes.py
```

This creates a cleaned vCard file with your changes applied.

## CLI Review Actions

For each contact, you can choose:

1. **Keep All** - Keep all email addresses as-is
2. **Primary Only** - Keep only the first email address
3. **Select Emails** - Choose specific emails to keep
4. **Split Contact** - Mark for manual splitting (adds a note)
5. **Skip** - Review this contact later
6. **Quit** - Save progress and exit

## Example Review Session

```
============================================================
Contact Review - 1 of 49 (2%)
============================================================

Name: 9yards Contact
Organization: Anyline

📧 Email Addresses (15)
----------------------------------------
1. barbara@anyline.com [PRIMARY]
2. stefan@anyline.com
3. lukas@anyline.com
4. jakob@anyline.io
... (more emails)

⚠️  Issues Found
----------------------------------------
• Too many email addresses (15)
• Mixed email domains (2 different domains)

Available Actions:
1. Keep All - Keep all email addresses
2. Primary Only - Keep only the first (primary) email
3. Select Emails - Choose which emails to keep
4. Split Contact - Mark for splitting into multiple contacts
5. Skip - Review this contact later
6. Quit - Save progress and exit

Enter your choice (1-6): 4
```

## Features

- ✅ Color-coded terminal output
- ✅ Progress tracking (shows X of Y)
- ✅ Saves after each decision
- ✅ Resume capability - quit anytime and continue later
- ✅ Interactive email selection
- ✅ Creates detailed report after applying changes

## Output Files

After completing the review and applying changes:
- `data/Sara_Export_CLEANED_YYYYMMDD.vcf` - Cleaned vCard file
- `data/Sara_Export_CLEANED_YYYYMMDD_report.txt` - Summary report

## Tips

- The first email is considered the "primary" email
- Press Enter to quickly move to the next contact
- Your progress is saved after each decision
- You can quit and resume anytime