#!/bin/bash

# Contact Cleaner - Start Review Script

echo "========================================"
echo "Contact Cleaner - CLI Review"
echo "========================================"
echo ""
echo "This will start the interactive review process."
echo "You'll review 49 contacts with multiple emails."
echo ""

# Activate virtual environment
source venv/bin/activate

# Run the review tool
python review_cli.py