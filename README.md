# Dayglass v2.1.0 for macOS

**Your Mac's Screen & Meeting Memory — 100% On-Device. Zero Cloud Bots.**

![Dayglass v2.1 Studio Live](https://igorganapolsky.github.io/dayglass-mac/dayglass-studio-live.png)

- **Website & Interactive Demo**: [https://igorganapolsky.github.io/dayglass-mac/](https://igorganapolsky.github.io/dayglass-mac/)
- **Direct Download (`.dmg`)**: [Download Dayglass v2.1.0 for macOS](https://github.com/IgorGanapolsky/dayglass-mac/releases/download/v2.1.0/Dayglass.dmg) (`SHA-256: 769a66d2b6580f2ec36f348ec8524c1d7876ad55aecb9c25fe0b9b89c0abc877`)
- **AI Search / LLM Manifest (`llms.txt`)**: [https://igorganapolsky.github.io/dayglass-mac/llms.txt](https://igorganapolsky.github.io/dayglass-mac/llms.txt)

---

## ⚡ Pricing & Instant Checkout (100% Offline License Key)

| Tier | Price | What Is Included & How AI Costs Are Covered | Instant 1-Click Checkout (Stripe & Gumroad) |
| :--- | :--- | :--- | :--- |
| **Dayglass Community (Free Trial)** | **$0 install** | Local Apple Vision OCR & SQLite FTS5 keyword search + **3 Free AI Preview Turns** (`$0.05` hard cap). **Paywall locks AI Copilot, Ask AI & AI Summaries after 3 turns.** | [Download Free `.DMG`](https://github.com/IgorGanapolsky/dayglass-mac/releases/download/v2.1.0/Dayglass.dmg) |
| **AI Agent Cost & Memory Playbook** | **$9.99 one-time** | Complete architecture guide + local SQLite/MCP setup | [Gumroad ($9.99) →](https://iganapolsky.gumroad.com/l/odrkon?wanted=true&utm_source=github_readme&utm_campaign=dayglass_v2_1) |
| **Dayglass Pro Monthly** | **$19 / month** | Unlimited AirPods call recording, 384K SubQ Snap GraphRAG, Claude/Cursor MCP & **On-Device AI (Ollama / Apple Silicon MLX / BYOK)**. *Does not include managed $200/mo Google AI Ultra cloud seat.* | [Stripe ($19/mo) →](https://buy.stripe.com/fZucN59eA1eScSd5e33sJ0U?utm_source=github_readme&utm_campaign=dayglass_v2_1) · [Gumroad ($19/mo) →](https://iganapolsky.gumroad.com/l/dayglass-pro?wanted=true&utm_source=github_readme&utm_campaign=dayglass_v2_1) |
| **Corporate-Expense Production Kit** | **$49 one-time** | **<$50 No-Approval Card Threshold** — Production MCP, DPO/AKV & 40 PreToolUse Rule-Pack | [Gumroad ($49) →](https://iganapolsky.gumroad.com/l/vcrho?wanted=true&utm_source=github_readme&utm_campaign=dayglass_v2_1) |
| **Dayglass Pro Annual** | **$149 / year** | Save 35% on Dayglass Pro (App + Unlimited Local Memory, MCP & On-Device AI / BYOK) | [Stripe Annual ($149/yr) →](https://buy.stripe.com/aFa28r62o8Hk19v49Z3sJ0W?utm_source=github_readme&utm_campaign=dayglass_v2_1) |
| **Dayglass Pro Lifetime** | **$249 one-time** | Own the Dayglass Mac app + On-Device AI & BYOK forever (`$0` cloud cost). *Managed Google AI Ultra seat not included.* | [Stripe Lifetime ($249) →](https://buy.stripe.com/4gM5kD1M82iW2dz9uj3sJ0V?utm_source=github_readme&utm_campaign=dayglass_v2_1) |
| **Dayglass Ultra (Managed Cloud AI)** | **$249 / month** | **Full Dayglass Pro + Managed Google AI Ultra Seat ($200/mo Gemini 4 Carbon & Claude Opus 5.5 frontier quota included).** | [Gumroad Ultra ($249/mo) →](https://iganapolsky.gumroad.com/l/dayglass-ultra?wanted=true&utm_source=github_readme&utm_campaign=dayglass_v2_1) |

> **Binary Distribution & Paywall Architecture:** This repository (`IgorGanapolsky/dayglass-mac`) distributes the signed macOS `.dmg` binary, Homebrew cask, and public docs only—core Dayglass source code lives in a private repository and zero cloud API keys are bundled in the app. Unlicensed installs get **3 free AI preview turns**, after which `/api/copilot/assist`, `/api/copilot/takeover`, `/api/ask`, and `/api/ask/stream` enforce a hard cryptographic license gate (`DGPRO-...` HMAC-SHA256 key, Stripe session/subscription ID, or Gumroad license key).

---

## Install in 10 Seconds

### Option 1: 1-Line Terminal Installer (Recommended — clears Gatekeeper quarantine automatically)

```bash
bash -c "$(curl -fsSL https://igorganapolsky.github.io/dayglass-mac/install.sh)"
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
