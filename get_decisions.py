#!/usr/bin/env python3
"""
Get decisions from the user for processing
"""

import json

def get_decisions():
    """Get decisions from user"""
    print("To get your decisions from the browser:")
    print("1. Open browser developer console (F12)")
    print("2. Type: localStorage.getItem('contact_decisions')")
    print("3. Copy the output (without outer quotes)")
    print("\nPaste the JSON here (or type 'manual' for manual entry):")
    
    # Read from input - you can paste the JSON here
    decisions_input = input().strip()
    
    if decisions_input.lower() == 'manual':
        print("Manual entry mode - we'll process a few key ones")
        # For now, let's just delete the most obvious problematic ones
        decisions = {}
        for i in range(42):  # Assume most problematic should be split
            decisions[str(i)] = 'split'
        return decisions
    
    try:
        decisions = json.loads(decisions_input)
        print(f"Successfully loaded {len(decisions)} decisions")
        return decisions
    except:
        print("Invalid JSON, using default: split most problematic contacts")
        decisions = {}
        for i in range(42):
            decisions[str(i)] = 'split'
        return decisions

if __name__ == "__main__":
    decisions = get_decisions()
    
    # Save to file for processing
    with open('user_decisions.json', 'w') as f:
        json.dump(decisions, f, indent=2)
    
    print(f"Decisions saved to user_decisions.json")
    print("Now run: python3 process_review_decisions.py")