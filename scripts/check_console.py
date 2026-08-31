#!/usr/bin/env python3
# /// script
# dependencies = [
#     "playwright",
# ]
# ///
"""Automated Console & Runtime Error Verification Suite.

Exhaustively exercises the static application across multiple viewports and
user interactions to ensure ZERO runtime exceptions, unhandled rejections,
or console errors occur.
"""

import argparse
import http.server
import socket
import socketserver
import sys
import threading
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT_DIR / "dist"


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST_DIR), **kwargs)

    def log_message(self, format, *args):
        pass


def run_console_checks(target_url: str | None = None) -> int:
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "❌ Error: playwright is required. Run with: uv run --with playwright scripts/check_console.py"
        )
        return 1

    httpd = None
    if target_url:
        base_url = target_url
    else:
        if not (DIST_DIR / "index.html").exists():
            print(f"❌ dist/index.html not found in {DIST_DIR}. Run build first.")
            return 1

        port = find_free_port()
        httpd = socketserver.TCPServer(("127.0.0.1", port), QuietHandler)
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()
        base_url = f"http://127.0.0.1:{port}/"

    console_errors: list[str] = []
    page_errors: list[str] = []
    network_errors: list[str] = []

    print("\n" + "=" * 80)
    print(f"  🛡️  AUTOMATED RUNTIME CONSOLE, NETWORK & EXCEPTION GUARD ({base_url})")
    print("=" * 80)

    def attach_listeners(page, context_label: str):
        page.on(
            "pageerror",
            lambda err: page_errors.append(f"[{context_label} PageError] {err}"),
        )
        page.on(
            "console",
            lambda msg: (
                console_errors.append(
                    f"[{context_label} Console {msg.type.upper()}] {msg.text}"
                )
                if msg.type in ["error"]
                else None
            ),
        )
        page.on(
            "response",
            lambda resp: (
                network_errors.append(
                    f"[{context_label} HTTP {resp.status}] Failed to load resource: {resp.url}"
                )
                if resp.status >= 400 and not resp.url.endswith("favicon.ico")
                else None
            ),
        )
        page.on(
            "requestfailed",
            lambda req: (
                network_errors.append(
                    f"[{context_label} RequestFailed] {req.url} - {req.failure}"
                )
                if not (
                    req.url.startswith(
                        ("mailto:", "tel:", "http://bit.ly", "https://www.youtube.com")
                    )
                    or "favicon.ico" in req.url
                )
                else None
            ),
        )

    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(executable_path="/usr/bin/chromium")
            except (PlaywrightError, OSError):
                browser = p.chromium.launch()

            # Test 1: Desktop Viewport Exhaustive Lifecycle
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            attach_listeners(page, "Desktop")

            print(
                "  ⏳ [1/8] Testing Initial Page Load (Desktop)...", end="", flush=True
            )
            page.goto(base_url, wait_until="networkidle")
            page.wait_for_timeout(1000)
            assert page.locator("#viewInteractive").is_visible(), (
                "Interactive view should be visible on load"
            )
            print(" ✓ OK")

            print("  ⏳ [2/8] Testing Theme Toggle...", end="", flush=True)
            page.evaluate("toggleTheme()")
            page.wait_for_timeout(200)
            page.evaluate("toggleTheme()")
            page.wait_for_timeout(200)
            print(" ✓ OK")

            print("  ⏳ [3/8] Testing Domain Filters...", end="", flush=True)
            for domain in [
                "graphics",
                "backend",
                "cloud",
                "ai",
                "sig",
                "all",
            ]:
                page.evaluate(f"filterByDomain('{domain}')")
                page.wait_for_timeout(150)
            print(" ✓ OK")

            print(
                "  ⏳ [4/8] Testing Smart Command Palette Search...", end="", flush=True
            )
            page.evaluate("openPalette()")
            page.wait_for_timeout(200)
            for query in ["Vulkan", "Rust", "FastAPI", "Thèse", "Compiz", "rpi"]:
                page.evaluate(f"setPaletteQuery('{query}')")
                page.wait_for_timeout(100)
            page.evaluate("closePalette()")
            page.wait_for_timeout(200)
            print(" ✓ OK")

            print(
                "  ⏳ [5/8] Testing View Switch to PDF & PDF.js Rendering...",
                end="",
                flush=True,
            )
            page.evaluate("switchMainView('doc')")
            # Wait for PDF to load and render canvas
            page.wait_for_timeout(2500)
            assert page.locator("#viewDocument").is_visible(), (
                "Document view should be visible"
            )
            print(" ✓ OK")

            print(
                "  ⏳ [6/8] Testing PDF Continuous, Dual & Single Modes Page 2...",
                end="",
                flush=True,
            )
            # Continuous mode: both canvasPage1 and canvasPage2 must be visible and rendered (> 0 width/height)
            page.evaluate("setDocMode('continuous')")
            page.wait_for_timeout(1000)
            c1_h = page.evaluate("document.getElementById('canvasPage1').height")
            c2_h = page.evaluate("document.getElementById('canvasPage2').height")
            c2_visible = page.evaluate(
                "getComputedStyle(document.getElementById('pageContainer2')).display !== 'none'"
            )
            assert c1_h > 100, f"Page 1 canvas height should be > 100, got {c1_h}"
            assert c2_h > 100, (
                f"Page 2 canvas height should be > 100 in continuous mode, got {c2_h}"
            )
            assert c2_visible, "Page 2 container must be visible in continuous mode"

            # Dual mode
            page.evaluate("setDocMode('dual')")
            page.wait_for_timeout(500)
            c2_h_dual = page.evaluate("document.getElementById('canvasPage2').height")
            assert c2_h_dual > 100, (
                f"Page 2 canvas height should be > 100 in dual mode, got {c2_h_dual}"
            )

            # Single mode page 2 navigation
            page.evaluate("setDocMode('single')")
            page.evaluate("nextDocPage()")
            page.wait_for_timeout(500)
            c2_h_single = page.evaluate("document.getElementById('canvasPage2').height")
            assert c2_h_single > 100, (
                f"Page 2 canvas height should be > 100 in single mode page 2, got {c2_h_single}"
            )

            # Zoom
            page.evaluate("zoomDoc(0.1)")
            page.wait_for_timeout(200)
            page.evaluate("zoomDoc(-0.1)")
            page.wait_for_timeout(200)
            print(
                "  ⏳ [7/9] Testing Exhaustive Click Crawler on All Interactive Elements...",
                end="",
                flush=True,
            )
            # Switch back to web view
            page.evaluate("switchMainView('web')")
            page.wait_for_timeout(200)

            # Fire click events across all interactive internal elements with safe stubs
            elem_count = page.evaluate("""() => {
                window.print = () => {};
                window.open = () => {};
                const elements = document.querySelectorAll(
                    'button, sl-button, sl-icon-button, .filter-tag, .tech-tag-item, .tech-kw'
                );
                elements.forEach(el => {
                    el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
                });
                return elements.length;
            }""")
            page.wait_for_timeout(200)

            # Close any open dialogs/modals
            page.evaluate("closeImageModal(); closeMediaModal();")
            page.wait_for_timeout(100)
            print(f" ✓ OK ({elem_count} interactive elements verified)")

            # Test 2: Mobile Viewport Initial Load & PDF Switch
            print(
                "  ⏳ [8/9] Testing Mobile Viewport (iPhone / Android)...",
                end="",
                flush=True,
            )
            mobile_page = browser.new_page(viewport={"width": 390, "height": 844})
            attach_listeners(mobile_page, "Mobile")
            mobile_page.goto(base_url, wait_until="networkidle")
            mobile_page.wait_for_timeout(1000)
            assert mobile_page.locator("#viewInteractive").is_visible(), (
                "Interactive view should be visible on mobile"
            )
            print(" ✓ OK")

            print(
                "  ⏳ [9/9] Testing Mobile PDF Switch & Rendering...",
                end="",
                flush=True,
            )
            mobile_page.evaluate("switchMainView('doc')")
            mobile_page.wait_for_timeout(2500)
            assert mobile_page.locator("#viewDocument").is_visible(), (
                "Document view should be visible on mobile"
            )
            mobile_page.close()
            print(" ✓ OK")

            browser.close()

    finally:
        if httpd:
            httpd.shutdown()

    print("=" * 80)
    all_errors = page_errors + console_errors + network_errors
    if all_errors:
        print(
            f"❌ FAILED : {len(all_errors)} runtime / console / network error(s) detected :\n"
        )
        for err in all_errors:
            print(f"  • {err}")
        print("=" * 80)
        return 1

    print(
        "🎉 SUCCESS : ZERO runtime errors, exceptions, console errors, or failed resources detected across all lifecycles!"
    )
    print("=" * 80 + "\n")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Console & Network Guard")
    parser.add_argument(
        "--url",
        dest="target_url",
        help="Target URL to test (e.g. remote preview)",
        default=None,
    )
    args, unknown = parser.parse_known_args()
    sys.exit(run_console_checks(args.target_url))
