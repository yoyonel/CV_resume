#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""Instant Public Staging Tunnel for testing local dev with third-party remote services (PageSpeed Insights, WebPageTest, etc.)."""

import argparse
import http.server
import re
import socketserver
import subprocess
import sys
import threading
import time
import urllib.parse
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


def find_free_port(preferred: int = 8008) -> int:
    import socket

    for port in [preferred, 8009, 8010, 8080, 8888, 0]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return s.getsockname()[1]
            except OSError:
                continue
    return preferred


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress HTTP request access logs to keep terminal clean


def start_http_server(directory: Path, port: int):
    handler = lambda *args, **kwargs: QuietHandler(
        *args, directory=str(directory), **kwargs
    )
    with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
        httpd.serve_forever()


def main():
    parser = argparse.ArgumentParser(
        description="Expose local dist build via Cloudflare Quick Tunnel for remote PageSpeed/Lighthouse audits."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8008,
        help="Local port to serve dist/ on (default: 8008)",
    )
    parser.add_argument(
        "--no-build", action="store_true", help="Skip rebuilding dist/ before serving"
    )
    args = parser.parse_args()

    dist_dir = ROOT_DIR / "dist"
    if not args.no_build or not (dist_dir / "index.html").exists():
        print("🔨 Building static site into dist/ ...")
        build_res = subprocess.run(
            ["uv", "run", str(ROOT_DIR / "scripts" / "build_site.py")], check=True
        )
        if build_res.returncode != 0:
            print("❌ Build failed.")
            sys.exit(1)

    port = find_free_port(args.port)
    server_thread = threading.Thread(
        target=start_http_server, args=(dist_dir, port), daemon=True
    )
    server_thread.start()
    print(f"📦 Local server listening on: http://127.0.0.1:{port}/", flush=True)

    # Start Cloudflare Quick Tunnel
    print("🌐 Creating Cloudflare Quick Tunnel (no account required)...", flush=True)
    try:
        proc = subprocess.Popen(
            ["cloudflared", "tunnel", "--url", f"http://127.0.0.1:{port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except FileNotFoundError:
        print(
            "❌ Error: cloudflared not found. Install it with: curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o ~/.local/bin/cloudflared && chmod +x ~/.local/bin/cloudflared"
        )
        sys.exit(1)

    public_url = None
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

    start_time = time.time()
    while time.time() - start_time < 20:
        if proc.poll() is not None:
            print("❌ cloudflared process terminated unexpectedly.")
            sys.exit(1)
        line = proc.stdout.readline() if proc.stdout else ""
        if line:
            match = url_pattern.search(line)
            if match:
                public_url = match.group(0)
                break
        time.sleep(0.1)

    if not public_url:
        print("❌ Could not obtain public tunnel URL from cloudflared output.")
        proc.terminate()
        sys.exit(1)

    encoded_url = urllib.parse.quote_plus(public_url + "/")
    pagespeed_url = f"https://pagespeed.web.dev/analysis?url={encoded_url}"
    webpagetest_url = f"https://www.webpagetest.org/?url={encoded_url}"

    print("\n" + "=" * 80, flush=True)
    print(
        "  🚀 INSTANT DEV STAGING TUNNEL ACTIVE (Cloudflare Quick Tunnel)", flush=True
    )
    print("=" * 80, flush=True)
    print(f"  🔗 Public Staging URL : {public_url}/", flush=True)
    print(
        "--------------------------------------------------------------------------------",
        flush=True,
    )
    print(
        "  📊 Test with Google PageSpeed Insights (Tiers Remote Google Cloud) :",
        flush=True,
    )
    print(f"     👉 {pagespeed_url}", flush=True)
    print(
        "--------------------------------------------------------------------------------",
        flush=True,
    )
    print("  📱 Test with WebPageTest (Vrais smartphones physiques) :", flush=True)
    print(f"     👉 {webpagetest_url}", flush=True)
    print("=" * 80, flush=True)
    print(
        "\nTunnel actif. Appuyez sur [Ctrl + C] pour fermer le tunnel et arrêter le serveur.\n",
        flush=True,
    )

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du tunnel et du serveur local...")
        proc.terminate()
        proc.wait(timeout=3)
        print("✓ Tunnel fermé proprement.")


if __name__ == "__main__":
    main()
