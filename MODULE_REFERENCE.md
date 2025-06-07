# 📚 Module Reference Guide

## 🧠 **AI Intelligence Modules** (Ready to Use)

### **`contact_intelligence.py`**
**Status**: ✅ Complete and tested  
**Purpose**: Core AI analysis engine that recognizes patterns humans see instantly

**Key Classes:**
- `ContactIntelligenceEngine`: Main AI analysis engine
- `IntelligenceInsight`: Individual issue detection with confidence scoring
- `ContactAnalysis`: Complete analysis results

**Key Functions:**
```python
analyze_contact_with_ai(vcard) -> ContactAnalysis
get_high_confidence_fixes(analysis) -> List[IntelligenceInsight]  
get_user_review_items(analysis) -> List[IntelligenceInsight]
```

**What it detects:**
- Email-derived usernames: `claudiaplatzer85` → `Claudia Platzer` (95% confidence)
- Case issues: `JOHN SMITH` → `John Smith`
- Numbers in names: `user123` → `user`
- Username patterns: Recognizes non-human name patterns
- Duplicate emails: Case-insensitive deduplication

**Example Usage:**
```python
from contact_intelligence import analyze_contact_with_ai
analysis = analyze_contact_with_ai(vcard)
print(f"Quality: {analysis.overall_quality_score:.1%}")
for insight in analysis.insights:
    print(f"{insight.current_value} → {insight.suggested_value}")
```

### **`ai_database_analyzer.py`**
**Status**: ✅ Complete and tested  
**Purpose**: Analyzes original source databases to show quality issues before merging

**Key Functions:**
```python
analyze_all_source_databases() -> Dict[str, Any]
show_claudia_platzer_equivalents() -> None
```

**Proven Results:**
- Sara: 3,075 contacts, 207 issues (185 email-derived names)
- iPhone Contacts: 2,931 contacts, 194 issues
- iPhone Suggested: 1,036 contacts, 175 issues
- **Total: 576 quality issues across 7,042 contacts (8.2% issue rate)**

**Usage:**
```bash
python ai_database_analyzer.py
```

### **`demo_intelligent_processing.py`**
**Status**: ✅ Complete and tested  
**Purpose**: Demonstrates AI capabilities on problematic contacts

**Features:**
- Shows Claudia Platzer case analysis
- Compares AI vs rule-based processing
- Demonstrates multiple issue detection

## 🔧 **Pipeline Modules** (Templates Ready)

### **`ai_first_pipeline.py`**
**Status**: ✅ Framework complete, needs module extraction  
**Purpose**: Complete AI-first processing pipeline

**Key Classes:**
- `AIFirstPipeline`: Main orchestration class
- Methods for individual database processing
- AI improvement application logic

**To Extract:**
- Individual database cleaner logic → `ai_database_cleaner.py`
- Core processing patterns already implemented

### **`intelligent_workflow.py`**
**Status**: ✅ Complete integration framework  
**Purpose**: Integrates AI intelligence with existing workflow

**Key Classes:**
- `IntelligentContactWorkflow`: AI-enhanced processing
- Integration with standard validation
- Automatic high-confidence fix application

## 🚧 **Modules to Build Next Session**

### **`ai_database_cleaner.py`** (30 minutes)
**Purpose**: Apply AI fixes to individual source databases  
**Template**: Extract from `ai_first_pipeline.py._apply_ai_improvements()`

**Required Functions:**
```python
class AISourceDatabaseCleaner:
    def clean_database(self, source_name: str, apply_fixes: bool = True)
    def apply_high_confidence_fixes(self, vcards: List, fixes: List)
    def validate_cleaned_database(self, cleaned_file: str)
```

**Implementation Pattern:**
1. Load source database
2. AI analyze each contact
3. Apply high-confidence fixes (confidence >= 0.90)
4. Validate cleaned version
5. Save as `{source}_AI_CLEANED.vcf`

### **`ai_duplicate_detector.py`** (2 hours)
**Purpose**: Intelligent duplicate detection across cleaned databases

**Required Classes:**
```python
class AIDuplicateDetector:
    def find_cross_database_duplicates(self, databases: List[str])
    def contextual_matching(self, contact1: vCard, contact2: vCard) -> float
    def generate_merge_suggestions(self, duplicates: List)
```

**Matching Strategies:**
- Email domain correlation
- Phone number normalization and matching
- Fuzzy name matching with cultural awareness
- Geographic proximity (same addresses)
- Social network analysis (shared contacts)

**Output**: Merge suggestions with confidence scores

### **`ai_intelligent_merger.py`** (1 hour)
**Purpose**: Merge AI-cleaned databases with intelligent conflict resolution

**Required Classes:**
```python
class AIIntelligentMerger:
    def merge_databases(self, cleaned_databases: List[str])
    def resolve_field_conflicts(self, contact_group: List[vCard])
    def choose_best_data(self, field_options: List, context: Dict)
```

**Conflict Resolution Logic:**
- Most recent data preference
- Most complete data preference  
- Source credibility scoring
- AI quality assessment for each field

## 📋 **Existing Modules (Don't Modify)**

### **Core Validation Stack**
- `vcard_validator.py`: RFC compliance validation
- `vcard_fixer.py`: Fix missing required fields
- `vcard_soft_compliance.py`: Data quality improvements
- `vcard_workflow.py`: Standard processing pipeline

### **Web Interface**
- `app.py`: Flask web application for manual review
- `analyzer.py`: Contact analysis for review queue
- `templates/`: HTML templates for web interface

### **Phonebook Operations**
- `phonebook_operations.py`: Core phonebook management
- **CRITICAL**: All phonebook modifications MUST follow the 6-step protocol in `PHONEBOOK_EDITING_PROTOCOL.md`

## 🔗 **Module Dependencies**

### **Import Structure:**
```python
# Core AI
from contact_intelligence import ContactIntelligenceEngine, analyze_contact_with_ai

# Processing
import vobject  # For vCard manipulation
from vcard_validator import VCardStandardsValidator  # For validation

# Standard library
import os, json, logging
from datetime import datetime
from typing import Dict, List, Any
```

### **File Paths:**
```python
SOURCE_DATABASES = {
    'sara': 'Imports/Sara_Export_Sara A. Kerner and 3.074 others.vcf',
    'iphone_contacts': 'Imports/iPhone_Contacts_Contacts.vcf', 
    'iphone_suggested': 'Imports/iPhone_Suggested_Suggested Contacts.vcf'
}

OUTPUT_PATTERN = "{source}_AI_CLEANED.vcf"
FINAL_OUTPUT = "data/MASTER_PHONEBOOK_AI_FIRST_{timestamp}.vcf"
```

## 🧪 **Testing Patterns**

### **Quick AI Test:**
```python
# Test AI engine
python contact_intelligence.py

# Test source analysis  
python ai_database_analyzer.py

# Test demonstration
python demo_intelligent_processing.py
```

### **Validation Pattern:**
```python
# Always validate after AI changes
from vcard_validator import VCardStandardsValidator
validator = VCardStandardsValidator()
is_valid, errors, warnings = validator.validate_file(cleaned_file)
```

## 📊 **Expected Performance**

### **Processing Times:**
- AI analysis: ~1,000 contacts/minute
- High-confidence fixes: ~2,000 contacts/minute
- Validation: ~5,000 contacts/minute

### **Quality Improvements:**
- Current merged database: 89.8% quality score
- Expected after AI-first: 96-98% quality score
- Issue reduction: 8.2% → <2% issue rate

### **Confidence Scoring:**
- 95%+ confidence: Auto-apply safe
- 85-94% confidence: Present as default choice
- 70-84% confidence: Needs user review
- <70% confidence: Flag for manual review

This reference guide provides everything needed to implement the AI-first approach in the next session.