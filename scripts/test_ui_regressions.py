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


def test_ui_issues():
    print("=" * 80)
    print("  🧪 RUNNING TARGETED REPRODUCTION TESTS FOR REPORTED UI ISSUES")
    print("=" * 80)

    with StaticServer() as base_url, sync_playwright() as p:
        browser = p.chromium.launch(**get_playwright_launch_args())
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
            chip_tooltip = chip_elem.get_attribute(
                "data-tooltip"
            ) or chip_elem.get_attribute("title")
            chip_href = chip_elem.get_attribute("href")
            chip_text = chip_elem.inner_text().strip()

            if not chip_tooltip:
                err = f"❌ Test 3 Failed: Contact chip [{chip_text}] lacks data-tooltip attribute"
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
                    f"    ✓ OK: [{chip_text}] (href={chip_href}) -> Clean hover & tooltip: '{chip_tooltip}'"
                )

        # Check all header interactive elements on hover: verify ZERO clipped slivers or pseudo-elements protruding past header bottom
        header_buttons = page.locator(".top-header button, .top-header a")
        header_count = header_buttons.count()
        print(
            f"    Testing all {header_count} header interactive elements for zero border overlap / zero clipping..."
        )
        for i in range(header_count):
            btn = header_buttons.nth(i)
            btn_label = (
                btn.get_attribute("aria-label")
                or btn.get_attribute("title")
                or btn.get_attribute("data-tooltip")
                or ""
            ).strip()
            btn.hover()
            page.wait_for_timeout(100)

            # Check if any pseudo-element ::after or ::before is protruding or clipped
            artifact_info = page.evaluate(
                """(el) => {
                const header = document.querySelector('.top-header');
                const headerRect = header.getBoundingClientRect();
                const btnRect = el.getBoundingClientRect();
                const after = window.getComputedStyle(el, '::after');
                if (after.content === 'none' || after.display === 'none' || after.visibility === 'hidden' || parseFloat(after.opacity) === 0) {
                    return { hasArtifact: false };
                }
                const afterHeight = parseFloat(after.height) || 0;
                const afterTop = parseFloat(after.top) || 0;
                const absBottom = btnRect.top + afterTop + afterHeight;
                // Protruding beyond header bottom
                const protrudes = absBottom > (headerRect.bottom + 1);
                // Clipped sliver (partially clipped by overflow:hidden)
                const isClippedSliver = afterHeight > 0 && afterHeight < 22;
                return {
                    hasArtifact: protrudes || isClippedSliver,
                    protrudes,
                    isClippedSliver,
                    afterHeight,
                    absBottom,
                    headerBottom: headerRect.bottom
                };
            }""",
                btn.element_handle(),
            )

            if artifact_info.get("hasArtifact"):
                err = f"❌ Test 3 Failed: Header button [{btn_label}] generated clipped sliver or overlapping pseudo-element! ({artifact_info})"
                errors.append(err)
                print(f"    {err}")
            else:
                print(f"    ✓ Header button hover & boundary OK: [{btn_label}]")

        # =========================================================================
        # ISSUE 4: Document ISO Single Page Navigation Controls & Keyboard
        # =========================================================================
        print(
            "\n  🔍 [Test 4/4] Checking Document ISO Single Page Navigation Controls (Next/Prev & Keyboard)..."
        )
        # Switch to Document ISO View and Single Page Mode to test single page pagination controls
        page.click("#tabDoc")
        page.wait_for_timeout(600)
        page.click("#btnModeSingle")
        page.wait_for_timeout(600)

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

        # =========================================================================
        # ISSUE 5: Filter Toggle & Shift+Click Multi-Selection (Domain & Tech)
        # =========================================================================
        print(
            "\n  🔍 [Test 5/5] Checking Filter Toggle & Shift+Click Multi-Selection..."
        )
        # Switch to Web Interactive view
        page.click("#tabWeb")
        page.wait_for_timeout(500)

        # 1. Click domain filter 'graphics' (1st click -> activate)
        page.click('.filter-tag[data-domain="graphics"]')
        page.wait_for_timeout(300)
        active_domains_1 = page.evaluate("Array.from(activeDomains)")
        graphics_active = page.evaluate(
            "document.querySelector('.filter-tag[data-domain=\"graphics\"]').classList.contains('active')"
        )
        if "graphics" not in active_domains_1 or not graphics_active:
            err = f"❌ Test 5 Failed: 1st click on 'graphics' filter did not activate it (active={active_domains_1})"
            errors.append(err)
            print(f"    {err}")
        else:
            print("    ✓ OK: 1st click on 'graphics' filter successfully activated it")

        # 2. Shift+Click on 'backend' filter -> Multi-selection (both graphics and backend active)
        page.click('.filter-tag[data-domain="backend"]', modifiers=["Shift"])
        page.wait_for_timeout(300)
        active_domains_multi = page.evaluate("Array.from(activeDomains)")
        backend_active = page.evaluate(
            "document.querySelector('.filter-tag[data-domain=\"backend\"]').classList.contains('active')"
        )
        graphics_still_active = page.evaluate(
            "document.querySelector('.filter-tag[data-domain=\"graphics\"]').classList.contains('active')"
        )
        if (
            "backend" not in active_domains_multi
            or "graphics" not in active_domains_multi
            or not (backend_active and graphics_still_active)
        ):
            err = f"❌ Test 5 Failed: Shift+Click multi-selection failed (active={active_domains_multi})"
            errors.append(err)
            print(f"    {err}")
        else:
            print(
                f"    ✓ OK: Shift+Click successfully accumulated multiple domain filters: {active_domains_multi}"
            )

        # 3. Normal click on 'Tous' -> resets to 'all'
        page.click('.filter-tag[data-domain="all"]')
        page.wait_for_timeout(300)
        active_domains_all = page.evaluate("Array.from(activeDomains)")
        if "all" not in active_domains_all:
            err = f"❌ Test 5 Failed: Clicking 'Tous' did not reset activeDomains to ['all'] (got {active_domains_all})"
            errors.append(err)
            print(f"    {err}")
        else:
            print("    ✓ OK: Clicking 'Tous' successfully reset all filters")

        # 4. Normal click toggle test: click 'graphics' then click 'graphics' again -> resets to 'all'
        page.click('.filter-tag[data-domain="graphics"]')
        page.wait_for_timeout(300)
        page.click('.filter-tag[data-domain="graphics"]')
        page.wait_for_timeout(300)
        active_domain_toggle = page.evaluate("Array.from(activeDomains)")
        if "all" not in active_domain_toggle:
            err = f"❌ Test 5 Failed: 2nd click on 'graphics' did not toggle back to 'all' (got {active_domain_toggle})"
            errors.append(err)
            print(f"    {err}")
        else:
            print(
                "    ✓ OK: 2nd click on 'graphics' successfully toggled back to 'all'"
            )

        # 5. Tech badge click and toggle
        first_tech = page.locator("#section-skills .tech-tag-item").first
        first_tech_text = (first_tech.text_content() or "").strip().lower()
        first_tech.scroll_into_view_if_needed()
        first_tech.click()
        page.wait_for_timeout(300)
        tech_active_1 = page.evaluate("Array.from(activeTechs)")
        if first_tech_text not in tech_active_1:
            err = f"❌ Test 5 Failed: 1st click on tech tag [{first_tech_text}] did not activate activeTechs (got {tech_active_1})"
            errors.append(err)
            print(f"    {err}")
        else:
            print(
                f"    ✓ OK: 1st click on tech tag [{first_tech_text}] activated filter: {tech_active_1}"
            )

        first_tech.click()
        page.wait_for_timeout(300)
        tech_active_2 = page.evaluate("Array.from(activeTechs)")
        if len(tech_active_2) != 0:
            err = f"❌ Test 5 Failed: 2nd click on tech tag [{first_tech_text}] did not clear activeTechs (got {tech_active_2})"
            errors.append(err)
            print(f"    {err}")
        else:
            print(
                f"    ✓ OK: 2nd click on tech tag [{first_tech_text}] successfully cleared activeTechs"
            )

        # =========================================================================
        # ISSUE 6: Project Card Media Gallery Buttons (switchCardMedia)
        # =========================================================================
        print(
            "\n  🔍 [Test 6/7] Checking Project Card Media Gallery Buttons (Gallery Switcher)..."
        )
        gallery_buttons = page.locator(
            ".media-gallery-thumbs button, .media-gallery-thumbs .btn"
        )
        btn_count = gallery_buttons.count()
        print(f"    Testing all {btn_count} gallery thumbnail buttons...")

        for i in range(btn_count):
            btn = gallery_buttons.nth(i)
            label = btn.inner_text().strip()
            btn.scroll_into_view_if_needed()
            btn.click()
            page.wait_for_timeout(200)
            btn_class = btn.get_attribute("class") or ""
            if "btn-primary" not in btn_class:
                err = f"❌ Test 6 Failed: Clicking gallery button [{label}] did not set class 'btn-primary' (class={btn_class})"
                errors.append(err)
                print(f"    {err}")
            else:
                print(f"    ✓ OK: Gallery button [{label}] activated successfully")

        # =========================================================================
        # ISSUE 7: Image Lightbox Multi-Resource Gallery & Keyboard Navigation
        # =========================================================================
        print(
            "\n  🔍 [Test 7/7] Checking Image Lightbox Multi-Resource Gallery & Keyboard Navigation..."
        )
        # Open Lightbox on suckless-odin card (#media-main-1)
        odin_main = page.locator("#media-main-1")
        odin_main.scroll_into_view_if_needed()
        odin_main.click()
        page.wait_for_timeout(300)

        # Check Lightbox opened
        lightbox_open = page.evaluate(
            "document.getElementById('imageModalDialog').open"
        )
        if not lightbox_open:
            err = "❌ Test 7 Failed: Lightbox #imageModalDialog did not open on click"
            errors.append(err)
            print(f"    {err}")
        else:
            print("    ✓ OK: Lightbox dialog opened successfully")

        # Check initial image
        img_src_1 = page.locator("#imageModalImg").get_attribute("src") or ""
        caption_1 = page.locator("#imageModalCaption").inner_text()
        print(f"    Lightbox Item 1: [{img_src_1}], caption='{caption_1}'")

        # Test Keyboard ArrowRight navigation
        page.keyboard.press("ArrowRight")
        page.wait_for_timeout(250)
        img_src_2 = page.locator("#imageModalImg").get_attribute("src") or ""
        caption_2 = page.locator("#imageModalCaption").inner_text()
        print(f"    Lightbox Item 2: [{img_src_2}], caption='{caption_2}'")

        if img_src_1 == img_src_2 or "2" not in caption_2:
            err = f"❌ Test 7 Failed: Pressing ArrowRight did not navigate to Image 2 (src1={img_src_1}, src2={img_src_2})"
            errors.append(err)
            print(f"    {err}")
        else:
            print("    ✓ OK: Keyboard ArrowRight navigated to Image 2 in gallery")

        # Test Prev Button click
        page.locator("#lightboxPrevBtn").click()
        page.wait_for_timeout(250)
        img_src_back = page.locator("#imageModalImg").get_attribute("src") or ""
        if img_src_back != img_src_1:
            err = f"❌ Test 7 Failed: Clicking #lightboxPrevBtn did not return to Image 1 (got {img_src_back})"
            errors.append(err)
            print(f"    {err}")
        else:
            print("    ✓ OK: Clicking #lightboxPrevBtn returned to Image 1 in gallery")

        # Check body overflow is locked when open
        body_overflow_open = page.evaluate("document.body.style.overflow")
        if body_overflow_open != "hidden":
            err = f"❌ Test 7 Failed: document.body.style.overflow is '{body_overflow_open}', expected 'hidden' when lightbox is open"
            errors.append(err)
            print(f"    {err}")
        else:
            print(
                "    ✓ OK: document.body.style.overflow is 'hidden' while Lightbox is open"
            )

        # Test Escape to close
        page.keyboard.press("Escape")
        page.wait_for_timeout(250)
        lightbox_closed = page.evaluate(
            "!document.getElementById('imageModalDialog').open"
        )
        body_overflow_closed = page.evaluate("document.body.style.overflow")
        if not lightbox_closed or body_overflow_closed != "":
            err = f"❌ Test 7 Failed: Escape close issue (open={not lightbox_closed}, body.overflow='{body_overflow_closed}')"
            errors.append(err)
            print(f"    {err}")
        else:
            print(
                "    ✓ OK: Pressing Escape closed Lightbox and restored body scroll (overflow='')"
            )

        # Test Backdrop Click & scroll restoration
        odin_main.click()
        page.wait_for_timeout(250)
        # Click on dialog backdrop (top-left outside the dialog box)
        page.mouse.click(10, 10)
        page.wait_for_timeout(250)
        lightbox_backdrop_closed = page.evaluate(
            "!document.getElementById('imageModalDialog').open"
        )
        body_overflow_backdrop = page.evaluate("document.body.style.overflow")
        if not lightbox_backdrop_closed or body_overflow_backdrop != "":
            err = f"❌ Test 7 Failed: Backdrop click close issue (open={not lightbox_backdrop_closed}, body.overflow='{body_overflow_backdrop}')"
            errors.append(err)
            print(f"    {err}")
        # =========================================================================
        # ISSUE 8: Interactive PDF Document Hyperlinks & Annotation Layer Verification
        # =========================================================================
        print(
            "\n  🔍 [Test 8] Checking Document ISO view interactive hyperlinks & annotation layer..."
        )
        page.evaluate("switchMainView('doc')")
        page.evaluate("setDocMode('dual')")
        page.wait_for_timeout(1500)

        links1 = page.locator("#annotationLayer1 a.pdf-link").all()
        links2 = page.locator("#annotationLayer2 a.pdf-link").all()

        if len(links1) == 0 or len(links2) == 0:
            err = f"❌ Test 8 Failed: Annotation layers missing links (Page 1: {len(links1)}, Page 2: {len(links2)})"
            errors.append(err)
            print(f"    {err}")
        else:
            print(
                f"    ✓ OK: Found {len(links1)} interactive links on Page 1 and {len(links2)} on Page 2"
            )

            # Check specific links (LI3DS and FOSS4G)
            li3ds = page.locator("#annotationLayer2 a.pdf-link[href*='LI3DS']").first
            foss4g = page.locator("#annotationLayer2 a.pdf-link[href*='foss4g']").first

            if not li3ds.is_visible() or not foss4g.is_visible():
                err = "❌ Test 8 Failed: Target hyperlinks (LI3DS or FOSS4G) not visible in annotationLayer"
                errors.append(err)
                print(f"    {err}")
            else:
                print(
                    f"    ✓ OK: Verified live target hyperlinks: LI3DS ({li3ds.get_attribute('href')}) and FOSS4G ({foss4g.get_attribute('href')})"
                )

        # =========================================================================
        # ISSUE 9: Collapsible Sections & Keyboard / Click Toggle Verification
        # =========================================================================
        print("\n  🔍 [Test 9] Checking Interactive Web View collapsible sections...")
        page.evaluate("switchMainView('web')")
        page.wait_for_timeout(300)

        # Test collapse / expand on Experiences section
        exp_btn = page.locator(
            "button.section-collapse-btn[aria-controls='section-experiences']"
        )
        exp_content = page.locator("#section-experiences")

        assert exp_btn.get_attribute("aria-expanded") == "true"
        assert exp_content.is_visible()

        # Click to collapse
        exp_btn.click()
        page.wait_for_timeout(200)
        assert exp_btn.get_attribute("aria-expanded") == "false"
        assert not exp_content.is_visible()
        print(
            "    ✓ OK: Clicking section button collapsed Experiences timeline (aria-expanded='false')"
        )

        # Click to expand
        exp_btn.click()
        page.wait_for_timeout(200)
        assert exp_btn.get_attribute("aria-expanded") == "true"
        assert exp_content.is_visible()
        print(
            "    ✓ OK: Clicking section button expanded Experiences timeline (aria-expanded='true')"
        )

        # Test collapseAllSections and expandAllSections
        page.evaluate("collapseAllSections()")
        page.wait_for_timeout(200)
        all_collapsed = page.evaluate("""() => {
            const ids = ['section-experiences', 'section-projects', 'section-skills', 'section-education'];
            return ids.every(id => document.getElementById(id).classList.contains('collapsed'));
        }""")
        assert all_collapsed, "All 4 sections must be collapsed"
        print(
            "    ✓ OK: collapseAllSections() successfully collapsed all 4 portfolio sections"
        )

        page.evaluate("expandAllSections()")
        page.wait_for_timeout(200)
        all_expanded = page.evaluate("""() => {
            const ids = ['section-experiences', 'section-projects', 'section-skills', 'section-education'];
            return ids.every(id => !document.getElementById(id).classList.contains('collapsed'));
        }""")
        assert all_expanded, "All 4 sections must be expanded"
        print(
            "    ✓ OK: expandAllSections() successfully expanded all 4 portfolio sections"
        )

        # Test reload persistence (F5 / Ctrl+R)
        page.locator(
            "button.section-collapse-btn[aria-controls='section-experiences']"
        ).click()
        page.locator(
            "button.section-collapse-btn[aria-controls='section-skills']"
        ).click()
        page.wait_for_timeout(200)

        # Reload page
        page.reload(wait_until="networkidle")
        page.wait_for_timeout(300)

        # Verify persisted state
        exp_collapsed = page.evaluate(
            "document.getElementById('section-experiences').classList.contains('collapsed')"
        )
        skills_collapsed = page.evaluate(
            "document.getElementById('section-skills').classList.contains('collapsed')"
        )
        proj_collapsed = page.evaluate(
            "document.getElementById('section-projects').classList.contains('collapsed')"
        )
        edu_collapsed = page.evaluate(
            "document.getElementById('section-education').classList.contains('collapsed')"
        )

        assert exp_collapsed and skills_collapsed, (
            "Experiences and Skills must remain collapsed after reload"
        )
        assert not proj_collapsed and not edu_collapsed, (
            "Projects and Education must remain expanded after reload"
        )
        print(
            "    ✓ OK: Section collapse states successfully persisted and restored across full page reload (F5 / Ctrl+R)"
        )

        # Restore all to expanded
        page.evaluate("expandAllSections()")

        # =========================================================================
        # ISSUE 10: Experience Card Collapsible Tags Accordion Verification
        # =========================================================================
        print("\n  🔍 [Test 10] Checking Experience Card collapsible tags accordion...")
        first_details = page.locator("#exp-letsignit .exp-tags-details").first
        first_summary = page.locator("#exp-letsignit .exp-tags-summary").first

        assert not first_details.evaluate("el => el.open"), (
            "Tags details must be closed by default"
        )
        print(
            "    ✓ OK: Experience tags accordion is collapsed by default (open=false)"
        )

        # Click summary to expand
        first_summary.click()
        page.wait_for_timeout(200)
        assert first_details.evaluate("el => el.open"), (
            "Tags details must be open after clicking summary"
        )
        print("    ✓ OK: Clicking summary expanded tags accordion (open=true)")

        # Click summary to re-collapse
        first_summary.click()
        page.wait_for_timeout(200)
        assert not first_details.evaluate("el => el.open")
        print("    ✓ OK: Clicking summary re-collapsed tags accordion")

        # Test auto-expansion on tech filter click
        page.evaluate("filterByTech('Python 3.13')")
        page.wait_for_timeout(200)
        assert first_details.evaluate("el => el.open"), (
            "Filtering by 'Python 3.13' must auto-expand matching tags accordion"
        )
        print(
            "    ✓ OK: filterByTech('Python 3.13') successfully auto-expanded matching card tags accordion"
        )
        # =========================================================================
        # ISSUE 11: Multi-Media Card Drag & Swipe (Red Zone) Verification
        # =========================================================================
        print(
            "\n  🔍 [Test 11] Checking Project Card Media drag and swipe (Red Zone)..."
        )
        # Scroll to rust-firework (or first multi-image card)
        media_box = page.locator("#media-main-1")
        media_box.scroll_into_view_if_needed()
        page.wait_for_timeout(200)

        # Get initial active image src
        initial_img_src = page.locator("#media-img-1").get_attribute("src")

        # Perform mouse drag left on media_box (simulate swipe left)
        box = media_box.bounding_box()
        assert box is not None, "Media box must be visible"
        center_x = box["x"] + box["width"] / 2
        center_y = box["y"] + box["height"] / 2

        page.mouse.move(center_x + 80, center_y)
        page.mouse.down()
        page.mouse.move(center_x - 80, center_y, steps=5)
        page.mouse.up()
        page.wait_for_timeout(300)

        # Verify image changed
        new_img_src = page.locator("#media-img-1").get_attribute("src")
        assert new_img_src != initial_img_src, (
            f"Image must change after drag left (was {initial_img_src}, got {new_img_src})"
        )
        print(
            "    ✓ OK: Mouse drag / swipe left on image area successfully switched to next image"
        )

        # Perform mouse drag right on media_box (simulate swipe right)
        page.mouse.move(center_x - 80, center_y)
        page.mouse.down()
        page.mouse.move(center_x + 80, center_y, steps=5)
        page.mouse.up()
        page.wait_for_timeout(300)

        # Verify no horizontal layout shift occurred on drag
        scroll_x_after_drag = page.evaluate("window.scrollX")
        assert scroll_x_after_drag == 0, (
            f"Page must not scroll horizontally during drag (window.scrollX={scroll_x_after_drag})"
        )

        # Test Prev/Next Navigation buttons (.media-card-prev, .media-card-next)
        next_btn = page.locator("#media-main-1 .media-card-next")
        prev_btn = page.locator("#media-main-1 .media-card-prev")
        assert next_btn.is_visible(timeout=1000) or next_btn.count() > 0, (
            "Next media navigation button must exist on multi-media card"
        )
        next_btn.click(force=True)
        page.wait_for_timeout(200)
        after_next_click_src = page.locator("#media-img-1").get_attribute("src")
        assert after_next_click_src != initial_img_src, (
            "Next button must cycle to next media"
        )
        print("    ✓ OK: Clicking .media-card-next successfully switched to next image")

        prev_btn.click(force=True)
        page.wait_for_timeout(200)
        after_prev_click_src = page.locator("#media-img-1").get_attribute("src")
        assert after_prev_click_src == initial_img_src, "Prev button must cycle back"
        print(
            "    ✓ OK: Clicking .media-card-prev successfully switched back to initial image"
        )

        # Test gallery thumbnail buttons and assert ZERO layout shift / ZERO expanding margin
        odin_card = page.locator("#proj-2")
        if odin_card.count() > 0:
            odin_card.scroll_into_view_if_needed()
            page.wait_for_timeout(200)
            odin_buttons = odin_card.locator(".media-gallery-thumbs button")
            btn_count = odin_buttons.count()
            for b_idx in range(btn_count):
                b = odin_buttons.nth(b_idx)
                b.click()
                page.wait_for_timeout(150)
                layout_check = page.evaluate("""() => ({
                    docScrollW: document.documentElement.scrollWidth,
                    docClientW: document.documentElement.clientWidth,
                    bodyScrollW: document.body.scrollWidth,
                    scrollX: window.scrollX
                })""")
                assert layout_check["scrollX"] == 0, (
                    f"Thumb click {b_idx} must not displace window.scrollX"
                )
                assert layout_check["docScrollW"] <= layout_check["docClientW"], (
                    f"Thumb click {b_idx} caused document horizontal overflow: {layout_check}"
                )
            print(
                f"    ✓ OK: Verified {btn_count} thumbnail buttons on Odin card: ZERO layout shift, ZERO horizontal scroll"
            )

        # =========================================================================
        # ISSUE 12: Lightbox Preserves Selected / Slid Gallery Clipart (TDD)
        # =========================================================================
        print(
            "\n  🔍 [Test 12] Checking Lightbox opens on currently selected clipart after slide..."
        )
        fw_card = page.locator("#proj-4")
        fw_card.scroll_into_view_if_needed()
        page.wait_for_timeout(200)

        # Select 3rd clipart (index 2: "Lumières Volumétriques GPU")
        fw_thumbs = fw_card.locator(".media-gallery-thumbs button")
        assert fw_thumbs.count() >= 3, (
            "rust-firework must have at least 3 gallery cliparts"
        )
        third_thumb = fw_thumbs.nth(2)
        third_label = (third_thumb.text_content() or "").strip()
        third_thumb.click()
        page.wait_for_timeout(200)

        # Ensure 3rd button is active on card
        assert "btn-primary" in (third_thumb.get_attribute("class") or ""), (
            "3rd thumbnail button must be active (btn-primary)"
        )

        # Click main media image to open fullscreen lightbox
        media_main = fw_card.locator("#media-main-4")
        media_main.click()
        page.wait_for_timeout(300)

        # Check lightbox dialog is open
        assert page.evaluate("document.getElementById('imageModalDialog').open"), (
            "Lightbox must be open"
        )

        # Check currentLightboxIndex is 2
        active_idx = page.evaluate("currentLightboxIndex")
        active_pill = page.locator(".lightbox-thumb-pill.active")
        active_pill_text = active_pill.inner_text() if active_pill.count() > 0 else ""
        caption_text = page.locator("#imageModalCaption").inner_text()

        print(f"    Active Lightbox Index: {active_idx} (expected 2)")
        print(f"    Active Pill Text: '{active_pill_text}' (expected '{third_label}')")
        print(f"    Caption Text: '{caption_text}'")

        if active_idx != 2:
            err = f"❌ Test 12 Failed: Lightbox opened on index {active_idx} instead of selected clipart 2 ({third_label})"
            errors.append(err)
            print(f"    {err}")
        else:
            print(
                f"    ✓ OK: Lightbox successfully opened on selected clipart (index 2: '{third_label}')"
            )

        # =========================================================================
        # ISSUE 13: Fullscreen Lightbox Drag and Swipe Navigation (TDD)
        # =========================================================================
        print(
            "\n  🔍 [Test 13] Checking Fullscreen Lightbox drag & swipe navigation..."
        )
        # Modal is currently open from Test 12. Ensure it is open.
        assert page.evaluate("document.getElementById('imageModalDialog').open"), (
            "Lightbox must still be open for Test 13"
        )

        lightbox_box = page.locator(".lightbox-image-container").bounding_box()
        assert lightbox_box is not None, "Lightbox image container must be visible"

        initial_lb_idx = page.evaluate("currentLightboxIndex")
        total_items = page.evaluate("currentLightboxGallery.length")
        assert total_items > 1, (
            f"Expected multi-image gallery in Lightbox, got {total_items}"
        )

        center_x = lightbox_box["x"] + lightbox_box["width"] / 2
        center_y = lightbox_box["y"] + lightbox_box["height"] / 2

        # Drag left: swipe left -> next image
        page.mouse.move(center_x + 100, center_y)
        page.mouse.down()
        page.mouse.move(center_x - 100, center_y, steps=5)
        page.mouse.up()
        page.wait_for_timeout(300)

        idx_after_left = page.evaluate("currentLightboxIndex")
        expected_next = (initial_lb_idx + 1) % total_items

        if idx_after_left != expected_next:
            err = f"❌ Test 13 Failed: Drag left on fullscreen Lightbox did not advance image (expected {expected_next}, got {idx_after_left})"
            errors.append(err)
            print(f"    {err}")
        else:
            print(
                f"    ✓ OK: Drag left on fullscreen Lightbox advanced image from {initial_lb_idx} to {idx_after_left}"
            )

        # Drag right: swipe right -> previous image
        page.mouse.move(center_x - 100, center_y)
        page.mouse.down()
        page.mouse.move(center_x + 100, center_y, steps=5)
        page.mouse.up()
        page.wait_for_timeout(300)

        idx_after_right = page.evaluate("currentLightboxIndex")
        if idx_after_right != initial_lb_idx:
            err = f"❌ Test 13 Failed: Drag right on fullscreen Lightbox did not return to previous image (expected {initial_lb_idx}, got {idx_after_right})"
            errors.append(err)
            print(f"    {err}")
        else:
            print(
                f"    ✓ OK: Drag right on fullscreen Lightbox navigated back to image {idx_after_right}"
            )

        page.keyboard.press("Escape")
        page.wait_for_timeout(200)

        # =========================================================================
        # ISSUE 14: Smart Search Auto-Expands Collapsed Sections & Navigates (TDD)
        # =========================================================================
        print(
            "\n  🔍 [Test 14] Checking Smart Search auto-expands collapsed section and scrolls to result..."
        )
        # 1. Switch to Web view and collapse all 4 sections
        page.evaluate("switchMainView('web')")
        page.evaluate("collapseAllSections()")
        page.wait_for_timeout(200)

        # Verify all sections are collapsed
        sections_state = page.evaluate("""() => ({
            exp: document.getElementById('section-experiences').classList.contains('collapsed'),
            proj: document.getElementById('section-projects').classList.contains('collapsed'),
            skills: document.getElementById('section-skills').classList.contains('collapsed'),
            edu: document.getElementById('section-education').classList.contains('collapsed')
        })""")
        assert all(sections_state.values()), (
            f"All sections must be collapsed: {sections_state}"
        )
        print("    ✓ OK: Verified all 4 sections are initially collapsed")

        # 2. Open Smart Search Palette
        page.keyboard.press("Control+k")
        page.wait_for_timeout(200)
        assert page.evaluate("document.getElementById('cmdPaletteDialog').open"), (
            "Command Palette must be open"
        )

        # 3. Type 'ign' into search input
        search_input = page.locator("#paletteSearchInput")
        search_input.fill("ign")
        page.wait_for_timeout(300)

        # 4. Click first result (LETSIGNIT)
        first_item = page.locator("#paletteResults .palette-item").first
        first_title = first_item.locator(".palette-item-title").inner_text()
        print(f"    Clicking search result: '{first_title}'")
        first_item.click()
        page.wait_for_timeout(400)

        # 5. Verify palette is closed
        assert not page.evaluate("document.getElementById('cmdPaletteDialog').open"), (
            "Command Palette must be closed after selection"
        )

        # 6. Verify section-experiences is auto-expanded
        exp_collapsed = page.evaluate(
            "document.getElementById('section-experiences').classList.contains('collapsed')"
        )
        if exp_collapsed:
            err = "❌ Test 14 Failed: section-experiences remained collapsed after selecting experience from Smart Search"
            errors.append(err)
            print(f"    {err}")
        else:
            print(
                "    ✓ OK: section-experiences was automatically expanded upon selecting search result"
            )

        # 7. Verify target element is visible in layout
        target_card = page.locator("#exp-letsignit")
        target_box = target_card.bounding_box()
        if target_box is None or target_box["height"] == 0:
            err = "❌ Test 14 Failed: Selected item #exp-letsignit is not visible in DOM layout"
            errors.append(err)
            print(f"    {err}")
        else:
            print(
                f"    ✓ OK: Target item #exp-letsignit is visible and rendered (h={target_box['height']}px, y={target_box['y']}px)"
            )

        # =========================================================================
        # ISSUE 15: Zero Header Overlap / Zero Clipping Artifacts Across Viewports & Themes (TDD & Regression Lock)
        # =========================================================================
        print(
            "\n  🔍 [Test 15] Comprehensive Header Boundary & Overlap Regression Lock (Themes, Focus, Hover, Viewports)..."
        )
        # Reset scroll to top
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(200)

        viewports_to_test = [
            {"width": 1440, "height": 900, "name": "Desktop (1440x900)"},
            {"width": 768, "height": 1024, "name": "Tablet (768x1024)"},
            {"width": 375, "height": 812, "name": "Mobile (375x812)"},
        ]

        for vp in viewports_to_test:
            page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
            page.wait_for_timeout(150)

            # Test both light and dark themes
            for theme in ["light", "dark"]:
                page.evaluate(f"applyTheme('{theme}')")
                page.wait_for_timeout(100)

                # Header geometry check
                header_check = page.evaluate("""() => {
                    const header = document.querySelector('.top-header');
                    if (!header) return { exists: false };
                    const headerRect = header.getBoundingClientRect();
                    const style = window.getComputedStyle(header);

                    // Verify header buttons & links
                    const buttons = Array.from(header.querySelectorAll('button, a'));
                    const badElements = [];

                    for (const el of buttons) {
                        const r = el.getBoundingClientRect();
                        const pseudoAfter = window.getComputedStyle(el, '::after');
                        const pseudoBefore = window.getComputedStyle(el, '::before');

                        const afterHasContent = pseudoAfter.content !== 'none' && pseudoAfter.display !== 'none';
                        const beforeHasContent = pseudoBefore.content !== 'none' && pseudoBefore.display !== 'none';

                        // Protrusion of button itself beyond header bottom
                        const protrudes = r.bottom > (headerRect.bottom + 1);

                        if (afterHasContent || beforeHasContent || protrudes) {
                            badElements.push({
                                tag: el.tagName,
                                id: el.id,
                                class: el.className,
                                afterHasContent,
                                beforeHasContent,
                                protrudes,
                                rBottom: r.bottom,
                                headerBottom: headerRect.bottom
                            });
                        }
                    }

                    return {
                        exists: true,
                        overflow: style.overflow,
                        contain: style.contain,
                        headerBottom: headerRect.bottom,
                        badElements
                    };
                }""")

                if not header_check.get("exists"):
                    err = f"❌ Test 15 Failed: .top-header not found in {vp['name']} ({theme})"
                    errors.append(err)
                    print(f"    {err}")
                    continue

                if header_check.get("badElements"):
                    err = f"❌ Test 15 Failed: Protruding elements or pseudo-tooltips found in {vp['name']} ({theme}): {header_check['badElements']}"
                    errors.append(err)
                    print(f"    {err}")
                else:
                    print(
                        f"    ✓ OK: {vp['name']} [{theme}] -> Clean header boundaries, zero pseudo-element tooltips"
                    )

                # Test hovering and focusing each button to ensure no transient clipped sliver appears
                for btn_sel in [
                    "#btn-iso-pdf",
                    "#btn-web-app",
                    "#search-trigger",
                    "#theme-toggle",
                    "#btn-print",
                ]:
                    loc = page.locator(btn_sel)
                    if loc.count() > 0 and loc.is_visible():
                        loc.hover()
                        page.wait_for_timeout(50)

                        # Verify point directly beneath header bottom has no header elements
                        overlap_detected = page.evaluate("""() => {
                            const header = document.querySelector('.top-header');
                            const hRect = header.getBoundingClientRect();
                            const sampleY = hRect.bottom + 2;
                            // Sample 5 points across header width
                            const sampleXs = [0.1, 0.3, 0.5, 0.7, 0.9].map(f => hRect.left + f * hRect.width);
                            for (const x of sampleXs) {
                                const topEl = document.elementFromPoint(x, sampleY);
                                if (topEl && header.contains(topEl)) {
                                    return { overlapped: true, tag: topEl.tagName, className: topEl.className, x, sampleY };
                                }
                            }
                            return { overlapped: false };
                        }""")

                        if overlap_detected.get("overlapped"):
                            err = f"❌ Test 15 Failed: Hover on {btn_sel} in {vp['name']} caused element to overlap boundary: {overlap_detected}"
                            errors.append(err)
                            print(f"    {err}")

        # Reset back to desktop and light theme
        page.set_viewport_size({"width": 1440, "height": 900})
        page.evaluate("applyTheme('light')")
        page.wait_for_timeout(100)
        print(
            "    ✓ OK: Comprehensive header boundary and overlap tests completed with zero regressions"
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
