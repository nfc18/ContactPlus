import sys
from collections import defaultdict

def get_email_distribution(filename):
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    email_count = 0
    distribution = defaultdict(int)
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('BEGIN:VCARD'):
            email_count = 0
        
        elif 'EMAIL' in line and ':' in line:
            email_count += 1
        
        elif line.startswith('END:VCARD'):
            distribution[email_count] += 1
    
    print("\nEmail Count Distribution:")
    print("=" * 40)
    print("Email Count | Number of Contacts")
    print("-" * 40)
    
    total_contacts = sum(distribution.values())
    for count in sorted(distribution.keys()):
        num_contacts = distribution[count]
        percentage = (num_contacts / total_contacts) * 100
        print(f"{count:11d} | {num_contacts:6d} ({percentage:5.2f}%)")
    
    print("-" * 40)
    print(f"Total:      | {total_contacts:6d}")
    
    # Calculate averages
    total_emails = sum(count * num for count, num in distribution.items())
    avg_emails = total_emails / total_contacts if total_contacts > 0 else 0
    
    print(f"\nAverage emails per contact: {avg_emails:.2f}")
    
    # Find highest email count
    max_emails = max(distribution.keys()) if distribution else 0
    print(f"Maximum emails for a single contact: {max_emails}")

if __name__ == "__main__":
    get_email_distribution(sys.argv[1])
