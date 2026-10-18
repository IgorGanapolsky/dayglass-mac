# Dayglass v2.0.0 for macOS

**Your Mac's Screen & Meeting Memory — 100% On-Device. Zero Cloud Bots.**

- **Website & Pricing**: [https://igorganapolsky.github.io/dayglass-mac/](https://igorganapolsky.github.io/dayglass-mac/)
- **Direct Download (`.dmg`)**: [Download Dayglass v2.0.0 for macOS](https://github.com/IgorGanapolsky/dayglass-mac/releases/download/v2.0.0/Dayglass.dmg) (`SHA-256: 0c2d815e3fbfabbf3e0f550a27687d027d8a414ba466aa84fa3d4086e233e03b`)

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

1. Download [`Dayglass.dmg`](https://github.com/IgorGanapolsky/dayglass-mac/releases/download/v2.0.0/Dayglass.dmg)
2. Drag `Dayglass.app` into `/Applications`
3. If macOS Gatekeeper prompts on first launch, run:
   ```bash
   xattr -dr com.apple.quarantine /Applications/Dayglass.app
   ```

## What's Inside Dayglass v2.0

- **384,000-Token SubQ Snap 3-Way Hybrid GraphRAG** (BM25 + 256d Dense Semantic + 2-Hop Episode Graph)
- **Bot-Free Dual-Source Call Recording** via macOS `ScreenCaptureKit` (records both your Mic and AirPods/Headphones without joining Zoom/Teams/Meet as a bot)
- **Cluely-Style Screen-Share-Invisible Live Meeting Copilot** (`NSWindowSharingNone` HUD)
- **Vitalik Buterin 4-Layer Paranoid Mode** (local reversible PII prompt rewriter, per-session circuit isolation, 4KB cover traffic padding, and SHA-256 zkAPI blind proofs)
- **Starred Focus Sessions (`Cmd+Ctrl+B`)** -> compiles 15-minute work windows into reusable `SKILL.md` agent skills
- **1-Click MCP Server** for Claude Desktop and Cursor
