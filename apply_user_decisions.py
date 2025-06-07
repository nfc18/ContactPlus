#!/usr/bin/env python3
"""
Apply user decisions from the exported JSON file
"""

import os
import json
import shutil
import vobject
from datetime import datetime
from process_review_decisions import DecisionProcessor

def main():
    """Apply the user's actual decisions"""
    
    # Load decisions from file
    with open('contact_decisions.json', 'r') as f:
        decisions = json.load(f)
    
    print(f"Loaded {len(decisions)} decisions from file")
    
    # Count decision types
    decision_counts = {'split': 0, 'delete': 0, 'keep': 0}
    for decision in decisions.values():
        decision_counts[decision] += 1
    
    print(f"\nDecision summary:")
    print(f"  Keep: {decision_counts['keep']}")
    print(f"  Split: {decision_counts['split']}")
    print(f"  Delete: {decision_counts['delete']}")
    
    # Process decisions
    processor = DecisionProcessor()
    processor.apply_decisions(decisions)

if __name__ == "__main__":
    main()