"""Only dayglass.io sends analytics, every event says it is Dayglass, the pricing view counts only when seen,
buy buttons say what they charge, and feedback goes to a private inbox.
Run one file at a time: python3 -m unittest tests.test_analytics_hosts

Stripe, PostHog and the ThumbGate ping are all intercepted, so nothing leaves this machine.
"""

from __future__ import annotations

import functools
import http.server
import json
import threading
import unittest
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SINK = "window.__events = []; window.__DG_EVENT_SINK = (n, p) => window.__events.push([n, p]);"
NOT_A_ROBOT = "Object.defineProperty(navigator, 'webdriver', {get: () => false});"
OUTBOUND = ("posthog.com", "thumbgate.ai", "stripe.com", "clarity.ms", "paradigmmachines.ai")


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):  # noqa: D102
        return


class AnalyticsHosts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT)))
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.local = f"http://127.0.0.1:{cls.server.server_address[1]}"
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.server.shutdown()

    def _context(self, fake_origin=None, robot=True):
        """A context whose outbound analytics are recorded and blocked. fake_origin serves the local files under that host."""
        ctx = self.browser.new_context()
        self.addCleanup(ctx.close)
        sent: list[tuple[str, str]] = []

        def outbound(route):
            sent.append((route.request.url, route.request.post_data or ""))
            route.abort()

        for host in OUTBOUND:
            ctx.route(f"**/*{host}/**", outbound)
        if fake_origin:
            host = urlparse(fake_origin).netloc

            def serve(route):
                path = urlparse(route.request.url).path.lstrip("/") or "index.html"
                if path.endswith("/"):
                    path += "index.html"
                target = ROOT / path
                if target.is_file():
                    route.fulfill(path=str(target), content_type="text/html" if path.endswith(".html") else None)
                else:
                    route.fulfill(status=404, body="")

            ctx.route(f"{fake_origin}/**", serve)
        if not robot:
            ctx.add_init_script(NOT_A_ROBOT)
        ctx.add_init_script(SINK)
        return ctx, sent

    def test_hosts_other_than_dayglass_io_send_nothing(self):
        for origin in (None, "https://example.test", "https://igorganapolsky.github.io", "https://dayglass.io.evil.test"):
            for path in ("/", "/pricing.html"):
                with self.subTest(origin=origin, path=path):
                    ctx, sent = self._context(origin, robot=False)  # a real-looking browser, only the host differs
                    page = ctx.new_page()
                    page.goto((origin or self.local) + path)
                    page.evaluate("trackPricingEvent('pricing_page_viewed'); trackPricingEvent('checkout_initiated');")
                    page.wait_for_timeout(300)
                    page.wait_for_timeout(200)
                    analytics = [u for u, _ in sent if "stripe.com" not in u]
                    self.assertEqual(analytics, [])

    def test_dayglass_io_sends_events_tagged_dayglass(self):
        for origin in ("https://dayglass.io", "https://www.dayglass.io"):
            with self.subTest(origin=origin):
                ctx, sent = self._context(origin, robot=False)
                page = ctx.new_page()
                page.goto(origin + "/?lnd_product=thumbgate")
                page.evaluate("trackPricingEvent('hero_pro_clicked')")
                page.wait_for_timeout(400)
                posts = [json.loads(b) for u, b in sent if "posthog.com" in u and b]
                self.assertTrue(posts, "dayglass.io should still send to PostHog")
                for body in posts:
                    props = body["properties"]
                    self.assertEqual((props["product"], props["app"], props["lnd_product"]), ("dayglass",) * 3)

    def test_page_talks_only_to_posthog_and_dayglass_io(self):
        allowed = {"dayglass.io", "www.dayglass.io", "us.i.posthog.com", "www.clarity.ms", "t.paradigmmachines.ai"}
        for origin in ("https://dayglass.io", "https://www.dayglass.io"):
            for path in ("/", "/pricing.html"):
                with self.subTest(origin=origin, path=path):
                    ctx, _ = self._context(origin, robot=False)
                    hosts: set[str] = set()
                    ctx.on("request", lambda r: hosts.add(urlparse(r.url).hostname or ""))
                    page = ctx.new_page()
                    page.goto(origin + path)
                    page.evaluate("document.getElementById('pricing').scrollIntoView()")
                    page.evaluate("trackPricingEvent('pricing_page_viewed'); trackPricingEvent('hero_pro_clicked'); trackPricingEvent('checkout_initiated')")
                    page.wait_for_timeout(500)
                    self.assertEqual(hosts - allowed, set())
                    self.assertIn("us.i.posthog.com", hosts, "the real site must still reach PostHog")
        for name in ("index.html", "pricing.html"):
            self.assertNotIn("thumbgate", (ROOT / name).read_text().lower())

    def test_both_pages_use_the_same_posthog_key_on_dayglass_io(self):
        keys = {}
        for path in ("/", "/pricing.html"):
            ctx, sent = self._context("https://dayglass.io", robot=False)
            page = ctx.new_page()
            page.goto("https://dayglass.io" + path)
            page.evaluate("trackPricingEvent('checkout_initiated', {plan: 'pro_annual'})")
            page.wait_for_timeout(400)
            bodies = [json.loads(b) for u, b in sent if "posthog.com" in u and b]
            self.assertTrue(bodies, f"{path} sent nothing to PostHog")
            keys[path] = {b["api_key"] for b in bodies}
        self.assertEqual(keys["/"], keys["/pricing.html"])
        self.assertTrue(next(iter(keys["/"])).startswith("phc_"))

    def test_arrival_and_pricing_exposure_are_separate_and_never_start_checkout(self):
        count = "name => window.__events.filter(e => e[0] === name).length"
        for path in ("/", "/pricing.html"):
            with self.subTest(path=path):
                ctx, sent = self._context()
                page = ctx.new_page()
                page.goto(self.local + path)
                page.wait_for_timeout(400)
                self.assertEqual(page.evaluate(count, "dayglass_site_arrival"), 1)
                if path == "/":
                    self.assertEqual(page.evaluate(count, "pricing_page_viewed"), 0)
                else:
                    self.assertEqual(page.evaluate(count, "pricing_page_viewed"), 1)  # legacy metric, load only
                self.assertEqual(page.evaluate(count, "pricing_section_seen"), 0, "not seen yet")
                page.locator(".cta-row a:has-text('See plans')").first.click()
                page.wait_for_function("window.__events.some(e => e[0] === 'pricing_section_seen')")
                page.evaluate("window.scrollTo(0, 0)")
                page.evaluate("document.querySelector('#pricing h2').scrollIntoView()")
                page.wait_for_timeout(300)
                self.assertEqual(page.evaluate(count, "pricing_section_seen"), 1, "exposure is recorded once")
                self.assertEqual(page.evaluate(count, "checkout_initiated"), 0)
                self.assertFalse([u for u, _ in sent if "stripe.com" in u])

    def test_call_to_task_example_replaces_the_savings_calculator(self):
        for path in ("/", "/pricing.html"):
            with self.subTest(path=path):
                ctx, _ = self._context()
                page = ctx.new_page()
                page.goto(self.local + path)
                body = page.inner_text("body")
                self.assertIn("From a client call to a task", body)
                self.assertIn("made-up details", body)
                self.assertEqual(page.locator("#roi-calculator, input[type=range]").count(), 0)
                self.assertNotIn("80%", body)

    def test_nav_and_hero_buttons_go_to_plans_and_buy_buttons_name_the_price(self):
        for path in ("/", "/pricing.html"):
            with self.subTest(path=path):
                ctx, sent = self._context()
                page = ctx.new_page()
                page.goto(self.local + path)
                for sel in ("nav a:has-text('See plans')", ".cta-row a:has-text('See plans')"):
                    link = page.locator(sel).first
                    self.assertEqual(link.get_attribute("href"), "#pricing")
                    self.assertIsNone(link.get_attribute("data-buy"), "must not start a checkout")
                self.assertEqual(page.locator("a:text-is('Get Pro')").count(), 0)
                for button in page.locator("[data-buy]").all():
                    text = button.inner_text()
                    self.assertRegex(text, r"\$\d+", f"buy button without an amount: {text!r}")
                page.locator(".cta-row a:has-text('See plans')").first.click()
                page.wait_for_timeout(200)
                self.assertFalse([u for u, _ in sent if "stripe.com" in u], "See plans must not reach Stripe")

    def test_feedback_is_private_and_the_public_thread_is_a_small_footer_link(self):
        for path in ("/", "/pricing.html"):
            with self.subTest(path=path):
                ctx, _ = self._context()
                page = ctx.new_page()
                page.goto(self.local + path)
                mail = page.locator("a[href^='mailto:igor@dayglass.io'][href*='What%20stopped%20me']")
                self.assertEqual(mail.count(), 1)
                self.assertEqual(mail.get_attribute("href"), "mailto:igor@dayglass.io?subject=What%20stopped%20me")
                body = page.inner_text("body")
                self.assertNotIn("public thread is the feedback", body)
                self.assertNotIn("What's wrong", body)
                self.assertEqual(page.locator("footer a[href$='/discussions/10']").count(), 1)
                self.assertEqual(page.locator("section a[href$='/discussions/10']").count(), 0)

    def test_clarity_loads_only_for_real_visitors_on_dayglass_io(self):
        pages = ("/", "/pricing.html", "/privacy.html", "/otter-alternative.html")
        def clarity_requests(origin, path, robot=False, owner=False):
            ctx, sent = self._context(origin, robot=robot)
            page = ctx.new_page()
            page.goto((origin or self.local) + path + ("?dg_owner=1" if owner else ""))
            page.wait_for_timeout(400)
            return [u for u, _ in sent if "clarity.ms" in u]
        for path in pages:
            with self.subTest(path=path):
                tags = clarity_requests("https://dayglass.io", path)
                self.assertEqual(tags, ["https://www.clarity.ms/tag/zjac22a5n1"])
                self.assertEqual(clarity_requests(None, path), [], "localhost must not load Clarity")
                self.assertEqual(clarity_requests("https://dayglass.io.evil.test", path), [])
                self.assertEqual(clarity_requests("https://dayglass.io", path, robot=True), [], "automated browsers")
                self.assertEqual(clarity_requests("https://dayglass.io", path, owner=True), [], "owner browsers")
        self.assertIn("Microsoft Clarity", (ROOT / "privacy.html").read_text())

    def test_orion_loads_only_for_real_visitors_and_its_agent_link_on_dayglass_io(self):
        tag = "https://t.paradigmmachines.ai/86vwvzk3zm3tvthbghw3.js"
        def orion_requests(origin, path, robot=False, query=""):
            ctx, sent = self._context(origin, robot=robot)
            page = ctx.new_page()
            page.goto((origin or self.local) + path + query)
            page.wait_for_timeout(400)
            return [u for u, _ in sent if "paradigmmachines.ai" in u]
        for path in ("/", "/pricing.html", "/privacy.html", "/otter-alternative.html", "/demo.html", "/faq.html"):
            with self.subTest(path=path):
                self.assertEqual(orion_requests("https://dayglass.io", path), [tag])
                self.assertEqual(orion_requests(None, path), [], "localhost must not load Orion")
                self.assertEqual(orion_requests("https://dayglass.io.evil.test", path), [])
                self.assertEqual(orion_requests("https://dayglass.io", path, robot=True), [], "automated browsers")
                self.assertEqual(orion_requests("https://dayglass.io", path, query="?dg_owner=1"), [], "owner browsers")
                self.assertEqual(orion_requests("https://dayglass.io", path, robot=True, query="?orion_agent=test"), [tag], "Orion agent link")
        for page in ROOT.glob("*.html"):
            self.assertIn('src="/orion.js"', page.read_text(), page.name)
        self.assertIn("Orion", (ROOT / "privacy.html").read_text())

if __name__ == "__main__":
    unittest.main()
