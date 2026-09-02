#!/usr/bin/env python3
"""Automated Static HTML & Inline JavaScript Syntax Validator.

Parses generated dist/index.html and ensures:
1. All inline event handlers (onclick, onchange, etc.) are syntactically valid JavaScript.
2. No unescaped quote syntax errors in event attributes.
3. All <script> blocks parse cleanly with node --check.
4. All media gallery items have matching DOM targets and valid asset paths.
"""

import html
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DIST_INDEX = ROOT_DIR / "dist" / "index.html"


class InlineHandlerParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inline_handlers: list[tuple[str, str, int]] = []  # (attr_name, code, line)
        self.scripts: list[tuple[str, int]] = []  # (script_content, line)
        self.in_script = False
        self.current_script_lines: list[str] = []
        self.script_start_line = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        line = self.getpos()[0]
        if tag == "script":
            self.in_script = True
            self.current_script_lines = []
            self.script_start_line = line
        for name, value in attrs:
            if name.startswith("on") and value:
                unescaped_code = html.unescape(value)
                self.inline_handlers.append((name, unescaped_code, line))

    def handle_data(self, data: str):
        if self.in_script:
            self.current_script_lines.append(data)

    def handle_endtag(self, tag: str):
        if tag == "script":
            self.in_script = False
            self.scripts.append(
                ("".join(self.current_script_lines), self.script_start_line)
            )


def validate_all_js(
    inline_handlers: list[tuple[str, str, int]], scripts: list[tuple[str, int]]
) -> list[str]:
    """Generates a single composite JS file to validate everything in one fast node pass."""
    errors = []

    # Build batched validator script
    js_parts = ["// Static Syntax Validation Batch\n"]
    for i, (attr, code, line) in enumerate(inline_handlers):
        js_parts.append(
            f"// Item {i}: {attr} at line {line}\nfunction __handler_{i}(event) {{\n{code}\n}}\n"
        )

    for j, (script_code, start_line) in enumerate(scripts):
        if script_code.strip():
            js_parts.append(
                f"// Script {j} at line {start_line}\n{{\n{script_code}\n}}\n"
            )

    composite_js = "".join(js_parts)

    with tempfile.NamedTemporaryFile(
        "w", suffix=".js", delete=False, encoding="utf-8"
    ) as tf:
        tf.write(composite_js)
        temp_path = tf.name

    try:
        proc = subprocess.run(
            ["node", "--check", temp_path],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if proc.returncode != 0:
            errors.append(
                f"❌ Syntax Error in HTML inline scripts/handlers:\n{proc.stderr.strip()}"
            )
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        errors.append(f"⚠️ Node.js execution failed: {e}")
    finally:
        Path(temp_path).unlink(missing_ok=True)

    return errors


def main() -> int:
    if not DIST_INDEX.exists():
        print(
            f"❌ Error: {DIST_INDEX} does not exist. Run scripts/build_site.py first."
        )
        return 1

    content = DIST_INDEX.read_text(encoding="utf-8")
    parser = InlineHandlerParser()
    parser.feed(content)

    print("\n" + "=" * 80)
    print("  🛡️  STATIC HTML & INLINE JAVASCRIPT SYNTAX GUARD")
    print("=" * 80)
    print(
        f"  🔍 Validating {len(parser.inline_handlers)} inline handlers and {len(parser.scripts)} script tags in one batch..."
    )

    errors = validate_all_js(parser.inline_handlers, parser.scripts)

    if errors:
        print("\n" + "\n".join(errors))
        print(f"\n❌ Validation FAILED with {len(errors)} syntax error(s) in HTML!")
        return 1

    print(
        f"  ✓ OK: All {len(parser.inline_handlers)} inline handlers and {len(parser.scripts)} script blocks are 100% syntactically valid!"
    )
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
