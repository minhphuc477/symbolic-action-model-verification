"""
UI/UX Research Dashboard Server Launcher
=========================================
Starts a local HTTP server and opens the dashboard in your default web browser.

Usage:
    python ui_ux/scripts/serve.py [--port 8080] [--no-browser]
"""

import argparse
import functools
import http.server
import os
import socketserver
import sys
import webbrowser
from pathlib import Path


def run_server(port: int = 8080, open_browser: bool = True) -> None:
    ui_dir = Path(__file__).resolve().parent.parent
    os.chdir(ui_dir)

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ui_dir))

    # Allow address reuse
    socketserver.TCPServer.allow_reuse_address = True

    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            url = f"http://localhost:{port}/index.html"
            print("=" * 72)
            print("🎨 SEARCH-TREE TOPOLOGY & SAFE CEG-OMR VISUALIZATION SUITE")
            print("=" * 72)
            print(f"[*] Dashboard directory : {ui_dir}")
            print(f"[*] Server running at   : {url}")
            print("[*] Press Ctrl+C to terminate the dashboard server.")
            print("=" * 72)

            if open_browser:
                webbrowser.open(url)

            httpd.serve_forever()
    except OSError as e:
        if "address already in use" in str(e).lower() or e.errno in (98, 10048):
            print(f"[!] Port {port} is in use. Trying port {port + 1}...")
            run_server(port=port + 1, open_browser=open_browser)
        else:
            raise e
    except KeyboardInterrupt:
        print("\n[*] Dashboard server stopped cleanly.")
        sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Serve the UI/UX Research Dashboard")
    parser.add_argument("--port", type=int, default=8080, help="HTTP port (default: 8080)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
    args = parser.parse_args()

    run_server(port=args.port, open_browser=not args.no_browser)
