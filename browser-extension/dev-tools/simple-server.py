#!/usr/bin/env python3
"""
Simple PrismWeave Development Server
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

def main():
    port = 8081
    server_dir = Path(__file__).parent
    
    print("🌟 PrismWeave Development Server")
    print("=" * 50)
    print(f"📁 Serving from: {server_dir}")
    print(f"🌐 Starting server on port {port}...")
    
    os.chdir(server_dir)
    
    try:
        with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
            print(f"✅ Server running on http://localhost:{port}")
            print("\n🚀 Available files:")
            print("   • Development tools and utilities")
            print("   • Bookmarklet generators")
            print("   • Testing and debugging tools")
            print("\n⏹️  Press Ctrl+C to stop")
            
            # Auto-open browser to main directory
            try:
                webbrowser.open(f'http://localhost:{port}')
                print("🌟 Browser opened automatically")
            except (webbrowser.Error, OSError):
                print("💡 Please open the URL above in your browser")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use")
            print("💡 Try a different port or close other servers")
        else:
            print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()