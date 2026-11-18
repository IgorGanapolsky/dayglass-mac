#!/usr/bin/env python3
"""Click every link and button on the public pages in headless Chromium, at phone and desktop widths.

Prints where each control lands. Never opens buy.stripe.com or checkout.stripe.com in a browser:
those requests are aborted, and the link is checked with a plain HTTP request instead.
Usage: python3 scripts/click_audit.py [--base http://127.0.0.1:8765]
"""

from __future__ import annotations

import argparse
import functools
import http.server
import threading
import urllib.error
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES = ("/", "/pricing.html", "/granola-alternative.html", "/fathom-alternative.html", "/otter-alternative.html")
WIDTHS = {"phone": (390, 844), "desktop": (1280, 900)}
STRIPE = ("buy.stripe.com", "checkout.stripe.com")
# The audit must not add machine events to the production funnel.
ANALYTICS = ("posthog.com", "/api/analytics/")


def http_status(url: str) -> str:
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "site-click-audit"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
            return str(response.status)
    except urllib.error.HTTPError as exc:
        return str(exc.code)
    except Exception as exc:  # noqa: BLE001
        return f"error {type(exc).__name__}"


def serve() -> tuple[http.server.ThreadingHTTPServer, str]:
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args: object) -> None:
            return

    handler = functools.partial(Quiet, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"


def audit(base: str) -> list[tuple[str, str, str, str, str]]:
    rows: list[tuple[str, str, str, str, str]] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for label, (w, h) in WIDTHS.items():
            for path in PAGES:
                ctx = browser.new_context(viewport={"width": w, "height": h})
                ctx.route("**/*", lambda route: route.abort() if any(s in route.request.url for s in STRIPE + ANALYTICS) else route.continue_())
                probe = ctx.new_page()
                probe.goto(base + path, wait_until="domcontentloaded")
                probe.wait_for_timeout(400)
                n = probe.evaluate("document.querySelectorAll('a[href], button, [onclick], summary').length")
                probe.close()
                for i in range(n):
                    page = ctx.new_page()
                    page.on("dialog", lambda d: d.dismiss())
                    page.goto(base + path, wait_until="domcontentloaded")
                    page.wait_for_timeout(200)
                    el = page.locator("a[href], button, [onclick], summary").nth(i)
                    desc = page.evaluate(
                        "e => (e.innerText||e.getAttribute('aria-label')||e.id||e.tagName).trim().slice(0,40).replace(/\\s+/g,' ')",
                        el.element_handle(),
                    )
                    href = el.get_attribute("href") or ""
                    buy = el.get_attribute("data-buy")
                    if ONLY and ONLY.lower() not in desc.lower():
                        page.close()
                        continue
                    if any(s in href for s in STRIPE):
                        rows.append((label, path, desc, href.split("?")[0], f"stripe link, HTTP GET {http_status(href)} (not opened in browser)"))
                        page.close()
                        continue
                    if href.startswith(("http", "mailto:")) and not href.startswith(base):
                        rows.append((label, path, desc, href.split("?")[0][:80], f"external link, HTTP {http_status(href) if href.startswith('http') else 'mailto'} (not followed in browser)"))
                        page.close()
                        continue
                    blocked: list[str] = []
                    page.on("requestfailed", lambda r, b=blocked: b.append(r.url) if any(x in r.url for x in STRIPE) else None)
                    before = page.url
                    try:
                        if not el.is_visible():
                            rows.append((label, path, desc, href[:60], "hidden at this width (skipped)"))
                            page.close()
                            continue
                        el.click(timeout=3000, no_wait_after=True)
                        page.wait_for_timeout(300)
                        after = page.url.replace(base, "") or "/"
                        if blocked:
                            host = blocked[0].split("/")[2]
                            rows.append((label, path, desc, href[:60], f"checkout redirect to {host}; request blocked, not opened"))
                            page.close()
                            continue
                        modal = page.evaluate("!!document.querySelector('.modal.open, .modal[style*=\"display: flex\"], .modal.show, dialog[open]')")
                        outcome = f"navigated to {after}" if page.url != before else ("same page, modal/panel opened" if modal else "same page (scroll, toggle or no visible change)")
                        rows.append((label, path, desc, href[:60], outcome))
                    except Exception as exc:  # noqa: BLE001
                        if buy and blocked:
                            # A buy button starts the Stripe flow; the audit aborts that request on purpose.
                            rows.append((label, path, desc, href[:60], f"Stripe checkout (not opened); request to {blocked[0].split('/')[2]} aborted"))
                            page.close()
                            continue
                        rows.append((label, path, desc, href[:60], f"ERROR {type(exc).__name__}"))
                    page.close()
                ctx.close()
        browser.close()
    return rows


ONLY = ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base")
    parser.add_argument("--only", default="", help="audit only controls whose text contains this")
    args = parser.parse_args()
    global ONLY
    ONLY = args.only
    server = None
    base = args.base
    if not base:
        server, base = serve()
    rows = audit(base)
    for r in rows:
        print(" | ".join(r))
    errors = [r for r in rows if r[4].startswith("ERROR") or " 404" in r[4] or "HTTP 4" in r[4] or "HTTP 5" in r[4]]
    print(f"{len(rows)} controls, {len(errors)} problems")
    if server:
        server.shutdown()
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
