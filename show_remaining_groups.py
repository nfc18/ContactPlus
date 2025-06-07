#!/usr/bin/env python3
"""
Just show the remaining groups for review
"""

import re

# Read the original HTML
with open('data/MASTER_CONTACTS_20250606_141220_review.html', 'r') as f:
    html = f.read()

# Your existing decisions
decided = ["0", "1", "2", "3"]

print("REMAINING 10 GROUPS TO REVIEW")
print("=" * 80)
print("You've already decided: 0=separate, 1=separate, 2=merge, 3=separate")
print("\nHere are the remaining groups:\n")

# Extract all groups
all_groups = re.split(r'<div class="match-group" id="group-\d+">', html)[1:]

group_num = 0
for group_content in all_groups:
    if str(group_num) in decided:
        group_num += 1
        continue
    
    print(f"\n{'='*80}")
    print(f"GROUP {group_num}")
    print("-" * 80)
    
    # Extract key info
    match_type = re.search(r'Match Type:</strong>\s*(\w+)', group_content)
    match_value = re.search(r'Match Value:</strong>\s*(.*?)<', group_content)
    
    if match_type:
        print(f"Match: {match_type.group(1)} = {match_value.group(1) if match_value else 'N/A'}")
    
    # Extract all contacts in this group
    contacts = re.findall(r'Source:\s*(.*?)</div>.*?Name:</span>\s*(.*?)</div>', group_content, re.DOTALL)
    
    for i, (source, name) in enumerate(contacts):
        print(f"\n  Contact {i+1}: {name.strip()} (from {source.strip()})")
        
        # Try to get org and email
        org_match = re.search(f'{name}.*?Organization:</span>\s*(.*?)</div>', group_content, re.DOTALL)
        email_match = re.search(f'{name}.*?Emails:</span>\s*(.*?)</div>', group_content, re.DOTALL)
        
        if org_match and org_match.group(1).strip() != "No organization":
            print(f"            Org: {org_match.group(1).strip()}")
        if email_match:
            print(f"            Email: {email_match.group(1).strip()}")
    
    group_num += 1

print(f"\n{'='*80}")
print("\nTo provide your decisions, just tell me:")
print('Example: "4=merge, 5=separate, 6=merge, 7=separate, 8=merge, 9=separate, 10=merge, 11=separate, 12=merge, 13=separate"')
print("\nOr you can go through them one by one if you prefer.")