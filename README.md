# Dayglass v2.1.0 for macOS

**Your Mac's Screen & Meeting Memory — 100% On-Device. Zero Cloud Bots.**

![Dayglass v2.1 Studio Live](https://igorganapolsky.github.io/dayglass-mac/dayglass-studio-live.png)

- **Website & Interactive Demo**: [https://igorganapolsky.github.io/dayglass-mac/](https://igorganapolsky.github.io/dayglass-mac/)
- **Direct Download (`.dmg`)**: [Download Dayglass v2.1.0 for macOS](https://github.com/IgorGanapolsky/dayglass-mac/releases/download/v2.1.0/Dayglass.dmg) (`SHA-256: 769a66d2b6580f2ec36f348ec8524c1d7876ad55aecb9c25fe0b9b89c0abc877`)
- **AI Search / LLM Manifest (`llms.txt`)**: [https://igorganapolsky.github.io/dayglass-mac/llms.txt](https://igorganapolsky.github.io/dayglass-mac/llms.txt)

---

## Pricing

| Tier | Price | What is included | Checkout |
| :--- | :--- | :--- | :--- |
| **Dayglass Community (Free Trial)** | **$0 install** | Local Apple Vision OCR and SQLite search, plus 3 free AI preview turns. After that, the AI routes stay closed until a license is already on the Mac. | [Download Free `.DMG`](https://github.com/IgorGanapolsky/dayglass-mac/releases/download/v2.1.0/Dayglass.dmg) |
| **AI Agent Cost & Memory Playbook** | **$9.99 one-time** | Architecture guide and local SQLite/MCP setup | [Gumroad ($9.99) →](https://iganapolsky.gumroad.com/l/odrkon?wanted=true&utm_source=github_readme&utm_campaign=dayglass_v2_1) |
| **Dayglass Pro Monthly** | **$19 / month** | Unlimited AirPods call recording, local history, and Claude/Cursor MCP on your Mac. | [Gumroad ($19/mo) →](https://iganapolsky.gumroad.com/l/dayglass-pro?wanted=true&utm_source=github_readme&utm_campaign=dayglass_v2_1) |
| **Corporate-Expense Production Kit** | **$49 one-time** | Production MCP kit, under a $50 card limit | [Gumroad ($49) →](https://iganapolsky.gumroad.com/l/vcrho?wanted=true&utm_source=github_readme&utm_campaign=dayglass_v2_1) |
| **Dayglass Ultra** | **$249 / month** | The Mac app plus managed cloud AI. The $19 plan is the Mac app and on-device memory. | [Gumroad Ultra ($249/mo) →](https://iganapolsky.gumroad.com/l/dayglass-ultra?wanted=true&utm_source=github_readme&utm_campaign=dayglass_v2_1) |

> This repository distributes the signed macOS `.dmg`, the Homebrew cask, and these docs. The app source stays private. A Gumroad payment does not write a license onto the Mac by itself.

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

1. Download [`Dayglass.dmg`](https://github.com/IgorGanapolsky/dayglass-mac/releases/download/v2.1.0/Dayglass.dmg)
2. Drag `Dayglass.app` into `/Applications`
3. If macOS Gatekeeper prompts on first launch, run:
   ```bash
   xattr -dr com.apple.quarantine /Applications/Dayglass.app
   ```

---

## What's Inside Dayglass v2.1

- **384,000-Token SubQ Snap 3-Way Hybrid GraphRAG** (BM25 + 256d Dense Semantic + 2-Hop Episode Graph in local SQLite)
- **Bot-Free Dual-Source Call Recording** via macOS `ScreenCaptureKit` (records both your Mic and AirPods/Headphones without joining Zoom/Teams/Meet as a bot)
- **On-Device AI Companion 3.0 & OpenUI Generative UI Cards** (answers *"is what they're pitching useful?"* in real time during calls)
- **Vitalik Buterin 4-Layer Paranoid Mode** (local reversible PII prompt rewriter, per-session circuit isolation, 4KB cover traffic padding, and SHA-256 zkAPI blind proofs)
- **Starred Focus Sessions (`Cmd+Ctrl+B`)** -> compiles 15-minute work windows into reusable `SKILL.md` agent skills
- **1-Click MCP Server** for Claude Desktop, Claude Code, Cursor, Poolside, and Oh-My-Pi
- **Live meeting for other agents:** while a Zoom, Teams, or Meet call is in progress, Claude, Cursor, and the other agents on your Mac read the speaker-tagged transcript through the local tool `dayglass_get_live_meeting`. The audio stays in `~/.dayglass`.
