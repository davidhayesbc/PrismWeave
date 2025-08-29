#!/usr/bin/env python3
"""
Simple Enhanced PrismWeave Bookmarklet Development Server
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

def main():
    port = 8081
    server_dir = Path(__file__).parent
    
    print("🌟 Enhanced PrismWeave Bookmarklet Generator")
    print("=" * 50)
    print(f"📁 Serving from: {server_dir}")
    print(f"🌐 Starting server on port {port}...")
    
    os.chdir(server_dir)
    
    try:
        with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
            print(f"✅ Server running on http://localhost:{port}")
            print(f"🎯 Enhanced generator: http://localhost:{port}/enhanced-local-generator.html")
            print("\n🚀 Features:")
            print("   • Enhanced with browser extension extraction logic")
            print("   • Advanced content detection and scoring")
            print("   • Professional HTML-to-Markdown conversion")
            print("   • Comprehensive metadata extraction")
            print("   • Content cleaning and validation")
            print("\n⏹️  Press Ctrl+C to stop")
            
            # Auto-open browser
            try:
                webbrowser.open(f'http://localhost:{port}/enhanced-local-generator.html')
                print("🌟 Browser opened automatically")
            except Exception:
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