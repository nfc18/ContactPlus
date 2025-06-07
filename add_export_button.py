#!/usr/bin/env python3
"""
Add an export button to the existing review interface
"""

import re

# Read the latest review file
import glob
review_files = glob.glob('data/SMART_CONTACT_REVIEW_*.html')
latest_review = sorted(review_files)[-1]

with open(latest_review, 'r') as f:
    html = f.read()

# Find the floating stats div and add export button
export_button = '''
        <button onclick="exportDecisions()" style="
            margin-top: 15px;
            width: 100%;
            padding: 10px;
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
        ">
            📥 Export Decisions
        </button>
'''

# Insert the button after the stats
pattern = r'(</div>\s*</div>\s*</div>\s*<script>)'
replacement = f'</div>{export_button}\n    </div>\n\n    <script>'

html_modified = re.sub(pattern, replacement, html)

# Save to new file
output_file = latest_review.replace('.html', '_with_export.html')
with open(output_file, 'w') as f:
    f.write(html_modified)

print(f"✅ Created: {output_file}")
print("\nOpening the modified review interface...")

import subprocess
subprocess.run(['open', output_file])

print("""
Instructions:
1. Click the blue "📥 Export Decisions" button at the bottom right
2. This will download a file called 'contact_decisions.json'
3. Move that file to this directory
4. Let me know when done, and I'll process your decisions
""")