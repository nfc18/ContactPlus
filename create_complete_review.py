#!/usr/bin/env python3
"""
Create a complete review interface for all 14 groups
"""

import os

def create_complete_review():
    """Create review with all groups visible and better navigation"""
    
    # Read original review file
    with open('data/MASTER_CONTACTS_20250606_141220_review.html', 'r') as f:
        original_html = f.read()
    
    # Extract just the body content with groups
    import re
    groups_match = re.findall(r'(<div class="match-group".*?</div>\s*</div>)', original_html, re.DOTALL)
    
    print(f"Extracted {len(groups_match)} groups")
    
    # Create new enhanced HTML
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Complete Contact Merge Review - All 14 Groups</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; 
            margin: 0; 
            background: #f0f2f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px;
        }
        .progress-bar {
            background: rgba(255,255,255,0.3);
            height: 30px;
            border-radius: 15px;
            margin: 20px auto;
            max-width: 600px;
            overflow: hidden;
        }
        .progress-fill {
            background: rgba(255,255,255,0.8);
            height: 100%;
            width: 0%;
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #667eea;
        }
        .nav-buttons {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            background: white;
            padding: 15px 30px;
            border-radius: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            display: flex;
            gap: 20px;
            align-items: center;
        }
        .match-group { 
            background: white; 
            margin: 30px 0; 
            padding: 25px; 
            border-radius: 15px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }
        .match-group.decided {
            border-color: #28a745;
            opacity: 0.7;
        }
        .group-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
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
            border: 1px solid #e0e0e0; 
            margin: 10px 0; 
            padding: 15px; 
            background: #f9f9f9;
            border-radius: 8px;
        }
        .source { 
            font-weight: bold; 
            color: #007bff; 
            margin-bottom: 10px;
        }
        .field { 
            margin: 5px 0; 
            display: flex;
            align-items: flex-start;
        }
        .field-label { 
            font-weight: bold; 
            display: inline-block; 
            width: 120px;
            color: #666;
        }
        .match-reason { 
            background: #e3f2fd; 
            padding: 15px; 
            margin: 15px 0; 
            border-left: 4px solid #2196f3;
            border-radius: 4px;
        }
        .actions { 
            margin-top: 20px;
            display: flex;
            gap: 15px;
            justify-content: center;
        }
        button { 
            padding: 12px 30px; 
            cursor: pointer;
            border: none;
            border-radius: 25px;
            font-weight: bold;
            transition: all 0.3s ease;
            font-size: 1em;
        }
        .merge-btn { 
            background: linear-gradient(135deg, #28a745, #20c997); 
            color: white;
        }
        .separate-btn { 
            background: linear-gradient(135deg, #dc3545, #c82333); 
            color: white;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .decision-display {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            max-height: 400px;
            overflow-y: auto;
            min-width: 300px;
        }
        .decision-display h4 {
            margin: 0 0 15px 0;
            color: #667eea;
        }
        .export-section {
            text-align: center;
            margin: 30px 0;
        }
        .export-btn {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 30px;
            font-size: 1.1em;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3);
        }
        .quick-nav {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .nav-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(60px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }
        .nav-item {
            padding: 10px;
            text-align: center;
            background: #f0f2f5;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .nav-item:hover {
            background: #667eea;
            color: white;
        }
        .nav-item.decided {
            background: #28a745;
            color: white;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Complete Contact Merge Review</h1>
        <p>Review all 14 potential duplicate groups</p>
        <div class="progress-bar">
            <div class="progress-fill" id="progressFill">0 / 14</div>
        </div>
    </div>
    
    <div class="container">
        <div class="quick-nav">
            <h3>Quick Navigation</h3>
            <div class="nav-grid" id="navGrid">
"""
    
    # Add navigation items
    for i in range(14):
        html += f'                <div class="nav-item" id="nav-{i}" onclick="scrollToGroup({i})">#{i+1}</div>\n'
    
    html += """            </div>
        </div>
        
        <div class="export-section">
            <button class="export-btn" onclick="exportDecisions()">
                📥 Export All Decisions
            </button>
        </div>
"""
    
    # Add all groups
    for group_html in groups_match:
        html += "\n" + group_html + "\n"
    
    # Add the rest of the HTML
    html += """
    </div>
    
    <div class="nav-buttons">
        <button onclick="previousGroup()">← Previous</button>
        <span id="currentGroup">Group 1 of 14</span>
        <button onclick="nextGroup()">Next →</button>
    </div>
    
    <div class="decision-display">
        <h4>Your Decisions</h4>
        <pre id="decisionsDisplay">{}</pre>
        <div style="margin-top: 15px;">
            <strong>Progress:</strong> <span id="decisionCount">0</span> / 14
        </div>
    </div>
    
    <script>
        let decisions = {};
        let currentGroupIndex = 0;
        const totalGroups = 14;
        
        // Load existing decisions
        const existingDecisions = {"0": "separate", "1": "separate", "2": "merge", "3": "separate"};
        decisions = {...existingDecisions};
        
        function markDecision(decision, groupId) {
            decisions[groupId] = decision;
            
            // Update UI
            const group = document.getElementById('group-' + groupId);
            group.classList.add('decided');
            
            const navItem = document.getElementById('nav-' + groupId);
            navItem.classList.add('decided');
            
            updateProgress();
            saveDecisions();
            
            // Auto-advance to next undecided group
            setTimeout(() => {
                for (let i = 0; i < totalGroups; i++) {
                    if (!decisions.hasOwnProperty(i)) {
                        scrollToGroup(i);
                        break;
                    }
                }
            }, 500);
        }
        
        function updateProgress() {
            const decided = Object.keys(decisions).length;
            const percentage = (decided / totalGroups) * 100;
            
            document.getElementById('progressFill').style.width = percentage + '%';
            document.getElementById('progressFill').textContent = decided + ' / ' + totalGroups;
            document.getElementById('decisionCount').textContent = decided;
            document.getElementById('decisionsDisplay').textContent = JSON.stringify(decisions, null, 2);
            
            if (decided === totalGroups) {
                alert('All decisions complete! Click Export to download.');
                exportDecisions();
            }
        }
        
        function saveDecisions() {
            localStorage.setItem('merge_decisions_complete', JSON.stringify(decisions));
        }
        
        function exportDecisions() {
            const dataStr = JSON.stringify(decisions, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'merge_decisions_complete.json';
            link.click();
        }
        
        function scrollToGroup(index) {
            const group = document.getElementById('group-' + index);
            if (group) {
                group.scrollIntoView({ behavior: 'smooth', block: 'center' });
                currentGroupIndex = index;
                document.getElementById('currentGroup').textContent = `Group ${index + 1} of ${totalGroups}`;
            }
        }
        
        function nextGroup() {
            if (currentGroupIndex < totalGroups - 1) {
                scrollToGroup(currentGroupIndex + 1);
            }
        }
        
        function previousGroup() {
            if (currentGroupIndex > 0) {
                scrollToGroup(currentGroupIndex - 1);
            }
        }
        
        // Initialize
        window.onload = function() {
            // Apply existing decisions
            for (let id in decisions) {
                const group = document.getElementById('group-' + id);
                if (group) group.classList.add('decided');
                const navItem = document.getElementById('nav-' + id);
                if (navItem) navItem.classList.add('decided');
            }
            updateProgress();
        };
    </script>
</body>
</html>"""
    
    # Save the file
    output_file = "data/COMPLETE_MERGE_REVIEW.html"
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"✅ Created complete review with all 14 groups")
    print(f"📄 File: {output_file}")
    print("\nFeatures:")
    print("- Quick navigation grid at top (shows completed items in green)")
    print("- Previous/Next buttons at bottom")
    print("- Your 4 existing decisions are pre-loaded")
    print("- Auto-advances to next undecided group after each decision")
    print("- Export button to download when complete")
    
    return output_file

if __name__ == "__main__":
    review_file = create_complete_review()
    
    import subprocess
    subprocess.run(['open', review_file])
    
    print("\n🎯 Continue reviewing from Group #5 (you've already decided on 1-4)")
    print("The interface will auto-advance after each decision!")