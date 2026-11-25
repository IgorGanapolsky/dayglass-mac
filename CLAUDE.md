# Dayglass public site and release repo

This repo is dayglass.io (plain static pages), the install script, the Homebrew cask and the public release links. The app source lives in the private `IgorGanapolsky/dayglass` repo; do not copy app code or private details here.

## Project rules (Igor)

- Plain language on every page and in every reply. Times in 12-hour form, for example 9:17 AM.
- No paid plans or paid services. No posts, emails or other sends outside the project without Igor's OK.
- Act on reversible work yourself (branch, commit, PR, merging your own PR once checks pass). Never hand Igor a command to run or a step to do; if something truly blocks you, say what in one line.

## Before you push

1. Run the `verify` skill (`.claude/skills/verify/SKILL.md`) and report the steps you ran and what you saw. No "done" without that evidence.
2. Review your own diff for the rules below before pushing (`/code-review` at medium works locally and reads this file). Fix what it finds that is real.

## Review rules

These each came up on at least two changes. Add a rule only after a pattern repeats on two PRs, and delete a rule once it stops earning its place.

- One price story. Prices on `index.html`, `pricing.html`, `llms.txt`, `README.md` and the FAQ must match each other (Free trial, Pro $149/year or $19/month, Lifetime $199 founding then $249). Change them together or not at all.
- Every product claim must be true of the shipped app. `scripts/check_site_claims.py` bans retired claims; if you add a new claim, it needs a source in the app repo or a measurement.
- Analytics loads only on dayglass.io hosts, never on localhost, previews or test runs (`tests/test_analytics_hosts.py`).
- The installer sends nothing but the GitHub download by default and never strips the macOS quarantine flag (`tests/test_installer.py`).
- Stripe checkout links are checked with plain HTTP, never opened in a browser by tests or audits, so the sales funnel stays clean.
- New pages go in `sitemap.xml` and, if they matter to AI search, `llms.txt`.

## When fixing a failing check or a review comment

- Make the smallest change that fixes it. A redesign, a price change or a new claim is its own task, not part of a fix.
- Try at most 3 times on the same failure. After the third, stop and report what you tried and what still fails, in one line each.
- After each push, say in one line what changed and how to undo it (usually `git revert <sha>`).
