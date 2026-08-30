#!/usr/bin/env python3
# /// script
# dependencies = [
#   "jinja2>=3.1.0",
# ]
# ///
import json
import os
import sys
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print(
        "Error: jinja2 is required. Run 'pip install jinja2' or use 'uv run scripts/render_resume.py'",
        file=sys.stderr,
    )
    sys.exit(1)


sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import calculate_age


def main():
    root_dir = Path(__file__).resolve().parent.parent
    profile_path = root_dir / "data" / "profile.json"
    template_dir = root_dir / "pandoc_resume"
    template_path = template_dir / "resume.md.j2"
    output_path = template_dir / "resume.md"

    if not profile_path.exists():
        print(f"Error: Profile file not found at {profile_path}", file=sys.stderr)
        sys.exit(1)

    with open(profile_path, "r", encoding="utf-8") as f:
        profile = json.load(f)

    # Allow environment variable overrides
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

    if "birthdate" in profile:
        profile["age"] = calculate_age(profile["birthdate"])

    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=False,
    )
    env.filters["age"] = calculate_age

    template = env.get_template("resume.md.j2")
    rendered = template.render(profile=profile)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered)

    print(
        f"Rendered {template_path.name} -> {output_path.name} (age: {profile.get('age', 'N/A')} ans)"
    )


if __name__ == "__main__":
    main()
