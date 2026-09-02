#!/usr/bin/env python3
"""Automated verification of default Document ISO view and exclusive PDF print rendering."""

import http.server
import socketserver
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright


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
        browser = p.chromium.launch(executable_path="/usr/bin/chromium")
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(base_url, wait_until="networkidle")
        page.wait_for_timeout(1500)

        # ---------------------------------------------------------------------
        # TEST 1: Default Arrival on Site -> Document ISO in Double Page Mode
        # ---------------------------------------------------------------------
        print(
            "\n  📄 [Test 1/3] Verifying default site startup (Document ISO in Double Page mode)..."
        )
        is_doc_visible = page.locator("#viewDocument").is_visible()
        is_web_visible = page.locator("#viewInteractive").is_visible()
        tab_doc_class = page.locator("#tabDoc").get_attribute("class") or ""
        btn_dual_class = page.locator("#btnModeDual").get_attribute("class") or ""

        if not is_doc_visible:
            err = "❌ Default view should be #viewDocument but it is not visible!"
            errors.append(err)
            print(f"    {err}")
        else:
            print("    ✓ Default view is #viewDocument (visible)")

        if is_web_visible:
            err = "❌ #viewInteractive should be hidden by default but is visible!"
            errors.append(err)
            print(f"    {err}")
        else:
            print("    ✓ #viewInteractive is hidden by default")

        if "active" not in tab_doc_class and "btn-primary" not in tab_doc_class:
            err = f"❌ #tabDoc should have class 'active' or 'btn-primary' by default (got '{tab_doc_class}')"
            errors.append(err)
            print(f"    {err}")
        else:
            print("    ✓ #tabDoc is active ('btn-primary')")

        if "active" not in btn_dual_class and "btn-primary" not in btn_dual_class:
            err = f"❌ #btnModeDual should have class 'active' or 'btn-primary' by default (got '{btn_dual_class}')"
            errors.append(err)
            print(f"    {err}")
        else:
            print("    ✓ #btnModeDual is active ('btn-primary')")

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
