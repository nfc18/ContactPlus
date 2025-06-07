#!/usr/bin/env python3
"""Simple Flask app for testing"""

from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Contact Cleaner - Test</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1>Contact Cleaner is Working!</h1>
        <p>Flask server is running correctly.</p>
        <div class="alert alert-info">
            <strong>Debug Info:</strong><br>
            Working Directory: ''' + os.getcwd() + '''<br>
            Review Queue Exists: ''' + str(os.path.exists('data/review_queue.json')) + '''<br>
            Templates Directory: ''' + str(os.path.exists('templates')) + '''
        </div>
        <a href="/main" class="btn btn-primary">Go to Main App</a>
    </div>
</body>
</html>
'''

@app.route('/main')
def main():
    # Import and use the main app
    from app import index as main_index
    return main_index()

if __name__ == '__main__':
    print("Starting simple test server...")
    print(f"Working directory: {os.getcwd()}")
    print(f"Templates exist: {os.path.exists('templates')}")
    print(f"Data exists: {os.path.exists('data/review_queue.json')}")
    app.run(debug=True, port=5000)