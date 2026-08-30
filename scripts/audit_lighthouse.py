#!/usr/bin/env python3
"""Automated Lighthouse audit runner for local preview and production endpoints."""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


def run_local_server(directory: Path, port: int = 8008) -> tuple[HTTPServer, Thread]:
    handler = lambda *args, **kwargs: QuietHandler(
        *args, directory=str(directory), **kwargs
    )
    server = HTTPServer(("127.0.0.1", port), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def audit_url(url: str, mode: str, output_path: str) -> dict:
    cmd = [
        "lighthouse",
        url,
        "--output",
        "json",
        "--output-path",
        output_path,
        '--chrome-flags="--headless --no-sandbox"',
    ]
    if mode == "mobile":
        cmd.extend(
            [
                "--form-factor=mobile",
                "--screenEmulation.mobile",
                "--throttling-method=simulate",
            ]
        )
    else:
        cmd.append("--preset=desktop")

    subprocess.run(" ".join(cmd), shell=True, check=True, capture_output=True)
    with open(output_path, "r", encoding="utf-8") as f:
        return json.load(f)


def print_report_card(data: dict, title: str) -> None:
    categories = data.get("categories", {})
    audits = data.get("audits", {})

    print("\n========================================================")
    print(f"  📊 LIGHTHOUSE AUDIT REPORT : {title}")
    print("========================================================")

    for cat_key in ["performance", "accessibility", "best-practices", "seo"]:
        if cat_key in categories:
            cat = categories[cat_key]
            score = round(cat.get("score", 0) * 100)
            badge = "🟢" if score >= 90 else "🟡" if score >= 50 else "🔴"
            print(f"  {badge} {cat.get('title', cat_key):<22} : {score:>3}/100")

    print("--------------------------------------------------------")
    print("  Core Web Vitals & Key Metrics :")
    metrics = [
        ("first-contentful-paint", "First Contentful Paint (FCP)"),
        ("largest-contentful-paint", "Largest Contentful Paint (LCP)"),
        ("total-blocking-time", "Total Blocking Time (TBT)"),
        ("cumulative-layout-shift", "Cumulative Layout Shift (CLS)"),
        ("speed-index", "Speed Index"),
    ]
    for key, label in metrics:
        if key in audits:
            val = audits[key].get("displayValue", "N/A")
            print(f"    • {label:<32}: {val}")
    print("========================================================\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Lighthouse audits against local or remote endpoints."
    )
    parser.add_argument(
        "--url",
        default="https://yoyonel.github.io/CV_resume/",
        help="Target URL to audit (default: PROD GitHub Pages)",
    )
    parser.add_argument(
        "--mode",
        choices=["all", "mobile", "desktop"],
        default="all",
        help="Audit mode (mobile, desktop, all)",
    )
    parser.add_argument(
        "--serve",
        type=str,
        default=None,
        help="Directory to serve locally before auditing",
    )
    parser.add_argument("--port", type=int, default=8008, help="Port for local server")

    args = parser.parse_args()
    server = None

    if args.serve:
        serve_path = Path(args.serve).resolve()
        if not serve_path.exists():
            print(
                f"Error: Serve directory not found at {serve_path}",
                file=sys.stderr,
            )
            sys.exit(1)
        server, _ = run_local_server(serve_path, args.port)
        url = f"http://127.0.0.1:{args.port}/"
        time.sleep(0.5)
    else:
        url = args.url

    with tempfile.TemporaryDirectory() as tmpdir:
        modes = ["mobile", "desktop"] if args.mode == "all" else [args.mode]

        try:
            for m in modes:
                report_path = os.path.join(tmpdir, f"lh_{m}.json")
                print(f"⏳ Running Lighthouse {m.upper()} audit on: {url} ...")
                report_data = audit_url(url, m, report_path)
                print_report_card(report_data, f"{url} [{m.upper()}]")
        finally:
            if server:
                server.shutdown()


if __name__ == "__main__":
    main()
