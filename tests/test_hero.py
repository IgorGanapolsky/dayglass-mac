"""The hero states the outcome, the privacy boundary has three rows, and the page follows the agreed order."""

from __future__ import annotations

import functools
import http.server
import threading
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ORDER = ["heroHeadline", "demo", "outcomes", "cmdBrew", "privacyBoundary", "compare", "pricing", "faq", "download"]


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):  # noqa: D102
        return


class Hero(unittest.TestCase):
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

    def _open(self, path, width):
        page = self.browser.new_page(viewport={"width": width, "height": 900})
        self.addCleanup(page.close)
        page.goto(self.base + path)
        return page

    def test_hero_text(self):
        for path in ("/", "/pricing.html"):
            page = self._open(path, 1280)
            self.assertEqual(page.inner_text("#heroHeadline"), "After every call, Dayglass remembers what was decided.")
            self.assertEqual(
                page.inner_text("#heroSubheadline").strip(),
                "Summaries, decisions and follow-ups for every call, searchable and stored on your Mac. "
                "Claude Code and Cursor can read them too. Live notes (beta) while the call runs.",
            )
            self.assertEqual(
                page.inner_text("#heroLocal"),
                "Local recording and storage. No meeting bot. Try your next 10 meetings free.",
            )

    def test_privacy_boundary_has_three_rows(self):
        for path in ("/", "/pricing.html"):
            page = self._open(path, 1280)
            self.assertEqual(
                page.locator("#privacyBoundary dt").all_inner_texts(),
                ["Recording and storage", "Dayglass AI", "Claude and Cursor"],
            )

    def test_privacy_boundary_makes_only_true_claims(self):
        for path in ("/", "/pricing.html"):
            text = self._open(path, 1280).locator("#privacyBoundary").inner_text()
            self.assertIn("audio is transcribed on the Mac and not kept by default", text)
            self.assertIn("only terms on your Never-share list are withheld before text goes to a cloud model you choose", text)
            for false_claim in ("Audio, screen text and notes stay", "phone numbers", "placeholders", "swapped", "Paranoid", "paranoid"):
                self.assertNotIn(false_claim, text)

    def test_section_order(self):
        page = self._open("/", 1280)
        tops = page.evaluate("ids => ids.map(i => document.getElementById(i).getBoundingClientRect().top + scrollY)", ORDER)
        self.assertEqual(tops, sorted(tops), dict(zip(ORDER, tops)))

    def test_no_sideways_scroll_on_a_phone(self):
        for path in ("/", "/pricing.html"):
            page = self._open(path, 390)
            self.assertLessEqual(page.evaluate("document.documentElement.scrollWidth"), 390, path)


if __name__ == "__main__":
    unittest.main()
