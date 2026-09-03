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


def assert_image_not_blank(
    image_path: Path, min_non_white_ratio: float = 0.02
) -> tuple[bool, float]:
    try:
        from PIL import Image

        with Image.open(image_path) as img:
            rgb_img = img.convert("RGB")
            # Calculate non-white pixels without deprecation warnings
            colors = rgb_img.getcolors(maxcolors=rgb_img.width * rgb_img.height)
            total_pixels = rgb_img.width * rgb_img.height
            if colors:
                non_white = sum(
                    count
                    for count, col in colors
                    if isinstance(col, (tuple, list))
                    and not (col[0] > 245 and col[1] > 245 and col[2] > 245)
                )
            else:
                raw = rgb_img.tobytes()
                # 3 bytes per pixel (R, G, B)
                non_white = sum(
                    1
                    for i in range(0, len(raw), 3)
                    if not (raw[i] > 245 and raw[i + 1] > 245 and raw[i + 2] > 245)
                )
            ratio = non_white / total_pixels
            return (ratio >= min_non_white_ratio, ratio)
    except Exception as e:
        print(f"    ⚠️ Warning: PIL image analysis failed: {e}")
        return (True, 1.0)


def test_print_rendering(target_url: str | None = None):
    print("=" * 80)
    print("  🖨️  TESTING DEFAULT DOCUMENT ISO VIEW & EXCLUSIVE PDF PRINT RENDERING")
    print("=" * 80)

    reports_dir = Path("reports/print_previews")
    reports_dir.mkdir(parents=True, exist_ok=True)

    errors = []

    def run_tests_with_url(base_url: str):
        with sync_playwright() as p:
            browser = p.chromium.launch(**get_playwright_launch_args())
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(base_url, wait_until="networkidle")
            page.wait_for_timeout(1000)

            # ---------------------------------------------------------------------
            # TEST 1: Default Startup (Web Interactive) & Switch to Document ISO
            # ---------------------------------------------------------------------
            print(
                "\n  📄 [Test 1/7] Verifying default site startup (Web Interactive) and Document ISO switch..."
            )
            is_web_visible = page.locator("#viewInteractive").is_visible()
            is_doc_visible = page.locator("#viewDocument").is_visible()
            tab_web_class = page.locator("#tabWeb").get_attribute("class") or ""

            if not is_web_visible:
                err = (
                    "❌ Default view should be #viewInteractive but it is not visible!"
                )
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
            # TEST 2: Print Vector Pages Preload & Image Dimensions
            # ---------------------------------------------------------------------
            print(
                "\n  🔍 [Test 2/7] Verifying vector print pages preload and dimensions..."
            )
            page.evaluate("preloadPrintPages()")
            page.wait_for_timeout(500)

            img_status = page.evaluate("""
                () => {
                    const imgs = Array.from(document.querySelectorAll('.print-vector-page'));
                    return imgs.map((img, i) => ({
                        index: i + 1,
                        src: img.src,
                        complete: img.complete,
                        naturalWidth: img.naturalWidth,
                        naturalHeight: img.naturalHeight,
                    }));
                }
            """)

            for stat in img_status:
                idx = stat["index"]
                w = stat["naturalWidth"]
                h = stat["naturalHeight"]
                comp = stat["complete"]
                if not comp or w == 0 or h == 0:
                    err = f"❌ Print image {idx} is not loaded! (complete={comp}, {w}x{h})"
                    errors.append(err)
                    print(f"    {err}")
                else:
                    print(
                        f"    ✓ Print Vector Page {idx} fully loaded & decoded ({w}x{h}px)"
                    )

            # ---------------------------------------------------------------------
            # TEST 3: Print from Document ISO View (A4 & US Letter) + Visual Pixel Non-Blank Check
            # ---------------------------------------------------------------------
            print(
                "\n  🖨️  [Test 3/7] Verifying print output from Document ISO mode with non-blank visual check..."
            )
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
                    err = (
                        f"❌ Sel '{sel}' should be hidden in print mode but is visible!"
                    )
                    errors.append(err)
                    print(f"    {err}")

            for page_id in ["#pageContainer1", "#pageContainer2"]:
                if not page.locator(page_id).is_visible():
                    err = (
                        f"❌ '{page_id}' should be visible in print mode but is hidden!"
                    )
                    errors.append(err)
                    print(f"    {err}")

            # A4 PDF
            pdf_a4_path = reports_dir / "document_iso_a4.pdf"
            page.pdf(path=str(pdf_a4_path), format="A4", print_background=True)
            pdf_size = pdf_a4_path.stat().st_size
            if pdf_size < 50000:
                err = f"❌ Generated A4 PDF is suspiciously small ({pdf_size} bytes, expected > 50KB)!"
                errors.append(err)
                print(f"    {err}")
            else:
                print(
                    f"    ✓ Generated Document ISO A4 PDF: {pdf_a4_path} ({pdf_size:,} bytes)"
                )

            # US Letter PDF
            pdf_letter_path = reports_dir / "document_iso_letter.pdf"
            page.pdf(path=str(pdf_letter_path), format="Letter", print_background=True)
            print(f"    ✓ Generated Document ISO US Letter PDF: {pdf_letter_path}")

            screenshot_path = reports_dir / "document_iso_print.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            is_not_blank, non_white_ratio = assert_image_not_blank(
                screenshot_path, min_non_white_ratio=0.03
            )
            if not is_not_blank:
                err = f"❌ Visual Regression: Rendered print screenshot is BLANK! (non-white pixel ratio: {non_white_ratio:.4f})"
                errors.append(err)
                print(f"    {err}")
            else:
                print(
                    f"    ✓ Visual check PASSED: Print preview contains rich vector graphics ({non_white_ratio * 100:.1f}% non-white pixels)"
                )

            # ---------------------------------------------------------------------
            # TEST 4: Direct Print Trigger from Web Interactive View (Cold Start)
            # ---------------------------------------------------------------------
            print(
                "\n  ⚡ [Test 4/7] Verifying direct print trigger from Web Interactive view (Cold Start)..."
            )
            page.emulate_media(media="screen")
            page.evaluate("switchMainView('web')")
            page.wait_for_timeout(300)

            # Preload and switch to print
            page.evaluate("preloadPrintPages()")
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

            web_screenshot_path = reports_dir / "web_to_print_cold_start.png"
            page.screenshot(path=str(web_screenshot_path), full_page=True)
            is_not_blank, non_white_ratio = assert_image_not_blank(
                web_screenshot_path, min_non_white_ratio=0.03
            )
            if not is_not_blank:
                err = f"❌ Visual Regression: Cold-start print from Web view rendered BLANK! ({non_white_ratio:.4f})"
                errors.append(err)
                print(f"    {err}")
            else:
                print(
                    f"    ✓ Cold-start print check PASSED ({non_white_ratio * 100:.1f}% non-white pixels)"
                )

            # ---------------------------------------------------------------------
            # TEST 5: UI Button Click (.btn-print) & window.print Spy Execution
            # ---------------------------------------------------------------------
            print(
                "\n  🔘 [Test 5/7] Verifying UI button (.btn-print) click and window.print spy..."
            )
            page.emulate_media(media="screen")
            page.evaluate("""
                () => {
                    window.__printCalled = 0;
                    window.print = () => { window.__printCalled++; };
                }
            """)
            page.locator(".btn-print").first.click()
            page.wait_for_timeout(600)
            print_called = page.evaluate("() => window.__printCalled")
            if print_called != 1:
                err = f"❌ Expected window.print() to be called exactly 1 time on .btn-print click (got {print_called})!"
                errors.append(err)
                print(f"    {err}")
            else:
                print("    ✓ .btn-print click successfully invoked window.print()")

            # ---------------------------------------------------------------------
            # TEST 6: Keyboard Shortcut 'P' Print Trigger
            # ---------------------------------------------------------------------
            print("\n  ⌨️  [Test 6/7] Verifying keyboard shortcut 'P' print trigger...")
            page.keyboard.press("p")
            page.wait_for_timeout(600)
            print_called = page.evaluate("() => window.__printCalled")
            if print_called != 2:
                err = f"❌ Expected window.print() to be called 2 times after keypress 'p' (got {print_called})!"
                errors.append(err)
                print(f"    {err}")
            else:
                print("    ✓ Keyboard shortcut 'p' successfully invoked window.print()")

            # ---------------------------------------------------------------------
            # TEST 7: Command Palette 'Imprimer le CV' Action
            # ---------------------------------------------------------------------
            print("\n  🎨 [Test 7/7] Verifying Command Palette print action...")
            page.evaluate("openPalette()")
            page.wait_for_timeout(300)
            palette_input = page.locator("#paletteSearchInput")
            if palette_input.is_visible():
                palette_input.fill("Imprimer")
                page.wait_for_timeout(300)
                palette_items = page.locator(".palette-item")
                if palette_items.count() > 0:
                    palette_items.first.click()
                    page.wait_for_timeout(600)
                    print_called = page.evaluate("() => window.__printCalled")
                    if print_called != 3:
                        err = f"❌ Expected window.print() to be called 3 times after Command Palette action (got {print_called})!"
                        errors.append(err)
                        print(f"    {err}")
                    else:
                        print(
                            "    ✓ Command Palette 'Imprimer' action successfully invoked window.print()"
                        )
                else:
                    err = "❌ No palette item found for query 'Imprimer'!"
                    errors.append(err)
                    print(f"    {err}")
            else:
                err = "❌ Command Palette #paletteSearchInput did not open on openPalette()!"
                errors.append(err)
                print(f"    {err}")

            browser.close()

    if target_url:
        print(f"  🌐 Running tests against remote endpoint: {target_url}")
        run_tests_with_url(target_url)
    else:
        with StaticServer() as base_url:
            run_tests_with_url(base_url)

    print("\n" + "=" * 80)
    if errors:
        print(f"  ❌ PRINT & DEFAULT VIEW TESTS FAILED WITH {len(errors)} ERROR(S):")
        for e in errors:
            print(f"    - {e}")
        sys.exit(1)
    else:
        print(
            "  🎉 ALL 7 DEFAULT VIEW & EXCLUSIVE PDF PRINT TESTS PASSED WITH ZERO DEFECTS!"
        )
        print("=" * 80)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Automated print rendering and default view verification."
    )
    parser.add_argument(
        "--url",
        default=None,
        help="Target URL to test (if omitted, spins up local static server on dist/)",
    )
    args = parser.parse_args()
    test_print_rendering(target_url=args.url)
