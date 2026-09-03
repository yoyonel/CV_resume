#!/usr/bin/env python3
"""Build script for the static GitHub Pages resume site powered by Typst & PDF.js ISO engine."""

import json
import re
import shutil
import sys
from datetime import UTC, datetime
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


TECH_FAMILIES_DEF = {
    "ai": [
        "AGY (Gemini)",
        "Antigravity (AGY)",
        "Claude Code",
        "MCP Servers",
        "Serveurs MCP",
        "MCP",
        "Dust",
        "n8n",
        "OpenAI API",
        "OpenAI",
        "Gemini",
        "LLM",
        "IA",
        "NLP",
        "spaCy",
        "Gensim",
        "TensorFlow",
    ],
    "infra": [
        "Raspberry Pi 4",
        "Raspberry Pi",
        "Docker Compose",
        "Docker / Podman",
        "Docker",
        "Podman",
        "Distrobox (clang-dev)",
        "Distrobox",
        "Azure / AKS",
        "Azure Blob Storage",
        "Azure Storage",
        "Azure",
        "AKS",
        "Google Cloud Platform",
        "GCP",
        "Kubernetes",
        "Digital Ocean",
        "Terraform",
        "Ansible",
        "GitLab CI",
        "GitHub Actions",
        "CI/CD",
        "SAML",
        "SCIM",
        "OAuth2",
        "Traefik",
        "Keycloak",
        "Argo",
        "Fluentd",
        "Rancher",
        "QEMU / KVM",
        "QEMU",
        "Vagrant",
        "POSIX Standard",
        "POSIX",
        "Linux",
        "Systemd Timers",
        "Systemd",
        "Ookla Speedtest CLI",
        "Speedtest CLI",
        "Speedtest",
        "VictoriaMetrics",
        "InfluxDB",
        "Telegraf",
        "Grafana",
        "Prometheus",
        "Elastic APM",
        "Elasticsearch",
        "Logstash",
        "Kibana",
        "MongoDB",
        "MongoEngine",
        "PyMongo",
        "Redis Streams",
        "Redis / Streams",
        "Redis",
        "RabbitMQ",
        "PostgreSQL",
        "PostGIS",
        "JSONB",
        "EventStore",
        "MariaDB/MySQL",
        "MariaDB",
        "MySQL",
        "MinIO",
        "MQTT",
        "HDFS",
    ],
    "core": [
        "C++17",
        "C++ (17/20)",
        "C++ (98/11/14/17)",
        "C++11",
        "C++14",
        "C++20",
        "C++",
        "C11",
        "Vulkan 1.x",
        "Vulkan",
        "OpenGL 4.5/4.6 Core",
        "OpenGL 4.5/4.6",
        "OpenGL 4.5+",
        "OpenGL 4.4 Core Profile",
        "OpenGL 4.4 Core",
        "OpenGL",
        "GLSL / SPIR-V",
        "GLSL / HLSL",
        "GLSL",
        "SPIR-V",
        "HLSL",
        "Shaders HLSL",
        "Shaders",
        "Compute Shaders",
        "Shader",
        "DirectX 9/10",
        "DirectX",
        "OpenCL",
        "CUDA",
        "OpenSceneGraph",
        "Cook-Torrance (GGX/Smith/Schlick)",
        "Cook-Torrance PBR",
        "Cook-Torrance",
        "PBR",
        "RHI BindGroups",
        "RHI",
        "RenderGraph automatique",
        "RenderGraph",
        "VkImageMemoryBarrier",
        "Dual-Filtering FP16",
        "FP16",
        "Auto-Exposure",
        "LDS",
        "HUD",
        "KTX2/Zstd",
        "745+ FPS",
        "Uber-Shader (15 FX)",
        "Uber-Shader",
        "Bloom tent 13-tap",
        "Bloom",
        "DoF",
        "Motion Blur NeighborMax",
        "Motion Blur",
        "FXAA 3.11",
        "Color Grading LUT 3D",
        "LUT 3D",
        "BRDF LUT",
        "split-sum BRDF LUT",
        "Monte Carlo",
        "SSBO",
        "Skyboxes cubemaps",
        "Skyboxes",
        "IcoSpheres",
        "Phong",
        "GLAD",
        "Volumetric dynamic lights",
        "Volumetric Lights",
        "Volumetric",
        "SIMD AVX2",
        "SIMD / AVX2",
        "SIMD",
        "ECS / Data-Oriented",
        "ECS",
        "Data-Oriented (SoA)",
        "Data-Oriented",
        "Rust",
        "Odin Language",
        "Odin",
        "Python 3.13",
        "Python 3.9+",
        "Python 3.8",
        "Python 3.x",
        "Python",
        "FastAPI",
        "Flask-admin",
        "Flask",
        "AsyncIO",
        "FastStream",
        "Pydantic",
        "Spectree",
        "gRPC",
        "GraphQL",
        "OpenAPI",
        "Asyncpg",
        "Pandas",
        "SQLAlchemy",
        "GeoAlchemy2",
        "GeoPandas",
        "Click",
        "Jinja2",
        "ROS",
        "Blender",
        "OpenCV",
        "FFMPEG",
        "LI3DS",
        "Compiz-Reloaded",
        "Compiz",
    ],
    "tools": [
        "Tracy Profiler",
        "Tracy GPU/CPU Profiler",
        "Tracy",
        "Intel VTune Profiler",
        "Intel VTune",
        "perf (Linux)",
        "RenderDoc",
        "Heaptrack",
        "Flamegraph",
        "GDB",
        "ASan / TSan / UBSan",
        "ASan",
        "TSan",
        "UBSan",
        "Cache Misses L1/L2/L3",
        "Cache Misses",
        "clang-tidy",
        "clang-dev",
        "Clang",
        "ctest",
        "llvm-cov",
        "LLVM",
        "CMake",
        "Makefile",
        "Justfile",
        "Taskfile",
        "TLA+",
        "Steam Proton",
        "Windows AMD64",
        "Playwright E2E",
        "Playwright",
        "Lighthouse 100/100",
        "Lighthouse",
        "Pytest",
        "GitFlow",
        "YouTrack",
        "Perforce",
        "Dear ImGui",
        "ImGui",
        "DocString",
        "YouTube",
        "CLI",
        "Jupyter",
        "GitHub Pages",
        "Chart.js",
        "Release",
        "Debug",
        "ctest",
        "llvm-cov",
        "clang-tidy",
        "clang-dev",
        "suckless",
    ],
}

TECH_LOOKUP: dict[str, str] = {}
for fam, kws in TECH_FAMILIES_DEF.items():
    for k in kws:
        TECH_LOOKUP[k.lower()] = fam


def get_tech_family(tag_name: str) -> str:
    """Returns the CSS family suffix (core, infra, ai, tools) for a technical keyword."""
    return TECH_LOOKUP.get(tag_name.lower().strip(), "tools")


_ALL_KWS = sorted(TECH_LOOKUP.keys(), key=len, reverse=True)
_KW_REGEX = re.compile(
    r"(?<!\w)(" + "|".join(re.escape(k) for k in _ALL_KWS) + r")(?!\w)",
    re.IGNORECASE,
)


def highlight_keywords(text: str) -> str:
    """Highlights technical keywords in descriptions with matching Typst family badge spans."""

    def repl(m: re.Match[str]) -> str:
        word = m.group(1)
        fam = get_tech_family(word)
        escaped_word = word.replace("'", "\\'")
        return f'<span class="tech-kw family-{fam}" onclick="filterByTech(\'{escaped_word}\', event)">{word}</span>'

    return _KW_REGEX.sub(repl, text)


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

    current_year = datetime.now(tz=UTC).year
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
    site_env.filters["tech_family"] = get_tech_family
    site_env.filters["highlight_kw"] = highlight_keywords
    html_tpl = site_env.get_template("index.html.j2")
    build_id = int(datetime.now(tz=UTC).timestamp())
    rendered_html = html_tpl.render(
        profile=profile,
        pdf_filename=dist_pdf_name,
        build_year=current_year,
        build_id=build_id,
        resume_data=resume_data,
        resume_json=json.dumps(resume_data, ensure_ascii=False, separators=(",", ":")),
    )
    html_content = minify_html_css(rendered_html)

    index_html_path = output_dir / "index.html"
    with open(index_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 5. Build static ADR Documentation
    try:
        from scripts.build_adr import build_adr_docs
    except ImportError:
        from build_adr import build_adr_docs
    build_adr_docs(output_dir / "adr" / "index.html")

    print(f"✓ Rich & ISO PDF Static Site built in: {output_dir}")
    print(f"  - HTML: {index_html_path}")
    print(f"  - PDF:  {output_dir / dist_pdf_name}")
    print(f"  - ADR:  {output_dir / 'adr' / 'index.html'}")
    print(f"  - SVGs: {len(svg_raw_pages)} vector pages in assets/")
    print(f"  - PNGs: {len(png_pages)} preview images in assets/")
    return output_dir


def main():
    build_site()


if __name__ == "__main__":
    main()
