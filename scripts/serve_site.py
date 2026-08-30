#!/usr/bin/env python3
# /// script
# dependencies = [
#   "jinja2>=3.1.0",
#   "typst>=0.15.0",
# ]
# ///
"""Local HTTP preview server for the static Typst resume site."""

import http.server
import os
import socketserver
import sys
import threading
import time
from pathlib import Path

from build_site import build_site


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Terse log output
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")


def watch_and_rebuild(dist_dir: Path, stop_event: threading.Event):
    root_dir = Path(__file__).resolve().parent.parent
    watched_files = [
        root_dir / "data" / "profile.json",
        root_dir / "typst_resume" / "resume.typ.j2",
        root_dir / "site_template" / "index.html.j2",
        root_dir / "scripts" / "build_site.py",
    ]

    last_mtimes = {}
    for f in watched_files:
        if f.exists():
            last_mtimes[f] = f.stat().st_mtime

    while not stop_event.is_set():
        time.sleep(0.5)
        changed = False
        for f in watched_files:
            if not f.exists():
                continue
            mtime = f.stat().st_mtime
            if f not in last_mtimes or mtime > last_mtimes[f]:
                last_mtimes[f] = mtime
                changed = True
                print(f"\n[Watcher] Detected change in {f.name} -> Recompiling...")

        if changed:
            try:
                build_site(dist_dir)
                print("[Watcher] Site recompiled successfully.")
            except (RuntimeError, ValueError, OSError) as e:
                print(f"[Watcher] Error during rebuild: {e}", file=sys.stderr)


import argparse
import socket


def get_lan_ip() -> str:
    """Detects the primary LAN IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except OSError:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def serve(port: int = 8000, host: str = "127.0.0.1"):
    root_dir = Path(__file__).resolve().parent.parent
    dist_dir = root_dir / "dist"

    print("Building site before starting server...")
    build_site(dist_dir)

    os.chdir(dist_dir)

    # Find free port if requested port is taken
    actual_port = port
    for p in range(port, port + 20):
        try:
            httpd = socketserver.TCPServer((host, p), QuietHandler)
            actual_port = p
            break
        except OSError:
            continue
    else:
        print(
            f"Error: Unable to bind to any port in range {port}-{port + 20}",
            file=sys.stderr,
        )
        sys.exit(1)

    stop_event = threading.Event()
    watcher_thread = threading.Thread(
        target=watch_and_rebuild, args=(dist_dir, stop_event), daemon=True
    )
    watcher_thread.start()

    lan_ip = get_lan_ip()
    print("\n" + "=" * 58)
    print("  🚀 PREVIEW SERVER READY:")
    print(f"  👉 Local: http://localhost:{actual_port}/")
    if host in ("0.0.0.0", "::") or host != "127.0.0.1":
        print(f"  📱 LAN (Smartphone Wi-Fi): http://{lan_ip}:{actual_port}/")
    print("=" * 58)
    print("Watching for source changes (data/profile.json, typst_resume/)...")
    print("Press Ctrl+C to stop.\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping preview server...")
    finally:
        stop_event.set()
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Serve static resume site locally or on LAN"
    )
    parser.add_argument(
        "port",
        nargs="?",
        type=int,
        default=8000,
        help="Port to listen on (default: 8000)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host interface to bind to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--lan",
        action="store_true",
        help="Bind to 0.0.0.0 for LAN / smartphone testing",
    )
    args = parser.parse_args()

    host_val = "0.0.0.0" if args.lan else args.host
    serve(port=args.port, host=host_val)
