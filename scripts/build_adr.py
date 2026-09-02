import argparse
from pathlib import Path

from adr_viewer.parse import parse_adr_files
from adr_viewer.render import generate_content


def build_adr_docs(
    output_path: Path | str = "dist/adr/index.html", all_docs: bool = False
) -> Path:
    """Compile static ADR documentation into specified output HTML file."""
    pattern = "docs/*.md" if all_docs else "docs/*_adr_[0-9][0-9][0-9][0-9]_*.md"
    adrs = parse_adr_files(pattern)

    root_dir = Path(__file__).resolve().parent.parent
    tpl_dir = str(root_dir / "docs" / "templates" / "adr")

    content = generate_content(adrs, tpl_dir, "CV_resume Architecture Decision Records")

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    print(
        f"✓ Documentation statique des ADRs ({len(adrs)} documents) générée dans : {out}"
    )
    return out


def main():
    parser = argparse.ArgumentParser(description="Build static ADR documentation.")
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
    args = parser.parse_args()
    build_adr_docs(args.output, args.all_docs)


if __name__ == "__main__":
    main()
