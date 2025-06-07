#!/usr/bin/env python3
"""
Add the missing Brian Fitzgerald contact to master phonebook (cleaned)
"""

import vobject
from datetime import datetime

# Create a clean Brian Fitzgerald contact
brian = vobject.vCard()
brian.add('version')
brian.version.value = '3.0'

brian.add('fn')
brian.fn.value = 'Brian Fitzgerald'

brian.add('n')
brian.n.value = vobject.vcard.Name(family='Fitzgerald', given='Brian')

# Add phone
brian.add('tel')
brian.tel.value = '+12035580815'
brian.tel.type_param = 'CELL'

# Add only Brian's emails (not Karen's)
brian.add('email')
brian.email.value = 'brian.fitzgerald@cognex.com'
brian.email.type_param = 'WORK'

brian.add('email') 
brian.email.value = 'brian@anyline.com'
brian.email.type_param = 'WORK'

# Add note about recovery
brian.add('note')
brian.note.value = f'Recovered missing contact on {datetime.now().strftime("%Y-%m-%d")} - US phone number was missing from master'

# Load master phonebook
master_path = "data/FINAL_MASTER_CONTACTS_20250606_143247.vcf"
with open(master_path, 'r', encoding='utf-8') as f:
    contacts = list(vobject.readComponents(f.read()))

print(f"Current master phonebook: {len(contacts)} contacts")

# Add Brian
contacts.append(brian)

# Save updated master
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
updated_path = f"data/MASTER_PHONEBOOK_{timestamp}.vcf"

with open(updated_path, 'w', encoding='utf-8') as f:
    for contact in contacts:
        f.write(contact.serialize())

print(f"\nAdded Brian Fitzgerald to phonebook")
print(f"New master phonebook: {len(contacts)} contacts")
print(f"Saved as: {updated_path}")

# Also create a summary
summary = {
    'update_date': datetime.now().isoformat(),
    'action': 'Added missing contact',
    'contact_added': {
        'name': 'Brian Fitzgerald',
        'phone': '+12035580815',
        'emails': ['brian.fitzgerald@cognex.com', 'brian@anyline.com'],
        'reason': 'US phone number was missing from master, contact was marked as keep in review'
    },
    'previous_count': len(contacts) - 1,
    'new_count': len(contacts),
    'new_master_file': updated_path
}

import json
with open(f'data/phonebook_update_{timestamp}.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("\n✅ Master phonebook updated successfully!")