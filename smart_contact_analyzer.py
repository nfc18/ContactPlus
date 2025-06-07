#!/usr/bin/env python3
"""
Smart Contact Analyzer - Identify legitimate vs problematic multi-email contacts
"""

import os
import re
import vobject
import json
from datetime import datetime
from difflib import SequenceMatcher
from collections import defaultdict

class SmartContactAnalyzer:
    """Analyze contacts to distinguish legitimate from problematic multi-email entries"""
    
    def __init__(self):
        self.personal_domains = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'icloud.com', 'me.com', 'aol.com', 'gmx.at', 'gmx.de',
            'gmx.net', 'web.de', 'live.com', 'googlemail.com'
        ]
        
        self.results = {
            'legitimate': [],
            'problematic': [],
            'borderline': []
        }
    
    def extract_name_from_email(self, email):
        """Extract potential name components from email"""
        local = email.split('@')[0].lower()
        
        # Remove numbers and special characters
        clean_local = re.sub(r'[\d\-\+_]', '', local)
        
        # Split by common separators
        parts = re.split(r'[._]', clean_local)
        parts = [p for p in parts if len(p) > 1]  # Filter out single characters
        
        return parts
    
    def calculate_name_similarity(self, name1, name2):
        """Calculate similarity between two names"""
        if not name1 or not name2:
            return 0
        return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
    
    def get_domain_type(self, email):
        """Classify email domain type"""
        domain = email.split('@')[1].lower()
        
        if any(pd in domain for pd in self.personal_domains):
            return 'personal'
        elif 'anyline' in domain:
            return 'anyline'
        elif '9yards' in domain:
            return 'nineyards'
        else:
            return 'company'
    
    def analyze_email_patterns(self, contact_name, emails):
        """Analyze if emails belong to the same person"""
        
        # Extract name parts from contact name
        contact_name_parts = set()
        if contact_name and contact_name != "No name":
            name_clean = re.sub(r'[^\w\s]', '', contact_name.lower())
            contact_name_parts = set(name_clean.split())
        
        # Analyze each email
        email_analysis = []
        different_people_detected = False
        
        for email in emails:
            email_parts = self.extract_name_from_email(email)
            domain_type = self.get_domain_type(email)
            
            # Check if email parts match contact name
            name_match_score = 0
            if contact_name_parts and email_parts:
                matches = 0
                for contact_part in contact_name_parts:
                    for email_part in email_parts:
                        if self.calculate_name_similarity(contact_part, email_part) > 0.8:
                            matches += 1
                            break
                name_match_score = matches / len(contact_name_parts)
            
            email_analysis.append({
                'email': email,
                'parts': email_parts,
                'domain_type': domain_type,
                'name_match_score': name_match_score
            })
        
        # Group emails by potential person
        person_groups = defaultdict(list)
        
        for analysis in email_analysis:
            if analysis['parts']:
                # Use first part as identifier (usually first name)
                key = analysis['parts'][0]
                person_groups[key].append(analysis)
            else:
                # Generic emails without clear name
                person_groups['generic'].append(analysis)
        
        # Check if multiple distinct people detected
        distinct_names = set()
        for group in person_groups.values():
            if group[0]['parts']:
                distinct_names.add(group[0]['parts'][0])
        
        different_people_detected = len(distinct_names) > 1
        
        return {
            'email_analysis': email_analysis,
            'person_groups': dict(person_groups),
            'different_people_detected': different_people_detected,
            'distinct_name_count': len(distinct_names)
        }
    
    def classify_contact(self, vcard):
        """Classify contact as legitimate, problematic, or borderline"""
        
        name = vcard.fn.value if hasattr(vcard, 'fn') and vcard.fn.value else "No name"
        
        if not hasattr(vcard, 'email_list') or len(vcard.email_list) < 5:
            return None  # Only analyze contacts with 5+ emails
        
        emails = [e.value for e in vcard.email_list if e.value]
        org = None
        if hasattr(vcard, 'org') and vcard.org.value:
            if isinstance(vcard.org.value, list):
                org = ' '.join(vcard.org.value)
            else:
                org = str(vcard.org.value)
        
        # Analyze email patterns
        analysis = self.analyze_email_patterns(name, emails)
        
        # Classification logic
        classification = self._determine_classification(name, emails, org, analysis)
        
        contact_data = {
            'name': name,
            'organization': org,
            'email_count': len(emails),
            'emails': emails,
            'analysis': analysis,
            'classification': classification['type'],
            'confidence': classification['confidence'],
            'reasons': classification['reasons'],
            'recommendation': classification['recommendation']
        }
        
        return contact_data
    
    def _determine_classification(self, name, emails, org, analysis):
        """Determine if contact is legitimate, problematic, or borderline"""
        
        reasons = []
        confidence = 100
        
        # Factor 1: Different people detected in emails
        if analysis['different_people_detected'] and analysis['distinct_name_count'] >= 3:
            reasons.append(f"Multiple distinct names in emails ({analysis['distinct_name_count']} detected)")
            confidence -= 60
            return {
                'type': 'problematic',
                'confidence': max(confidence, 10),
                'reasons': reasons,
                'recommendation': 'split'
            }
        
        # Factor 2: Check name consistency
        name_matches = 0
        for email_data in analysis['email_analysis']:
            if email_data['name_match_score'] > 0.7:
                name_matches += 1
        
        name_consistency = name_matches / len(emails) if emails else 0
        
        if name_consistency < 0.3:
            reasons.append(f"Low name consistency ({name_consistency:.1%} of emails match contact name)")
            confidence -= 40
        
        # Factor 3: Domain analysis
        domain_types = defaultdict(int)
        for email_data in analysis['email_analysis']:
            domain_types[email_data['domain_type']] += 1
        
        # Factor 4: Specific problematic patterns
        
        # Check for obvious company mixing
        company_domains = set()
        for email in emails:
            domain = email.split('@')[1].lower()
            if domain not in [d for d in self.personal_domains] and 'anyline' not in domain:
                company_domains.add(domain)
        
        if len(company_domains) >= 3:
            reasons.append(f"Multiple unrelated company domains ({len(company_domains)} companies)")
            confidence -= 50
        
        # Check for role-based emails mixed with personal
        role_emails = [e for e in emails if any(role in e.lower() for role in 
                      ['admin', 'info', 'support', 'team', 'noreply', 'office'])]
        if role_emails:
            reasons.append(f"Contains {len(role_emails)} role-based emails")
            confidence -= 30
        
        # Factor 5: Legitimate patterns
        
        # Same person, different companies (job changes)
        if name_consistency > 0.7 and len(company_domains) <= 2:
            reasons.append("Good name consistency, likely job changes")
            confidence += 20
        
        # Same person, different email formats at same company
        anyline_emails = [e for e in emails if 'anyline' in e.lower()]
        if len(anyline_emails) >= 3 and name_consistency > 0.5:
            reasons.append("Multiple Anyline emails with good name consistency")
            confidence += 10
        
        # Personal + work emails
        personal_emails = [e for e in emails if any(pd in e.lower() for pd in self.personal_domains)]
        if len(personal_emails) <= 2 and len(emails) - len(personal_emails) <= 3:
            reasons.append("Reasonable mix of personal and work emails")
            confidence += 15
        
        # Final classification
        if confidence >= 70:
            return {
                'type': 'legitimate',
                'confidence': confidence,
                'reasons': reasons,
                'recommendation': 'keep'
            }
        elif confidence >= 40:
            return {
                'type': 'borderline',
                'confidence': confidence,
                'reasons': reasons,
                'recommendation': 'review'
            }
        else:
            return {
                'type': 'problematic',
                'confidence': confidence,
                'reasons': reasons,
                'recommendation': 'split'
            }
    
    def analyze_database(self, filepath):
        """Analyze all multi-email contacts in a database"""
        
        print(f"\nAnalyzing: {os.path.basename(filepath)}")
        print("-" * 80)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            vcards = list(vobject.readComponents(f.read()))
        
        contacts_analyzed = 0
        
        for vcard in vcards:
            result = self.classify_contact(vcard)
            if result:
                contacts_analyzed += 1
                result['source_database'] = os.path.basename(filepath)
                self.results[result['classification']].append(result)
        
        print(f"Analyzed {contacts_analyzed} contacts with 5+ emails")
        print(f"  Legitimate: {len([r for r in self.results['legitimate'] if r['source_database'] == os.path.basename(filepath)])}")
        print(f"  Borderline: {len([r for r in self.results['borderline'] if r['source_database'] == os.path.basename(filepath)])}")
        print(f"  Problematic: {len([r for r in self.results['problematic'] if r['source_database'] == os.path.basename(filepath)])}")
    
    def generate_review_interface(self, output_path):
        """Generate interactive review interface"""
        
        # Combine borderline and problematic for review
        review_contacts = self.results['borderline'] + self.results['problematic']
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Smart Contact Review - {len(review_contacts)} Contacts</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; 
            margin: 0; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{ 
            max-width: 1400px; 
            margin: 0 auto; 
            padding: 20px;
        }}
        .header {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .stats {{
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-top: 20px;
        }}
        .stat-box {{
            background: white;
            padding: 15px 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .contact-card {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            margin-bottom: 30px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}
        .contact-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        }}
        .card-header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .classification {{
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }}
        .legitimate {{ background: #d4edda; color: #155724; }}
        .borderline {{ background: #fff3cd; color: #856404; }}
        .problematic {{ background: #f8d7da; color: #721c24; }}
        .card-content {{
            padding: 30px;
        }}
        .contact-info {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}
        .info-section h4 {{
            margin: 0 0 15px 0;
            color: #2c3e50;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }}
        .email-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 10px;
        }}
        .email-item {{
            background: #f8f9fa;
            padding: 10px 15px;
            border-radius: 8px;
            border-left: 4px solid #007bff;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9em;
        }}
        .email-personal {{ border-left-color: #28a745; }}
        .email-anyline {{ border-left-color: #17a2b8; }}
        .email-company {{ border-left-color: #ffc107; }}
        .reasons {{
            background: #e9ecef;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .reasons h4 {{
            margin: 0 0 15px 0;
            color: #495057;
        }}
        .reason-item {{
            padding: 8px 0;
            border-bottom: 1px solid #dee2e6;
        }}
        .reason-item:last-child {{ border-bottom: none; }}
        .actions {{
            display: flex;
            gap: 15px;
            justify-content: center;
            padding: 25px;
            background: #f8f9fa;
            border-top: 1px solid #dee2e6;
        }}
        .btn {{
            padding: 15px 30px;
            border: none;
            border-radius: 25px;
            font-weight: 600;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            min-width: 120px;
        }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        }}
        .btn-split {{
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            color: white;
        }}
        .btn-delete {{
            background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
            color: white;
        }}
        .btn-keep {{
            background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
            color: white;
        }}
        .decided {{
            opacity: 0.6;
            transform: scale(0.98);
        }}
        .progress-bar {{
            position: fixed;
            top: 0;
            left: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s ease;
            z-index: 1000;
        }}
        .floating-stats {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: rgba(44, 62, 80, 0.95);
            backdrop-filter: blur(10px);
            color: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            z-index: 1000;
        }}
    </style>
</head>
<body>
    <div class="progress-bar" id="progressBar"></div>
    
    <div class="container">
        <div class="header">
            <h1>Smart Contact Review</h1>
            <p>Review {len(review_contacts)} contacts with multiple email addresses</p>
            <div class="stats">
                <div class="stat-box">
                    <strong>{len(self.results['legitimate'])}</strong><br>
                    <small>Legitimate (Auto-kept)</small>
                </div>
                <div class="stat-box">
                    <strong>{len(self.results['borderline'])}</strong><br>
                    <small>Borderline (Review)</small>
                </div>
                <div class="stat-box">
                    <strong>{len(self.results['problematic'])}</strong><br>
                    <small>Problematic (Review)</small>
                </div>
            </div>
        </div>
"""
        
        for i, contact in enumerate(review_contacts):
            classification_class = contact['classification']
            
            html += f"""
        <div class="contact-card" id="contact-{i}" data-contact-id="{i}">
            <div class="card-header">
                <div>
                    <h2 style="margin: 0;">{contact['name']}</h2>
                    <div style="margin-top: 8px; opacity: 0.8;">
                        {contact['source_database']} • {contact['email_count']} emails
                    </div>
                </div>
                <div class="classification {classification_class}">
                    {contact['classification'].title()} ({contact['confidence']}%)
                </div>
            </div>
            
            <div class="card-content">
                <div class="contact-info">
                    <div class="info-section">
                        <h4>Contact Details</h4>
                        <p><strong>Name:</strong> {contact['name']}</p>
                        <p><strong>Organization:</strong> {contact['organization'] or 'None'}</p>
                        <p><strong>Email Count:</strong> {contact['email_count']}</p>
                        <p><strong>Recommendation:</strong> {contact['recommendation'].title()}</p>
                    </div>
                    
                    <div class="info-section">
                        <h4>Analysis Results</h4>
                        <p><strong>Distinct Names:</strong> {contact['analysis']['distinct_name_count']}</p>
                        <p><strong>Different People:</strong> {'Yes' if contact['analysis']['different_people_detected'] else 'No'}</p>
                        <p><strong>Person Groups:</strong> {len(contact['analysis']['person_groups'])}</p>
                    </div>
                </div>
                
                <div class="info-section">
                    <h4>Email Addresses</h4>
                    <div class="email-grid">
"""
            
            for email_data in contact['analysis']['email_analysis']:
                email = email_data['email']
                domain_type = email_data['domain_type']
                css_class = f"email-{domain_type}"
                
                html += f"""
                        <div class="email-item {css_class}">
                            {email}
                            <div style="font-size: 0.8em; opacity: 0.7; margin-top: 5px;">
                                {domain_type} • Match: {email_data['name_match_score']:.1%}
                            </div>
                        </div>
"""
            
            html += f"""
                    </div>
                </div>
                
                <div class="reasons">
                    <h4>Analysis Reasons</h4>
"""
            
            for reason in contact['reasons']:
                html += f'<div class="reason-item">• {reason}</div>'
            
            html += f"""
                </div>
            </div>
            
            <div class="actions">
                <button class="btn btn-split" onclick="makeDecision('split', {i})">
                    ✂️ Split Contact
                </button>
                <button class="btn btn-delete" onclick="makeDecision('delete', {i})">
                    🗑️ Delete Contact
                </button>
                <button class="btn btn-keep" onclick="makeDecision('keep', {i})">
                    ✅ Keep As-Is
                </button>
            </div>
        </div>
"""
        
        html += f"""
    </div>
    
    <div class="floating-stats" id="floatingStats">
        <div><strong>Progress:</strong> <span id="progressText">0 / {len(review_contacts)}</span></div>
        <div style="margin-top: 5px; font-size: 0.9em;">
            Split: <span id="splitCount">0</span> | 
            Delete: <span id="deleteCount">0</span> | 
            Keep: <span id="keepCount">0</span>
        </div>
    </div>

    <script>
        let decisions = {{}};
        let totalContacts = {len(review_contacts)};
        let counts = {{ split: 0, delete: 0, keep: 0 }};
        
        function makeDecision(decision, contactId) {{
            // Remove previous decision if exists
            if (decisions[contactId]) {{
                counts[decisions[contactId]]--;
            }}
            
            // Add new decision
            decisions[contactId] = decision;
            counts[decision]++;
            
            // Update UI
            const card = document.getElementById('contact-' + contactId);
            card.classList.add('decided');
            
            updateProgress();
            saveDecisions();
        }}
        
        function updateProgress() {{
            const completed = Object.keys(decisions).length;
            const percentage = (completed / totalContacts) * 100;
            
            document.getElementById('progressBar').style.width = percentage + '%';
            document.getElementById('progressText').textContent = completed + ' / ' + totalContacts;
            document.getElementById('splitCount').textContent = counts.split;
            document.getElementById('deleteCount').textContent = counts.delete;
            document.getElementById('keepCount').textContent = counts.keep;
            
            if (completed === totalContacts) {{
                document.getElementById('floatingStats').style.background = 'rgba(39, 174, 96, 0.95)';
                document.getElementById('floatingStats').innerHTML = 
                    '<div><strong>✅ All Done!</strong></div><div style="margin-top: 5px;">Ready to process decisions</div>';
            }}
        }}
        
        function saveDecisions() {{
            localStorage.setItem('contact_decisions', JSON.stringify(decisions));
            console.log('Decisions saved:', decisions);
        }}
        
        // Load saved decisions
        window.onload = function() {{
            const saved = localStorage.getItem('contact_decisions');
            if (saved) {{
                decisions = JSON.parse(saved);
                
                // Apply saved decisions to UI
                for (let contactId in decisions) {{
                    const card = document.getElementById('contact-' + contactId);
                    if (card) {{
                        card.classList.add('decided');
                        counts[decisions[contactId]]++;
                    }}
                }}
                
                updateProgress();
            }}
        }};
        
        // Export function
        function exportDecisions() {{
            const dataStr = JSON.stringify(decisions, null, 2);
            const dataBlob = new Blob([dataStr], {{type: 'application/json'}});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'contact_decisions.json';
            link.click();
        }}
    </script>
</body>
</html>
"""
        
        with open(output_path, 'w') as f:
            f.write(html)
    
    def save_analysis_report(self, output_path):
        """Save detailed analysis report"""
        report = {
            'analysis_date': datetime.now().isoformat(),
            'summary': {
                'legitimate': len(self.results['legitimate']),
                'borderline': len(self.results['borderline']),
                'problematic': len(self.results['problematic']),
                'total_analyzed': sum(len(self.results[cat]) for cat in self.results)
            },
            'results': self.results
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)


def main():
    """Run smart contact analysis on all three final databases"""
    
    print("Smart Contact Analysis")
    print("=" * 80)
    print("Analyzing multi-email contacts to distinguish legitimate from problematic...")
    
    analyzer = SmartContactAnalyzer()
    
    # Analyze all three databases
    databases = [
        "data/Sara_Export_VALIDATED_20250606_FINAL.vcf",
        "data/iPhone_Contacts_VALIDATED_20250606_120917_FINAL.vcf", 
        "data/iPhone_Suggested_VALIDATED_20250606_120917_FINAL.vcf"
    ]
    
    for db_path in databases:
        if os.path.exists(db_path):
            analyzer.analyze_database(db_path)
        else:
            print(f"Warning: Database not found - {db_path}")
    
    # Generate review interface
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    review_path = f"data/SMART_CONTACT_REVIEW_{timestamp}.html"
    report_path = f"data/smart_analysis_report_{timestamp}.json"
    
    analyzer.generate_review_interface(review_path)
    analyzer.save_analysis_report(report_path)
    
    # Print summary
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"✅ Legitimate contacts: {len(analyzer.results['legitimate'])} (will be kept as-is)")
    print(f"⚠️  Borderline contacts: {len(analyzer.results['borderline'])} (need review)")
    print(f"🚨 Problematic contacts: {len(analyzer.results['problematic'])} (need review)")
    
    total_review = len(analyzer.results['borderline']) + len(analyzer.results['problematic'])
    print(f"\n📋 Review needed: {total_review} contacts")
    print(f"📄 Review interface: {review_path}")
    print(f"📊 Analysis report: {report_path}")
    
    print(f"\n🎯 Next steps:")
    print(f"   1. Open {review_path} in your browser")
    print(f"   2. Review each contact and decide: Split, Delete, or Keep")
    print(f"   3. Process your decisions to clean the databases")


if __name__ == "__main__":
    main()