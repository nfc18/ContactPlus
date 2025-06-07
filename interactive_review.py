#!/usr/bin/env python3
"""
Interactive review system for manual contact merging
"""

import os
import json
import shutil
import vobject
from datetime import datetime
from intelligent_merge import IntelligentContactMerger

def create_interactive_review(database_path):
    """Create interactive review for the final cleaned database"""
    
    print("Creating Interactive Review System")
    print("=" * 80)
    
    # Load the cleaned database
    with open(database_path, 'r', encoding='utf-8') as f:
        vcards = list(vobject.readComponents(f.read()))
    
    print(f"Loaded {len(vcards)} contacts from cleaned database")
    
    # Re-run matching on the cleaned database
    merger = IntelligentContactMerger()
    
    # Prepare contacts with dummy source (since it's already merged)
    vcards_with_source = [('merged', vcard) for vcard in vcards]
    
    # Find remaining matches
    match_groups = merger.find_matches(vcards_with_source)
    
    # Filter for manual review confidence
    review_groups = []
    for group in match_groups:
        if 70 <= group['confidence'] < 95:
            review_groups.append(group)
    
    print(f"Found {len(review_groups)} groups needing manual review")
    
    if not review_groups:
        print("✅ No contacts need manual review!")
        return None
    
    # Generate enhanced interactive HTML
    review_path = f"data/INTERACTIVE_REVIEW_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    generate_enhanced_review_html(review_groups, review_path)
    
    # Generate decisions JSON template
    decisions_path = review_path.replace('.html', '_decisions.json')
    generate_decisions_template(review_groups, decisions_path)
    
    print(f"\n✅ Interactive review created:")
    print(f"   HTML: {review_path}")
    print(f"   Decisions: {decisions_path}")
    print(f"\n📋 Next steps:")
    print(f"   1. Open the HTML file in your browser")
    print(f"   2. Review each potential match")
    print(f"   3. Click 'MERGE' or 'KEEP SEPARATE' for each")
    print(f"   4. Run the processor to apply your decisions")
    
    return review_path, decisions_path

def generate_enhanced_review_html(review_groups, output_path):
    """Generate enhanced HTML with better interface"""
    
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Contact Merge Review - Final Review</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { margin: 0; font-size: 2.5em; }
        .header p { margin: 10px 0 0 0; opacity: 0.9; }
        .progress {
            background: #ecf0f1;
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid #ddd;
        }
        .progress-bar {
            background: #3498db;
            height: 10px;
            border-radius: 5px;
            transition: width 0.3s ease;
        }
        .content { padding: 30px; }
        .match-group { 
            background: #f8f9fa; 
            margin: 30px 0; 
            border-radius: 15px; 
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }
        .match-group:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        .match-group.decided-merge { border-color: #27ae60; background: #d5f4e6; }
        .match-group.decided-separate { border-color: #e74c3c; background: #fdf2f2; }
        .match-header {
            background: white;
            padding: 20px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .confidence { 
            font-weight: bold; 
            padding: 8px 16px; 
            border-radius: 20px; 
            font-size: 0.9em;
        }
        .high-conf { background: #d4edda; color: #155724; }
        .med-conf { background: #fff3cd; color: #856404; }
        .low-conf { background: #f8d7da; color: #721c24; }
        .contact { 
            background: white;
            margin: 15px 20px; 
            padding: 20px; 
            border-radius: 10px;
            border-left: 4px solid #3498db;
        }
        .source { 
            font-weight: bold; 
            color: #2980b9; 
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .field { 
            margin: 8px 0; 
            display: flex;
            align-items: flex-start;
        }
        .field-label { 
            font-weight: 600; 
            width: 120px; 
            color: #555;
            flex-shrink: 0;
        }
        .field-value {
            flex: 1;
            word-break: break-word;
        }
        .match-reason { 
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
            padding: 20px; 
            margin: 20px; 
            border-radius: 10px;
            border-left: 4px solid #2196f3; 
        }
        .actions { 
            padding: 25px; 
            text-align: center; 
            background: #f8f9fa;
            border-top: 1px solid #eee;
        }
        button { 
            padding: 12px 30px; 
            margin: 0 10px; 
            border: none;
            border-radius: 25px;
            cursor: pointer; 
            font-weight: 600;
            font-size: 1em;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .merge-btn { 
            background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); 
            color: white; 
        }
        .separate-btn { 
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); 
            color: white; 
        }
        .status { 
            position: fixed; 
            bottom: 30px; 
            right: 30px; 
            background: #2c3e50; 
            color: white; 
            padding: 15px 25px; 
            border-radius: 25px; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            z-index: 1000;
        }
        .completed { background: #27ae60 !important; }
        .email-list, .phone-list { display: flex; flex-wrap: wrap; gap: 5px; }
        .email-item, .phone-item { 
            background: #e9ecef; 
            padding: 4px 8px; 
            border-radius: 12px; 
            font-size: 0.85em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Final Contact Review</h1>
            <p>Review these """ + str(len(review_groups)) + """ potential matches and decide whether to merge or keep separate</p>
        </div>
        
        <div class="progress">
            <div style="margin-bottom: 10px;">
                <span id="progress-text">0 of """ + str(len(review_groups)) + """ completed</span>
            </div>
            <div style="background: #ecf0f1; border-radius: 5px; height: 10px;">
                <div id="progress-bar" class="progress-bar" style="width: 0%;"></div>
            </div>
        </div>

        <div class="content">
"""
    
    for i, group in enumerate(review_groups):
        conf_class = 'high-conf' if group['confidence'] >= 85 else 'med-conf' if group['confidence'] >= 70 else 'low-conf'
        
        html += f"""
        <div class="match-group" id="group-{i}" data-group-id="{i}">
            <div class="match-header">
                <div>
                    <h3 style="margin: 0;">Potential Match #{i+1}</h3>
                    <div style="margin-top: 5px; font-size: 0.9em; color: #666;">
                        <strong>Match Type:</strong> {group['match_type'].replace('_', ' ').title()} | 
                        <strong>Match Value:</strong> {group['match_value']}
                    </div>
                </div>
                <div class="confidence {conf_class}">
                    {group['confidence']}% Confidence
                </div>
            </div>
"""
        
        for idx, source, vcard in group['contacts']:
            name = vcard.fn.value if hasattr(vcard, 'fn') else "No name"
            
            # Extract organization
            org = ""
            if hasattr(vcard, 'org') and vcard.org.value:
                if isinstance(vcard.org.value, list):
                    org = ' '.join(vcard.org.value)
                else:
                    org = str(vcard.org.value)
            
            html += f"""
            <div class="contact">
                <div class="source">Source: {source.replace('_', ' ').title()}</div>
                <div class="field">
                    <div class="field-label">Name:</div>
                    <div class="field-value"><strong>{name}</strong></div>
                </div>
"""
            
            if org:
                html += f"""
                <div class="field">
                    <div class="field-label">Organization:</div>
                    <div class="field-value">{org}</div>
                </div>
"""
            
            # Emails
            if hasattr(vcard, 'email_list') and vcard.email_list:
                emails = [e.value for e in vcard.email_list if e.value]
                if emails:
                    html += f"""
                <div class="field">
                    <div class="field-label">Emails:</div>
                    <div class="field-value">
                        <div class="email-list">
"""
                    for email in emails[:5]:  # Show max 5
                        html += f'<span class="email-item">{email}</span>'
                    if len(emails) > 5:
                        html += f'<span class="email-item">+{len(emails)-5} more</span>'
                    html += """
                        </div>
                    </div>
                </div>
"""
            
            # Phones
            if hasattr(vcard, 'tel_list') and vcard.tel_list:
                phones = [t.value for t in vcard.tel_list if t.value]
                if phones:
                    html += f"""
                <div class="field">
                    <div class="field-label">Phones:</div>
                    <div class="field-value">
                        <div class="phone-list">
"""
                    for phone in phones[:3]:  # Show max 3
                        html += f'<span class="phone-item">{phone}</span>'
                    if len(phones) > 3:
                        html += f'<span class="phone-item">+{len(phones)-3} more</span>'
                    html += """
                        </div>
                    </div>
                </div>
"""
            
            html += """
            </div>
"""
        
        html += f"""
            <div class="actions">
                <button class="merge-btn" onclick="makeDecision('merge', {i})">
                    ✓ MERGE CONTACTS
                </button>
                <button class="separate-btn" onclick="makeDecision('separate', {i})">
                    ✗ KEEP SEPARATE
                </button>
            </div>
        </div>
"""
    
    html += """
        </div>
    </div>
    
    <div id="status" class="status">
        0 decisions made
    </div>

    <script>
        let decisions = {};
        let totalGroups = """ + str(len(review_groups)) + """;
        
        function makeDecision(decision, groupId) {
            decisions[groupId] = decision;
            
            const group = document.getElementById('group-' + groupId);
            group.classList.remove('decided-merge', 'decided-separate');
            group.classList.add('decided-' + decision);
            
            updateProgress();
            saveDecisions();
        }
        
        function updateProgress() {
            const completed = Object.keys(decisions).length;
            const percentage = (completed / totalGroups) * 100;
            
            document.getElementById('progress-text').textContent = 
                completed + ' of ' + totalGroups + ' completed';
            document.getElementById('progress-bar').style.width = percentage + '%';
            
            const status = document.getElementById('status');
            status.textContent = completed + ' decisions made';
            
            if (completed === totalGroups) {
                status.textContent = '✅ All decisions complete!';
                status.classList.add('completed');
            }
        }
        
        function saveDecisions() {
            // Save to localStorage for persistence
            localStorage.setItem('merge_decisions', JSON.stringify(decisions));
            
            // In a real implementation, this would save to the JSON file
            console.log('Decisions saved:', decisions);
        }
        
        // Load saved decisions on page load
        window.onload = function() {
            const saved = localStorage.getItem('merge_decisions');
            if (saved) {
                decisions = JSON.parse(saved);
                
                // Apply saved decisions to UI
                for (let groupId in decisions) {
                    const group = document.getElementById('group-' + groupId);
                    group.classList.add('decided-' + decisions[groupId]);
                }
                
                updateProgress();
            }
        };
        
        // Export decisions function
        function exportDecisions() {
            const dataStr = JSON.stringify(decisions, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'merge_decisions.json';
            link.click();
        }
    </script>
</body>
</html>
"""
    
    with open(output_path, 'w') as f:
        f.write(html)

def generate_decisions_template(review_groups, output_path):
    """Generate template JSON for decisions"""
    template = {
        "review_date": datetime.now().isoformat(),
        "total_groups": len(review_groups),
        "decisions": {},
        "instructions": "Set each group_id to either 'merge' or 'separate'"
    }
    
    for i in range(len(review_groups)):
        template["decisions"][str(i)] = "undecided"
    
    with open(output_path, 'w') as f:
        json.dump(template, f, indent=2)

def main():
    """Create interactive review for the final cleaned database"""
    
    # Use the latest cleaned database
    database_path = "data/FINAL_CLEANED_MERGED_20250606_134153.vcf"
    
    if not os.path.exists(database_path):
        print(f"Error: Database not found: {database_path}")
        return
    
    create_interactive_review(database_path)

if __name__ == "__main__":
    main()