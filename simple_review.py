#!/usr/bin/env python3
"""
Dead simple review - just print the groups and ask for decisions
"""

import json

# Read the original HTML to extract the contact info
with open('data/MASTER_CONTACTS_20250606_141220_review.html', 'r') as f:
    html = f.read()

# Extract each group's text content
import re

# Your existing decisions
decisions = {"0": "separate", "1": "separate", "2": "merge", "3": "separate"}

print("CONTACT MERGE REVIEW")
print("=" * 80)
print(f"You've already reviewed 4 groups. Here are the remaining 10:\n")

# Simple extraction of contact info
groups = re.findall(r'group-(\d+)".*?Match Type:</strong>\s*(\w+).*?Match Value:</strong>\s*(.*?)</div>(.*?)(?=<div class="match-group"|</body>)', html, re.DOTALL)

for group_id, match_type, match_value, content in groups:
    if group_id in decisions:
        continue  # Skip already decided
    
    print(f"\n{'='*80}")
    print(f"GROUP #{int(group_id)+1} (ID: {group_id})")
    print(f"Match Type: {match_type}")
    print(f"Match Value: {match_value}")
    print("-" * 40)
    
    # Extract contact details
    contacts = re.findall(r'Source:\s*(.*?)</div>.*?Name:</span>\s*(.*?)</div>.*?(?:Organization:</span>\s*(.*?)</div>)?.*?(?:Emails:</span>\s*(.*?)</div>)?', content, re.DOTALL)
    
    for i, (source, name, org, emails) in enumerate(contacts):
        print(f"\nContact {i+1}:")
        print(f"  Source: {source}")
        print(f"  Name: {name}")
        if org and org.strip() != "No organization":
            print(f"  Org: {org}")
        if emails:
            print(f"  Emails: {emails}")
    
    # Get decision
    while True:
        decision = input(f"\nDecision for Group {group_id} (m=merge, s=separate): ").strip().lower()
        if decision in ['m', 's']:
            decisions[group_id] = 'merge' if decision == 'm' else 'separate'
            print(f"✓ Recorded: {'MERGE' if decision == 'm' else 'KEEP SEPARATE'}")
            break
        else:
            print("Please enter 'm' for merge or 's' for separate")

# Save decisions
with open('merge_decisions_final.json', 'w') as f:
    json.dump(decisions, f, indent=2)

print(f"\n{'='*80}")
print("ALL DONE!")
print(f"Saved to: merge_decisions_final.json")
print("\nSummary:")
merge_count = sum(1 for d in decisions.values() if d == 'merge')
print(f"  Merge: {merge_count}")
print(f"  Keep Separate: {14 - merge_count}")