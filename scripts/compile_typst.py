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
from datetime import date, datetime, timezone
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


def calculate_age(birthdate_val: str | date | datetime) -> int:
    if isinstance(birthdate_val, str):
        bdate = datetime.strptime(birthdate_val, "%Y-%m-%d").replace(tzinfo=timezone.utc).date()
    elif isinstance(birthdate_val, (datetime, date)):
        bdate = birthdate_val if isinstance(birthdate_val, date) else birthdate_val.date()
    else:
        raise TypeError(f"Unsupported birthdate format: {type(birthdate_val)}")
    today = datetime.now(tz=timezone.utc).date()
    return today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))


def process_profile_data(profile: dict) -> dict:
    current_year = datetime.now(tz=timezone.utc).year
    if "birthdate" in profile:
        profile["age"] = calculate_age(profile["birthdate"])
    if "email" in profile:
        profile["email_escaped"] = profile["email"].replace("@", "\\@")
    if "skills_seniority" in profile:
        for item in profile["skills_seniority"]:
            end = item.get("end_year") or current_year
            item["years"] = max(1, end - item["start_year"])
    return profile


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

    with open(output_typ_path, "w", encoding="utf-8") as f:
        f.write(rendered)

    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    typst.compile(str(output_typ_path), output=str(output_pdf_path))
    print(f"Compiled Typst resume -> {output_pdf_path} (age: {profile.get('age', 'N/A')} ans)")


if __name__ == "__main__":
    main()
