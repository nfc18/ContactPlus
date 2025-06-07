# Data Enhancement Strategies

## Overview
This document outlines strategies for enriching contact data using LinkedIn exports, email analysis, and other data sources to create more complete and valuable contact records.

## LinkedIn Data Enhancement

### Data Mapping
LinkedIn provides rich professional information that can enhance existing contacts:

```python
LINKEDIN_FIELD_MAPPING = {
    'Position': 'job_title',
    'Company': 'organization',
    'URL': 'linkedin_url',
    'Connected On': 'linkedin_connection_date',
    # Extended fields from profile export
    'Industry': 'industry',
    'Location': 'work_location',
    'Summary': 'professional_summary'
}
```

### Matching Strategy
```python
def match_linkedin_contact(linkedin_record, existing_contacts):
    """Match LinkedIn connection with existing contacts"""
    
    candidates = []
    
    # Stage 1: Email matching (highest confidence)
    if linkedin_record.email:
        email_matches = find_contacts_by_email(
            existing_contacts, 
            linkedin_record.email
        )
        for match in email_matches:
            candidates.append((match, 1.0, 'email'))
    
    # Stage 2: Name + Company matching
    name_matches = find_contacts_by_name(
        existing_contacts,
        linkedin_record.first_name,
        linkedin_record.last_name
    )
    
    for match in name_matches:
        if match.organization:
            company_sim = fuzzy_match_company(
                match.organization,
                linkedin_record.company
            )
            if company_sim > 0.8:
                candidates.append((match, 0.9 * company_sim, 'name_company'))
    
    # Stage 3: Name-only matching (lower confidence)
    if not candidates:
        for match in name_matches:
            name_score = calculate_name_similarity(
                match,
                linkedin_record.first_name,
                linkedin_record.last_name
            )
            if name_score > 0.85:
                candidates.append((match, name_score * 0.7, 'name_only'))
    
    # Return best match
    if candidates:
        return max(candidates, key=lambda x: x[1])
    return None, 0, None
```

### Enhancement Rules
```python
def enhance_with_linkedin(contact, linkedin_data):
    """Enhance contact with LinkedIn data"""
    
    enhancements = {}
    
    # Always add LinkedIn URL if not present
    if not contact.linkedin_url and linkedin_data.url:
        enhancements['linkedin_url'] = linkedin_data.url
    
    # Update professional information
    if linkedin_data.position:
        if not contact.job_title:
            enhancements['job_title'] = linkedin_data.position
        elif linkedin_data.connected_on > contact.job_title_updated:
            # LinkedIn data is newer
            enhancements['job_title'] = linkedin_data.position
            enhancements['previous_job_title'] = contact.job_title
    
    # Company information
    if linkedin_data.company:
        if not contact.organization:
            enhancements['organization'] = linkedin_data.company
        elif linkedin_data.company != contact.organization:
            # Job change detected
            enhancements['organization'] = linkedin_data.company
            enhancements['previous_organization'] = contact.organization
            enhancements['job_change_detected'] = datetime.now()
    
    # Add professional email if different from personal
    if linkedin_data.email and linkedin_data.email not in contact.emails:
        if is_professional_email(linkedin_data.email):
            enhancements['professional_email'] = linkedin_data.email
    
    return enhancements
```

## Email Analysis Enhancement

### Interaction Analysis
```python
class EmailInteractionAnalyzer:
    def __init__(self, mailbox_path):
        self.sent_folder = mailbox_path + '/Sent'
        self.inbox_folder = mailbox_path + '/INBOX'
        
    def analyze_contact_interactions(self, contact):
        """Analyze email interactions with a contact"""
        
        stats = {
            'total_sent': 0,
            'total_received': 0,
            'first_interaction': None,
            'last_interaction': None,
            'average_response_time': None,
            'interaction_frequency': 'none',
            'email_addresses_found': set(),
            'extracted_data': {}
        }
        
        # Search sent emails
        sent_emails = self.search_emails(
            self.sent_folder,
            contact.emails
        )
        
        # Search received emails
        received_emails = self.search_emails(
            self.inbox_folder,
            contact.emails,
            search_from=True
        )
        
        # Calculate statistics
        all_emails = sent_emails + received_emails
        if all_emails:
            stats['total_sent'] = len(sent_emails)
            stats['total_received'] = len(received_emails)
            stats['first_interaction'] = min(e.date for e in all_emails)
            stats['last_interaction'] = max(e.date for e in all_emails)
            
            # Calculate frequency
            days_span = (stats['last_interaction'] - stats['first_interaction']).days
            if days_span > 0:
                emails_per_month = len(all_emails) / (days_span / 30)
                stats['interaction_frequency'] = self.categorize_frequency(emails_per_month)
            
            # Extract signature data
            for email in received_emails[-5:]:  # Last 5 emails
                extracted = self.extract_signature_data(email)
                stats['extracted_data'].update(extracted)
        
        return stats
    
    def categorize_frequency(self, emails_per_month):
        if emails_per_month >= 10:
            return 'very_frequent'
        elif emails_per_month >= 4:
            return 'frequent'
        elif emails_per_month >= 1:
            return 'regular'
        elif emails_per_month >= 0.25:
            return 'occasional'
        else:
            return 'rare'
```

### Signature Extraction
```python
def extract_signature_data(email_body):
    """Extract contact information from email signatures"""
    
    extracted_data = {}
    
    # Find signature block (usually after -- or multiple newlines)
    signature = extract_signature_block(email_body)
    if not signature:
        return extracted_data
    
    # Phone number extraction
    phone_patterns = [
        r'(?:Phone|Ph|Tel|Cell|Mobile)[:\s]*([+\d\s\-\(\)]+)',
        r'(?:T|M):\s*([+\d\s\-\(\)]+)',
        r'\b(\+?\d{1,3}[\s\-\.]?\(?\d{1,4}\)?[\s\-\.]?\d{1,4}[\s\-\.]?\d{1,4})\b'
    ]
    
    for pattern in phone_patterns:
        matches = re.findall(pattern, signature, re.IGNORECASE)
        for match in matches:
            cleaned_phone = clean_phone_number(match)
            if validate_phone_number(cleaned_phone):
                extracted_data.setdefault('phones', []).append(cleaned_phone)
    
    # Job title extraction
    title_patterns = [
        r'^([^|]+)\s*\|\s*([^|]+)',  # Name | Title | Company
        r'^\s*([A-Za-z\s]+)\n\s*([A-Za-z\s,&]+)',  # Name \n Title
    ]
    
    lines = signature.split('\n')
    for i, line in enumerate(lines):
        for pattern in title_patterns:
            match = re.match(pattern, line)
            if match and i < 5:  # Title usually in first few lines
                potential_title = match.group(2).strip()
                if is_valid_job_title(potential_title):
                    extracted_data['job_title'] = potential_title
    
    # Company extraction
    company_indicators = ['Inc', 'LLC', 'Ltd', 'Corp', 'GmbH', 'AG']
    for line in lines:
        for indicator in company_indicators:
            if indicator in line:
                extracted_data['company'] = clean_company_name(line)
                break
    
    # Social media links
    social_patterns = {
        'linkedin': r'linkedin\.com/in/([a-zA-Z0-9\-]+)',
        'twitter': r'twitter\.com/([a-zA-Z0-9_]+)',
        'github': r'github\.com/([a-zA-Z0-9\-]+)'
    }
    
    for platform, pattern in social_patterns.items():
        match = re.search(pattern, signature, re.IGNORECASE)
        if match:
            extracted_data[f'{platform}_url'] = match.group(0)
    
    return extracted_data
```

### Email Pattern Analysis
```python
def analyze_email_patterns(contact, email_stats):
    """Derive insights from email patterns"""
    
    insights = {
        'relationship_type': 'unknown',
        'communication_style': {},
        'topics': [],
        'time_patterns': {}
    }
    
    # Relationship type based on email domains
    if email_stats['total_sent'] + email_stats['total_received'] > 10:
        work_emails = sum(1 for e in contact.emails if is_work_email(e))
        personal_emails = len(contact.emails) - work_emails
        
        if work_emails > personal_emails:
            insights['relationship_type'] = 'professional'
        else:
            insights['relationship_type'] = 'personal'
    
    # Communication patterns
    if email_stats['total_sent'] > email_stats['total_received'] * 2:
        insights['communication_style']['initiator'] = True
    elif email_stats['total_received'] > email_stats['total_sent'] * 2:
        insights['communication_style']['responder'] = True
    else:
        insights['communication_style']['balanced'] = True
    
    # Time patterns (when emails are typically exchanged)
    if email_stats.get('email_times'):
        hour_distribution = analyze_hour_distribution(email_stats['email_times'])
        insights['time_patterns'] = {
            'peak_hours': hour_distribution['peak'],
            'timezone_estimate': estimate_timezone(hour_distribution)
        }
    
    return insights
```

## External API Enhancement (Optional)

### Clearbit Integration
```python
class ClearbitEnhancer:
    def __init__(self, api_key):
        self.client = clearbit.Client(api_key)
    
    def enhance_contact(self, contact):
        """Enhance contact using Clearbit API"""
        
        enhancements = {}
        
        # Try person lookup first
        if contact.email:
            try:
                person = self.client.Person.find(email=contact.email)
                if person:
                    enhancements.update({
                        'full_name': person.get('name', {}).get('fullName'),
                        'job_title': person.get('employment', {}).get('title'),
                        'company': person.get('employment', {}).get('name'),
                        'location': person.get('location'),
                        'bio': person.get('bio'),
                        'avatar_url': person.get('avatar'),
                        'social_profiles': person.get('socialProfiles', {})
                    })
            except clearbit.NotFoundError:
                pass
        
        # Try company lookup
        if contact.organization:
            try:
                company = self.client.Company.find(name=contact.organization)
                if company:
                    enhancements.update({
                        'company_domain': company.get('domain'),
                        'company_description': company.get('description'),
                        'company_industry': company.get('industry'),
                        'company_size': company.get('metrics', {}).get('employees')
                    })
            except clearbit.NotFoundError:
                pass
        
        return enhancements
```

### Social Media Enhancement
```python
def enhance_from_social_media(contact):
    """Extract publicly available social media information"""
    
    enhancements = {}
    
    # LinkedIn public profile
    if contact.linkedin_url:
        public_data = scrape_linkedin_public(contact.linkedin_url)
        if public_data:
            enhancements.update({
                'headline': public_data.get('headline'),
                'skills': public_data.get('skills', []),
                'education': public_data.get('education', [])
            })
    
    # Twitter bio
    if contact.twitter_handle:
        twitter_data = get_twitter_bio(contact.twitter_handle)
        if twitter_data:
            enhancements.update({
                'twitter_bio': twitter_data.get('description'),
                'twitter_followers': twitter_data.get('followers_count'),
                'twitter_verified': twitter_data.get('verified')
            })
    
    return enhancements
```

## Enhancement Priority and Conflict Resolution

### Data Source Priority
```python
DATA_SOURCE_PRIORITY = {
    'email_signature': 0.9,      # Most recent, directly from person
    'linkedin_export': 0.85,     # Professional, relatively recent
    'clearbit_api': 0.7,         # Third-party, may be outdated
    'social_media_scrape': 0.6,  # Public data, possibly incomplete
    'email_analysis': 0.5        # Inferred data
}

def resolve_enhancement_conflicts(existing_value, enhancements):
    """Resolve conflicts when multiple sources provide different values"""
    
    if not enhancements:
        return existing_value
    
    # If no existing value, take highest priority enhancement
    if not existing_value:
        return max(enhancements, key=lambda x: x['priority'])['value']
    
    # Check if any enhancement is significantly newer
    for enhancement in enhancements:
        if enhancement['timestamp'] > existing_value['timestamp'] + timedelta(days=180):
            if enhancement['priority'] >= 0.7:
                return enhancement['value']
    
    # Otherwise, trust existing value unless high-priority source disagrees
    max_priority_enhancement = max(enhancements, key=lambda x: x['priority'])
    if max_priority_enhancement['priority'] > existing_value.get('priority', 0.5):
        return max_priority_enhancement['value']
    
    return existing_value
```

## Privacy and Compliance

### Data Enhancement Rules
1. **Consent**: Only enhance data for contacts where relationship exists
2. **Source Tracking**: Always track where enhanced data came from
3. **Opt-out**: Respect contacts who don't want data enhancement
4. **Local Processing**: Prefer local analysis over API calls
5. **Data Minimization**: Only enhance relevant professional data

### Implementation
```python
def is_enhancement_allowed(contact):
    """Check if contact allows data enhancement"""
    
    # Check opt-out flag
    if contact.enhancement_opted_out:
        return False
    
    # Check relationship exists
    if not (contact.emails or contact.phone_numbers):
        return False
    
    # Check interaction history
    if contact.interaction_count == 0:
        return False
    
    # Check data age
    if contact.last_updated < datetime.now() - timedelta(days=730):
        return False
    
    return True
```