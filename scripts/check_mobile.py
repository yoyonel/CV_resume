#!/usr/bin/env python3
"""Automated mobile responsiveness & zero-overflow validation using Playwright."""

import sys
from pathlib import Path

try:
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import sync_playwright
except ImportError:
    print(
        "Error: playwright is required. Run with 'uv run --with playwright scripts/check_mobile.py'",
        file=sys.stderr,
    )
    sys.exit(1)

from build_site import build_site

VIEWPORTS = [
    ("mobile_360", 360, 740, "Standard Android (360x740)"),
    ("mobile_390", 390, 844, "iPhone 14/15 (390x844)"),
    ("mobile_412", 412, 915, "Google Pixel 7 (412x915)"),
    ("tablet_768", 768, 1024, "iPad / Tablette (768x1024)"),
    ("desktop_1280", 1280, 800, "Laptop Desktop (1280x800)"),
]


def run_mobile_checks() -> int:
    root_dir = Path(__file__).resolve().parent.parent
    dist_dir = root_dir / "dist"
    index_html = dist_dir / "index.html"
    reports_dir = root_dir / "reports" / "mobile_previews"
    reports_dir.mkdir(parents=True, exist_ok=True)

    if not index_html.exists():
        print("Building site before running checks...")
        build_site(dist_dir)

    print("=" * 72)
    print("  📱 AUTOMATED MOBILE & RESPONSIVE LAYOUT VERIFICATION (Playwright)")
    print("=" * 72)

    failures = 0

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(executable_path="/usr/bin/chromium")
        except (PlaywrightError, OSError):
            browser = p.chromium.launch()

        for name, w, h, label in VIEWPORTS:
            page = browser.new_page(viewport={"width": w, "height": h})
            page.goto(index_html.as_uri())
            page.wait_for_timeout(800)

            # 1. Test Vue Interactive
            page.evaluate("switchMainView('web')")
            page.wait_for_timeout(400)

            m_web = page.evaluate("""() => ({
                docScrollWidth: document.documentElement.scrollWidth,
                docClientWidth: document.documentElement.clientWidth,
                bodyScrollWidth: document.body.scrollWidth
            })""")

            # 2. Test Vue Document ISO
            page.evaluate("switchMainView('doc')")
            page.wait_for_timeout(600)

            m_doc = page.evaluate("""() => ({
                docScrollWidth: document.documentElement.scrollWidth,
                docClientWidth: document.documentElement.clientWidth,
                bodyScrollWidth: document.body.scrollWidth
            })""")

            # Capture screenshots
            page.screenshot(path=str(reports_dir / f"{name}_doc.png"))
            page.evaluate("switchMainView('web')")
            page.wait_for_timeout(300)
            page.screenshot(path=str(reports_dir / f"{name}_web.png"))
            page.close()

            # Evaluations (docScrollWidth must NOT exceed docClientWidth)
            web_ok = m_web["docScrollWidth"] <= m_web["docClientWidth"]
            doc_ok = m_doc["docScrollWidth"] <= m_doc["docClientWidth"]

            if web_ok and doc_ok:
                status = "✓ PASS"
                detail = f"Web: {m_web['docScrollWidth']}/{w}px | Doc: {m_doc['docScrollWidth']}/{w}px"
                print(f"  {status:8} | {label:<30} | {detail}")
            else:
                status = "✗ FAIL"
                failures += 1
                detail = f"Web: {m_web['docScrollWidth']}/{w}px (OK: {web_ok}) | Doc: {m_doc['docScrollWidth']}/{w}px (OK: {doc_ok})"
                print(f"  {status:8} | {label:<30} | {detail}", file=sys.stderr)

        browser.close()

    print("=" * 72)
    if failures == 0:
        print(f"  🎉 All {len(VIEWPORTS)} viewports passed zero-overflow validation!")
        print(
            f"  📸 Screenshot artifacts saved in: {reports_dir.relative_to(root_dir)}/"
        )
        return 0
    else:
        print(
            f"  ❌ {failures} viewport(s) failed zero-overflow check!", file=sys.stderr
        )
        return 1


if __name__ == "__main__":
    sys.exit(run_mobile_checks())
