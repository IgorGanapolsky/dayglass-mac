<!-- Public copy of docs/EDR-POSTURE.md from the private IgorGanapolsky/dayglass repository. File and function references are to that source. -->

# Dayglass and endpoint security (CrowdStrike Falcon)

Dayglass records the screen and meetings, so on a managed Mac it sits close to what endpoint detection looks for. This page lists what CrowdStrike says Falcon flags, what Dayglass changed to stay clearly legitimate, and what is left for a security team to review. Nothing here hides Dayglass from Falcon. There is no packing, obfuscation, process hiding, injection, or tampering with security tools, and there must never be.

## What Falcon looks for

CrowdStrike's behavioral indicators of attack (IOAs) judge sequences of behavior and intent, not file hashes. A tool that is legitimate on its own is flagged by its context: process lineage, command line, and what it touches next ([IOA vs IOC](https://www.crowdstrike.com/en-us/cybersecurity-101/threat-intelligence/ioa-vs-ioc/), [AI-powered IOAs](https://www.crowdstrike.com/en-us/blog/introducing-ai-powered-indicators-of-attack-ioas/), [living-off-the-land](https://www.crowdstrike.com/en-us/blog/beyond-the-binary-stop-attackers-living-off-your-land/)). On macOS, CrowdStrike's own write-ups show IOAs firing on:

- `xattr` removing quarantine to get past Gatekeeper, then `chmod` and run ([SHAMOS](https://www.crowdstrike.com/en-us/blog/falcon-prevents-cookie-spider-shamos-delivery-macos/)).
- AppleScript through `osascript` for reconnaissance and collection, often fed by `curl` ([SHAMOS](https://www.crowdstrike.com/en-us/blog/falcon-prevents-cookie-spider-shamos-delivery-macos/), [Falcon macOS network visibility](https://www.crowdstrike.com/en-us/blog/enhanced-network-visibility-dive-into-falcon-macos-sensor-new-capabilities/)).
- Collection of Keychain, browser, and Notes data ([SHAMOS](https://www.crowdstrike.com/en-us/blog/falcon-prevents-cookie-spider-shamos-delivery-macos/)).
- Persistence through Login Items, LaunchAgents, LaunchDaemons, and cron ([macOS malware analysis](https://www.crowdstrike.com/en-us/blog/how-crowdstrike-analyzes-macos-malware-to-optimize-automated-detection-capabilities/)), and plists created and loaded by hand with `launchctl` ([OverWatch Mac intrusion](https://www.crowdstrike.com/en-us/blog/overwatch-insights-reviewing-a-new-intrusion-targeting-mac-systems/)).
- Decoding or obfuscating payloads, security software discovery, and screen capture, all on OverWatch's tactic list for that intrusion ([OverWatch Mac intrusion](https://www.crowdstrike.com/en-us/blog/overwatch-insights-reviewing-a-new-intrusion-targeting-mac-systems/)).

Other vendors describe the same macOS patterns: fake password dialogs with `osascript … with hidden answer`, copying `login.keychain-db`, and stealing Safari and Chrome cookies ([Unit 42, AMOS](https://unit42.paloaltonetworks.com/atomic-macos-amos-stealer-activity/), [SentinelOne, Atomic Stealer](https://www.sentinelone.com/blog/atomic-stealer-threat-actor-spawns-second-variant-of-macos-malware-sold-on-telegram/), [Red Canary, AppleScript](https://redcanary.com/threat-detection-report/techniques/applescript/)), and LaunchAgent plists written by interpreters or unsigned binaries ([Elastic rule](https://www.elastic.co/docs/reference/security/prebuilt-rules/rules/macos/persistence_suspicious_launch_agent_or_launch_daemon)).

## What Dayglass changed

| Behavior Falcon flags | Change in Dayglass |
| --- | --- |
| Credential access: Keychain tampering; defense evasion: answering security prompts for the user | Removed the copilot action that deleted another vendor's Keychain items and auto-clicked Deny or Cancel in `SecurityAgent` (`dayglass/copilot.py`). UI automation now refuses `SecurityAgent`, `coreautha`, System Settings, Keychain Access, Installer, and Falcon windows. |
| Input capture or injection into a password prompt | Computer use (clicks, typing, hotkeys, screenshots, Chrome and DevTools control) is off unless the user sets `DAYGLASS_COMPUTER_USE=1`. Copilot's Accessibility inspection, Chrome AppleScript and planned UI actions use the same switch. When it is on, typing and hotkeys still refuse when a security prompt is in front (`dayglass/computer_use.py`, `dayglass/copilot.py`). |
| Living off the land: `osascript` command injection into `do shell script` | Hotkey names are escaped and stripped of newlines before they reach AppleScript (`dayglass/computer_use.py`). |
| Collection: another app's private data | Stopped reading Outlook's mail database (`HxStore.hxd`) and attachment cache. Removed hard-coded meeting content (`dayglass/calendar_sync.py`). |
| Privacy-database probing and tampering (`TCC.db`, `tccutil`) | The native app no longer runs `sqlite3` on `TCC.db` or `tccutil reset`. It uses only `CGPreflightScreenCaptureAccess` and `CGRequestScreenCaptureAccess`. For a grant left over from an older build it tells the user to switch Dayglass off and on in Settings (`macos/main.swift`). |
| Credential access through the `security` tool | API keys for chat providers are read and written with Security.framework `SecItem` calls in process, not `security find-generic-password -w` (`dayglass/keychain.py`, `dayglass/chat_engine.py`). |
| Shell spawned by an app to load persistence | The app loads its own LaunchAgent with `/bin/launchctl` directly, after checking the plist's label and program, instead of `bash -c` with `PlistBuddy` (`macos/main.swift`). |
| Unattributed persistence | The server LaunchAgent declares `AssociatedBundleIdentifiers`, so macOS shows it as part of Dayglass in Login Items (`dayglass/bundled_runtime.py`). Label, path, and logs stay under the app's own names (`com.iganapolsky.dayglass-server`, `~/.dayglass/logs`). |
| Impairing defenses: stopping security agents | Health cleanup and the crash-loop guard act only on Dayglass's own LaunchAgents (`com.iganapolsky.dayglass*`) and its own stale MCP processes. `com.crowdstrike.*`, Jamf, Kandji, Intune, Defender, Mosyle, Addigy, Zscaler, Palo Alto, Fortinet, SentinelOne and Apple MDM labels are excluded even if a rule ever matched. Everything else, including other user agents, Ollama and LM Studio, is reported only (`dayglass/mac_health.py`, `dayglass/crash_guard.py`). Dayglass no longer kills macOS `spindump`. |
| Gatekeeper bypass with `xattr -d com.apple.quarantine` | The DMG's "Install CLI" script no longer strips quarantine. A DMG is built only notarized and stapled: notarization is on by default and the DMG step refuses to run without it. Unnotarized builds are local installs only (`scripts/build_app.sh`, `scripts/build_mas_pkg.sh`). |
| Screen capture (T1113) by a command-line tool | No `screencapture -x` anywhere. Frames come from `dayglass-framecapture`, a ScreenCaptureKit helper signed inside the app. The helper only checks that Screen Recording is already granted and skips the frame when it is not; Dayglass asks macOS for that permission once, from the app's Fix button. It needs macOS 14 or newer and exits with code 4 below that, which Dayglass reports in one line. Background frames and hourly pictures are taken only while a meeting is in progress unless the user sets `DAYGLASS_CAPTURE_ALL_DAY=1` (`macos/framecapture.swift`, `dayglass/capture.py`, `dayglass/engine.py`, `dayglass/snapshots.py`). |
| Unrestricted headless agent (not changed here) | The headless "do it" agent still has its full-access mode (Claude Code `bypassPermissions`, Cursor `--force`). Full access is the product default today. Whether to change that is the owner's call and is deferred, not part of this hardening (`dayglass/agent_tasks.py`, `dayglass/agent_policy.json`). |
| `curl … \| bash` installers | Removed from product copy. Install is the Homebrew cask or the notarized DMG (`dayglass/growth.py`, `dayglass/growth_engineer_agent.py`). |
| Entitlements and permissions declared honestly | The Apple Events usage text now says what Dayglass does with it: reads titles, detects calls, shows notifications, and clicks or types only when asked (`macos/Info.plist`). |

Already in place before this work: every binary in the bundle, including the bundled Python and helpers, is signed with hardened runtime. The local server listens on `127.0.0.1` only ([PRIVACY-FACTS.md](PRIVACY-FACTS.md)).

Tests: `tests/test_edr_hardening.py`.

## Standards map items and how each is proved

| Map item | Change | Proof |
| --- | --- | --- |
| 1. Notarized, stapled DMGs only; no quarantine strip | Notarization on by default; DMG step refuses without it; `xattr -dr com.apple.quarantine` removed | `test_dmg_is_only_built_notarized_and_stapled`, `test_installer_does_not_strip_gatekeeper_quarantine`; `bash -n scripts/build_app.sh` |
| 2. `security … -w` replaced with SecItem | `dayglass/keychain.py` (SecItemCopyMatching, Add, Update, Delete) | `test_api_keys_use_secitem_not_the_security_tool`; a live add, read, update and delete of a throwaway item under a test-only service name |
| 2. `tccutil reset` and the `TCC.db` read replaced with CoreGraphics preflight and request | `ScreenGrant` keeps only `CGPreflightScreenCaptureAccess` and `CGRequestScreenCaptureAccess` | `test_fix_button_never_resets_privacy_grants_and_tells_the_user_instead`, `test_native_app_does_not_read_tcc_db_or_shell_out_for_launchd`; `swiftc -typecheck macos/main.swift` |
| 2. `bash -c launchctl bootstrap` replaced with SMAppService | `bash -c` removed; `/bin/launchctl` runs directly after checking the plist. SMAppService not done (see above) | `test_native_app_does_not_read_tcc_db_or_shell_out_for_launchd` |
| 3. Cleanup scoped to Dayglass's own labels; never CrowdStrike or MDM | Only `com.iganapolsky.dayglass*` and Dayglass's stale MCP processes; security and MDM prefixes excluded; the rest report-only | `test_only_dayglass_launchagents_are_managed`, `test_crash_guard_never_unloads_vendor_agents`, `test_remediate_leaves_vendor_agents_loaded`, `test_remediate_only_terminates_dayglass_processes` |
| 4. Capture only during meetings, through the signed ScreenCaptureKit helper | `dayglass-framecapture`; meeting-only background and hourly pictures | `test_no_screencapture_subprocess_anywhere_in_the_app`, `test_frames_come_from_the_signed_helper_in_the_app_bundle`, `test_background_capture_only_runs_during_a_meeting`, `test_hourly_snapshot_keeps_no_picture_outside_a_meeting` |
| 4. Computer use out of the recorder | Off unless `DAYGLASS_COMPUTER_USE=1` | `test_computer_use_is_off_unless_the_user_turns_it_on`, `test_synthetic_typing_refuses_security_prompts`, `test_hotkey_cannot_break_out_of_applescript` |
| 4. Full-access headless agent mode | Deferred: unchanged, needs the owner's decision | none |

Computer use is switched off, not moved into a separate signed app. A separate app would be the cleaner split; until then the recorder never clicks, types or drives a browser unless the user opts in.

## For security to review

These are normal for what Dayglass does, but a strict policy may still alert on them. They can't be removed in code without removing the feature:

- **Screen Recording and microphone.** Dayglass captures the meeting window and records calls, with the macOS permissions and usage strings in `macos/Info.plist`. On OverWatch's list this is screen capture (T1113). A screenshot the user asks for in chat is also taken outside meetings.
- **LaunchAgent loaded with `launchctl`, not `SMAppService`.** The app bootstraps its own `com.iganapolsky.dayglass-server` plist from `~/Library/LaunchAgents` with `/bin/launchctl` directly. Moving to `SMAppService.agent(plistName:)` needs the plist inside the bundle (`Contents/Library/LaunchAgents`, `BundleProgram`), a migration that removes the old plist, and an install test on a real Mac. That was not done here.
- **Helpers compiled on the Mac.** In a development checkout, Dayglass compiles some Swift helpers with `swiftc` into `~/.dayglass/bin` when no bundled copy exists. Those are ad-hoc signed. The release app uses only its signed bundled helpers, and the capture helper is never compiled locally.
- **Process and folder listing in hourly context.** The hourly snapshot runs `ps -axo pid,tty,comm,args` and `lsof` to name the projects being worked on (`dayglass/snapshots.py`). That is process discovery on OverWatch's list.
- **`osascript` spawned from Python.** Calendar notifications, meeting detection in Teams and Zoom, Chrome tab titles, and user-requested UI actions run `osascript -e` from the Python server (`dayglass/meetings.py`, `dayglass/calendar_sync.py`, `dayglass/copilot.py`, `dayglass/capture.py`). The parent is Dayglass's signed bundled Python, not a temp-folder script. Moving these into the signed native app is the longer-term fix.
- **Accessibility automation of other apps.** Copilot UI actions and the Teams roster reader read and press controls in other apps' windows, with the user's Accessibility grant (`dayglass/copilot.py`, `macos/teamscaptions.swift`).
- **Outlook calendar widget file.** Dayglass reads Outlook's calendar widget `store.json` from Office's group container and mirrors it to `~/.dayglass` for the background server (`macos/main.swift`, `dayglass/calendar_sync.py`). macOS asks before allowing this. EventKit is the alternative when Outlook calendars are in macOS Calendar.
- **Ad-hoc local builds.** A local build with `DAYGLASS_ALLOW_ADHOC=1` is not Developer ID signed. Managed Macs should run the notarized release only.
- **Base64 in a developer check.** `scripts/verify-dayglass-personal-github.sh` decodes a base64 list of words the personal repo must not contain. It is a CI check, not shipped in the app.

Not done, by design: allow-listing Dayglass in Falcon, or any exclusion. That is the security team's call through the Falcon console, not something an app should ask for or work around.
