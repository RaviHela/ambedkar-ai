import http.server
import socketserver
import ssl

PORT = 8080

handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), handler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    print("For voice to work, use Chrome and allow microphone access")
    httpd.serve_forever()
