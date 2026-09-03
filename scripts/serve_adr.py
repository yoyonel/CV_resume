import argparse
import socket
import sys

from adr_viewer.server import run_server

try:
    from scripts.build_adr import load_adrs_and_render
except ImportError:
    from build_adr import load_adrs_and_render


def find_free_port(start_port: int = 8088, max_attempts: int = 20) -> int:
    """Find the first available TCP port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return start_port


def main() -> None:
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

    adrs, content = load_adrs_and_render(all_docs=args.all_docs)

    if not adrs:
        print("⚠️  Aucun ADR trouvé.")
        sys.exit(1)

    print("=" * 80)
    print("  🧭 VISUALISEUR INTERACTIF D'ARCHITECTURE DECISION RECORDS (ADR)")
    print("=" * 80)
    print(f"  • ADRs chargés : {len(adrs)}")
    for a in adrs:
        status_str = getattr(a, "status", "UNKNOWN").upper()
        title_str = getattr(a, "title", "Sans titre")
        print(f"    - [{status_str:<8}] {title_str}")
    print(f"\n  🚀 Serveur démarré sur : http://localhost:{port}/")
    print("  (Appuyez sur Ctrl+C pour arrêter le serveur)")
    print("=" * 80)

    run_server(content, port)


if __name__ == "__main__":
    main()
