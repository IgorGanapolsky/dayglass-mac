---
name: steward
description: Rules for keeping a Dayglass site PR green (failing checks, conflicts, review comments). Read by the PR watch from /ship and /steward.
user-invocable: false
disable-model-invocation: true
---

# Keeping a Dayglass site PR green

- The only CI is the `Public release links` workflow (`scripts/check_public_release_links.py` and `scripts/check_site_claims.py`). Run both before pushing a fix.
- If `check_site_claims.py` fails, change the page copy so the claim is true. Never remove a banned phrase from the list to get green.
- If the release-link check fails on the `.dmg`, check whether the latest GitHub release still has `Dayglass.dmg` before touching any page. A missing asset is a release problem in the app repo, not a site fix.
- On a conflict in `index.html` or `pricing.html`, keep `main`'s prices and copy and re-apply only this PR's change on top.
- Keep fixes small. A comment that asks for a redesign, a new page, a price change or a new claim goes back to the author with a one-line summary; do not do it inside the fix.
- At most 3 pushes for the same problem. Then stop and report what you tried.
- After each push, comment one line: what changed and how to undo it.
