#!/usr/bin/env python3
"""
Open the review interface and show instructions
"""

import os
import subprocess
import glob

# Find the latest review file
review_files = glob.glob('data/SMART_CONTACT_REVIEW_*.html')
if not review_files:
    print("❌ No review file found!")
    exit(1)

latest_review = sorted(review_files)[-1]
print(f"Opening: {latest_review}")

# Open in browser
subprocess.run(['open', latest_review])

print("""
Instructions to get your decisions:
===================================

1. The review interface should now be open in your browser
2. To access the browser console:
   - Chrome/Edge: Press Cmd+Option+J (Mac) or Ctrl+Shift+J (Windows)
   - Safari: First enable Developer menu in Preferences > Advanced
     Then press Cmd+Option+C
   - Firefox: Press Cmd+Option+K (Mac) or Ctrl+Shift+K (Windows)

3. In the console, type this command:
   copy(localStorage.getItem('contact_decisions'))

4. Press Enter - this copies your decisions to clipboard

5. Come back here and run: python3 extract_decisions.py
   Then paste your decisions when prompted

Alternative: If console access is difficult, I can create a button in the interface to export decisions.
""")