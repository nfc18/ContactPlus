#!/usr/bin/env python3
"""
Create version with prominent export button at the top
"""

import glob

# Read the latest review file
review_files = glob.glob('data/SMART_CONTACT_REVIEW_*.html')
latest_review = sorted(review_files)[-1]

with open(latest_review, 'r') as f:
    html = f.read()

# Add export button in the header section, right after the stats
export_section = '''
            <div style="margin-top: 30px;">
                <button onclick="exportDecisions()" style="
                    padding: 15px 40px;
                    background: linear-gradient(135deg, #3498db, #2980b9);
                    color: white;
                    border: none;
                    border-radius: 30px;
                    cursor: pointer;
                    font-weight: bold;
                    font-size: 1.1em;
                    box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3);
                    transition: all 0.3s ease;
                ">
                    📥 EXPORT YOUR DECISIONS
                </button>
                <p style="margin-top: 10px; color: #666; font-size: 0.9em;">
                    Click to download your review decisions as JSON file
                </p>
            </div>
'''

# Find the end of stats div in header and insert the export section
html_modified = html.replace(
    '        </div>\n        </div>',
    f'        </div>{export_section}\n        </div>',
    1  # Only replace first occurrence (in header)
)

# Save to new file
output_file = latest_review.replace('.html', '_EXPORT.html')
with open(output_file, 'w') as f:
    f.write(html_modified)

print(f"✅ Created: {output_file}")

import subprocess
subprocess.run(['open', output_file])

print("""
The page is now open with a prominent blue EXPORT button at the TOP of the page,
right under the statistics. Click it to download your decisions!
""")