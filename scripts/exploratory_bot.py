#!/usr/bin/env python3
# /// script
# dependencies = [
#     "playwright",
# ]
# ///
"""Autonomous Guided Exploratory E2E Testing Bot (Chaos Monkey & History Tracker).

Explores the CV / Portfolio application with a pseudo-random guided walk,
exercising interactive components, view switches, search palette, PDF.js ISO
viewer, project galleries, modals, responsive viewport morphing, and theme toggles.

Tracks, records, and exports all executed steps, metrics, and health audits
to structured session reports (JSONL + Markdown).
"""

from __future__ import annotations

import argparse
import contextlib
import datetime
import http.server
import json
import random
import socket
import socketserver
import sys
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT_DIR / "dist"
REPORTS_DIR = ROOT_DIR / "reports" / "bot_sessions"


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST_DIR), **kwargs)

    def log_message(self, format, *args):
        pass


@dataclass
class BotStepLog:
    step: int
    time_iso: str
    action: str
    description: str
    target: str | None
    duration_ms: float
    view_before: str
    view_after: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    status: str = "PASS"


@dataclass
class BotSessionReport:
    seed: int
    start_time: str
    end_time: str
    total_steps: int
    passed_steps: int
    warned_steps: int
    failed_steps: int
    total_duration_sec: float
    target_url: str
    unique_dom_elements_touched: int
    feature_coverage: dict[str, int]
    steps: list[BotStepLog] = field(default_factory=list)
    uncaught_exceptions: list[str] = field(default_factory=list)
    console_errors: list[str] = field(default_factory=list)
    console_warnings: list[str] = field(default_factory=list)
    network_errors: list[str] = field(default_factory=list)


PALETTE_QUERIES = [
    "rust",
    "vulkan",
    "fastapi",
    "python",
    "tracy",
    "opengl",
    "shader",
    "suckless",
    "odin",
    "docker",
    "c++",
    "jinja",
    "typst",
    "geotribu",
    "inria",
    "shadow",
    "xyz_not_found_test",
    "particules",
    "grafana",
    "linux",
]

VIEWPORTS = [
    {"name": "Desktop (1280x800)", "width": 1280, "height": 800},
    {"name": "Mobile (390x844)", "width": 390, "height": 844},
    {"name": "Tablet (768x1024)", "width": 768, "height": 1024},
    {"name": "UltraWide (1920x1080)", "width": 1920, "height": 1080},
    {"name": "Compact Android (360x740)", "width": 360, "height": 740},
]


class ExploratoryBot:
    def __init__(
        self, base_url: str, seed: int, max_steps: int, fail_on_warn: bool = False
    ):
        self.base_url = base_url
        self.seed = seed
        self.max_steps = max_steps
        self.fail_on_warn = fail_on_warn
        self.rng = random.Random(seed)
        self.touched_elements: set[str] = set()
        self.feature_counters: dict[str, int] = {
            "view_switch": 0,
            "domain_filters": 0,
            "tech_filters": 0,
            "palette_search": 0,
            "gallery_media": 0,
            "image_lightbox": 0,
            "media_modal": 0,
            "pdf_controls": 0,
            "theme_toggle": 0,
            "viewport_morph": 0,
            "scroll_random": 0,
            "anchor_nav": 0,
        }
        self.page_errors: list[str] = []
        self.console_errors: list[str] = []
        self.console_warnings: list[str] = []
        self.network_errors: list[str] = []
        self.step_logs: list[BotStepLog] = []

    def get_current_view(self, page) -> str:
        try:
            return page.evaluate(
                "() => document.getElementById('viewDocument').style.display !== 'none' ? 'ISO Document' : 'Portfolio Web'"
            )
        except Exception:  # noqa: BLE001
            return "Unknown"

    def execute_step(self, step_idx: int, page) -> BotStepLog:
        start_t = time.perf_counter()
        view_before = self.get_current_view(page)
        curr_errors_count = len(self.page_errors) + len(self.console_errors)
        curr_warnings_count = len(self.console_warnings)

        action_weights = [
            ("view_switch", 0.12),
            ("domain_filters", 0.15),
            ("tech_filters", 0.12),
            ("palette_search", 0.15),
            ("gallery_media", 0.12),
            ("image_lightbox", 0.08),
            ("media_modal", 0.05),
            ("pdf_controls", 0.12),
            ("theme_toggle", 0.04),
            ("viewport_morph", 0.05),
        ]

        action_type = self.rng.choices(
            [a[0] for a in action_weights],
            weights=[a[1] for a in action_weights],
            k=1,
        )[0]

        description = ""
        target_name: str | None = None

        try:
            if action_type == "view_switch":
                target_view = self.rng.choice(["web", "doc"])
                page.evaluate(f"switchMainView('{target_view}')")
                page.wait_for_timeout(100)
                description = f"Switched view to {target_view.upper()}"
                target_name = f"switchMainView({target_view})"
                self.feature_counters["view_switch"] += 1

            elif action_type == "domain_filters":
                page.evaluate("switchMainView('web')")
                domains = ["all", "python", "cpp-3d", "spatial-gis", "management"]
                chosen_domain = self.rng.choice(domains)
                is_shift = self.rng.choice([True, False])
                page.evaluate(
                    f"filterByDomain('{chosen_domain}', {{ shiftKey: {str(is_shift).lower()}, ctrlKey: false, metaKey: false }})"
                )
                page.wait_for_timeout(80)
                description = f"Filter domain '{chosen_domain}' (Shift={is_shift})"
                target_name = f".filter-tag[data-domain={chosen_domain}]"
                self.touched_elements.add(target_name)
                self.feature_counters["domain_filters"] += 1

            elif action_type == "tech_filters":
                page.evaluate("switchMainView('web')")
                techs = [
                    "Python",
                    "Rust",
                    "C++",
                    "Vulkan",
                    "FastAPI",
                    "Docker",
                    "Jinja2",
                    "Typst",
                    "OpenGL",
                    "Web Components",
                ]
                chosen_tech = self.rng.choice(techs)
                is_shift = self.rng.choice([True, False])
                page.evaluate(
                    f"filterByTech('{chosen_tech}', {{ shiftKey: {str(is_shift).lower()}, ctrlKey: false, metaKey: false }})"
                )
                page.wait_for_timeout(80)
                description = f"Filter tech keyword '{chosen_tech}' (Shift={is_shift})"
                target_name = f".tech-kw[{chosen_tech}]"
                self.touched_elements.add(target_name)
                self.feature_counters["tech_filters"] += 1

            elif action_type == "palette_search":
                page.evaluate("openPalette()")
                page.wait_for_timeout(60)
                query = self.rng.choice(PALETTE_QUERIES)
                page.evaluate(
                    """val => {
                    const inp = document.getElementById('paletteSearchInput');
                    if (inp) {
                        inp.value = val;
                        inp.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                }""",
                    query,
                )
                page.wait_for_timeout(80)
                # Randomly navigate search results or close
                if self.rng.random() < 0.5:
                    page.keyboard.press("ArrowDown")
                    page.keyboard.press("ArrowDown")
                if self.rng.random() < 0.3:
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(80)
                page.evaluate("closePalette()")
                page.wait_for_timeout(60)
                description = f"Command Palette search '{query}'"
                target_name = "#cmdPaletteDialog"
                self.touched_elements.add(target_name)
                self.feature_counters["palette_search"] += 1

            elif action_type == "gallery_media":
                page.evaluate("switchMainView('web')")
                cards = [1, 2, 4, 5]
                card_idx = self.rng.choice(cards)
                count = page.evaluate(
                    f"document.querySelectorAll('.media-thumb-btn-{card_idx}').length"
                )
                if count > 0:
                    chosen_btn_idx = self.rng.randint(0, count - 1)
                    page.evaluate(
                        f"() => {{ const btns = document.querySelectorAll('.media-thumb-btn-{card_idx}'); if (btns.length > {chosen_btn_idx}) btns[{chosen_btn_idx}].click(); }}"
                    )
                    page.wait_for_timeout(80)
                    target_name = f".media-thumb-btn-{card_idx}[{chosen_btn_idx}]"
                    description = (
                        f"Toggled project #{card_idx} gallery item #{chosen_btn_idx}"
                    )
                    self.touched_elements.add(target_name)
                    self.feature_counters["gallery_media"] += 1
                else:
                    description = "Skipped gallery (no buttons found)"

            elif action_type == "image_lightbox":
                page.evaluate("switchMainView('web')")
                # Open image lightbox
                page.evaluate(
                    "openImageModal('/assets/projects/volumetric-lights.png', 'Test Volumetric')"
                )
                page.wait_for_timeout(100)
                # Close it safely
                page.evaluate("closeImageModal()")
                page.wait_for_timeout(60)
                description = "Opened and closed Image Lightbox Modal"
                target_name = "#imageModalDialog"
                self.touched_elements.add(target_name)
                self.feature_counters["image_lightbox"] += 1

            elif action_type == "media_modal":
                page.evaluate("switchMainView('web')")
                # Open media presentation modal
                page.evaluate("openMediaModal('https://bit.ly/36mb5Ez', 'Test Slides')")
                page.wait_for_timeout(100)
                # Close it safely
                page.evaluate("closeMediaModal()")
                page.wait_for_timeout(60)
                description = "Opened and closed Multimedia Presentation Modal"
                target_name = "#mediaModalDialog"
                self.touched_elements.add(target_name)
                self.feature_counters["media_modal"] += 1

            elif action_type == "pdf_controls":
                page.evaluate("switchMainView('doc')")
                page.wait_for_timeout(100)
                sub_action = self.rng.choice(
                    [
                        "mode_single",
                        "mode_dual",
                        "mode_continuous",
                        "zoom_in",
                        "zoom_out",
                        "page_toggle",
                    ]
                )
                if sub_action == "mode_single":
                    page.evaluate("setDocMode('single')")
                    description = "Set ISO Document mode to 'Page Simple'"
                elif sub_action == "mode_dual":
                    page.evaluate("setDocMode('dual')")
                    description = "Set ISO Document mode to 'Double Page'"
                elif sub_action == "mode_continuous":
                    page.evaluate("setDocMode('continuous')")
                    description = "Set ISO Document mode to 'Continu'"
                elif sub_action == "zoom_in":
                    page.evaluate("zoomDoc(0.1)")
                    description = "Zoom In ISO Document (+10%)"
                elif sub_action == "zoom_out":
                    page.evaluate("zoomDoc(-0.1)")
                    description = "Zoom Out ISO Document (-10%)"
                elif sub_action == "page_toggle":
                    page.evaluate("docPageNum === 1 ? nextDocPage() : prevDocPage()")
                    description = "Toggled ISO Document Page (1 <-> 2)"
                page.wait_for_timeout(80)
                target_name = f"#viewDocument controls ({sub_action})"
                self.touched_elements.add("#viewDocument")
                self.feature_counters["pdf_controls"] += 1

            elif action_type == "theme_toggle":
                page.evaluate("toggleTheme()")
                page.wait_for_timeout(60)
                description = "Toggled theme (Light <-> Dark)"
                target_name = "#themeToggleBtn"
                self.touched_elements.add(target_name)
                self.feature_counters["theme_toggle"] += 1

            elif action_type == "viewport_morph":
                chosen_vp = self.rng.choice(VIEWPORTS)
                page.set_viewport_size(
                    {"width": chosen_vp["width"], "height": chosen_vp["height"]}
                )
                page.wait_for_timeout(100)
                description = f"Morphed viewport to {chosen_vp['name']}"
                target_name = f"viewport({chosen_vp['width']}x{chosen_vp['height']})"
                self.feature_counters["viewport_morph"] += 1

        except Exception as ex:  # noqa: BLE001
            description = f"Action {action_type} encountered exception: {ex}"
            self.page_errors.append(f"[Bot Execution Exception] {ex}")

        duration_ms = round((time.perf_counter() - start_t) * 1000, 2)
        view_after = self.get_current_view(page)

        # Collect new errors / warnings during this step
        step_errors = (self.page_errors + self.console_errors)[curr_errors_count:]
        step_warnings = self.console_warnings[curr_warnings_count:]

        status = "PASS"
        if step_errors or (step_warnings and self.fail_on_warn):
            status = "FAIL"
        elif step_warnings:
            status = "WARN"

        log_entry = BotStepLog(
            step=step_idx,
            time_iso=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            action=action_type,
            description=description,
            target=target_name,
            duration_ms=duration_ms,
            view_before=view_before,
            view_after=view_after,
            errors=step_errors,
            warnings=step_warnings,
            status=status,
        )
        self.step_logs.append(log_entry)
        return log_entry


def generate_reports(report: BotSessionReport) -> tuple[Path, Path]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp_slug = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y%m%d_%H%M%S"
    )
    jsonl_path = REPORTS_DIR / f"session_{timestamp_slug}_seed{report.seed}.jsonl"
    md_path = REPORTS_DIR / f"session_{timestamp_slug}_seed{report.seed}.md"

    # 1. JSONL Machine Log
    with open(jsonl_path, "w", encoding="utf-8") as f:
        f.writelines(
            json.dumps(asdict(s), ensure_ascii=False) + "\n" for s in report.steps
        )

    # 2. Markdown Human Report
    md_content = f"""# 🤖 Rapport d'Exploration E2E (Guided Chaos Monkey)

**Date de Session** : {report.start_time}  
**Graine Aléatoire (Seed)** : `{report.seed}`  
**URL Cible** : `{report.target_url}`  
**Durée Totale** : {report.total_duration_sec:.2f}s  
**Statut Global** : {"🟢 PASS (Zéro Erreur)" if report.failed_steps == 0 else "🔴 FAIL (" + str(report.failed_steps) + " échecs)"}

> 🔁 **Commande de Rejeu Déterministe** :  
> `task test:bot -- --seed {report.seed} --steps {report.total_steps}`

---

## 📊 Métriques & Synthèse d'Exécution

| Métrique | Valeur |
|:---|:---|
| **Actions Totales Exécutées** | **{report.total_steps}** |
| **Actions Réussies (PASS)** | **{report.passed_steps}** |
| **Actions avec Avertissements (WARN)** | **{report.warned_steps}** |
| **Actions en Échec (FAIL)** | **{report.failed_steps}** |
| **Éléments DOM Uniques Explorés** | **{report.unique_dom_elements_touched}** |
| **Exceptions Runtime Non Catchées** | **{len(report.uncaught_exceptions)}** |
| **Erreurs Console DevTools** | **{len(report.console_errors)}** |
| **Avertissements Console (Warnings)** | **{len(report.console_warnings)}** |
| **Requêtes Réseau Échouées** | **{len(report.network_errors)}** |

---

## 🎯 Couverture Fonctionnelle

| Composant / Fonctionnalité | Nombre d'Actions |
|:---|:---|
"""
    for feat, count in report.feature_coverage.items():
        md_content += f"| `{feat}` | {count} |\n"

    md_content += """
---

## 📜 Journal Chronologique des Actions

| # | Heure (UTC) | Action | Description | Cible | Durée | Statut |
|:---|:---|:---|:---|:---|:---|:---|
"""
    for s in report.steps:
        icon = "🟢" if s.status == "PASS" else ("🟡" if s.status == "WARN" else "🔴")
        target_str = f"`{s.target}`" if s.target else "-"
        md_content += f"| {s.step} | {s.time_iso[11:19]} | `{s.action}` | {s.description} | {target_str} | {s.duration_ms}ms | {icon} {s.status} |\n"

    if report.console_errors or report.uncaught_exceptions or report.console_warnings:
        md_content += """
---

## ⚠️ Journal des Anomalies Détectées

"""
        for err in report.uncaught_exceptions:
            md_content += f"- 🔴 **[Uncaught Exception]** `{err}`\n"
        for err in report.console_errors:
            md_content += f"- 🔴 **[Console Error]** `{err}`\n"
        for warn in report.console_warnings:
            md_content += f"- 🟡 **[Console Warning]** `{warn}`\n"
        for net in report.network_errors:
            md_content += f"- 🔴 **[Network Error]** `{net}`\n"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return jsonl_path, md_path


def run_bot(
    steps: int | None = None,
    duration: float | None = None,
    seed: int | None = None,
    target_url: str | None = None,
    fail_on_warn: bool = False,
) -> int:
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "❌ Error: playwright is required. Run with: uv run --with playwright scripts/exploratory_bot.py"
        )
        return 1

    if steps is None and duration is None:
        steps = 50

    if seed is None:
        seed = random.randint(10000, 99999)

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

    bot = ExploratoryBot(base_url, seed, steps or 99999, fail_on_warn)

    mode_label = f"{duration}s duration limit" if duration else f"{steps} steps"
    print("\n" + "=" * 80)
    print(f"  🤖 AUTONOMOUS GUIDED EXPLORATORY BOT (Seed: {seed} | Mode: {mode_label})")
    print(f"  🎯 Target: {base_url}")
    print("=" * 80)

    start_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    start_perf = time.perf_counter()

    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(executable_path="/usr/bin/chromium")
            except (PlaywrightError, OSError):
                browser = p.chromium.launch()

            page = browser.new_page(viewport={"width": 1280, "height": 800})

            # Attach listeners
            page.on("pageerror", lambda err: bot.page_errors.append(str(err)))
            page.on(
                "console",
                lambda msg: (
                    bot.console_errors.append(msg.text)
                    if msg.type in ["error"]
                    else (
                        bot.console_warnings.append(msg.text)
                        if msg.type in ["warning"]
                        else None
                    )
                ),
            )
            page.on(
                "requestfailed",
                lambda req: (
                    bot.network_errors.append(f"{req.url} - {req.failure}")
                    if req.url.startswith(base_url)
                    and not req.url.endswith("favicon.ico")
                    and "net::ERR_ABORTED" not in str(req.failure)
                    else None
                ),
            )

            # Initial navigation
            page.goto(base_url, wait_until="networkidle")
            page.wait_for_timeout(300)

            # Prevent native print or navigation dialog blocking
            page.evaluate("() => { window.print = () => {}; }")

            step_num = 1
            while True:
                elapsed = time.perf_counter() - start_perf
                if duration is not None and elapsed >= duration:
                    break
                if steps is not None and step_num > steps:
                    break

                entry = bot.execute_step(step_num, page)

                # Capture screenshot on failure
                if entry.status == "FAIL":
                    screenshot_dir = REPORTS_DIR / "screenshots"
                    screenshot_dir.mkdir(parents=True, exist_ok=True)
                    screenshot_path = (
                        screenshot_dir / f"fail_step_{step_num:03d}_{seed}.png"
                    )
                    with contextlib.suppress(Exception):
                        page.screenshot(path=str(screenshot_path))

                icon = (
                    "✓"
                    if entry.status == "PASS"
                    else ("⚠️" if entry.status == "WARN" else "❌")
                )
                step_str = (
                    f"[{step_num:03d}]" if duration else f"[{step_num:03d}/{steps:03d}]"
                )
                print(
                    f"  {step_str} {icon} {entry.action:16s} | {entry.description[:42]:42s} ({entry.duration_ms:5.1f}ms | {elapsed:4.1f}s)",
                    flush=True,
                )
                step_num += 1

            browser.close()

    finally:
        if httpd:
            httpd.shutdown()

    end_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    total_duration = time.perf_counter() - start_perf

    passed = sum(1 for s in bot.step_logs if s.status == "PASS")
    warned = sum(1 for s in bot.step_logs if s.status == "WARN")
    failed = sum(1 for s in bot.step_logs if s.status == "FAIL")

    report = BotSessionReport(
        seed=seed,
        start_time=start_iso,
        end_time=end_iso,
        total_steps=len(bot.step_logs),
        passed_steps=passed,
        warned_steps=warned,
        failed_steps=failed,
        total_duration_sec=total_duration,
        target_url=base_url,
        unique_dom_elements_touched=len(bot.touched_elements),
        feature_coverage=bot.feature_counters,
        steps=bot.step_logs,
        uncaught_exceptions=bot.page_errors,
        console_errors=bot.console_errors,
        console_warnings=bot.console_warnings,
        network_errors=bot.network_errors,
    )

    jsonl_path, md_path = generate_reports(report)

    print("\n" + "=" * 80)
    print("  📊 EXPLORATION SUMMARY & HEALTH AUDIT")
    print("=" * 80)
    print(
        f"  • Status                     : {'🎉 100% HEALTHY' if failed == 0 else '❌ DETECTED ANOMALIES'}"
    )
    print(
        f"  • Steps Executed             : {len(bot.step_logs)} ({passed} passed, {warned} warnings, {failed} failed)"
    )
    print(f"  • Unique DOM Targets Touched : {len(bot.touched_elements)}")
    print(f"  • Total Duration             : {total_duration:.2f}s")
    print(f"  • Machine History (JSONL)    : {jsonl_path.relative_to(ROOT_DIR)}")
    print(f"  • Human Report (Markdown)    : {md_path.relative_to(ROOT_DIR)}")
    print("=" * 80 + "\n")

    return 1 if failed > 0 else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Autonomous Exploratory E2E Testing Bot"
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=None,
        help="Number of exploration steps (default: 50 if --duration not set)",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Run exploration for N seconds (e.g. 60 for 1 minute)",
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="Reproducible random seed"
    )
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="Target URL (e.g. Surge deployment or local)",
    )
    parser.add_argument(
        "--fail-on-warn", action="store_true", help="Treat console warnings as failures"
    )
    args = parser.parse_args()

    sys.exit(
        run_bot(
            steps=args.steps,
            duration=args.duration,
            seed=args.seed,
            target_url=args.url,
            fail_on_warn=args.fail_on_warn,
        )
    )
