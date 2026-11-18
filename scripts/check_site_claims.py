#!/usr/bin/env python3
"""Fail when a public page carries a covert-recording badge or a retired competitor claim.

By default it reads the pages in this repo (the site is plain static files, so these are the
built pages). With --base https://dayglass.io it fetches the live pages over HTTP instead.
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = (
    "index.html",
    "pricing.html",
    "privacy.html",
    "granola-alternative.html",
    "otter-alternative.html",
    "fathom-alternative.html",
    "limitless-alternative.html",
    "rewind-alternative.html",
    "llms.txt",
)
BANNED = (
    "Stealth",
    "Invisible on Screen Share",
    "No local MCP",
    # Paranoid mode never runs on the cloud Ask AI path (chat_engine.py applies only the Never-share list).
    "Paranoid Mode",
    "Paranoid mode",
    "100% On-Device",
    "swapped for placeholders",
    "swapped out for placeholders",
    # capture.py skips a keyword list of apps and titles, not private browser windows.
    "private windows",
    "private browser windows",
)


def load(name: str, base: str | None) -> str:
    if base:
        url = f"{base.rstrip('/')}/{name.removesuffix('.html')}" if name.endswith(".html") else f"{base.rstrip('/')}/{name}"
        if name == "index.html":
            url = base.rstrip("/") + "/"
        with urllib.request.urlopen(url, timeout=30) as response:  # noqa: S310
            return response.read().decode("utf-8", "replace")
    return (ROOT / name).read_text(encoding="utf-8")


def find_banned(text: str) -> list[str]:
    lowered = text.lower()
    return [item for item in BANNED if item.lower() in lowered]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", help="fetch live pages from this origin instead of reading files")
    args = parser.parse_args(argv)
    errors = []
    names = list(PAGES) + ["server.json"]
    if not args.base:
        names += sorted(str(p.relative_to(ROOT)) for p in (ROOT / "Casks").glob("*.rb"))
    for name in names:
        if not args.base and not (ROOT / name).exists():
            continue
        for hit in find_banned(load(name, args.base)):
            errors.append(f"{name} contains {hit!r}")
    if errors:
        print("site claims check failed:", file=sys.stderr)
        for item in errors:
            print(f"- {item}", file=sys.stderr)
        return 1
    print("site claims ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
