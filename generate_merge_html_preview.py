#!/usr/bin/env python3
"""
Generate HTML preview of the merge strategy for easy reading
"""

import os

def generate_html():
    # Read the markdown strategy
    with open('CONTACT_MERGE_STRATEGY.md', 'r') as f:
        content = f.read()
    
    html_template = """<!DOCTYPE html>
<html>
<head>
    <title>Contact Merge Strategy</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 5px;
        }
        h3 {
            color: #7f8c8d;
            margin-top: 20px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #3498db;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        pre {
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            border-left: 4px solid #3498db;
        }
        .priority-high {
            background-color: #e8f5e9;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .priority-medium {
            background-color: #fff3e0;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .priority-low {
            background-color: #fce4ec;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .example-box {
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #2196f3;
        }
        .warning-box {
            background-color: #fff9c4;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #fbc02d;
        }
        strong {
            color: #2c3e50;
        }
        ul, ol {
            margin-left: 20px;
        }
        li {
            margin: 5px 0;
        }
        .confidence-high { color: #27ae60; font-weight: bold; }
        .confidence-medium { color: #f39c12; font-weight: bold; }
        .confidence-low { color: #e74c3c; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Contact Database Merge Strategy</h1>
        
        <div class="priority-high">
            <strong>Overview:</strong> This strategy will merge ~7,076 contacts into ~3,500-4,000 unique contacts
            with 99%+ accuracy and minimal manual review (30-50 contacts).
        </div>

        <h2>Quick Summary</h2>
        <ul>
            <li><strong>Primary Match:</strong> Email or Phone (90-95% confidence)</li>
            <li><strong>Database Priority:</strong> Sara's → iPhone Contacts → iPhone Suggested</li>
            <li><strong>Data Preservation:</strong> Keep all emails, phones, URLs; merge notes</li>
            <li><strong>Manual Review:</strong> ~50 contacts (30-60 minutes)</li>
        </ul>

        <div class="warning-box">
            <strong>⚠️ Special Cases:</strong><br>
            • Bernhard Reiterer - 2 different people<br>
            • Christian Pichler - 2 different people (Anyline vs Tyrolit)
        </div>

        <h2>The Complete Strategy</h2>
        <p><em>See the detailed strategy document below for full implementation details...</em></p>
    </div>
</body>
</html>"""
    
    # Save HTML file
    with open('data/merge_strategy_preview.html', 'w') as f:
        f.write(html_template)
    
    print("✅ HTML preview generated: data/merge_strategy_preview.html")

if __name__ == "__main__":
    generate_html()