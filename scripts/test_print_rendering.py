#!/usr/bin/env python3
"""Automated verification of default Document ISO view and exclusive PDF print rendering."""

import http.server
import socketserver
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

try:
    from scripts.common import get_playwright_launch_args
except ImportError:
    from common import get_playwright_launch_args


class StaticServer:
    def __init__(self, directory: str = "dist"):
        self.directory = directory
        self.httpd = None
        self.port = None

    def __enter__(self):
        handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(
            *args, directory=self.directory, **kwargs
        )
        self.httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
        self.port = self.httpd.server_address[1]
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        return f"http://127.0.0.1:{self.port}"

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.httpd:
            self.httpd.shutdown()


def test_print_rendering():
    print("=" * 80)
    print("  🖨️  TESTING DEFAULT DOCUMENT ISO VIEW & EXCLUSIVE PDF PRINT RENDERING")
    print("=" * 80)

    reports_dir = Path("reports/print_previews")
    reports_dir.mkdir(parents=True, exist_ok=True)

    errors = []

    with StaticServer() as base_url, sync_playwright() as p:
        browser = p.chromium.launch(**get_playwright_launch_args())
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(base_url, wait_until="networkidle")
        page.wait_for_timeout(1500)

        # ---------------------------------------------------------------------
        # TEST 1: Default Startup (Web Interactive) & Switch to Document ISO
        # ---------------------------------------------------------------------
        print(
            "\n  📄 [Test 1/3] Verifying default site startup (Web Interactive) and Document ISO switch..."
        )
        is_web_visible = page.locator("#viewInteractive").is_visible()
        is_doc_visible = page.locator("#viewDocument").is_visible()
        tab_web_class = page.locator("#tabWeb").get_attribute("class") or ""

        if not is_web_visible:
            err = "❌ Default view should be #viewInteractive but it is not visible!"
            errors.append(err)
            print(f"    {err}")
        else:
            print("    ✓ Default view is #viewInteractive (visible)")

        if is_doc_visible:
            err = "❌ #viewDocument should be hidden by default but is visible!"
            errors.append(err)
            print(f"    {err}")
        else:
            print("    ✓ #viewDocument is hidden by default")

        if "active" not in tab_web_class and "btn-primary" not in tab_web_class:
            err = f"❌ #tabWeb should have class 'active' or 'btn-primary' by default (got '{tab_web_class}')"
            errors.append(err)
            print(f"    {err}")
        else:
            print("    ✓ #tabWeb is active ('btn-primary')")

        # Switch to Document ISO view
        page.locator("#tabDoc").click()
        page.wait_for_timeout(1000)
        is_doc_visible_after = page.locator("#viewDocument").is_visible()
        if not is_doc_visible_after:
            err = "❌ Clicking #tabDoc did not switch to #viewDocument!"
            errors.append(err)
            print(f"    {err}")
        else:
            print("    ✓ Switched to #viewDocument successfully")

        # ---------------------------------------------------------------------
        # TEST 2: Print from Document ISO View (A4 & US Letter)
        # ---------------------------------------------------------------------
        print("\n  🖨️  [Test 2/3] Verifying print output from Document ISO mode...")
        page.emulate_media(media="print")
        page.wait_for_timeout(500)

        hidden_selectors = [
            "header.top-header",
            ".filter-bar",
            ".doc-controls",
            ".page-tag",
            "#singlePageNav",
            "#viewDocument .hero-card",
            ".search-trigger-btn",
            "#viewInteractive",
        ]

        for sel in hidden_selectors:
            if page.locator(sel).first.is_visible():
                err = f"❌ Sel '{sel}' should be hidden in print mode but is visible!"
                errors.append(err)
                print(f"    {err}")

        for page_id in ["#pageContainer1", "#pageContainer2"]:
            if not page.locator(page_id).is_visible():
                err = f"❌ '{page_id}' should be visible in print mode but is hidden!"
                errors.append(err)
                print(f"    {err}")

        # A4 PDF
        pdf_a4_path = reports_dir / "document_iso_a4.pdf"
        page.pdf(path=str(pdf_a4_path), format="A4", print_background=True)
        print(f"    ✓ Generated Document ISO A4 PDF: {pdf_a4_path}")

        # US Letter PDF
        pdf_letter_path = reports_dir / "document_iso_letter.pdf"
        page.pdf(path=str(pdf_letter_path), format="Letter", print_background=True)
        print(f"    ✓ Generated Document ISO US Letter PDF: {pdf_letter_path}")

        screenshot_path = reports_dir / "document_iso_print.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"    ✓ Generated Print Screenshot: {screenshot_path}")

        # ---------------------------------------------------------------------
        # TEST 3: Print when triggered from Web Interactive View
        # ---------------------------------------------------------------------
        print(
            "\n  ⚡ [Test 3/3] Verifying print output when triggered from Web Interactive view..."
        )
        page.emulate_media(media="screen")
        page.evaluate("switchMainView('web')")
        page.wait_for_timeout(500)

        # Trigger print emulation
        page.emulate_media(media="print")
        page.wait_for_timeout(500)

        # In print mode, #viewInteractive must STILL be hidden and #viewDocument must be printed
        if page.locator("#viewInteractive").is_visible():
            err = "❌ #viewInteractive must be hidden in print mode even if screen was on web view!"
            errors.append(err)
            print(f"    {err}")
        else:
            print("    ✓ #viewInteractive is hidden in print mode")

        if (
            not page.locator("#pageContainer1").is_visible()
            or not page.locator("#pageContainer2").is_visible()
        ):
            err = "❌ PDF pages #pageContainer1 and #pageContainer2 must be visible in print mode!"
            errors.append(err)
            print(f"    {err}")
        else:
            print(
                "    ✓ PDF pages #pageContainer1 and #pageContainer2 are visible in print mode"
            )

        browser.close()

    print("\n" + "=" * 80)
    if errors:
        print(f"  ❌ PRINT & DEFAULT VIEW TESTS FAILED WITH {len(errors)} ERROR(S):")
        for e in errors:
            print(f"    - {e}")
        sys.exit(1)
    else:
        print(
            "  🎉 ALL DEFAULT VIEW & EXCLUSIVE PDF PRINT TESTS PASSED WITH ZERO DEFECTS!"
        )
        print("=" * 80)


if __name__ == "__main__":
    test_print_rendering()
