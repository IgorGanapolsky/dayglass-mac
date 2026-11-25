"""Checks of the chaptered demo page: deep links, job switch, buttons, analytics and phone layout.
Run: python3 -m unittest tests.test_demo

PostHog, Stripe and Clarity are intercepted, so nothing leaves this machine.
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
REDUCED = {"reduced_motion": "reduce"}


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):  # noqa: D102
        return


class Demo(unittest.TestCase):
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

    def _open(self, query="", width=1280, **ctx):
        context = self.browser.new_context(viewport={"width": width, "height": 900}, **ctx)
        self.addCleanup(context.close)
        self.sent = []
        for host in ("posthog.com", "stripe.com", "clarity.ms"):
            context.route(f"**/*{host}/**", lambda route: (self.sent.append(route.request.url), route.abort()))
        page = context.new_page()
        page.add_init_script(SINK)
        page.goto(self.base + "/demo.html" + query)
        return page

    def test_deep_link_opens_that_chapter_and_job(self):
        page = self._open("?chapter=3&role=sales", **REDUCED)
        self.assertTrue(page.inner_text("#chapterTitle").startswith("3. Claude Code reads the live call"))
        self.assertIn("Acme Retail discovery", page.inner_text("#stage"))
        self.assertIn("dayglass_get_live_meeting", page.inner_text("#stage"))

    def test_out_of_range_deep_link_is_clamped(self):
        page = self._open("?chapter=99&role=nope", **REDUCED)
        self.assertTrue(page.inner_text("#chapterTitle").startswith("5."))
        self.assertIn("Q4 rollout sync", page.inner_text("#stage"))

    def test_job_switch_and_next_and_end_card(self):
        page = self._open(**REDUCED)
        page.click('.role[data-role="consultant"]')
        self.assertIn("Brightline workshop", page.inner_text("#stage"))
        for _ in range(4):
            page.click("#nextBtn")
        self.assertTrue(page.inner_text("#chapterTitle").startswith("5. Ask what happened today"))
        self.assertTrue(page.is_visible("#endcard"))
        self.assertIn("chapter=5", page.url)
        self.assertIn("role=consultant", page.url)
        names = [e[0] for e in page.evaluate("window.__events")]
        for name in ("demo_viewed", "demo_role_selected", "demo_chapter_viewed", "demo_completed"):
            self.assertIn(name, names)

    def test_autoplay_advances(self):
        page = self._open()
        page.wait_for_function("document.getElementById('chapterTitle').textContent.startsWith('2.')", timeout=15000)

    def test_download_click_is_tracked_and_local_visit_sends_nothing(self):
        page = self._open("?chapter=5", **REDUCED)
        # Keep the page here so the recorded events can be read after the click.
        page.evaluate("document.getElementById('demoDownloadEnd').addEventListener('click', e => e.preventDefault())")
        page.click("#demoDownloadEnd")
        events = page.evaluate("window.__events")
        self.assertIn(["dmg_download_clicked", {"source": "demo_end", "chapter": 5, "role": "engineer"}], events)
        self.assertEqual([u for u in self.sent if "posthog" in u], [])

    def test_only_true_price_claims(self):
        text = self._open(**REDUCED).inner_text("body")
        for claim in ("$19 a month", "$149 a year", "first 10 meetings", "14-day money-back"):
            self.assertIn(claim, text)
        self.assertIn("fictional", text)

    def test_no_sideways_scroll_on_a_phone(self):
        for chapter in range(1, 6):
            page = self._open(f"?chapter={chapter}", 375, **REDUCED)
            self.assertLessEqual(page.evaluate("document.documentElement.scrollWidth"), 375, chapter)


if __name__ == "__main__":
    unittest.main()
