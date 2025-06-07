#!/usr/bin/env python3
"""Flask web application for contact review"""

import json
import os
from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY

def load_review_queue():
    """Load review queue from JSON file"""
    if not os.path.exists(config.REVIEW_QUEUE_FILE):
        return {'items': [], 'total_items': 0}
    
    with open(config.REVIEW_QUEUE_FILE, 'r') as f:
        return json.load(f)

def load_decisions():
    """Load review decisions from JSON file"""
    if not os.path.exists(config.DECISIONS_FILE):
        return {'decisions': {}, 'stats': {'reviewed': 0, 'pending': 0}}
    
    with open(config.DECISIONS_FILE, 'r') as f:
        return json.load(f)

def save_decisions(decisions):
    """Save review decisions to JSON file"""
    with open(config.DECISIONS_FILE, 'w') as f:
        json.dump(decisions, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    """Dashboard page"""
    queue = load_review_queue()
    decisions = load_decisions()
    
    # Calculate statistics
    total_items = queue.get('total_items', 0)
    reviewed = len(decisions.get('decisions', {}))
    pending = total_items - reviewed
    
    # Load analysis stats if available
    stats_file = os.path.join(config.DATA_DIR, 'analysis_stats.json')
    analysis_stats = {}
    if os.path.exists(stats_file):
        with open(stats_file, 'r') as f:
            analysis_stats = json.load(f)
    
    return render_template('index.html', 
                         total_items=total_items,
                         reviewed=reviewed,
                         pending=pending,
                         analysis_stats=analysis_stats)

@app.route('/review')
def review():
    """Review interface"""
    queue = load_review_queue()
    decisions = load_decisions()
    
    # Find next unreviewed contact
    next_contact = None
    current_index = 0
    
    for idx, item in enumerate(queue.get('items', [])):
        if item['id'] not in decisions.get('decisions', {}):
            next_contact = item
            current_index = idx + 1
            break
    
    if not next_contact:
        return redirect(url_for('complete'))
    
    total_items = queue.get('total_items', 0)
    reviewed = len(decisions.get('decisions', {}))
    
    return render_template('review.html',
                         contact=next_contact,
                         current=current_index,
                         total=total_items,
                         reviewed=reviewed)

@app.route('/api/decision', methods=['POST'])
def save_decision():
    """Save review decision"""
    data = request.json
    contact_id = data.get('contact_id')
    action = data.get('action')
    
    if not contact_id or not action:
        return jsonify({'error': 'Missing required fields'}), 400
    
    decisions = load_decisions()
    
    # Save decision
    decisions['decisions'][contact_id] = {
        'action': action,
        'timestamp': datetime.now().isoformat(),
        'details': data.get('details', {})
    }
    
    # Update stats
    if 'stats' not in decisions:
        decisions['stats'] = {}
    decisions['stats']['reviewed'] = len(decisions['decisions'])
    decisions['stats']['last_review'] = datetime.now().isoformat()
    
    save_decisions(decisions)
    
    return jsonify({'success': True, 'reviewed': len(decisions['decisions'])})

@app.route('/complete')
def complete():
    """Review complete page"""
    decisions = load_decisions()
    reviewed = len(decisions.get('decisions', {}))
    
    # Calculate decision breakdown
    decision_counts = {}
    for decision in decisions.get('decisions', {}).values():
        action = decision['action']
        decision_counts[action] = decision_counts.get(action, 0) + 1
    
    return render_template('complete.html',
                         reviewed=reviewed,
                         decision_counts=decision_counts)

@app.route('/api/apply-changes', methods=['POST'])
def apply_changes():
    """Apply all review decisions to create new vCard"""
    # This would be implemented in Phase 1E
    return jsonify({'message': 'Changes will be applied in Phase 1E'}), 501

if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    # Check if review queue exists
    if not os.path.exists(config.REVIEW_QUEUE_FILE):
        print("⚠️  No review queue found. Please run analyze_contacts.py first!")
    else:
        print("✅ Starting web server at http://localhost:5000")
    
    app.run(debug=config.DEBUG, port=5001)