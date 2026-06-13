import subprocess
import sys
import os
import webbrowser
import time

# Install dependencies if needed
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import http.server
    import socketserver
except:
    pass

# Open the HTML file in browser
html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")

print("🚀 Starting Expense Tracker Frontend...")
print("📂 Serving from:", os.path.dirname(html_path))
print("🌐 Opening http://localhost:3000")
print("⏹  Press Ctrl+C to stop\n")

os.chdir(os.path.dirname(html_path))

# Auto open browser after 1 second
def open_browser():
    time.sleep(1)
    webbrowser.open("http://localhost:3000")

import threading
threading.Thread(target=open_browser).start()

# Start simple HTTP server
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", 3000), Handler) as httpd:
    httpd.serve_forever()