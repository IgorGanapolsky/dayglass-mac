"""Headless checks of the page's analytics: a normal redirect to Stripe is not an abandon,
and automated visits send nothing to the production funnel. Run: python3 -m unittest discover tests

Stripe requests are aborted, so no checkout session is ever created.
"""

from __future__ import annotations

import functools
import http.server
import threading
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SINK = "window.__events = []; window.__DG_EVENT_SINK = (n, p) => window.__events.push([n, p]);"


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):  # noqa: D102
        return


class SiteEvents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT)))
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.server.shutdown()

    def _page(self, path):
        ctx = self.browser.new_context()
        self.addCleanup(ctx.close)
        posts = []
        ctx.route("**/*stripe.com/**", lambda r: r.abort())
        ctx.route("**/*posthog.com/**", lambda r: (posts.append(r.request.url), r.abort()))
        page = ctx.new_page()
        page.add_init_script(SINK)
        page.goto(self.base + path)
        return page, posts

    def test_stripe_redirect_is_a_click_not_an_abandon(self):
        for path in ("/", "/pricing.html"):
            with self.subTest(path=path):
                page, _ = self._page(path)
                # One synchronous step: click, then the pagehide the real redirect fires.
                names = page.evaluate(
                    "() => { beginStripeCheckout('pro_annual', 149);"
                    " window.dispatchEvent(new Event('pagehide'));"
                    " return window.__events.map(e => e[0]); }"
                )
                self.assertIn("checkout_initiated", names)
                self.assertNotIn("checkout_abandoned", names)

    def test_failed_redirect_does_not_hide_a_later_real_abandon(self):
        for path in ("/", "/pricing.html"):
            with self.subTest(path=path):
                ctx = self.browser.new_context()
                self.addCleanup(ctx.close)
                ctx.route("**/*stripe.com/**", lambda r: r.fulfill(status=204))  # a 204 navigation leaves the page where it is: a redirect that did not happen
                ctx.route("**/*posthog.com/**", lambda r: r.abort())
                page = ctx.new_page()
                page.add_init_script(SINK)
                page.goto(self.base + path)
                page.evaluate("beginStripeCheckout('pro_annual', 149)")
                page.wait_for_timeout(5300)  # the redirect failed and the visitor is still here
                page.evaluate("window.dispatchEvent(new Event('pagehide'))")
                names = [e[0] for e in page.evaluate("window.__events")]
                self.assertIn("checkout_abandoned", names)

    def test_coming_back_from_the_back_button_resets_the_guard(self):
        ctx = self.browser.new_context()
        self.addCleanup(ctx.close)
        ctx.route("**/*stripe.com/**", lambda r: r.fulfill(status=204))
        page = ctx.new_page()
        page.goto(self.base + "/")
        page.evaluate("beginStripeCheckout('pro_annual', 149)")
        self.assertTrue(page.evaluate("redirectingToStripe"))
        page.evaluate("window.dispatchEvent(new PageTransitionEvent('pageshow', {persisted: true}))")
        self.assertFalse(page.evaluate("redirectingToStripe"))

    def test_leaving_without_a_redirect_still_counts_as_abandon(self):
        page, _ = self._page("/")
        page.evaluate("checkoutStarted = true; checkoutPlan = 'pro_annual';")
        page.evaluate("window.dispatchEvent(new Event('pagehide'))")
        self.assertIn("checkout_abandoned", [e[0] for e in page.evaluate("window.__events")])

    def test_headless_visit_sends_nothing_to_posthog(self):
        for path in ("/", "/pricing.html"):
            with self.subTest(path=path):
                page, posts = self._page(path)
                page.evaluate("trackPricingEvent('pricing_page_viewed')")
                page.wait_for_timeout(300)
                self.assertEqual(posts, [])


if __name__ == "__main__":
    unittest.main()
