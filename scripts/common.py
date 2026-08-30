"""Shared profile processing and helper functions for CV resume scripts."""

from datetime import date, datetime, timezone
from typing import Any


def calculate_age(birthdate_val: str | date | datetime) -> int:
    """Calculate integer age in years from a birthdate string or date/datetime object."""
    if isinstance(birthdate_val, str):
        bdate = (
            datetime.strptime(birthdate_val, "%Y-%m-%d")
            .replace(tzinfo=timezone.utc)
            .date()
        )
    elif isinstance(birthdate_val, (datetime, date)):
        bdate = (
            birthdate_val if isinstance(birthdate_val, date) else birthdate_val.date()
        )
    else:
        raise TypeError(f"Unsupported birthdate format: {type(birthdate_val)}")
    today = datetime.now(tz=timezone.utc).date()
    return (
        today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))
    )


def process_profile_data(profile: dict[str, Any]) -> dict[str, Any]:
    """Enrich profile dictionary with calculated age, escaped email, and skill seniority."""
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
