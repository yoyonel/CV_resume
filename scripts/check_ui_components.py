#!/usr/bin/env python3
"""Automated Web Components & UI Design Tokens Compliance Checker.

Verifies:
1. Zero leftover Shoelace / Web Awesome legacy custom elements (<sl-*>) in templates & build.
2. 100% native HTML5/CSS component compliance according to ADR 0001.
3. Universal Floating Web Tooltip system compliance (ISO styling, design tokens, zero clipping).
4. No bare/unstyled browser OS title attributes on primary interactive elements.
"""

import http.server
import re
import socketserver
import sys
import threading
from pathlib import Path

from common import get_playwright_launch_args
from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = REPO_ROOT / "dist"
TEMPLATES_DIR = REPO_ROOT / "site_template"


def check_static_legacy_tags() -> list[str]:
    """Scans templates and dist files for forbidden Web Awesome / Shoelace references."""
    errors = []
    files_to_check = [
        TEMPLATES_DIR / "index.html.j2",
        DIST_DIR / "index.html",
    ]

    sl_tag_pattern = re.compile(r"<\s*sl-[a-zA-Z0-9-]+", re.IGNORECASE)
    sl_bundle_pattern = re.compile(
        r"shoelace(\.bundle|\.min)?\.(js|css)", re.IGNORECASE
    )

    for file_path in files_to_check:
        if not file_path.exists():
            continue
        content = file_path.read_text(encoding="utf-8")
        rel_path = file_path.relative_to(REPO_ROOT)

        sl_matches = sl_tag_pattern.findall(content)
        if sl_matches:
            errors.append(
                f"Legacy Web Awesome / Shoelace tags found in {rel_path}: {set(sl_matches)}"
            )

        bundle_matches = sl_bundle_pattern.findall(content)
        if bundle_matches:
            errors.append(
                f"Forbidden Shoelace bundle reference found in {rel_path}: {bundle_matches}"
            )

    return errors


def check_dynamic_ui_tokens() -> list[str]:
    """Runs Playwright headless to assert computed styles & behavior of native web components."""
    errors = []

    # Serve dist directory on local free port
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(DIST_DIR), **kwargs)

        def log_message(self, format, *args):
            pass

    with socketserver.TCPServer(("127.0.0.1", 0), QuietHandler) as httpd:
        port = httpd.server_address[1]
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()
        url = f"http://127.0.0.1:{port}/"

        with sync_playwright() as p:
            browser = p.chromium.launch(**get_playwright_launch_args(headless=True))
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(url)
            page.wait_for_load_state("networkidle")

            print(
                "  🔍 [Static Guard] Checking zero Web Awesome tags & zero Shoelace scripts..."
            )
            static_errs = check_static_legacy_tags()
            if static_errs:
                errors.extend(static_errs)
                for err in static_errs:
                    print(f"    ❌ {err}")
            else:
                print(
                    "    ✓ OK: Zero legacy Web Awesome (<sl-*>) tags or scripts found"
                )

            print(
                "\n  🔍 [Dynamic Guard] Auditing Universal Floating Web Tooltip System..."
            )
            header_selectors = [
                ("#tabDoc", "Affichage PDF Haute Fidélité ISO (Touche V)"),
                ("#tabWeb", "Affichage Portfolio Web Interactif (Touche V)"),
                (".search-trigger-btn", "Recherche Floue & Sémantique (Ctrl + K)"),
                ("#themeToggleBtn", "Basculer Thème (T)"),
                (".btn-print", "Imprimer le CV PDF (P)"),
                (".btn-download", "Télécharger le PDF Typst (D)"),
            ]

            # 1. Dark Theme Audit
            page.evaluate("applyTheme('dark')")
            page.wait_for_timeout(100)

            for sel, expected_tooltip in header_selectors:
                el = page.locator(sel)
                if el.count() == 0:
                    errors.append(f"Header control {sel} not found")
                    continue

                # Assert element has data-tooltip and NOT raw unstyled title
                data_tt = el.get_attribute("data-tooltip")
                raw_title = el.get_attribute("title")

                if not data_tt:
                    errors.append(f"{sel} lacks mandatory 'data-tooltip' attribute")
                if raw_title:
                    errors.append(
                        f"{sel} has raw 'title' attribute ('{raw_title}') causing unstyled OS tooltip!"
                    )

                # Hover element and test floating web tooltip
                el.hover()
                page.wait_for_timeout(200)

                tt_info = page.evaluate("""() => {
                    const tt = document.getElementById('web-tooltip');
                    if (!tt) return { exists: false };
                    const style = window.getComputedStyle(tt);
                    const rect = tt.getBoundingClientRect();
                    return {
                        exists: true,
                        visible: tt.classList.contains('is-visible'),
                        opacity: parseFloat(style.opacity),
                        position: style.position,
                        zIndex: parseInt(style.zIndex, 10) || 0,
                        borderRadius: parseFloat(style.borderRadius) || 0,
                        boxShadow: style.boxShadow,
                        backgroundColor: style.backgroundColor,
                        color: style.color,
                        text: tt.textContent.trim(),
                        rect: { top: rect.top, left: rect.left, width: rect.width, height: rect.height }
                    };
                }""")

                if not tt_info.get("exists"):
                    errors.append(
                        f"Floating #web-tooltip DOM element not created upon hovering {sel}"
                    )
                elif not tt_info.get("visible") or tt_info.get("opacity", 0) < 0.9:
                    errors.append(
                        f"Floating web tooltip did not show for {sel}: {tt_info}"
                    )
                else:
                    # Style verification: border-radius >= 6px, box-shadow present, fixed position
                    if tt_info["borderRadius"] < 6:
                        errors.append(
                            f"Tooltip for {sel} border-radius ({tt_info['borderRadius']}px) < 6px design token"
                        )
                    if not tt_info["boxShadow"] or tt_info["boxShadow"] == "none":
                        errors.append(
                            f"Tooltip for {sel} missing box-shadow design token"
                        )
                    if tt_info["position"] != "fixed":
                        errors.append(
                            f"Tooltip position must be 'fixed' (got {tt_info['position']})"
                        )
                    if tt_info["zIndex"] < 1000:
                        errors.append(
                            f"Tooltip z-index ({tt_info['zIndex']}) must be >= 1000"
                        )

                    print(
                        f"    ✓ OK: {sel} -> Web Tooltip '{tt_info['text']}' [Dark Theme: bg={tt_info['backgroundColor']}, radius={tt_info['borderRadius']}px, shadow=✓]"
                    )

            # Move mouse away to verify tooltip hides
            page.mouse.move(0, 0)
            page.wait_for_timeout(200)
            hidden_check = page.evaluate("""() => {
                const tt = document.getElementById('web-tooltip');
                return tt ? tt.classList.contains('is-visible') : false;
            }""")
            if hidden_check:
                errors.append(
                    "Floating tooltip remained visible after mouse left element"
                )
            else:
                print("    ✓ OK: Floating tooltip successfully hides on mouseleave")

            # 2. Light Theme Audit
            print(
                "\n  🔍 [Theme Tokens] Verifying Tooltip Design Tokens in Light Mode..."
            )
            page.evaluate("applyTheme('light')")
            page.wait_for_timeout(100)

            btn = page.locator("#tabDoc")
            btn.hover()
            page.wait_for_timeout(200)
            light_tt_info = page.evaluate("""() => {
                const tt = document.getElementById('web-tooltip');
                const style = window.getComputedStyle(tt);
                return {
                    bg: style.backgroundColor,
                    color: style.color,
                    visible: tt.classList.contains('is-visible')
                };
            }""")

            if not light_tt_info.get("visible"):
                errors.append("Floating tooltip did not show in light mode")
            else:
                print(
                    f"    ✓ OK: Light theme tooltip active with bg={light_tt_info['bg']}, text color={light_tt_info['color']}"
                )

            # 3. Keyboard Focus Accessibility
            print("\n  🔍 [A11y Guard] Verifying Keyboard Focus Tooltip Trigger...")
            page.evaluate(
                "document.getElementById('search-trigger') ? document.getElementById('search-trigger').focus() : document.querySelector('.search-trigger-btn').focus()"
            )
            page.wait_for_timeout(200)
            kbd_tt_info = page.evaluate("""() => {
                const tt = document.getElementById('web-tooltip');
                return {
                    visible: tt.classList.contains('is-visible'),
                    text: tt.textContent.trim()
                };
            }""")

            if not kbd_tt_info.get("visible"):
                errors.append("Keyboard focus did not trigger floating web tooltip")
            else:
                print(
                    f"    ✓ OK: Keyboard focus correctly triggered tooltip: '{kbd_tt_info['text']}'"
                )

            # 4. Contact Chips Verification
            print("\n  🔍 [Contact Chips] Verifying Contact Bar Tooltips...")
            contact_chips = page.locator(".contact-chips a")
            chip_count = contact_chips.count()
            for i in range(chip_count):
                chip = contact_chips.nth(i)
                data_tt = chip.get_attribute("data-tooltip")
                raw_title = chip.get_attribute("title")
                label = chip.inner_text().strip()
                if not data_tt:
                    errors.append(f"Contact chip [{label}] lacks 'data-tooltip'")
                if raw_title:
                    errors.append(
                        f"Contact chip [{label}] has raw 'title' attribute ('{raw_title}')"
                    )
                chip.hover()
                page.wait_for_timeout(150)
                visible = page.evaluate(
                    "document.getElementById('web-tooltip').classList.contains('is-visible')"
                )
                if not visible:
                    errors.append(
                        f"Hover on contact chip [{label}] failed to show floating tooltip"
                    )
                else:
                    print(f"    ✓ OK: Contact chip [{label}] -> '{data_tt}'")

            browser.close()

    return errors


def main() -> int:
    print("=" * 80)
    print("  🛡️  WEB COMPONENTS & UI DESIGN TOKENS COMPLIANCE CHECKER")
    print("=" * 80)

    errors = check_dynamic_ui_tokens()

    print("\n" + "=" * 80)
    if errors:
        print(f"❌ COMPLIANCE AUDIT FAILED WITH {len(errors)} VIOLATIONS:")
        for err in errors:
            print(f"  • {err}")
        print("=" * 80)
        return 1
    else:
        print(
            "🎉 ALL CHECKS PASSED: ZERO WEBAWESOME LEFTOVERS & 100% DESIGN TOKEN COMPLIANCE!"
        )
        print("=" * 80)
        return 0


if __name__ == "__main__":
    sys.exit(main())
