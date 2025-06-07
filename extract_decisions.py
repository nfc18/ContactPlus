#!/usr/bin/env python3
"""
Extract decisions from the browser localStorage
"""

print("""
To get your review decisions from the browser:

1. Open the SMART_CONTACT_REVIEW HTML file in your browser (if not already open)
2. Right-click anywhere on the page
3. Select "Inspect" or "Inspect Element"
4. Go to the "Console" tab
5. Type this command and press Enter:
   
   copy(localStorage.getItem('contact_decisions'))
   
6. This copies your decisions to clipboard
7. Paste the result here:
""")

# Wait for user to paste
print("\nPaste your decisions below (then press Enter twice):")
lines = []
while True:
    line = input()
    if line:
        lines.append(line)
    else:
        if lines:  # Only break if we have some input
            break

decisions_json = '\n'.join(lines)

# Save to file
with open('user_decisions.json', 'w') as f:
    f.write(decisions_json)

print(f"\n✅ Saved your decisions to user_decisions.json")
print("Now I can process them with the decision processor.")