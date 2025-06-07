import sys

def process_vcf(filename):
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    in_vcard = False
    email_count = 0
    contact_name = ""
    emails = []
    
    results = []
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('BEGIN:VCARD'):
            in_vcard = True
            email_count = 0
            contact_name = ""
            emails = []
        
        elif line.startswith('FN:'):
            contact_name = line[3:]
        
        elif 'EMAIL' in line and ':' in line:
            email_count += 1
            email = line.split(':', 1)[1] if ':' in line else ""
            emails.append(email)
        
        elif line.startswith('END:VCARD'):
            if email_count > 3:
                if not contact_name:
                    contact_name = "Unknown"
                results.append((email_count, contact_name, emails))
            in_vcard = False
    
    # Sort by email count descending
    results.sort(key=lambda x: x[0], reverse=True)
    
    # Print results
    print(f"\nContacts with more than 3 email addresses:")
    print("=" * 80)
    for count, name, email_list in results[:20]:
        print(f"{count} emails: {name}")
        for email in email_list[:5]:  # Show first 5 emails
            print(f"    - {email}")
        if len(email_list) > 5:
            print(f"    ... and {len(email_list) - 5} more")
        print()
    
    # Statistics
    more_than_3 = len([r for r in results if r[0] > 3])
    more_than_4 = len([r for r in results if r[0] > 4])
    
    print(f"\nStatistics:")
    print(f"Contacts with more than 3 emails: {more_than_3}")
    print(f"Contacts with more than 4 emails: {more_than_4}")

if __name__ == "__main__":
    process_vcf(sys.argv[1])
