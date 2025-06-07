#!/usr/bin/env python3
"""Run the Flask app with proper settings"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == '__main__':
    print("=" * 60)
    print("Starting Contact Cleaner Web Interface")
    print("=" * 60)
    print()
    print("The server will start on port 8888")
    print()
    print("Open your browser and go to one of these URLs:")
    print("  • http://127.0.0.1:8888")
    print("  • http://localhost:8888")
    print()
    print("If Safari doesn't work, try Chrome or Firefox")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Run on all interfaces, port 8888
    app.run(host='0.0.0.0', port=8888, debug=False)