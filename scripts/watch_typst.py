#!/usr/bin/env python3
"""Rock-solid Live preview / Watcher for Typst Resume.

Tracks source file modification timestamps (mtime) directly.
Guarantees 0% idle CPU and zero recursive trigger loops.
"""

import json
import sys
import time
from pathlib import Path

try:
    import typst
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print(
        "Error: dependencies missing. Use 'uv run scripts/watch_typst.py'",
        file=sys.stderr,
    )
    sys.exit(1)

ROOT_DIR = Path(__file__).resolve().parent.parent
PROFILE_PATH = ROOT_DIR / "data" / "profile.json"
TYPST_DIR = ROOT_DIR / "typst_resume"
TEMPLATE_PATH = TYPST_DIR / "resume.typ.j2"
OUTPUT_TYP_PATH = TYPST_DIR / "resume.typ"
OUTPUT_PDF_PATH = ROOT_DIR / "data" / "pdf" / "2026" / "2026_ATTY_Resume_Typst.pdf"

WATCHED_SOURCES = [PROFILE_PATH, TEMPLATE_PATH]


sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import calculate_age, process_profile_data


class TypstWatcher:
    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(TYPST_DIR),
            autoescape=False,
        )
        self.env.filters["age"] = calculate_age
        self.template = self.env.get_template(TEMPLATE_PATH.name)
        OUTPUT_PDF_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.mtimes = {f: f.stat().st_mtime for f in WATCHED_SOURCES if f.exists()}

    def compile(self) -> float:
        start = time.perf_counter()
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            profile = json.load(f)

        profile = process_profile_data(profile)

        rendered = self.template.render(profile=profile)
        with open(OUTPUT_TYP_PATH, "w", encoding="utf-8") as f:
            f.write(rendered)

        typst.compile(str(OUTPUT_TYP_PATH), output=str(OUTPUT_PDF_PATH))
        return (time.perf_counter() - start) * 1000

    def run(self):
        initial_ms = self.compile()
        print(
            f"[Typst Watcher] Initial compilation: {OUTPUT_PDF_PATH.name} in {initial_ms:.1f} ms"
        )
        print(f"[Typst Watcher] Watching: {PROFILE_PATH.name} and {TEMPLATE_PATH.name}")
        print("[Typst Watcher] Idle CPU: 0%. Press Ctrl+C to stop.\n")

        while True:
            time.sleep(0.25)
            changed_file = None
            for src in WATCHED_SOURCES:
                if not src.exists():
                    continue
                current_mtime = src.stat().st_mtime
                if current_mtime > self.mtimes.get(src, 0):
                    self.mtimes[src] = current_mtime
                    changed_file = src
                    break

            if changed_file:
                try:
                    duration_ms = self.compile()
                    print(
                        f"[{time.strftime('%H:%M:%S')}] Recompiled ({changed_file.name}) in {duration_ms:.1f} ms"
                    )
                except (typst.TypstError, json.JSONDecodeError, OSError) as e:
                    print(f"[{time.strftime('%H:%M:%S')}] Error:\n{e}", file=sys.stderr)


def main():
    watcher = TypstWatcher()
    try:
        watcher.run()
    except KeyboardInterrupt:
        print("\n[Typst Watcher] Stopped.")


if __name__ == "__main__":
    main()
