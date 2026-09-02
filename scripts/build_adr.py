import argparse
from pathlib import Path

from adr_viewer.parse import parse_adr_files
from adr_viewer.render import generate_content


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

    pattern = "docs/*.md" if args.all_docs else "docs/*_adr_[0-9][0-9][0-9][0-9]_*.md"
    adrs = parse_adr_files(pattern)

    root_dir = Path(__file__).resolve().parent.parent
    tpl_dir = str(root_dir / "docs" / "templates" / "adr")

    content = generate_content(adrs, tpl_dir, "CV_resume Architecture Decision Records")

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(
        f"✓ Documentation statique des ADRs ({len(adrs)} documents) générée dans : {out_path}"
    )


if __name__ == "__main__":
    main()
