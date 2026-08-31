#!/usr/bin/env python3
"""E2E Test Suite triggering reported UI issues:
1. Search trigger 'Ctrl K' badge alignment / positioning inside button.
2. Command Palette search input visibility, focus, and real-time query filtering.
3. Header & filter-bar contact chips and tooltip visibility (no clipping).
"""

import http.server
import socketserver
import sys
import threading

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


def test_ui_issues():
    print("=" * 80)
    print("  🧪 RUNNING TARGETED REPRODUCTION TESTS FOR REPORTED UI ISSUES")
    print("=" * 80)

    with StaticServer() as base_url, sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/chromium")
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto(base_url, wait_until="networkidle")
        page.wait_for_timeout(1000)

        errors = []

        # =========================================================================
        # ISSUE 1: 'Ctrl K' Badge Alignment in Search Trigger Button
        # =========================================================================
        print(
            "\n  🔍 [Test 1/3] Checking 'Ctrl K' positioning in Search Trigger Button..."
        )
        btn_box = page.locator(".search-trigger-btn").bounding_box()
        badge_locator = page.locator(
            ".search-trigger-btn .search-shortcut-badge, .search-trigger-btn kbd, .search-trigger-btn .search-shortcut-kbd"
        )

        if not badge_locator.count():
            errors.append(
                "❌ Test 1 Failed: Shortcut badge/kbd element not found inside .search-trigger-btn"
            )
            print("    ❌ FAILED: Shortcut badge not found")
        else:
            badge_box = badge_locator.first.bounding_box()
            if btn_box is None or badge_box is None:
                errors.append(
                    "❌ Test 1 Failed: Could not determine button or badge bounding box"
                )
                print("    ❌ FAILED: Bounding box is None")
            else:
                print(
                    f"    Button Box: y={btn_box['y']:.1f}, h={btn_box['height']:.1f}"
                )
                print(
                    f"    Badge Box:  y={badge_box['y']:.1f}, h={badge_box['height']:.1f}"
                )

                # The badge must be vertically aligned WITHIN the button boundaries
                is_within_v = (badge_box["y"] >= btn_box["y"] - 3) and (
                    badge_box["y"] + badge_box["height"]
                    <= btn_box["y"] + btn_box["height"] + 3
                )
                if not is_within_v:
                    diff_y = badge_box["y"] - btn_box["y"]
                    err = f"❌ Test 1 Failed: 'Ctrl K' badge is floating outside button! (y-offset from button top: {diff_y:.1f}px, expected inside button [0px .. {btn_box['height']:.1f}px])"
                    errors.append(err)
                    print(f"    {err}")
                else:
                    print("    ✓ OK: Badge is vertically centered inside button")

        # =========================================================================
        # ISSUE 2: Command Palette Search Input & Query Filtering
        # =========================================================================
        print(
            "\n  🔍 [Test 2/3] Checking Smart Search Command Palette Input & Interactive Search..."
        )
        page.click(".search-trigger-btn")
        page.wait_for_timeout(600)

        input_info = page.evaluate("""() => {
            const slInput = document.getElementById('paletteSearchInput');
            if (!slInput) return { exists: false };
            
            const rect = slInput.getBoundingClientRect();
            const style = window.getComputedStyle(slInput);
            const isCustomDefined = customElements.get(slInput.tagName.toLowerCase()) !== undefined;
            
            // Check if real native input exists (either directly or in shadow DOM)
            let nativeInput = slInput.tagName === 'INPUT' ? slInput : null;
            if (!nativeInput && slInput.shadowRoot) {
                nativeInput = slInput.shadowRoot.querySelector('input');
            }
            
            return {
                exists: true,
                tagName: slInput.tagName,
                isCustomDefined: isCustomDefined,
                display: style.display,
                width: rect.width,
                height: rect.height,
                hasNativeInput: nativeInput !== null,
                nativeInputVisible: nativeInput ? (nativeInput.getBoundingClientRect().width > 100) : false
            };
        }""")
        print(f"    Palette Input Info: {input_info}")

        if not input_info["exists"]:
            errors.append(
                "❌ Test 2 Failed: #paletteSearchInput element not found in DOM"
            )
            print("    ❌ FAILED: #paletteSearchInput element not found")
        elif input_info["tagName"] == "SL-INPUT" and not input_info["isCustomDefined"]:
            err = "❌ Test 2 Failed: <sl-input> is an unregistered HTMLUnknownElement (display: inline, width: 60px). User CANNOT see or type in search box!"
            errors.append(err)
            print(f"    {err}")
        elif (
            not input_info["hasNativeInput"]
            or input_info["width"] < 150
            or input_info["height"] < 24
        ):
            err = f"❌ Test 2 Failed: Search input is collapsed or invisible (w={input_info['width']}px, h={input_info['height']}px)"
            errors.append(err)
            print(f"    {err}")
        else:
            # Try typing a query into the palette
            page.keyboard.type("Vulkan")
            page.wait_for_timeout(300)
            results_text = page.locator("#paletteResults").inner_text()
            if "Vulkan" not in results_text and "suckless" not in results_text:
                err = f"❌ Test 2 Failed: Typing 'Vulkan' in search did not filter results. Results container: {results_text[:100]}"
                errors.append(err)
                print(f"    {err}")
            else:
                print(
                    "    ✓ OK: Search input is visible and interactive search returns filtered results"
                )

        # Close palette
        page.keyboard.press("Escape")
        page.wait_for_timeout(400)

        # =========================================================================
        # ISSUE 3: Header Contact Chips & Tooltip Clipping in .filter-bar
        # =========================================================================
        print(
            "\n  🔍 [Test 3/3] Checking Header Contact Chips & Tooltip Overflow in .filter-bar..."
        )
        filter_bar_style = page.evaluate("""() => {
            const fb = document.querySelector('.filter-bar');
            const style = window.getComputedStyle(fb);
            return {
                overflowX: style.overflowX,
                overflowY: style.overflowY,
                height: fb.clientHeight,
                scrollHeight: fb.scrollHeight
            };
        }""")
        print(f"    Filter Bar Style: {filter_bar_style}")

        # Check if contact chips text has vertical clipping
        chips_info = page.evaluate("""() => {
            const chips = Array.from(document.querySelectorAll('.contact-chip'));
            return chips.map(c => {
                const rect = c.getBoundingClientRect();
                const textSpan = c.querySelector('span');
                const textRect = textSpan ? textSpan.getBoundingClientRect() : rect;
                return {
                    text: c.innerText.trim(),
                    chipH: rect.height,
                    textH: textRect.height,
                    clipped: textRect.height > rect.height
                };
            });
        }""")
        print(f"    Contact Chips Info: {chips_info}")

        for chip in chips_info:
            if chip["clipped"]:
                err = f"❌ Test 3 Failed: Contact chip '{chip['text']}' has text clipped vertically (chipH={chip['chipH']}, textH={chip['textH']})"
                errors.append(err)
                print(f"    {err}")

        # Interactive hover test on each contact chip
        contact_chips = page.locator(".contact-chips a")
        chip_count = contact_chips.count()
        print(
            f"    Found {chip_count} contact chips to test with hover interactions..."
        )

        for i in range(chip_count):
            chip_elem = contact_chips.nth(i)
            chip_title = chip_elem.get_attribute("title")
            chip_href = chip_elem.get_attribute("href")
            chip_text = chip_elem.inner_text().strip()

            if not chip_title:
                err = f"❌ Test 3 Failed: Contact chip [{chip_text}] lacks accessible native title attribute"
                errors.append(err)
                print(f"    {err}")

            # Hover chip and check for visual artifacts / clipped popups
            chip_elem.hover()
            page.wait_for_timeout(200)

            # Detect any clipped tooltip popup or floating UI element
            has_clipped_popup = page.evaluate("""() => {
                const popups = Array.from(document.querySelectorAll('sl-popup, .tooltip, [part~="base"]'));
                for (const p of popups) {
                    const rect = p.getBoundingClientRect();
                    // Detect clipped sliver popup (like the 2px white line in reported bug)
                    if (rect.height > 0 && rect.height < 12 && rect.width > 20) {
                        return true;
                    }
                }
                return false;
            }""")

            if has_clipped_popup:
                err = f"❌ Test 3 Failed: Hovering on [{chip_text}] generated a clipped/collapsed popup sliver!"
                errors.append(err)
                print(f"    {err}")
            else:
                print(
                    f"    ✓ OK: [{chip_text}] (href={chip_href}) -> Clean hover & title: '{chip_title}'"
                )

        # =========================================================================
        # ISSUE 4: Document ISO Single Page Navigation Controls & Keyboard
        # =========================================================================
        print(
            "\n  🔍 [Test 4/4] Checking Document ISO Single Page Navigation Controls (Next/Prev & Keyboard)..."
        )
        # Switch to Document view
        page.click("#tabDoc")
        page.wait_for_timeout(1000)

        # Check that page 1 is active
        p1_active = page.evaluate(
            "document.getElementById('pageContainer1').classList.contains('active')"
        )
        p2_active = page.evaluate(
            "document.getElementById('pageContainer2').classList.contains('active')"
        )
        lbl_text = page.locator("#lblPageNum").inner_text().strip()

        if not p1_active or p2_active or "1" not in lbl_text:
            err = f"❌ Test 4 Failed: Expected Page 1 active initially. (p1={p1_active}, p2={p2_active}, label='{lbl_text}')"
            errors.append(err)
            print(f"    {err}")
        else:
            print("    ✓ OK: Page 1 active initially")

        # Click next page button
        page.click("#btnNextPage")
        page.wait_for_timeout(600)
        p1_active = page.evaluate(
            "document.getElementById('pageContainer1').classList.contains('active')"
        )
        p2_active = page.evaluate(
            "document.getElementById('pageContainer2').classList.contains('active')"
        )
        lbl_text = page.locator("#lblPageNum").inner_text().strip()

        if not p2_active or p1_active or "2" not in lbl_text:
            err = f"❌ Test 4 Failed: Clicking #btnNextPage did not navigate to Page 2! (p1={p1_active}, p2={p2_active}, label='{lbl_text}')"
            errors.append(err)
            print(f"    {err}")
        else:
            print("    ✓ OK: Clicking #btnNextPage successfully switched to Page 2 / 2")

        # Click prev page button
        page.click("#btnPrevPage")
        page.wait_for_timeout(600)
        p1_active = page.evaluate(
            "document.getElementById('pageContainer1').classList.contains('active')"
        )
        if not p1_active:
            err = "❌ Test 4 Failed: Clicking #btnPrevPage did not return to Page 1!"
            errors.append(err)
            print(f"    {err}")
        else:
            print("    ✓ OK: Clicking #btnPrevPage successfully returned to Page 1 / 2")

        # Test Keyboard ArrowRight navigation
        page.keyboard.press("ArrowRight")
        page.wait_for_timeout(600)
        p2_active = page.evaluate(
            "document.getElementById('pageContainer2').classList.contains('active')"
        )
        if not p2_active:
            err = "❌ Test 4 Failed: Pressing ArrowRight did not navigate to Page 2!"
            errors.append(err)
            print(f"    {err}")
        else:
            print(
                "    ✓ OK: Pressing ArrowRight keyboard shortcut successfully navigated to Page 2 / 2"
            )

        # Test Keyboard ArrowLeft navigation
        page.keyboard.press("ArrowLeft")
        page.wait_for_timeout(600)
        p1_active = page.evaluate(
            "document.getElementById('pageContainer1').classList.contains('active')"
        )
        if not p1_active:
            err = "❌ Test 4 Failed: Pressing ArrowLeft did not return to Page 1!"
            errors.append(err)
            print(f"    {err}")
        else:
            print(
                "    ✓ OK: Pressing ArrowLeft keyboard shortcut successfully returned to Page 1 / 2"
            )

        browser.close()

        print("\n" + "=" * 80)
        if errors:
            print(f"❌ TEST SUITE FAILED WITH {len(errors)} DETECTED REGRESSIONS:")
            for e in errors:
                print(f"  {e}")
            print("=" * 80)
            return 1
        else:
            print("🎉 ALL TESTS PASSED! ZERO UI REGRESSIONS DETECTED!")
            print("=" * 80)
            return 0


if __name__ == "__main__":
    sys.exit(test_ui_issues())
