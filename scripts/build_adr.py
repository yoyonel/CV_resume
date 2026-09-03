import argparse
from pathlib import Path
from typing import Any

from adr_viewer.parse import parse_adr_files
from adr_viewer.render import generate_content


def load_adrs_and_render(
    all_docs: bool = False,
) -> tuple[list[Any], str]:
    """Parse ADR files and render HTML content using project template."""
    pattern = "docs/*.md" if all_docs else "docs/*_adr_[0-9][0-9][0-9][0-9]_*.md"
    adrs = parse_adr_files(pattern)
    root_dir = Path(__file__).resolve().parent.parent
    tpl_dir = str(root_dir / "docs" / "templates" / "adr")
    content = generate_content(adrs, tpl_dir, "CV_resume Architecture Decision Records")
    return adrs, content


def build_adr_docs(
    output_path: Path | str = "dist/adr/index.html", all_docs: bool = False
) -> Path:
    """Compile static ADR documentation into specified output HTML file."""
    adrs, content = load_adrs_and_render(all_docs=all_docs)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    print(
        f"✓ Documentation statique des ADRs ({len(adrs)} documents) générée dans : {out}"
    )
    return out


def list_adrs(all_docs: bool = False) -> None:
    """Display a formatted list of all Architecture Decision Records in the terminal."""
    pattern = "docs/*.md" if all_docs else "docs/*_adr_[0-9][0-9][0-9][0-9]_*.md"
    adrs = parse_adr_files(pattern)
    if not adrs:
        print(f"\n⚠️  Aucun ADR trouvé avec le pattern : {pattern}")
        return

    print(f"\n📂 Architecture Decision Records ({len(adrs)} documents trouvés) :")
    print("-" * 80)
    for a in adrs:
        status_str = getattr(a, "status", "UNKNOWN").upper()
        title_str = getattr(a, "title", "Sans titre")
        print(f"  • [{status_str:<9}] {title_str}")
    print("-" * 80)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build or list static ADR documentation."
    )
    parser.add_argument(
        "--output",
        default="dist/adr/index.html",
        help="Output HTML path (default: dist/adr/index.html)",
    )
    parser.add_argument(
        "--all-docs",
        action="store_true",
        help="Include all markdown documents in docs/ instead of only numbered ADRs",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all Architecture Decision Records and their statuses",
    )
    args = parser.parse_args()

    if args.list:
        list_adrs(args.all_docs)
    else:
        build_adr_docs(args.output, args.all_docs)


if __name__ == "__main__":
    main()
