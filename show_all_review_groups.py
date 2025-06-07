#!/usr/bin/env python3
"""
Extract and display all review groups from the HTML
"""

import re

# Read the review file
with open('data/MASTER_CONTACTS_20250606_141220_review.html', 'r') as f:
    content = f.read()

# Find all group IDs
groups = re.findall(r'id="group-(\d+)"', content)
print(f"Found {len(groups)} groups in HTML: {sorted(set(groups))}")

# Check if there's a continuation marker
if "markDecision" in content:
    decision_calls = re.findall(r"markDecision\('(?:merge|separate)', (\d+)\)", content)
    unique_groups = sorted(set(decision_calls), key=int)
    print(f"Decision buttons for groups: {unique_groups}")

# Let's also check the end of the file
lines = content.split('\n')
print(f"\nTotal lines in file: {len(lines)}")
print("\nLast 20 lines:")
for line in lines[-20:]:
    print(line)

# Check if file might be truncated
if not content.strip().endswith('</html>'):
    print("\n⚠️  WARNING: HTML file appears to be truncated!")