# Contact Rating System Design

## Overview
The contact rating system evaluates each contact based on multiple factors to determine their importance and relevance. This helps prioritize which contacts to keep, export, and maintain.

## Rating Scale
- **0-100 points**: Comprehensive scoring system
- **Export Thresholds**:
  - Premium (80-100): Inner circle, frequent contacts
  - Standard (60-79): Regular professional/personal contacts
  - Archive (40-59): Occasional contacts worth keeping
  - Review (0-39): Candidates for removal or update

## Rating Components

### 1. Interaction Frequency (30 points max)
```python
def calculate_interaction_score(contact, email_stats):
    """Score based on email interaction frequency and recency"""
    
    score = 0
    
    # Email volume scoring (15 points)
    total_emails = email_stats['total_sent'] + email_stats['total_received']
    
    if total_emails >= 100:
        volume_score = 15
    elif total_emails >= 50:
        volume_score = 12
    elif total_emails >= 20:
        volume_score = 9
    elif total_emails >= 10:
        volume_score = 6
    elif total_emails >= 5:
        volume_score = 3
    else:
        volume_score = total_emails * 0.6
    
    score += volume_score
    
    # Recency scoring (10 points)
    if email_stats['last_interaction']:
        days_since_contact = (datetime.now() - email_stats['last_interaction']).days
        
        if days_since_contact <= 30:
            recency_score = 10
        elif days_since_contact <= 90:
            recency_score = 8
        elif days_since_contact <= 180:
            recency_score = 6
        elif days_since_contact <= 365:
            recency_score = 4
        elif days_since_contact <= 730:
            recency_score = 2
        else:
            recency_score = 0
            
        score += recency_score
    
    # Two-way communication bonus (5 points)
    if email_stats['total_sent'] > 0 and email_stats['total_received'] > 0:
        ratio = min(email_stats['total_sent'], email_stats['total_received']) / \
                max(email_stats['total_sent'], email_stats['total_received'])
        score += ratio * 5
    
    return min(score, 30)
```

### 2. Data Completeness (20 points max)
```python
def calculate_completeness_score(contact):
    """Score based on how complete the contact information is"""
    
    score = 0
    weights = {
        'name': 3,           # Full name
        'email': 3,          # At least one email
        'phone': 3,          # At least one phone
        'organization': 2,   # Company/Organization
        'title': 2,          # Job title
        'address': 2,        # Physical address
        'photo': 2,          # Has photo
        'linkedin': 1,       # LinkedIn URL
        'birthday': 1,       # Birthday
        'notes': 1,          # Has notes/context
    }
    
    # Check each field
    if contact.first_name and contact.last_name:
        score += weights['name']
    
    if contact.emails and len(contact.emails) > 0:
        score += weights['email']
        # Bonus for multiple emails
        if len(contact.emails) >= 2:
            score += 1
    
    if contact.phones and len(contact.phones) > 0:
        score += weights['phone']
        # Bonus for mobile number
        if any(is_mobile_number(p) for p in contact.phones):
            score += 1
    
    if contact.organization:
        score += weights['organization']
    
    if contact.job_title:
        score += weights['title']
    
    if contact.address and contact.address.city:
        score += weights['address']
    
    if contact.photo:
        score += weights['photo']
    
    if contact.linkedin_url:
        score += weights['linkedin']
    
    if contact.birthday:
        score += weights['birthday']
    
    if contact.notes and len(contact.notes) > 20:
        score += weights['notes']
    
    return min(score, 20)
```

### 3. Relationship Type (25 points max)
```python
def calculate_relationship_score(contact, metadata):
    """Score based on relationship type and importance"""
    
    score = 0
    
    # Determine relationship type
    relationship_type = determine_relationship_type(contact, metadata)
    
    # Base scores by type
    type_scores = {
        'family': 25,
        'close_friend': 23,
        'vip_professional': 22,
        'regular_professional': 15,
        'regular_personal': 15,
        'acquaintance': 8,
        'service_provider': 5,
        'unknown': 2
    }
    
    score = type_scores.get(relationship_type, 2)
    
    # Apply modifiers
    modifiers = calculate_relationship_modifiers(contact, metadata)
    
    # Decision maker bonus
    if modifiers.get('is_decision_maker'):
        score = min(score * 1.2, 25)
    
    # Long-term relationship bonus
    if modifiers.get('years_known', 0) >= 5:
        score = min(score + 2, 25)
    
    # Referral source bonus
    if modifiers.get('is_referral_source'):
        score = min(score + 3, 25)
    
    return score

def determine_relationship_type(contact, metadata):
    """Determine the type of relationship"""
    
    # Check for family indicators
    if is_family_member(contact, metadata):
        return 'family'
    
    # Check VIP list
    if contact.email in metadata.get('vip_emails', []):
        if is_professional_contact(contact):
            return 'vip_professional'
        else:
            return 'close_friend'
    
    # Check interaction patterns
    if metadata.get('interaction_frequency') == 'very_frequent':
        if is_professional_contact(contact):
            return 'regular_professional'
        else:
            return 'regular_personal'
    
    # Check for service providers
    if is_service_provider(contact):
        return 'service_provider'
    
    # Default based on available data
    if contact.organization or contact.job_title:
        return 'acquaintance'
    
    return 'unknown'
```

### 4. Recency (15 points max)
```python
def calculate_recency_score(contact, interactions):
    """Score based on how recently the contact was active"""
    
    score = 0
    
    # Find most recent activity
    activities = []
    
    if interactions.get('last_email_date'):
        activities.append(interactions['last_email_date'])
    
    if contact.last_modified:
        activities.append(contact.last_modified)
    
    if contact.linkedin_connection_date:
        activities.append(contact.linkedin_connection_date)
    
    if contact.created_date:
        activities.append(contact.created_date)
    
    if not activities:
        return 0
    
    most_recent = max(activities)
    days_ago = (datetime.now() - most_recent).days
    
    # Scoring based on recency
    if days_ago <= 7:
        score = 15
    elif days_ago <= 30:
        score = 13
    elif days_ago <= 90:
        score = 10
    elif days_ago <= 180:
        score = 7
    elif days_ago <= 365:
        score = 5
    elif days_ago <= 730:
        score = 3
    elif days_ago <= 1095:
        score = 1
    else:
        score = 0
    
    return score
```

### 5. Data Quality (10 points max)
```python
def calculate_quality_score(contact):
    """Score based on data quality and validity"""
    
    score = 10  # Start with perfect score, deduct for issues
    issues = []
    
    # Check email validity
    for email in contact.emails:
        if not is_valid_email(email):
            score -= 1
            issues.append(f"Invalid email: {email}")
    
    # Check phone validity
    for phone in contact.phones:
        if not is_valid_phone_number(phone):
            score -= 0.5
            issues.append(f"Invalid phone: {phone}")
    
    # Check for data in wrong fields
    if contact.notes:
        # Check for email in notes
        if re.search(r'[\w\.-]+@[\w\.-]+\.\w+', contact.notes):
            score -= 1
            issues.append("Email found in notes field")
        
        # Check for phone in notes
        if re.search(r'\+?\d{10,}', contact.notes):
            score -= 1
            issues.append("Phone found in notes field")
    
    # Check name quality
    if contact.first_name:
        # All caps or all lowercase
        if contact.first_name.isupper() or contact.first_name.islower():
            score -= 0.5
            issues.append("Name formatting issues")
        
        # Contains numbers
        if any(char.isdigit() for char in contact.first_name):
            score -= 1
            issues.append("Name contains numbers")
    
    # Check for placeholder data
    placeholder_names = ['test', 'unknown', 'na', 'n/a', 'xxx']
    if contact.first_name and contact.first_name.lower() in placeholder_names:
        score -= 2
        issues.append("Placeholder name detected")
    
    # Missing critical data
    if not contact.first_name and not contact.last_name and not contact.organization:
        score -= 3
        issues.append("No name or organization")
    
    contact.quality_issues = issues
    return max(score, 0)
```

## Composite Rating Calculation
```python
def calculate_contact_rating(contact, email_stats, metadata):
    """Calculate overall contact rating"""
    
    # Calculate individual component scores
    scores = {
        'interaction': calculate_interaction_score(contact, email_stats),
        'completeness': calculate_completeness_score(contact),
        'relationship': calculate_relationship_score(contact, metadata),
        'recency': calculate_recency_score(contact, email_stats),
        'quality': calculate_quality_score(contact)
    }
    
    # Calculate total
    total_score = sum(scores.values())
    
    # Create rating object
    rating = ContactRating(
        contact_id=contact.id,
        total_score=total_score,
        component_scores=scores,
        calculated_at=datetime.now(),
        category=categorize_score(total_score),
        export_recommended=total_score >= 60,
        quality_issues=contact.quality_issues
    )
    
    return rating

def categorize_score(score):
    """Categorize contact based on score"""
    if score >= 80:
        return 'premium'
    elif score >= 60:
        return 'standard'
    elif score >= 40:
        return 'archive'
    else:
        return 'review'
```

## Special Cases and Overrides

### Manual Overrides
```python
RATING_OVERRIDES = {
    'never_delete': [
        'family',
        'emergency_contact',
        'legal_contact',
        'medical_contact'
    ],
    'always_premium': [
        'spouse',
        'child',
        'parent',
        'sibling',
        'board_member',
        'investor'
    ],
    'boost_rating': {
        'client': 10,
        'referral_source': 15,
        'mentor': 20,
        'key_vendor': 10
    }
}

def apply_rating_overrides(contact, rating):
    """Apply manual overrides to rating"""
    
    # Check never delete
    for tag in contact.tags:
        if tag in RATING_OVERRIDES['never_delete']:
            rating.never_delete = True
            rating.total_score = max(rating.total_score, 60)
    
    # Check always premium
    for tag in contact.tags:
        if tag in RATING_OVERRIDES['always_premium']:
            rating.total_score = max(rating.total_score, 85)
            rating.category = 'premium'
    
    # Apply boosts
    for tag, boost in RATING_OVERRIDES['boost_rating'].items():
        if tag in contact.tags:
            rating.total_score = min(rating.total_score + boost, 100)
    
    return rating
```

### Decay Functions
```python
def apply_time_decay(rating, contact):
    """Apply time-based decay to ratings"""
    
    # No decay for certain categories
    if rating.never_delete or contact.relationship_type == 'family':
        return rating
    
    # Calculate months since last interaction
    if contact.last_interaction:
        months_inactive = (datetime.now() - contact.last_interaction).days / 30
        
        # Apply decay after 6 months
        if months_inactive > 6:
            decay_rate = 0.02  # 2% per month after 6 months
            decay_factor = max(0.5, 1 - (decay_rate * (months_inactive - 6)))
            rating.total_score *= decay_factor
            rating.decay_applied = True
    
    return rating
```

## Rating Analytics

### Distribution Analysis
```python
def analyze_rating_distribution(ratings):
    """Analyze the distribution of contact ratings"""
    
    distribution = {
        'premium': 0,
        'standard': 0,
        'archive': 0,
        'review': 0
    }
    
    quality_issues = defaultdict(int)
    
    for rating in ratings:
        distribution[rating.category] += 1
        
        for issue in rating.quality_issues:
            quality_issues[issue] += 1
    
    # Calculate percentages
    total = len(ratings)
    percentages = {k: (v/total)*100 for k, v in distribution.items()}
    
    # Identify common quality issues
    top_issues = sorted(quality_issues.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        'distribution': distribution,
        'percentages': percentages,
        'total_contacts': total,
        'export_recommended': sum(1 for r in ratings if r.export_recommended),
        'top_quality_issues': top_issues,
        'average_score': sum(r.total_score for r in ratings) / total
    }
```

### Rating History
```python
def track_rating_changes(contact, new_rating):
    """Track how ratings change over time"""
    
    # Get previous rating
    previous_rating = get_latest_rating(contact)
    
    if previous_rating:
        change = RatingChange(
            contact_id=contact.id,
            previous_score=previous_rating.total_score,
            new_score=new_rating.total_score,
            change_amount=new_rating.total_score - previous_rating.total_score,
            change_date=datetime.now(),
            factors=identify_change_factors(previous_rating, new_rating)
        )
        
        # Alert on significant changes
        if abs(change.change_amount) > 20:
            create_rating_alert(contact, change)
        
        return change
    
    return None
```

## Export Recommendations

### Export Strategy
```python
def generate_export_recommendations(ratings):
    """Generate recommendations for which contacts to export"""
    
    recommendations = {
        'immediate_export': [],      # Score >= 80
        'standard_export': [],       # Score 60-79
        'review_needed': [],         # Score 40-59 with quality issues
        'archive_only': [],          # Score 40-59 without issues
        'consider_deletion': []      # Score < 40
    }
    
    for rating in ratings:
        contact = get_contact(rating.contact_id)
        
        if rating.total_score >= 80:
            recommendations['immediate_export'].append({
                'contact': contact,
                'score': rating.total_score,
                'reason': 'High value contact'
            })
        
        elif rating.total_score >= 60:
            recommendations['standard_export'].append({
                'contact': contact,
                'score': rating.total_score,
                'reason': 'Regular contact'
            })
        
        elif rating.total_score >= 40:
            if rating.quality_issues:
                recommendations['review_needed'].append({
                    'contact': contact,
                    'score': rating.total_score,
                    'issues': rating.quality_issues,
                    'reason': 'Quality issues need resolution'
                })
            else:
                recommendations['archive_only'].append({
                    'contact': contact,
                    'score': rating.total_score,
                    'reason': 'Low interaction, but data is clean'
                })
        
        else:
            if not rating.never_delete:
                recommendations['consider_deletion'].append({
                    'contact': contact,
                    'score': rating.total_score,
                    'last_interaction': contact.last_interaction,
                    'reason': 'Very low score and interaction'
                })
    
    return recommendations
```