# Merge Conflict Resolution Design

## Overview
This document outlines the design for handling merge conflicts when combining duplicate contacts. The system provides both automated and manual resolution options with different UI approaches.

## Conflict Types and Severity Levels

### 1. Low-Severity Conflicts (Auto-Resolvable)
- **Different phone number formats**: +1-555-1234 vs (555) 1234
- **Case differences**: john.doe@email.com vs JOHN.DOE@EMAIL.COM
- **Missing vs present data**: One contact has a field, other doesn't
- **Obvious quality differences**: Low-res vs high-res photo

### 2. Medium-Severity Conflicts (Rule-Based Resolution)
- **Multiple values**: Contact A has 2 emails, Contact B has 3 emails
- **Date conflicts**: Different birthdays with close dates (typos)
- **Name variations**: Bob Smith vs Robert Smith
- **Company variations**: Google vs Google Inc. vs Google LLC

### 3. High-Severity Conflicts (Manual Review Required)
- **Different people**: Same name but clearly different individuals
- **Conflicting critical data**: Different birthdays (not close)
- **Multiple photos**: Different people in photos
- **Excessive data**: More than 3 email addresses total
- **VIP contacts**: Contacts marked as important/starred

## UI Approach Comparison

### Option 1: Web-Based Interface (Recommended)

#### Advantages:
- **Visual comparison**: Side-by-side contact cards
- **Rich interactions**: Drag-and-drop field selection
- **Photo preview**: Visual comparison of contact photos
- **Batch processing**: Review multiple conflicts efficiently
- **Responsive design**: Works on desktop and mobile
- **Persistent sessions**: Can pause and resume review

#### Design Layout:
```
┌─────────────────────────────────────────────────────────┐
│  Contact Merge Review                    [23 remaining] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐     ┌─────────────────┐          │
│  │   Contact A     │ VS  │   Contact B     │          │
│  │  [Photo A]      │     │  [Photo B]      │          │
│  │                 │     │                 │          │
│  │ John Doe        │     │ John M. Doe     │          │
│  │ Google Inc.     │     │ Google LLC      │          │
│  │ john@gmail.com  │     │ jdoe@google.com │          │
│  │ +1-555-1234     │     │ (555) 123-4567  │          │
│  └─────────────────┘     └─────────────────┘          │
│                                                         │
│  Confidence: 78% match                                  │
│  Issues: Different middle initial, company names       │
│                                                         │
│  ┌─────────────────── Merged Result ──────────────────┐│
│  │ Name: [John M. Doe ▼]                              ││
│  │ Company: [Google LLC ▼]                            ││
│  │ Emails: ✓ john@gmail.com                           ││
│  │         ✓ jdoe@google.com                          ││
│  │ Phones: [+1-555-123-4567 ▼]                       ││
│  └────────────────────────────────────────────────────┘│
│                                                         │
│  [Skip] [Keep Both] [Auto-Resolve All] [Merge →]      │
└─────────────────────────────────────────────────────────┘
```

### Option 2: Terminal-Based Interface

#### Advantages:
- **Scriptable**: Can be automated or run in CI/CD
- **Lightweight**: No web server required
- **SSH-friendly**: Can be used remotely
- **Keyboard-driven**: Fast for power users

#### Design Example:
```
Contact Merge Conflict (23 remaining)
=====================================

CONTACT A:                    CONTACT B:
Name: John Doe               Name: John M. Doe
Company: Google Inc.         Company: Google LLC  
Email: john@gmail.com        Email: jdoe@google.com
Phone: +1-555-1234          Phone: (555) 123-4567
Photo: [YES]                Photo: [YES - Different]

Confidence: 78% match
Issues: Different middle initial, company names, photos

Choose fields for merged contact:
1. Name:    [A] John Doe  [B] John M. Doe  [C] Custom
2. Company: [A] Google Inc.  [B] Google LLC  [C] Custom
3. Email:   [A] john@gmail.com  [B] jdoe@google.com  [K] Keep both
4. Phone:   [A] +1-555-1234  [B] (555) 123-4567  [C] Custom
5. Photo:   [A] Use A  [B] Use B  [V] View both

Actions: [M]erge  [S]kip  [K]eep both  [D]etails  [Q]uit
> 
```

### Option 3: Hybrid Approach (Best of Both Worlds)

#### Implementation:
1. **Default to automation**: Resolve easy conflicts automatically
2. **Web UI for complex cases**: Visual review when needed
3. **CLI for power users**: Terminal interface with same capabilities
4. **API for integration**: RESTful API for custom interfaces

## Conflict Resolution Workflow

### 1. Pre-Processing Phase
```python
def categorize_conflicts(contact_pairs):
    """Categorize conflicts by severity"""
    auto_resolve = []
    rule_based = []
    manual_review = []
    
    for pair in contact_pairs:
        severity = calculate_conflict_severity(pair)
        if severity < 0.3:
            auto_resolve.append(pair)
        elif severity < 0.7:
            rule_based.append(pair)
        else:
            manual_review.append(pair)
    
    return auto_resolve, rule_based, manual_review
```

### 2. Resolution Strategies

#### Auto-Resolution Rules:
1. **Data Quality**: Always prefer complete over incomplete
2. **Recency**: Prefer recently updated information
3. **Source Trust**: LinkedIn > Phone > Manual entry
4. **Format Standards**: Prefer E.164 phone, proper case names

#### Manual Review Features:
1. **Field-level selection**: Choose value for each field
2. **Custom values**: Edit any field during merge
3. **Keep both**: Option to not merge
4. **Add notes**: Document why decision was made
5. **Bulk actions**: Apply same rule to similar conflicts

### 3. Conflict Queue Management

```python
class ConflictQueue:
    def __init__(self):
        self.queue = PriorityQueue()
        self.session_state = {}
    
    def add_conflicts(self, conflicts):
        """Add conflicts with priority scoring"""
        for conflict in conflicts:
            priority = self.calculate_priority(conflict)
            self.queue.put((priority, conflict))
    
    def calculate_priority(self, conflict):
        """Higher score = review first"""
        score = 0
        score += conflict.severity * 100
        score += conflict.vip_status * 50
        score += conflict.data_richness * 20
        return score
    
    def save_progress(self):
        """Save review session for resume"""
        with open('merge_session.json', 'w') as f:
            json.dump(self.session_state, f)
```

## User Experience Design

### 1. Guided Review Process
- **Progress indicator**: "23 of 150 conflicts remaining"
- **Time estimate**: "Approximately 10 minutes remaining"
- **Smart ordering**: Similar conflicts grouped together
- **Learning system**: Apply previous decisions to similar cases

### 2. Conflict Context
- **Relationship info**: Show email/call frequency
- **Data sources**: Where each piece of data came from
- **Timeline**: When data was added/modified
- **Duplicates**: Show if part of larger duplicate cluster

### 3. Efficiency Features
- **Keyboard shortcuts**: 
  - `Space`: Accept suggestion
  - `K`: Keep both
  - `S`: Skip
  - `1-9`: Select field option
- **Bulk actions**: "Apply to all similar conflicts"
- **Smart defaults**: Pre-select likely correct options
- **Undo/Redo**: Reverse recent decisions

## Implementation Architecture

### 1. Backend API
```python
@app.route('/api/conflicts/next', methods=['GET'])
def get_next_conflict():
    """Get next conflict for review"""
    conflict = conflict_queue.get_next()
    return {
        'conflict_id': conflict.id,
        'contacts': [conflict.contact_a, conflict.contact_b],
        'suggestions': merge_engine.suggest_resolution(conflict),
        'metadata': {
            'confidence': conflict.confidence,
            'severity': conflict.severity,
            'similar_pending': conflict.similar_count
        }
    }

@app.route('/api/conflicts/<id>/resolve', methods=['POST'])
def resolve_conflict(id):
    """Submit resolution for a conflict"""
    resolution = request.json
    result = merge_engine.apply_resolution(id, resolution)
    
    # Learn from decision
    ml_engine.train_on_decision(id, resolution)
    
    return {'success': True, 'next_conflict_id': result.next_id}
```

### 2. Frontend Components
```javascript
// React component for conflict review
const ConflictReviewer = () => {
    const [conflict, setConflict] = useState(null);
    const [resolution, setResolution] = useState({});
    
    const handleFieldSelection = (field, value) => {
        setResolution({...resolution, [field]: value});
    };
    
    const submitResolution = async () => {
        await api.resolveConflict(conflict.id, resolution);
        loadNextConflict();
    };
    
    return (
        <ConflictCard 
            conflict={conflict}
            onFieldSelect={handleFieldSelection}
            onSubmit={submitResolution}
        />
    );
};
```

## Machine Learning Enhancement

### 1. Learning from User Decisions
```python
class MergeMLEngine:
    def __init__(self):
        self.model = self.load_or_create_model()
    
    def extract_features(self, contact_pair):
        """Extract features for ML model"""
        return {
            'name_similarity': fuzz.ratio(
                contact_pair.a.name, 
                contact_pair.b.name
            ),
            'company_match': contact_pair.a.company == contact_pair.b.company,
            'email_domain_match': self.compare_email_domains(contact_pair),
            'phone_area_match': self.compare_phone_areas(contact_pair),
            'data_completeness_diff': self.completeness_score(contact_pair)
        }
    
    def predict_resolution(self, contact_pair):
        """Predict how user would resolve this conflict"""
        features = self.extract_features(contact_pair)
        prediction = self.model.predict(features)
        return prediction
```

### 2. Improving Over Time
- Track user decisions
- Identify patterns in resolutions
- Reduce manual review needs
- Suggest bulk actions for similar conflicts

## Integration with Main Workflow

### 1. Checkpoint System
```python
class MergeCheckpoint:
    def __init__(self):
        self.auto_resolved = []
        self.manually_resolved = []
        self.skipped = []
        self.kept_both = []
    
    def save(self):
        """Save checkpoint for rollback"""
        checkpoint = {
            'timestamp': datetime.now(),
            'stats': self.get_stats(),
            'decisions': self.get_all_decisions()
        }
        save_to_history(checkpoint)
```

### 2. Rollback Capability
- Each merge decision is logged
- Can undo individual merges
- Can rollback entire sessions
- Maintains original contact data

## Recommended Implementation

### Phase 1: CLI with Smart Defaults
- Build terminal interface first
- Implement auto-resolution rules
- Create simple review interface
- Test with small batches

### Phase 2: Web UI
- Build React-based interface
- Add visual comparison features
- Implement drag-and-drop
- Add photo comparison

### Phase 3: ML Enhancement
- Collect user decision data
- Train prediction model
- Reduce manual review needs
- Add confidence scoring

### Phase 4: Advanced Features
- Bulk operations
- Custom rules engine
- API for integrations
- Mobile app support

## Conclusion

The hybrid approach provides the best user experience:
1. **Automate simple conflicts** to reduce user burden
2. **Web UI for complex cases** with visual aids
3. **CLI for automation** and power users
4. **ML to improve over time** and reduce manual work

This design ensures that users can efficiently review conflicts while maintaining control over important decisions, with the system learning and improving from their choices.