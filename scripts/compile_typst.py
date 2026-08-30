#!/usr/bin/env python3
# /// script
# dependencies = [
#   "jinja2>=3.1.0",
#   "typst>=0.15.0",
# ]
# ///
import json
import os
import sys
from pathlib import Path

try:
    import typst
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print(
        "Error: jinja2 and typst are required. Use 'uv run scripts/compile_typst.py'",
        file=sys.stderr,
    )
    sys.exit(1)


sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import calculate_age, process_profile_data


def main():
    root_dir = Path(__file__).resolve().parent.parent
    profile_path = root_dir / "data" / "profile.json"
    typst_dir = root_dir / "typst_resume"
    output_typ_path = typst_dir / "resume.typ"
    output_pdf_path = root_dir / "data" / "pdf" / "2026" / "2026_ATTY_Resume_Typst.pdf"

    if not profile_path.exists():
        print(f"Error: Profile file not found at {profile_path}", file=sys.stderr)
        sys.exit(1)

    with open(profile_path, "r", encoding="utf-8") as f:
        profile = json.load(f)

    env_mappings = {
        "CV_NAME": "name",
        "CV_BIRTHDATE": "birthdate",
        "CV_EMAIL": "email",
        "CV_PHONE": "phone",
        "CV_ADDRESS": "address",
        "CV_MOBILITY": "mobility",
        "CV_TITLE": "title",
        "CV_SPECIALTIES": "specialties",
    }
    for env_var, key in env_mappings.items():
        if env_var in os.environ:
            profile[key] = os.environ[env_var]

    profile = process_profile_data(profile)

    env = Environment(
        loader=FileSystemLoader(typst_dir),
        autoescape=False,
    )
    env.filters["age"] = calculate_age

    template = env.get_template("resume.typ.j2")
    rendered = template.render(profile=profile)

    check_only = "--check" in sys.argv

    if (
        not output_typ_path.exists()
        or output_typ_path.read_text(encoding="utf-8") != rendered
    ):
        if check_only:
            # Validate template in memory
            typst.compile(rendered)
            print("✓ Typst syntax & compilation check passed (check mode)")
            return
        output_typ_path.write_text(rendered, encoding="utf-8")

    if check_only:
        typst.compile(str(output_typ_path))
        print("✓ Typst syntax & compilation check passed (check mode)")
        return

    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    typst.compile(str(output_typ_path), output=str(output_pdf_path))
    print(
        f"Compiled Typst resume -> {output_pdf_path} (age: {profile.get('age', 'N/A')} ans)"
    )


if __name__ == "__main__":
    main()
