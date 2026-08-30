#!/usr/bin/env python3
# /// script
# dependencies = [
#   "jinja2>=3.1.0",
#   "typst>=0.15.0",
# ]
# ///
"""Build script for the static GitHub Pages resume site powered by Typst & PDF.js ISO engine."""

import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import cast

try:
    import typst
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print(
        "Error: jinja2 and typst are required. Run with 'uv run scripts/build_site.py'",
        file=sys.stderr,
    )
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import calculate_age, process_profile_data


def minify_html_css(html: str) -> str:
    """Minifies inline CSS blocks, strips comments and compacts HTML whitespace."""

    def repl_css(m: re.Match[str]) -> str:
        css = m.group(1)
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
        css = re.sub(r"\s+", " ", css)
        css = re.sub(r"\s*([\{\};:,])\s*", r"\1", css)
        css = css.replace(";}", "}")
        return f"<style>{css.strip()}</style>"

    html = re.sub(r"<style[^>]*>(.*?)</style>", repl_css, html, flags=re.DOTALL)
    # Strip HTML comments
    html = re.sub(r"<!--(?!\[if).*?-->", "", html, flags=re.DOTALL)
    # Compact whitespace between tags
    html = re.sub(r">\s+<", "><", html)
    return html


def load_structured_resume_data(data_path: Path, profile: dict) -> dict:
    """Loads rich structured resume data from JSON and injects profile context."""
    if not data_path.exists():
        raise FileNotFoundError(f"Resume data file not found at {data_path}")
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["profile"] = profile
    return data


def build_site(output_dir: Path | None = None) -> Path:
    root_dir = Path(__file__).resolve().parent.parent
    profile_path = root_dir / "data" / "profile.json"
    resume_data_path = root_dir / "data" / "resume_data.json"
    typst_dir = root_dir / "typst_resume"
    template_dir = root_dir / "site_template"

    if output_dir is None:
        output_dir = root_dir / "dist"

    output_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    # 0. Copy static assets if they exist in site_template/assets
    src_assets = template_dir / "assets"
    if src_assets.exists():
        for item in src_assets.iterdir():
            dest = assets_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)

    output_typ_path = typst_dir / "resume.typ"

    with open(profile_path, "r", encoding="utf-8") as f:
        profile_data = json.load(f)

    profile = process_profile_data(profile_data)
    resume_data = load_structured_resume_data(resume_data_path, profile)

    # 1. Render Typst template
    jinja_env = Environment(
        loader=FileSystemLoader(typst_dir),
        autoescape=False,
    )
    jinja_env.filters["age"] = calculate_age
    template = jinja_env.get_template("resume.typ.j2")
    rendered_typ = template.render(profile=profile)

    with open(output_typ_path, "w", encoding="utf-8") as f:
        f.write(rendered_typ)

    current_year = datetime.now(tz=timezone.utc).year
    pdf_year_path = (
        root_dir
        / "data"
        / "pdf"
        / str(current_year)
        / f"{current_year}_ATTY_Resume_Typst.pdf"
    )
    pdf_year_path.parent.mkdir(parents=True, exist_ok=True)

    # 2. Compile to PDF (100% ISO Master Document)
    typst.compile(str(output_typ_path), output=str(pdf_year_path))
    dist_pdf_name = f"{current_year}_ATTY_Resume_Typst.pdf"
    shutil.copy2(pdf_year_path, output_dir / dist_pdf_name)
    shutil.copy2(pdf_year_path, output_dir / "Lionel_ATTY_Resume_Typst.pdf")
    shutil.copy2(pdf_year_path, assets_dir / "cv_master.pdf.dat")
    shutil.copy2(output_typ_path, output_dir / "resume.typ")

    # 3. Compile SVG & PNG for vector fallbacks and social sharing
    svg_raw_pages = typst.compile(str(output_typ_path), format="svg")
    for idx, raw_svg in enumerate(cast(list[bytes], svg_raw_pages)):
        svg_file_path = assets_dir / f"cv-page-{idx + 1}.svg"
        with open(svg_file_path, "w", encoding="utf-8") as f:
            f.write(raw_svg.decode("utf-8"))

    png_pages = typst.compile(str(output_typ_path), format="png", ppi=150)
    for idx, raw_png in enumerate(cast(list[bytes], png_pages)):
        png_file_path = assets_dir / f"cv-page-{idx + 1}.png"
        with open(png_file_path, "wb") as f:
            f.write(raw_png)

    # 4. Render index.html via Jinja2 template with rich context
    site_env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=False,
    )
    html_tpl = site_env.get_template("index.html.j2")
    rendered_html = html_tpl.render(
        profile=profile,
        pdf_filename=dist_pdf_name,
        build_year=current_year,
        resume_data=resume_data,
        resume_json=json.dumps(resume_data, ensure_ascii=False, separators=(",", ":")),
    )
    html_content = minify_html_css(rendered_html)

    index_html_path = output_dir / "index.html"
    with open(index_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✓ Rich & ISO PDF Static Site built in: {output_dir}")
    print(f"  - HTML: {index_html_path}")
    print(f"  - PDF:  {output_dir / dist_pdf_name}")
    print(f"  - SVGs: {len(svg_raw_pages)} vector pages in assets/")
    print(f"  - PNGs: {len(png_pages)} preview images in assets/")
    return output_dir


def main():
    build_site()


if __name__ == "__main__":
    main()
