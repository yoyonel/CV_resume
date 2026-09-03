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

    res = subprocess.run(" ".join(cmd), shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Lighthouse error output:\n{res.stderr}", file=sys.stderr)
        raise RuntimeError(f"Lighthouse command failed with exit code {res.returncode}")

    with open(output_path, "r", encoding="utf-8") as f:
        return json.load(f)


def append_github_step_summary(data: dict, title: str) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    categories = data.get("categories", {})

    lines = [
        f"### 📊 Lighthouse Audit : {title}",
        "",
        "| Catégorie | Score | Statut |",
        "| :--- | :---: | :---: |",
    ]
    for cat_key in ["performance", "accessibility", "best-practices", "seo"]:
        if cat_key in categories:
            cat = categories[cat_key]
            score = round(cat.get("score", 0) * 100)
            badge = "🟢 PASS (>= 80)" if score >= 80 else "🔴 FAIL (< 80)"
            lines.append(
                f"| **{cat.get('title', cat_key)}** | **{score}/100** | {badge} |"
            )
    lines.append("")
    try:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    except Exception:
        pass


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

    failed_audits = []
    for k, v in audits.items():
        score = v.get("score")
        if (
            score is not None
            and score < 0.9
            and v.get("title")
            and k not in [m[0] for m in metrics]
        ):
            disp = f" - {v.get('displayValue')}" if v.get("displayValue") else ""
            failed_audits.append((k, v.get("title", ""), score, disp))

    lcp_elem = audits.get("largest-contentful-paint-element", {})
    lcp_items = lcp_elem.get("details", {}).get("items", [])
    if lcp_items:
        node = lcp_items[0].get("node", {})
        snippet = node.get("snippet", "")
        if snippet:
            print(f"    • LCP Element: {snippet[:80]}")

    if failed_audits:
        print("--------------------------------------------------------")
        print("  ⚠️ Opportunities & Diagnostics (< 90) :")
        for k, title, sc, disp in failed_audits:
            print(f"    • [{round(sc * 100):>2}/100] {title}{disp}")
            # Print item snippets if available
            items = audits.get(k, {}).get("details", {}).get("items", [])
            if isinstance(items, list):
                for it in items[:2]:
                    if isinstance(it, dict):
                        snip = (
                            it.get("node", {}).get("snippet")
                            or it.get("url")
                            or it.get("label")
                        )
                        if snip:
                            print(f"        -> {str(snip)[:80]}")

    print("========================================================\n")


def check_score_thresholds(
    data: dict, min_score: int, mode_label: str, target_url: str = ""
) -> list[str]:
    categories = data.get("categories", {})
    failures = []
    is_surge_preview = "surge.sh" in target_url

    for cat_key in ["performance", "accessibility", "best-practices", "seo"]:
        if cat_key in categories:
            cat = categories[cat_key]
            score = round(cat.get("score", 0) * 100)
            title = cat.get("title", cat_key)
            # Surge.sh free tier automatically injects 'X-Robots-Tag: noindex' header on previews,
            # which caps Lighthouse SEO score to ~69 due to provider header.
            cat_min = 65 if (cat_key == "seo" and is_surge_preview) else min_score
            if score < cat_min:
                failures.append(
                    f"[{mode_label}] {title}: {score}/100 (seuil minimal requis: {cat_min}/100)"
                )
    return failures


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
    parser.add_argument(
        "--min-score",
        type=int,
        default=80,
        help="Minimal score threshold for all categories (default: 80)",
    )

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

    all_failures: list[str] = []

    with tempfile.TemporaryDirectory() as tmpdir:
        modes = ["mobile", "desktop"] if args.mode == "all" else [args.mode]

        try:
            for m in modes:
                report_path = os.path.join(tmpdir, f"lh_{m}.json")
                print(f"⏳ Running Lighthouse {m.upper()} audit on: {url} ...")
                report_data = audit_url(url, m, report_path)
                print_report_card(report_data, f"{url} [{m.upper()}]")
                append_github_step_summary(report_data, f"{url} [{m.upper()}]")
                if args.min_score > 0:
                    failures = check_score_thresholds(
                        report_data, args.min_score, m.upper(), target_url=url
                    )
                    all_failures.extend(failures)
        finally:
            if server:
                server.shutdown()

    if all_failures:
        print("=" * 60)
        print("❌ LIGHTHOUSE AUDIT GATES FAILED (Scores under minimal threshold):")
        for f in all_failures:
            print(f"  • {f}")
        print("=" * 60)
        sys.exit(1)
    elif args.min_score > 0:
        print(
            f"🎉 ALL LIGHTHOUSE CATEGORIES PASSED MINIMUM THRESHOLD (>= {args.min_score}/100)!\n"
        )


if __name__ == "__main__":
    main()
