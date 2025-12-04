from __future__ import annotations

import argparse
import getpass
import os
import sys
import time
import requests
from collections import defaultdict
from typing import List, Dict


def fetch_starred(username: str, token: str | None = None, per_page: int = 100) -> List[dict]:
    session = requests.Session()
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    repos: List[dict] = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/starred"
        resp = session.get(url, headers=headers, params={"per_page": per_page, "page": page})
        if resp.status_code == 404:
            raise SystemExit(f"User '{username}' not found (404).")
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        repos.extend(data)
        page += 1

        try:
            remaining = int(resp.headers.get("X-RateLimit-Remaining", "0"))
            reset = int(resp.headers.get("X-RateLimit-Reset", "0"))
        except Exception:
            remaining = 0
            reset = 0

        if remaining <= 1 and reset > int(time.time()):
            wait = max(0, reset - int(time.time()) + 1)
            print(f"Rate limit near exhaustion — sleeping {wait}s until reset.", file=sys.stderr)
            time.sleep(wait)
        else:
            time.sleep(1)

    return repos


def group_by_language(repos: List[dict]) -> Dict[str, List[dict]]:
    groups: Dict[str, List[dict]] = defaultdict(list)
    for r in repos:
        lang = r.get("language") or "Autres"
        groups[lang].append(r)
    return groups


def write_markdown(username: str, groups: Dict[str, List[dict]], out_path: str) -> None:
    total = sum(len(v) for v in groups.values())
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# Starred repos de {username}\n\n")
        for lang, items in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            f.write(f"## {lang} — {len(items)} repos\n\n")
            for r in items:
                name = r.get("full_name")
                desc = (r.get("description") or "").replace("\n", " ")
                url = r.get("html_url")
                f.write(f"- **[{name}]({url})** — {desc}\n")
            f.write("\n")

    print(f"Fini — {total} repos exportés dans {out_path}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Export GitHub starred repos to Markdown.")
    p.add_argument("--username", "-u", required=True, help="GitHub username to fetch starred repos for")
    p.add_argument("--token", "-t", help="GitHub token (or set env GITHUB_TOKEN)")
    p.add_argument("--per-page", type=int, default=100, help="Items per page (max 100)")
    p.add_argument("--output", "-o", default="starred.md", help="Output markdown file path")
    return p.parse_args()


def main() -> None:
    if len(sys.argv) == 1:
        interactive_menu()
        return

    args = parse_args()
    token = args.token or os.environ.get("GITHUB_TOKEN")
    if args.per_page <= 0 or args.per_page > 100:
        print("--per-page must be between 1 and 100", file=sys.stderr)
        sys.exit(2)

    repos = fetch_starred(args.username, token=token, per_page=args.per_page)
    groups = group_by_language(repos)
    write_markdown(args.username, groups, args.output)


def interactive_menu() -> None:
    """Simple interactive menu to configure and run the exporter."""
    username: str | None = None
    token: str | None = os.environ.get("GITHUB_TOKEN")
    per_page: int = 100
    output: str = "starred.md"

    def show() -> None:
        print("\nCurrent configuration:")
        print(f"  Username : {username or '<not set>'}")
        print(f"  Token    : {'<set>' if token else '<not set>'}")
        print(f"  Per page : {per_page}")
        print(f"  Output   : {output}\n")

    while True:
        show()
        print("Menu:")
        print("  1) Set username")
        print("  2) Set token (hidden input)")
        print("  3) Set per-page (1-100)")
        print("  4) Set output file")
        print("  5) Run export now")
        print("  6) Quit")
        choice = input("Choose an option [1-6]: ").strip()
        if choice == "1":
            val = input("GitHub username: ").strip()
            username = val or username
        elif choice == "2":
            tok = getpass.getpass("GitHub token (empty to clear): ")
            token = tok or None
        elif choice == "3":
            try:
                v = int(input("Per page (1-100): ").strip())
                if 1 <= v <= 100:
                    per_page = v
                else:
                    print("Value out of range; must be 1..100")
            except ValueError:
                print("Invalid number")
        elif choice == "4":
            out = input("Output file path: ").strip()
            if out:
                output = out
        elif choice == "5":
            if not username:
                print("Username is required before running.")
                continue
            try:
                repos = fetch_starred(username, token=token, per_page=per_page)
                groups = group_by_language(repos)
                write_markdown(username, groups, output)
            except SystemExit as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")
            cont = input("Run again? [y/N]: ").strip().lower()
            if cont != "y":
                break
        elif choice == "6":
            break
        else:
            print("Invalid choice, please select 1..6")


if __name__ == "__main__":
    main()
