#!/usr/bin/env python3
import http.server
import socketserver

PORT = 8080

Handler = http.server.SimpleHTTPRequestHandler

print(f"Starting simple HTTP server on port {PORT}")
print(f"Try accessing: http://localhost:{PORT}")
print(f"Or try: http://127.0.0.1:{PORT}")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server running... Press Ctrl+C to stop")
    httpd.serve_forever()