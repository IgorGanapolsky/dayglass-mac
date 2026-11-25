---
name: verify
description: Check a dayglass.io site, installer or cask change end to end before committing or calling it done.
---

# Verify a Dayglass site change

Run these from the repo root. Report each step you ran and what you saw. Never report success for a step you did not run; say "not run" and why.

1. Claims and links:
   - `python3 scripts/check_site_claims.py` must print `site claims ok`.
   - `python3 scripts/check_public_release_links.py` checks the published `.dmg` and the Stripe links. In a cloud container the GitHub release download can return HTTP 401 from the network proxy; that is the container, not the release. Say so and rely on the GitHub Actions run (`Public release links` workflow) for this step.
2. Tests: `cd tests && python3 -m unittest -v`.
   - The browser tests (`test_hero`, `test_site_events`, `test_analytics_hosts`) need Python Playwright and Chromium. On Igor's Mac they run as is. In a cloud container, `pip install playwright` and set `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`; if they still fail to start the browser, report them as "not run here" rather than passed.
   - `test_installer` needs macOS; on Linux it fails with "Dayglass requires macOS". Report it as "needs the Mac", not as a pass.
3. Look at the change: serve the site with `python3 -m http.server 8765` and open each changed page at phone width (390 px) and desktop width (1280 px). Take a screenshot of each. For a link or button change, run `python3 scripts/click_audit.py --base http://127.0.0.1:8765`.
4. Prices: if any page mentions a price, confirm it matches the price story in `CLAUDE.md` on every page that shows prices.
5. Report: one line per step with the result. List anything you could not run and where it will run instead (CI or the Mac).

If a step is flaky, run it again once. If it is flaky twice, note it in the `steward` skill so the next agent knows.
