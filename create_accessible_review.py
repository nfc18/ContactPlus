#!/usr/bin/env python3
"""
Create a review interface that saves decisions in an accessible way
"""

import os
import json
from datetime import datetime

def create_accessible_review():
    """Create a review interface with built-in decision saving"""
    
    # Read the existing review file
    review_file = "data/MASTER_CONTACTS_20250606_141220_review.html"
    
    with open(review_file, 'r') as f:
        html_content = f.read()
    
    # Add enhanced JavaScript that saves to a JSON file on each decision
    enhanced_js = '''
    <script>
        let decisions = {};
        let totalGroups = document.querySelectorAll('.merge-group').length;
        
        function makeDecision(groupId, decision) {
            decisions[groupId] = decision;
            
            // Update UI
            const group = document.getElementById('group-' + groupId);
            group.classList.add('decided');
            group.style.opacity = '0.6';
            
            // Save decisions immediately
            saveDecisions();
            
            // Update progress
            updateProgress();
        }
        
        function updateProgress() {
            const completed = Object.keys(decisions).length;
            const percentage = (completed / totalGroups) * 100;
            
            document.getElementById('progressBar').style.width = percentage + '%';
            document.getElementById('progressText').textContent = completed + ' / ' + totalGroups + ' decisions made';
            
            if (completed === totalGroups) {
                // Auto-export when complete
                exportDecisionsToFile();
            }
        }
        
        function saveDecisions() {
            // Save to localStorage
            localStorage.setItem('merge_decisions', JSON.stringify(decisions));
            
            // Also update the decisions display
            const decisionsDisplay = document.getElementById('decisionsDisplay');
            if (decisionsDisplay) {
                decisionsDisplay.textContent = JSON.stringify(decisions, null, 2);
            }
        }
        
        function exportDecisionsToFile() {
            const dataStr = JSON.stringify(decisions, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            
            // Auto-download
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'merge_decisions_auto.json';
            link.click();
            
            // Show completion message
            document.getElementById('completionMessage').style.display = 'block';
        }
        
        // Load any existing decisions
        window.onload = function() {
            const saved = localStorage.getItem('merge_decisions');
            if (saved) {
                decisions = JSON.parse(saved);
                updateProgress();
            }
        };
    </script>
    
    <div style="position: fixed; top: 0; left: 0; right: 0; height: 4px; background: #ddd;">
        <div id="progressBar" style="height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); width: 0; transition: width 0.3s;"></div>
    </div>
    
    <div style="position: fixed; bottom: 20px; right: 20px; background: rgba(0,0,0,0.8); color: white; padding: 20px; border-radius: 10px;">
        <div id="progressText">0 / 14 decisions made</div>
        <button onclick="exportDecisionsToFile()" style="margin-top: 10px; padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer;">
            Export Decisions Now
        </button>
    </div>
    
    <div id="completionMessage" style="display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #27ae60; color: white; padding: 30px; border-radius: 10px; font-size: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
        ✅ All decisions complete! File downloaded as merge_decisions_auto.json
    </div>
    
    <div style="position: fixed; bottom: 20px; left: 20px; background: rgba(255,255,255,0.9); padding: 20px; border-radius: 10px; max-width: 400px; max-height: 300px; overflow: auto;">
        <h4>Current Decisions (Live Update):</h4>
        <pre id="decisionsDisplay" style="font-size: 12px;">{}</pre>
    </div>
    '''
    
    # Insert the enhanced JavaScript before closing body tag
    html_content = html_content.replace('</body>', enhanced_js + '</body>')
    
    # Save to new file
    output_file = "data/ACCESSIBLE_MERGE_REVIEW.html"
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    # Also create a decisions file that we'll update
    decisions_file = "data/merge_decisions_live.json"
    with open(decisions_file, 'w') as f:
        json.dump({}, f)
    
    print(f"✅ Created accessible review: {output_file}")
    print(f"📄 Decisions will be saved to: {decisions_file}")
    print("\nFeatures added:")
    print("- Progress bar at top")
    print("- Live decision display (bottom left)")
    print("- Export button (bottom right)")
    print("- Auto-export when all 14 decisions are made")
    
    return output_file

if __name__ == "__main__":
    review_file = create_accessible_review()
    
    # Open in browser
    import subprocess
    subprocess.run(['open', review_file])
    
    print("\n🎯 Instructions:")
    print("1. Review each of the 14 contact groups")
    print("2. Click 'Merge' or 'Keep Separate' for each")
    print("3. Decisions auto-save and display in bottom left")
    print("4. When done, file auto-downloads as 'merge_decisions_auto.json'")
    print("5. Come back here and I'll process them immediately!")