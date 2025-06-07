# Testing Strategy for Contact Cleaner System

## Overview
This document outlines comprehensive testing strategies to ensure vCard standard compliance, data integrity, and system reliability throughout the contact cleaning pipeline.

## Test Categories

### 1. vCard Compliance Testing

#### Parser Testing
```python
class VCardParserTests:
    """Test vCard parsing for various formats and edge cases"""
    
    def test_vcard_versions(self):
        """Test parsing of different vCard versions"""
        test_cases = [
            # vCard 2.1
            """BEGIN:VCARD
VERSION:2.1
N:Doe;John;;;
FN:John Doe
TEL;HOME:+1234567890
END:VCARD""",
            
            # vCard 3.0
            """BEGIN:VCARD
VERSION:3.0
N:Doe;John;Q.;Dr.;Jr.
FN:Dr. John Q. Doe Jr.
EMAIL;TYPE=INTERNET:john@example.com
END:VCARD""",
            
            # vCard 4.0
            """BEGIN:VCARD
VERSION:4.0
FN:John Doe
N:Doe;John;;;
EMAIL;TYPE=work:john@example.com
TEL;TYPE="voice,work";VALUE=uri:tel:+1234567890
END:VCARD"""
        ]
        
        for vcard_text in test_cases:
            contact = parse_vcard(vcard_text)
            assert contact.first_name == "John"
            assert contact.last_name == "Doe"
    
    def test_encoding_handling(self):
        """Test various character encodings"""
        test_cases = [
            # UTF-8 with special characters
            ("Müller", "UTF-8"),
            ("José", "UTF-8"),
            ("北京", "UTF-8"),
            # Quoted-printable
            ("M=C3=BCller", "QUOTED-PRINTABLE"),
            # Base64
            ("TcO8bGxlcg==", "BASE64")
        ]
        
        for encoded_name, encoding in test_cases:
            vcard = f"""BEGIN:VCARD
VERSION:3.0
N;ENCODING={encoding}:{encoded_name};;;;
END:VCARD"""
            contact = parse_vcard(vcard)
            assert contact.last_name  # Should decode properly
    
    def test_photo_handling(self):
        """Test photo parsing and validation"""
        # Test base64 embedded photo
        vcard_embedded = """BEGIN:VCARD
VERSION:3.0
PHOTO;ENCODING=b;TYPE=JPEG:/9j/4AAQSkZJRg...
END:VCARD"""
        
        # Test URI photo reference
        vcard_uri = """BEGIN:VCARD
VERSION:4.0
PHOTO:https://example.com/photo.jpg
END:VCARD"""
        
        contact1 = parse_vcard(vcard_embedded)
        assert contact1.photo_data
        assert contact1.photo_type == "JPEG"
        
        contact2 = parse_vcard(vcard_uri)
        assert contact2.photo_uri == "https://example.com/photo.jpg"
```

#### Generator Testing
```python
class VCardGeneratorTests:
    """Test vCard generation for standard compliance"""
    
    def test_minimal_vcard_generation(self):
        """Test generation of minimal valid vCard"""
        contact = Contact(
            first_name="John",
            last_name="Doe"
        )
        
        vcard = generate_vcard(contact, version="4.0")
        
        # Validate required fields
        assert "BEGIN:VCARD" in vcard
        assert "VERSION:4.0" in vcard
        assert "FN:John Doe" in vcard
        assert "END:VCARD" in vcard
        
        # Validate with external validator
        assert validate_vcard_syntax(vcard)
    
    def test_special_character_escaping(self):
        """Test proper escaping of special characters"""
        test_cases = [
            ("Semi;colon", "Semi\\;colon"),
            ("Back\\slash", "Back\\\\slash"),
            ("New\nline", "New\\nline"),
            ("Comma,Test", "Comma\\,Test")
        ]
        
        for input_text, expected in test_cases:
            contact = Contact(first_name=input_text)
            vcard = generate_vcard(contact)
            assert expected in vcard
    
    def test_line_folding(self):
        """Test line folding for long lines (75 chars)"""
        long_note = "A" * 100
        contact = Contact(
            first_name="John",
            notes=long_note
        )
        
        vcard = generate_vcard(contact)
        lines = vcard.split('\n')
        
        # Check no line exceeds 75 characters
        for line in lines:
            assert len(line) <= 75
        
        # Check folded lines start with space
        assert any(line.startswith(' ') for line in lines)
```

### 2. Data Cleaning Testing

#### Field Validation Tests
```python
class DataCleaningTests:
    """Test data cleaning and validation rules"""
    
    def test_email_validation(self):
        """Test email address validation and cleaning"""
        test_cases = [
            # Valid emails
            ("john@example.com", True, "john@example.com"),
            ("JOHN@EXAMPLE.COM", True, "john@example.com"),
            ("john+tag@example.com", True, "john+tag@example.com"),
            
            # Invalid emails
            ("invalid.email", False, None),
            ("@example.com", False, None),
            ("john@", False, None),
            ("john doe@example.com", False, None)
        ]
        
        for email, should_validate, expected in test_cases:
            result = validate_and_clean_email(email)
            if should_validate:
                assert result == expected
            else:
                assert result is None
    
    def test_phone_normalization(self):
        """Test phone number normalization"""
        test_cases = [
            # US numbers
            ("(555) 123-4567", "+15551234567"),
            ("555-123-4567", "+15551234567"),
            ("5551234567", "+15551234567"),
            
            # International
            ("+44 20 7123 4567", "+442071234567"),
            ("0043 1 234 5678", "+4312345678"),
            
            # With extensions
            ("+1-555-123-4567 ext 123", "+15551234567"),
        ]
        
        for input_phone, expected in test_cases:
            result = normalize_phone_number(input_phone, default_country="US")
            assert result == expected
    
    def test_name_capitalization(self):
        """Test proper name capitalization"""
        test_cases = [
            ("JOHN DOE", "John Doe"),
            ("john doe", "John Doe"),
            ("mcdonald", "McDonald"),
            ("o'brien", "O'Brien"),
            ("van der berg", "van der Berg"),
            ("josé garcía", "José García")
        ]
        
        for input_name, expected in test_cases:
            result = clean_name(input_name)
            assert result == expected
```

#### Data Extraction Tests
```python
class DataExtractionTests:
    """Test extraction of data from wrong fields"""
    
    def test_extract_from_notes(self):
        """Test extracting contact info from notes field"""
        notes = """
        Call me at 555-123-4567
        Email: john@example.com
        LinkedIn: linkedin.com/in/johndoe
        Twitter: @johndoe
        """
        
        extracted = extract_data_from_notes(notes)
        
        assert "555-123-4567" in extracted['phones']
        assert "john@example.com" in extracted['emails']
        assert "linkedin.com/in/johndoe" in extracted['linkedin']
        assert "@johndoe" in extracted['twitter']
    
    def test_preserve_legitimate_notes(self):
        """Ensure legitimate notes are preserved"""
        notes = "Met at conference in 2023. Interested in AI projects."
        
        extracted = extract_data_from_notes(notes)
        cleaned_notes = extracted['cleaned_notes']
        
        assert "conference" in cleaned_notes
        assert "AI projects" in cleaned_notes
```

### 3. Deduplication Testing

#### Duplicate Detection Tests
```python
class DuplicateDetectionTests:
    """Test duplicate detection algorithms"""
    
    def test_exact_email_match(self):
        """Test detection of duplicates with same email"""
        contact1 = Contact(
            first_name="John",
            last_name="Doe",
            emails=["john@example.com"]
        )
        contact2 = Contact(
            first_name="Johnny",
            last_name="Doe",
            emails=["john@example.com"]
        )
        
        score = calculate_match_score(contact1, contact2)
        assert score > 0.95  # Very high confidence
    
    def test_fuzzy_name_matching(self):
        """Test fuzzy matching for similar names"""
        test_pairs = [
            # Should match
            (("Bob", "Smith"), ("Robert", "Smith"), True),
            (("Jon", "Doe"), ("John", "Doe"), True),
            (("Chris", "Johnson"), ("Christopher", "Johnson"), True),
            
            # Should not match
            (("John", "Smith"), ("John", "Jones"), False),
            (("Maria", "Garcia"), ("Marie", "Garcia"), False),
        ]
        
        for (first1, last1), (first2, last2), should_match in test_pairs:
            contact1 = Contact(first_name=first1, last_name=last1)
            contact2 = Contact(first_name=first2, last_name=last2)
            
            score = calculate_match_score(contact1, contact2)
            if should_match:
                assert score > 0.7
            else:
                assert score < 0.5
    
    def test_same_name_different_people(self):
        """Test detection of different people with same name"""
        contact1 = Contact(
            first_name="John",
            last_name="Smith",
            organization="Apple Inc.",
            emails=["john.smith@apple.com"]
        )
        contact2 = Contact(
            first_name="John",
            last_name="Smith",
            organization="Microsoft",
            emails=["john.smith@microsoft.com"]
        )
        
        score = calculate_match_score(contact1, contact2)
        assert score < 0.5  # Low confidence, likely different people
        
        # Check for warning flag
        warnings = detect_potential_issues(contact1, contact2)
        assert "different_companies" in warnings
```

### 4. Merge Operation Testing

#### Merge Logic Tests
```python
class MergeOperationTests:
    """Test contact merging operations"""
    
    def test_basic_merge(self):
        """Test basic merge of two contacts"""
        primary = Contact(
            first_name="John",
            emails=["john@example.com"],
            phones=["+1234567890"]
        )
        duplicate = Contact(
            first_name="John",
            last_name="Doe",
            emails=["john.doe@example.com"],
            organization="Example Corp"
        )
        
        merged = merge_contacts(primary, [duplicate])
        
        assert merged.last_name == "Doe"
        assert len(merged.emails) == 2
        assert merged.organization == "Example Corp"
        assert len(merged.phones) == 1
    
    def test_photo_selection(self):
        """Test selection of best photo during merge"""
        photo1 = Photo(data="...", width=100, height=100, size=10000)
        photo2 = Photo(data="...", width=500, height=500, size=50000)
        photo3 = Photo(data="...", width=1000, height=1000, size=200000)
        
        best_photo = select_best_photo([photo1, photo2, photo3])
        assert best_photo == photo3  # Highest resolution
    
    def test_conflict_resolution(self):
        """Test resolution of conflicting data"""
        primary = Contact(
            first_name="John",
            job_title="Developer",
            updated_at=datetime(2023, 1, 1)
        )
        duplicate = Contact(
            first_name="John",
            job_title="Senior Developer",
            updated_at=datetime(2024, 1, 1)
        )
        
        merged = merge_contacts(primary, [duplicate])
        assert merged.job_title == "Senior Developer"  # Newer data wins
```

### 5. Enhancement Testing

#### LinkedIn Enhancement Tests
```python
class LinkedInEnhancementTests:
    """Test LinkedIn data enhancement"""
    
    def test_linkedin_matching(self):
        """Test matching LinkedIn profiles to contacts"""
        contact = Contact(
            first_name="John",
            last_name="Doe",
            organization="Example Corp"
        )
        
        linkedin_data = {
            'First Name': 'John',
            'Last Name': 'Doe',
            'Company': 'Example Corporation',
            'Position': 'Senior Developer'
        }
        
        match_score = match_linkedin_to_contact(contact, linkedin_data)
        assert match_score > 0.8
        
        enhanced = enhance_with_linkedin(contact, linkedin_data)
        assert enhanced.job_title == "Senior Developer"
```

### 6. Rating System Testing

#### Rating Calculation Tests
```python
class RatingSystemTests:
    """Test contact rating calculations"""
    
    def test_high_value_contact(self):
        """Test rating for high-value contact"""
        contact = Contact(
            first_name="John",
            last_name="Doe",
            emails=["john@example.com"],
            phones=["+1234567890"],
            organization="Important Corp",
            job_title="CEO"
        )
        
        email_stats = {
            'total_sent': 50,
            'total_received': 45,
            'last_interaction': datetime.now() - timedelta(days=5)
        }
        
        rating = calculate_contact_rating(contact, email_stats, {})
        assert rating.total_score >= 80
        assert rating.category == 'premium'
    
    def test_low_quality_contact(self):
        """Test rating for low-quality contact"""
        contact = Contact(
            first_name="UNKNOWN",
            emails=["invalid@"],
            notes="phone: not-a-number"
        )
        
        email_stats = {
            'total_sent': 0,
            'total_received': 0,
            'last_interaction': None
        }
        
        rating = calculate_contact_rating(contact, email_stats, {})
        assert rating.total_score < 40
        assert rating.category == 'review'
        assert len(rating.quality_issues) > 0
```

### 7. Integration Testing

#### End-to-End Pipeline Tests
```python
class IntegrationTests:
    """Test complete pipeline from import to export"""
    
    def test_full_pipeline(self):
        """Test complete contact processing pipeline"""
        # 1. Import
        vcf_file = "test_contacts.vcf"
        contacts = import_contacts(vcf_file)
        assert len(contacts) > 0
        
        # 2. Clean
        cleaned = []
        for contact in contacts:
            cleaned_contact = clean_contact(contact)
            cleaned.append(cleaned_contact)
        
        # 3. Deduplicate
        duplicates = find_duplicates(cleaned)
        merged_contacts = process_duplicates(duplicates)
        
        # 4. Enhance
        enhanced = []
        for contact in merged_contacts:
            enhanced_contact = enhance_contact(contact)
            enhanced.append(enhanced_contact)
        
        # 5. Rate
        ratings = []
        for contact in enhanced:
            rating = calculate_rating(contact)
            ratings.append(rating)
        
        # 6. Export
        export_list = filter_for_export(enhanced, ratings, threshold=60)
        export_vcf = generate_export_vcf(export_list)
        
        # Validate export
        assert validate_vcard_syntax(export_vcf)
        assert len(export_list) <= len(contacts)
```

### 8. Performance Testing

#### Load Testing
```python
class PerformanceTests:
    """Test system performance with large datasets"""
    
    def test_large_import(self):
        """Test importing large vCard file"""
        # Generate test file with 10,000 contacts
        large_vcf = generate_test_vcf(10000)
        
        start_time = time.time()
        contacts = import_contacts(large_vcf)
        import_time = time.time() - start_time
        
        assert len(contacts) == 10000
        assert import_time < 30  # Should complete in 30 seconds
    
    def test_deduplication_performance(self):
        """Test deduplication performance"""
        # Generate contacts with 20% duplicates
        contacts = generate_test_contacts(5000, duplicate_rate=0.2)
        
        start_time = time.time()
        duplicates = find_duplicates(contacts)
        dedup_time = time.time() - start_time
        
        assert dedup_time < 60  # Should complete in 1 minute
        assert len(duplicates) > 0
```

### 9. Error Handling Tests

#### Robustness Testing
```python
class ErrorHandlingTests:
    """Test error handling and recovery"""
    
    def test_malformed_vcard(self):
        """Test handling of malformed vCard data"""
        malformed_vcards = [
            "BEGIN:VCARD\nVERSION:3.0\n",  # Missing END
            "VERSION:3.0\nFN:John\nEND:VCARD",  # Missing BEGIN
            "BEGIN:VCARD\nVERSION:3.0\nFN:John\nEMAIL;ENCODING=UNKNOWN:test\nEND:VCARD",  # Unknown encoding
        ]
        
        for vcard in malformed_vcards:
            try:
                contact = parse_vcard(vcard)
                # Should handle gracefully
                assert contact is not None or contact is None
            except Exception as e:
                # Should not crash
                assert isinstance(e, VCardParseError)
    
    def test_recovery_mechanisms(self):
        """Test rollback and recovery features"""
        contact = Contact(id="test123", first_name="John")
        
        # Simulate failed merge
        try:
            with transaction() as tx:
                contact.first_name = "Jane"
                contact.emails = ["invalid-email"]  # Will fail validation
                save_contact(contact)
        except ValidationError:
            # Should rollback
            pass
        
        # Verify rollback worked
        recovered = get_contact("test123")
        assert recovered.first_name == "John"
```

## Test Data Management

### Test Data Generator
```python
def generate_test_data():
    """Generate comprehensive test data"""
    
    test_scenarios = {
        'perfect_contact': Contact(
            first_name="John",
            last_name="Doe",
            emails=["john@example.com"],
            phones=["+1234567890"],
            organization="Example Corp",
            job_title="CEO",
            address=Address(street="123 Main St", city="Boston", country="USA")
        ),
        
        'minimal_contact': Contact(
            first_name="Jane"
        ),
        
        'messy_contact': Contact(
            first_name="JOHN",
            last_name="doe",
            emails=["JOHN@EXAMPLE.COM", "invalid@"],
            notes="phone: 555-1234\nemail: john2@example.com"
        ),
        
        'duplicate_pair': [
            Contact(first_name="Bob", emails=["bob@example.com"]),
            Contact(first_name="Robert", emails=["bob@example.com"])
        ]
    }
    
    return test_scenarios
```

## Continuous Testing Strategy

### Automated Test Suite
- Run unit tests on every commit
- Run integration tests before merges
- Performance tests weekly
- Full regression tests before releases

### Test Coverage Requirements
- Minimum 80% code coverage
- 100% coverage for critical paths (merge, deduplication)
- All vCard standard requirements tested
- All data cleaning rules tested

### Testing Tools
- **pytest**: Unit and integration testing
- **hypothesis**: Property-based testing for edge cases
- **pytest-benchmark**: Performance testing
- **vcard-validator**: External vCard validation
- **faker**: Generate realistic test data