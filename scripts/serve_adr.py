import argparse
import socket
import sys
from pathlib import Path

from adr_viewer.parse import parse_adr_files
from adr_viewer.render import generate_content
from adr_viewer.server import run_server


def find_free_port(start_port: int = 8088, max_attempts: int = 20) -> int:
    """Find the first available TCP port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return start_port


def main():
    parser = argparse.ArgumentParser(
        description="Serve interactive ADR viewer locally."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Preferred port (defaults to next free port from 8088)",
    )
    parser.add_argument(
        "--all-docs",
        action="store_true",
        help="Include all markdown documents in docs/ instead of only numbered ADRs",
    )
    args = parser.parse_args()

    port = args.port if args.port is not None else find_free_port(8088)

    pattern = "docs/*.md" if args.all_docs else "docs/*_adr_[0-9][0-9][0-9][0-9]_*.md"
    adrs = parse_adr_files(pattern)

    if not adrs:
        print(f"⚠️  Aucun ADR trouvé avec le pattern : {pattern}")
        sys.exit(1)

    print("=" * 80)
    print("  🧭 VISUALISEUR INTERACTIF D'ARCHITECTURE DECISION RECORDS (ADR)")
    print("=" * 80)
    print(f"  • ADRs chargés : {len(adrs)}")
    for a in adrs:
        print(f"    - [{a.status.upper():<8}] {a.title}")
    print(f"\n  🚀 Serveur démarré sur : http://localhost:{port}/")
    print("  (Appuyez sur Ctrl+C pour arrêter le serveur)")
    print("=" * 80)

    root_dir = Path(__file__).resolve().parent.parent
    tpl_dir = str(root_dir / "docs" / "templates" / "adr")

    content = generate_content(adrs, tpl_dir, "CV_resume Architecture Decision Records")
    run_server(content, port)


if __name__ == "__main__":
    main()
