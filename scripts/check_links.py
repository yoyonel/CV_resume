#!/usr/bin/env python3
"""Automated link validator for CV_resume static website, PDF and source templates."""

import argparse
import concurrent.futures
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0.0.0 Safari/537.36"
)

# Known domains that block automated bots with 403/429/999/111 even when page exists
BOT_PROTECTED_DOMAINS = [
    "linkedin.com",
    "www.linkedin.com",
    "archive.org",
    "web.archive.org",
    "intel.com",
    "www.intel.com",
    "youtu.be",
    "youtube.com",
    "www.youtube.com",
]

# XML Namespaces and Schemas that are not web pages
IGNORED_SCHEMAS = [
    "w3.org",
    "www.w3.org",
    "json-schema.org",
    "schemas.microsoft.com",
    "schema.org",
]


def extract_urls_from_text(text: str) -> set[str]:
    """Extract http(s) URLs from any text string."""
    pattern = r"https?://[a-zA-Z0-9_\-\.\:\@\%\+~#=\?\/&()]+"
    matches = re.findall(pattern, text)
    cleaned = set()
    for url in matches:
        u = url.rstrip(".,;'\">")
        if u.endswith(")") and u.count("(") < u.count(")"):
            u = u.rstrip(")")
        parsed = urllib.parse.urlparse(u)
        domain = parsed.netloc.lower()
        if any(ign in domain for ign in IGNORED_SCHEMAS):
            continue
        if u.startswith(("https://fonts.", "https://cdnjs.", "https://cdn.jsdelivr.")):
            continue
        if u:
            cleaned.add(u)
    return cleaned


def extract_from_text_file(file_path: Path) -> set[tuple[str, str]]:
    """Extract URLs from any text or markup file (HTML, Markdown, Jinja2, JSON)."""
    if not file_path.exists():
        return set()
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    urls = extract_urls_from_text(content)
    return {(u, str(file_path.name)) for u in urls}


def extract_from_pdf(file_path: Path) -> set[tuple[str, str]]:
    """Extract hyperlinked URIs directly from PDF binary objects."""
    if not file_path.exists():
        return set()
    data = file_path.read_bytes()
    # Match URIs with possible escaped parentheses in PDF syntax
    raw_matches = re.findall(rb"/URI\s*\(((?:\\\(|\\\)|[^)])+)\)", data)
    urls = set()
    for m in raw_matches:
        try:
            raw_str = m.decode("utf-8", errors="ignore").strip()
            # Unescape PDF literal string escaped parens
            u = raw_str.replace(r"\(", "(").replace(r"\)", ")")
            if u:
                urls.add((u, f"PDF ({file_path.name})"))
        except UnicodeDecodeError:
            pass
    return urls


def check_url(url: str, timeout: float = 10.0) -> dict:
    """Check a single URL status code and response time."""
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc.lower()

    result = {
        "url": url,
        "status": None,
        "ok": False,
        "error": None,
        "redirect_url": None,
        "elapsed_ms": 0,
        "note": "",
    }

    start_time = time.perf_counter()

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        },
    )

    # Domains that prefer GET over HEAD
    prefer_get = "archive.org" in domain or "linkedin.com" in domain

    for attempt in range(2):
        try:
            if prefer_get or attempt > 0:
                req.get_method = lambda: "GET"
            else:
                req.get_method = lambda: "HEAD"

            with urllib.request.urlopen(req, timeout=timeout) as response:
                result["status"] = response.getcode()
                result["ok"] = 200 <= response.getcode() < 400
                if response.geturl() != url:
                    result["redirect_url"] = response.geturl()
                result["error"] = None
                break
        except urllib.error.HTTPError as e:
            if any(d in domain for d in BOT_PROTECTED_DOMAINS) and e.code in (
                403,
                429,
                999,
            ):
                result["status"] = e.code
                result["ok"] = True
                result["note"] = f"Bot protected ({e.code})"
                result["error"] = None
                break
            if e.code in (405, 403, 501, 503, 400):
                prefer_get = True
                time.sleep(0.5)
                continue
            result["status"] = e.code
            result["error"] = f"HTTP {e.code}: {e.reason}"
            break
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            if any(d in domain for d in BOT_PROTECTED_DOMAINS):
                result["status"] = "PROT"
                result["ok"] = True
                result["note"] = f"Protected domain rate limit ({e})"
                result["error"] = None
                break
            result["error"] = str(e)
            if attempt == 0:
                time.sleep(1.0)
                continue

    result["elapsed_ms"] = int((time.perf_counter() - start_time) * 1000)
    return result


def collect_all_links(root_dir: Path) -> dict[str, list[str]]:
    """Collect all unique URLs categorized by source."""
    url_to_sources: dict[str, list[str]] = {}

    def add_link(u: str, src: str):
        u = u.strip()
        if not u.startswith("http://") and not u.startswith("https://"):
            return
        if u not in url_to_sources:
            url_to_sources[u] = []
        if src not in url_to_sources[u]:
            url_to_sources[u].append(src)

    # 1. Dist HTML
    html_dist = root_dir / "dist" / "index.html"
    for u, src in extract_from_text_file(html_dist):
        add_link(u, src)

    # 2. PDF Files
    for pdf_file in root_dir.glob("data/pdf/*/*.pdf"):
        for u, src in extract_from_pdf(pdf_file):
            add_link(u, src)

    # 3. Profile & Data JSON
    profile_json = root_dir / "data" / "profile.json"
    for u, src in extract_from_text_file(profile_json):
        add_link(u, src)

    # 4. Templates & Markdown
    for f in list(root_dir.glob("pandoc_resume/**/*.md*")) + list(
        root_dir.glob("site_template/**/*.j2")
    ):
        for u, src in extract_from_text_file(f):
            add_link(u, src)

    return url_to_sources


def main():
    parser = argparse.ArgumentParser(
        description="Check all hyperlinks in CV_resume site, PDF and sources."
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=8.0,
        help="HTTP timeout per link in seconds (default: 8.0s)",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=10,
        help="Max concurrent HTTP requests (default: 10)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Display all links including healthy ones",
    )
    args = parser.parse_args()

    root_dir = Path(__file__).resolve().parent.parent
    print(f"🔍 Collecting all hyperlinks across {root_dir.name}...")
    url_sources = collect_all_links(root_dir)

    total = len(url_sources)
    print(f"📡 Found {total} unique URLs across HTML, PDF, and templates.\n")

    results = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=args.concurrency
    ) as executor:
        future_to_url = {
            executor.submit(check_url, url, args.timeout): url for url in url_sources
        }
        for future in concurrent.futures.as_completed(future_to_url):
            res = future.result()
            res["sources"] = url_sources[res["url"]]
            results.append(res)

    results.sort(key=lambda x: (0 if not x["ok"] else 1, x["url"]))

    broken = [r for r in results if not r["ok"]]
    redirects = [r for r in results if r["ok"] and r["redirect_url"]]
    healthy = [r for r in results if r["ok"] and not r["redirect_url"]]

    # Print Table Summary
    print("=" * 80)
    print(f"{'STATUS':<10} | {'LATENCY':<8} | {'URL & SOURCES'}")
    print("=" * 80)

    for r in results:
        status_str = f"[{r['status'] or 'ERR'}]"
        if not r["ok"]:
            color_prefix = "❌ "
        elif r["note"]:
            color_prefix = "⚠️  "
        elif r["redirect_url"]:
            color_prefix = "↪️  "
        else:
            color_prefix = "✅ "

        sources_str = ", ".join(r["sources"][:3])
        if len(r["sources"]) > 3:
            sources_str += f" (+{len(r['sources']) - 3})"

        if not r["ok"] or args.verbose or r["redirect_url"]:
            print(
                f"{color_prefix}{status_str:<7} | {r['elapsed_ms']:>5}ms | {r['url']}"
            )
            print(f"          |          | ↳ Sources: {sources_str}")
            if r["redirect_url"]:
                print(f"          |          | ↳ Redirige vers: {r['redirect_url']}")
            if r["error"]:
                print(f"          |          | ↳ Erreur: {r['error']}")
            print("-" * 80)

    print("\n📊 Link Verification Summary :")
    print(f"  - Total URLs testées : {total}")
    print(f"  - Liens valides (200) : {len(healthy)}")
    print(f"  - Redirections (301/302) : {len(redirects)}")
    print(f"  - Liens brisés (404/ERR) : {len(broken)}")

    if broken:
        print("\n❌ Attention : Liens brisés détectés !")
        for b in broken:
            print(
                f"  - {b['url']} -> {b['error']} (sources: {', '.join(b['sources'])})"
            )
        sys.exit(1)
    else:
        print("\n✅ Tous les liens sont valides et accessibles !")
        sys.exit(0)


if __name__ == "__main__":
    main()
