#!/usr/bin/env python3
"""Simple test to verify Flask is working"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <html>
    <body>
        <h1>Flask is working!</h1>
        <p>If you see this, the server is running correctly.</p>
        <p><a href="/test">Test endpoint</a></p>
    </body>
    </html>
    """

@app.route('/test')
def test():
    return "Test successful!"

if __name__ == '__main__':
    print("Starting test server on http://localhost:5001")
    app.run(port=5001, debug=True)