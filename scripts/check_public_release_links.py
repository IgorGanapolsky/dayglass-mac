#!/usr/bin/env python3
"""Fail when the public site points at a missing release or a retired price."""

from __future__ import annotations

import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COPY_FILES = ("index.html", "pricing.html", "llms.txt")
BANNED = (
    "Free Forever",
    "free forever",
    "$0 / forever",
    "$0/mo forever",
    "Annual — $149",
    "Lifetime — $249",
    "$249 Once",
    "v2.2.0",
    "meetings/week forever",
    "Dayglass Ultra",
    "$9.99",
    "Roast Dayglass",
    "meetings a week",
    "Nothing leaves your laptop",
)
# Only Dayglass's own payment links may appear; any other Stripe link is a wiring mistake.
ALLOWED_CHECKOUT = (
    "https://buy.stripe.com/00w9AT0Ks0da18Ce6UeUU00",
    "https://buy.stripe.com/cNieVdbp64tq04y0g4eUU01",
    "https://buy.stripe.com/7sY28r8cUcZWg3w0g4eUU02",
)
LATEST_DMG = "https://github.com/IgorGanapolsky/dayglass-mac/releases/latest/download/Dayglass.dmg"


def _head(url: str) -> int:
    request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return int(response.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)


def main() -> int:
    errors: list[str] = []
    downloads: set[str] = set()
    for name in COPY_FILES:
        text = (ROOT / name).read_text(encoding="utf-8")
        for banned in BANNED:
            if banned in text:
                errors.append(f"{name} contains retired release copy")
                break
        for link in re.findall(r"https://buy\.stripe\.com/[A-Za-z0-9]+", text):
            if link not in ALLOWED_CHECKOUT:
                errors.append(f"{name} has a checkout link that is not Dayglass's own")
        for url in re.findall(
            r"https://github\.com/IgorGanapolsky/dayglass-mac/releases/(?:download|latest/download)/[^\"'\s)]+",
            text,
        ):
            downloads.add(url)
    if not downloads:
        errors.append("no download URLs found")
    for url in sorted(downloads):
        if url != LATEST_DMG:
            errors.append("a download URL is not the latest-release disk image")
            continue
        status = _head(url)
        if status not in (200, 302):
            errors.append(f"published disk image returned HTTP {status}")
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    if any(link not in home for link in ALLOWED_CHECKOUT):
        errors.append("a Dayglass checkout link is missing")
    if "$19" not in home or "$149" not in home or "$249" not in home:
        errors.append("current prices are missing")
    if errors:
        print("public release links failed:", file=sys.stderr)
        for item in errors:
            print(f"- {item}", file=sys.stderr)
        return 1
    print("public release links ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
