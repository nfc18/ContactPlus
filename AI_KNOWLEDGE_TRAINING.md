# 🧠 AI Knowledge Training: User Preferences & Edge Cases

## 📋 **Purpose**
Capture user domain knowledge and preferences to enhance AI decision-making and minimize manual intervention during implementation.

## 🎯 **Knowledge Categories to Capture**

### **1. Contact Name Handling Preferences**
*Help AI understand how you want names formatted and corrected*

**Examples to Discuss:**
- Germanic names with special characters (ü, ö, ä)
- Professional titles (Dr., Ing., Prof.)
- Multiple family names (compound surnames)
- Nicknames vs formal names
- Business contacts vs personal contacts

**Questions for You:**
- How do you prefer compound names? "Smith-Jones" or "Smith Jones"?
- Should professional titles be kept or moved to a separate field?
- For nicknames like "Mike" with email "michael@...", prefer Mike or Michael?

### **2. Email Address Conflict Resolution**
*When contacts have multiple emails, how to prioritize*

**Examples to Discuss:**
- Personal Gmail vs work corporate email
- Old vs new email addresses
- Primary vs secondary email designation
- Email validation (keep invalid emails or remove?)

**Questions for You:**
- Which email domains do you consider most reliable?
- How to handle outdated company emails for people who changed jobs?
- Should the AI prioritize @gmail.com over corporate emails for personal contacts?

### **3. Phone Number Preferences**
*How to handle multiple phones and formatting*

**Examples to Discuss:**
- Mobile vs landline preference
- International vs local number formatting
- Austrian vs German vs other country codes
- WhatsApp numbers vs regular phone numbers

**Questions for You:**
- Prefer mobile or landline as primary?
- How do you want international numbers formatted?
- Should country codes always be included?

### **4. Duplicate Contact Merge Strategy**
*When AI finds potential duplicates, how to merge them*

**Examples to Discuss:**
- Contact with more complete info vs more recent info
- iPhone vs Sara's export vs other source priority
- Photo selection criteria
- Note field combination approach

**Questions for You:**
- Which source do you trust most for accuracy?
- For photos: prefer higher resolution or more recent?
- How to combine notes from multiple sources?

### **5. Business vs Personal Contact Classification**
*How to categorize and handle different contact types*

**Examples to Discuss:**
- Contacts like "Anyline Team", "Support", "Buchhaltung"
- Personal contacts at work email addresses
- Family members with business roles
- Service providers (doctors, lawyers, etc.)

**Questions for You:**
- Should business contacts be in separate category or mixed?
- How to handle contacts that are both personal and business?
- Preferred naming for business contacts?

### **6. Data Quality Thresholds**
*When to auto-fix vs flag for review*

**Examples to Discuss:**
- Confidence levels for automatic fixes
- Types of changes that always need approval
- Data that should never be auto-modified

**Questions for You:**
- What confidence level makes you comfortable with auto-fixes?
- Are there any fields that should never be automatically changed?
- Preference for conservative (ask more) vs aggressive (fix more) approach?

### **7. Geographic and Cultural Preferences**
*Handle location-specific naming and formatting conventions*

**Examples to Discuss:**
- Austrian vs German naming conventions
- Address formatting preferences
- Phone number regional formatting
- Language preferences for contacts

**Questions for You:**
- Any Austrian-specific naming patterns to preserve?
- Preferred address format?
- How to handle contacts from different countries?

### **8. Special Cases and Edge Patterns**
*Known problematic patterns and preferred solutions*

**Examples to Discuss:**
- Contacts you know are problematic
- Family naming patterns
- Work colleague naming conventions
- Service provider contact formats

**Questions for You:**
- Any specific contacts you know need special handling?
- Family members with similar names?
- Colleagues with standardized naming?

### **9. Source Reliability Ranking**
*Which databases to trust more when conflicts arise*

**Questions for You:**
- Rank your sources by reliability: Sara's export, iPhone contacts, iPhone suggested
- Which source typically has more recent information?
- Which source has better name formatting?
- Any sources that tend to have specific types of errors?

### **10. Field Priority Rules**
*When merging, which version of each field to prefer*

**Questions for You:**
- For conflicting phone numbers, prefer mobile or landline?
- For conflicting emails, prefer personal or work?
- For conflicting names, prefer formal or informal?
- For conflicting addresses, prefer home or work?

---

## 📝 **Knowledge Capture Template**

### **Example Template for Each Category:**
```
Category: Contact Name Handling
Rule: [Your preference]
Confidence: [How sure you are about this rule]
Examples: [Specific cases where this applies]
Exceptions: [Cases where this rule doesn't apply]
Priority: [High/Medium/Low importance]
```

---

## 🎯 **Next Steps for Knowledge Capture Session**

### **Preparation for Discussion:**
1. **Review your existing contacts** to identify patterns you prefer
2. **Think about past merge decisions** you've made manually
3. **Consider your workflow preferences** for different contact types
4. **Identify any "VIP" contacts** that need special handling

### **Discussion Format:**
- Go through each category systematically
- Provide specific examples from your actual data
- Define clear rules and exceptions
- Set confidence levels for AI decision-making

### **Implementation in AI System:**
```python
# Example of how your preferences will be encoded
USER_PREFERENCES = {
    'name_formatting': {
        'compound_surnames': 'hyphenated',  # vs 'spaced'
        'professional_titles': 'separate_field',  # vs 'keep_in_name'
        'confidence_threshold': 0.90
    },
    'email_priority': {
        'personal_domains': ['gmail.com', 'gmx.net'],
        'trust_ranking': ['iphone_contacts', 'sara_export'],
        'keep_invalid': False
    },
    'merge_strategy': {
        'photo_selection': 'highest_resolution',  # vs 'most_recent'
        'note_combination': 'preserve_all',  # vs 'smart_merge'
        'source_priority': ['iphone_contacts', 'sara_export', 'iphone_suggested']
    }
}
```

---

## 🔧 **Implementation Benefits**

### **With Your Knowledge Training:**
- AI makes decisions aligned with your preferences
- Reduces manual review from ~30% to ~5% of contacts
- Consistent handling across all contact processing
- Faster implementation with fewer interruptions

### **Without Knowledge Training:**
- AI must ask for guidance on many edge cases
- Inconsistent decision-making
- More manual intervention required
- Longer implementation time

---

## 📋 **Ready for Knowledge Capture Session**

When you're ready, we'll go through each category systematically to capture your preferences and enhance the AI system's decision-making capabilities.

This will transform the AI from a general-purpose tool into a personalized contact processing system that thinks like you would.