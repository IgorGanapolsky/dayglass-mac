# Dayglass for macOS

**Your private AI memory for work. Bot-free meeting notes that Claude Code and Cursor can read while the call is live.**

![Dayglass Studio Live](https://igorganapolsky.github.io/dayglass-mac/dayglass-studio-live.png)

- **Website & Interactive Demo**: [https://igorganapolsky.github.io/dayglass-mac/](https://igorganapolsky.github.io/dayglass-mac/)
- **Direct Download (`.dmg`)**: [Download Dayglass for macOS](https://github.com/IgorGanapolsky/dayglass-mac/releases/latest/download/Dayglass.dmg) (SHA-256 is in `SHA256SUMS` on the release page)
- **AI Search / LLM Manifest (`llms.txt`)**: [https://igorganapolsky.github.io/dayglass-mac/llms.txt](https://igorganapolsky.github.io/dayglass-mac/llms.txt)

---

## Pricing

| Plan | Price | What is included | Get it |
| :--- | :--- | :--- | :--- |
| **Free trial** | **$0, no card** | Your first 10 meetings with everything included. After that, capture, transcripts, search and export stay free. Ask AI on older history, AI briefs and the Claude/Cursor live link need Pro. | [Download Free `.DMG`](https://github.com/IgorGanapolsky/dayglass-mac/releases/latest/download/Dayglass.dmg) |
| **Pro** | **$149/year** (save 35%) or **$19/month** | Everything, on every meeting: the Claude Code/Cursor live link over MCP, Ask AI on older history, AI briefs, unlimited meetings. | [Pricing page](https://igorganapolsky.github.io/dayglass-mac/#pricing) |
| **Lifetime** | **$249 once** (founding price $199 for the first 100 buyers) | Everything in Pro, no subscription. | [Pricing page](https://igorganapolsky.github.io/dayglass-mac/#pricing) |

14-day money-back guarantee, just email us.

> This repository distributes the signed macOS `.dmg`, the Homebrew cask, and these docs. The app source stays private.

---

## Install in 10 Seconds

### Option 1: 1-Line Terminal Installer (Recommended — clears Gatekeeper quarantine automatically)

```bash
curl -fsSL https://igorganapolsky.github.io/dayglass-mac/install.sh | bash
```

### Option 2: Homebrew Cask

```bash
brew install --cask igorganapolsky/dayglass/dayglass
```

### Option 3: Direct `.dmg` Download

1. Download [`Dayglass.dmg`](https://github.com/IgorGanapolsky/dayglass-mac/releases/latest/download/Dayglass.dmg)
2. Drag `Dayglass.app` into `/Applications`
3. If macOS Gatekeeper prompts on first launch, run:
   ```bash
   xattr -dr com.apple.quarantine /Applications/Dayglass.app
   ```

---

## What's Inside Dayglass

- **384,000-Token SubQ Snap 3-Way Hybrid GraphRAG** (BM25 + 256d Dense Semantic + 2-Hop Episode Graph in local SQLite)
- **Bot-free call recording** via macOS `ScreenCaptureKit` (records both your Mic and AirPods/Headphones without joining Zoom/Teams/Meet as a bot)
- **On-Device AI Companion 3.0 & OpenUI Generative UI Cards** (answers *"is what they're pitching useful?"* in real time during calls)
- **Vitalik Buterin 4-Layer Paranoid Mode** (local reversible PII prompt rewriter, per-session circuit isolation, 4KB cover traffic padding, and SHA-256 zkAPI blind proofs)
- **Starred Focus Sessions (`Cmd+Ctrl+B`)** -> compiles 15-minute work windows into reusable `SKILL.md` agent skills
- **1-Click MCP Server** for Claude Desktop, Claude Code, Cursor, Poolside, and Oh-My-Pi
- **Live meeting for other agents:** while a Zoom, Teams, or Meet call is in progress, Claude, Cursor, and the other agents on your Mac read the speaker-tagged transcript through the local tool `dayglass_get_live_meeting`. The audio stays in `~/.dayglass`.

## Privacy

Audio, screen and the database stay on your Mac. If you turn on a cloud model for Ask AI, the question and the relevant meeting text are sent to that model, after emails, phone numbers, secrets and known names are swapped out for placeholders. With a local model nothing leaves the Mac.
