<!-- Public copy of docs/SECURITY-REVIEW-PACK.md from the private IgorGanapolsky/dayglass repository. File and function references are to that source. -->

# Dayglass security review pack

For a security reviewer deciding whether Dayglass may run on a managed Mac. Each claim points at the code, or at command output captured from the current public release, v2.4.1.

v2.4.1 was built from dayglass commit `467a332`. Anything below marked **planned** is not in any release yet.

The `dayglass` source repository is private. The public copy of this pack, the participant-data page and the SBOM are in the `dayglass-mac` repository under `security/`. Code references are to the private source, by file and function name.

Related: [PRIVACY-FACTS.md](PRIVACY-FACTS.md) (what is recorded), [MEETING-PARTICIPANT-DATA.md](MEETING-PARTICIPANT-DATA.md) (other people's data), [EDR-POSTURE.md](EDR-POSTURE.md) (CrowdStrike Falcon).

## What this pack does not cover

- Dayglass has no SOC 2 report, no ISO 27001 certificate, and no third-party penetration test. It is built and maintained by one developer.
- A live screen-frame capture through the ScreenCaptureKit helper has not been verified on a real, unlocked session.
- The server still starts from a per-user LaunchAgent plist; moving it to `SMAppService` is not done.

## Data flow

The app and its server listen on `127.0.0.1` only (`dayglass/server.py`). The server has no login or token, so any process on the Mac can call it; it refuses requests whose `Host` is not loopback and requests from other web origins (`local_request_allowed`, `DayglassHandler.parse_request`). The Swift app talks only to that server and to local Ollama or LM Studio. Screenshots, screen text, audio and transcripts stay in `~/.dayglass`.

These are all the hosts outside the Mac that the code can reach. Hosts that appear in the code only as links a user can click are not listed.

| Host | When | What leaves the Mac |
| --- | --- | --- |
| `github.com` (`IgorGanapolsky/dayglass-mac` releases) | Install or update, by `install.sh` or Homebrew | Nothing beyond the download request |
| `us.i.posthog.com` | As of 20 Nov 2026, `install.sh` makes no analytics request unless the person installing sets `DAYGLASS_INSTALL_PING=1` (`install.sh` lines 66-72) | Event `app_installed_via_script`, a random 12-character id, the word `latest`, CPU type. In the app, analytics go out only if someone sets a PostHog key, and none ships (`DEFAULT_POSTHOG_PROJECT_KEY = ""` in `dayglass/analytics.py`) |
| `api.anthropic.com`, `api.openai.com`, `generativelanguage.googleapis.com` | Only if the user picks a cloud AI, adds their own key and confirms (`dayglass/chat_engine.py`) | The question and the meeting notes that match it. `DAYGLASS_CHAT_LOCAL_ONLY=1` blocks it |
| `huggingface.co` | Only if search by meaning or voice output is turned on | Model download request, once |
| `github.com` (`astral-sh/uv` release) | Only when voice output is first installed (`dayglass/tts.py`) | Download request |
| `vendor-api.setapp.com` | Setapp build only | Setapp licence check (`dayglass/setapp_vendor.py`) |
| `api.ipify.org` | Only when the user runs `dayglass privacy` or opens privacy status | Public IP lookup (`dayglass/privacy_routing.py`) |
| `itunes.apple.com` | Only when the revenue report endpoint is opened (`dayglass/analytics.py`) | The Dayglass App Store id |
| `thumbgate.ai` | Only with consent and a key the user sets (`dayglass/feedback.py`) | The feedback vote |
| A host the user configures | Only if set: `DAYGLASS_ADO_PROJECT_URL`, `DAYGLASS_FEEDBACK_WEBHOOK_URL`, `DAYGLASS_ULTRAMARINE_BASE_URL`, `DAYGLASS_LIVE_SUMMARY_URL` (loopback only) | What that feature sends to the host the user chose |

During a call, Dayglass no longer looks up or opens links it reads off a shared screen; that happens only with `DAYGLASS_VERIFY_SCREEN_URLS=1` (`_clean_and_verify_screen_url` in `dayglass/meetings.py`). Test: `tests/test_edr_hardening.py::test_screen_urls_are_not_fetched_unless_opted_in`.

## Permissions

Asked of the user by macOS (`macos/Info.plist`):

| Permission | Why |
| --- | --- |
| Screen Recording | Screenshots of the meeting window during calls. Capture runs only during meetings unless the user sets `DAYGLASS_CAPTURE_ALL_DAY=1` (`capture_outside_meetings` in `dayglass/capture.py`). Since 2.4.1 |
| Microphone | Meeting audio for on-device transcription |
| Calendars (full access) | Upcoming events for meeting prep |
| Automation (Apple Events) | Window and browser tab titles, Teams and Zoom call detection, notifications. Computer use (clicking or typing) is off unless the user turns it on, and it never acts on password or permission prompts |

Outside meetings no screenshot is taken, but an hourly snapshot still saves the front app and window title, the open-window list, recently changed file paths under project folders and terminal working folders (`build_context` in `dayglass/snapshots.py`). Private windows and paths are left out.

Entitlements on the v2.4.1 app (`codesign -d --entitlements`): `automation.apple-events`, `device.audio-input`, `network.client`, `network.server`, `personal-information.calendars`. The App Store build adds the app sandbox (`macos/DayglassMAS.entitlements`). App Transport Security allows only local networking as an exception (`NSAllowsLocalNetworking`).

Dayglass does not use Accessibility to answer system prompts, does not run `tccutil`, does not touch other apps' LaunchAgents, and does not read other apps' private stores ([EDR-POSTURE.md](EDR-POSTURE.md), `tests/test_edr_hardening.py`).

## Where data is kept, for how long, and who can read it

All of it is in `~/.dayglass` (or `DAYGLASS_HOME`), mostly `dayglass.sqlite`. The folder is created with mode 700. An administrator, and any process running as that macOS user, can read it. Dayglass does not encrypt the database; FileVault, if on, encrypts the disk. Full detail is in [MEETING-PARTICIPANT-DATA.md](MEETING-PARTICIPANT-DATA.md).

| Data | Kept | In 2.4.1 |
| --- | --- | --- |
| Meeting audio (WAV chunks) | Deleted right after its transcription step, unless a caller asks to keep it (`transcribe_recordings` in `dayglass/meetings.py`). `keep_audio` defaults to false and `keep_audio=True` appears nowhere in `dayglass/` on `main` | Yes |
| Transcripts, speaker names, Teams roster, captions, speaker samples | No limit. Kept until `dayglass forget-meetings --yes` or removal of `~/.dayglass`. A 90-day default is **planned**, not in any release | Yes, as described |
| Screenshot images | Newest 400 kept | Yes |
| Text read off screenshots | No limit, until `~/.dayglass` is removed | Yes |
| Hourly snapshot folders | 30 days | Yes |

No voice model or voiceprint is built.

## Deleting data

- **One meeting.** Not possible yet. A per-meeting delete is planned and is not in any release.
- **All meetings (in 2.4.1).** `dayglass forget-meetings --yes` deletes all meeting and participant data, rebuilds the search index and runs `VACUUM`. Screen history stays. Proof on a throwaway folder: `scripts/prove_forget_meetings.sh`.
- **Everything.** Quit Dayglass and remove `~/.dayglass`.

- **Not removed by `forget-meetings`.** Exported markdown copies of meetings (`~/.dayglass/exports/meetings`, `DAYGLASS_EXPORT_DIR`, and any Obsidian or other vault folder Dayglass wrote to), and the `turn_reactions` table. Delete exported files yourself.

Test: `tests/test_edr_hardening.py::test_forget_meeting_data_clears_participants_and_audio`.

## Uninstall

The Homebrew cask lives in a separate repository (`homebrew-dayglass`) that this pack does not review. The manual steps below are what Dayglass itself installs.

By hand:

1. Quit Dayglass from the menu bar.
2. `launchctl bootout gui/$(id -u)/com.iganapolsky.dayglass-server`
3. Remove `~/Library/LaunchAgents/com.iganapolsky.dayglass-server.plist`.
4. Remove `/Applications/Dayglass.app` and `~/.local/bin/dayglass`.
5. Remove data: `~/.dayglass` (or `DAYGLASS_HOME`, logs are in its `logs` folder), `~/Library/Application Support/Dayglass`, `~/Library/Preferences/com.iganapolsky.dayglass.plist`.
6. In Keychain Access, delete items whose service starts with `com.dayglass.` (cloud AI keys, if any were added).
7. In System Settings > Privacy & Security, remove Dayglass from Screen Recording, Microphone, Calendars and Automation.

## SBOM

[sbom/dayglass-2.4.1.cdx.json](sbom/dayglass-2.4.1.cdx.json) (CycloneDX 1.5), written by `scripts/sbom_from_dmg.py` from the mounted v2.4.1 DMG without running anything in it. 59 components:

- 49 Mach-O files with SHA-256, all arm64: the Swift app, nine Swift helpers (`dayglass-framecapture`, `-livetranscribe`, `-localchat`, `-micinuse`, `-ocr`, `-snapmask`, `-systemaudio`, `-teamscaptions`, `-windowlist`), the Rust core library, bundled Python 3.12.14, `ffmpeg` (a build configured with `--enable-gpl`), `whisper-cli` with its `ggml` and `libomp` libraries, and the native modules of the Python packages
- The Whisper model `ggml-tiny.en.bin`, with SHA-256
- Seven bundled Python packages with versions: `flatbuffers` 25.12.19, `numpy` 2.5.5, `onnxruntime` 1.32.0, `packaging` 26.3, `pip` 26.2.1, `protobuf` 7.36.2, `tokenizers` 0.23.3
- The Dayglass Python source (282 files), as one hash over every file's hash
- `Install CLI.command`

## Signing and notarization, v2.4.1

Captured 2026-11-20 18:28 UTC from `Dayglass.dmg`, SHA-256 `f65644e1652f18884ce4708c03fe3a78b9fd031cdda42b7f456bfa939298e47a` (matches the release's `SHA256SUMS`).

```
$ xcrun stapler validate Dayglass.dmg
The validate action worked!

$ spctl --assess --type open --context context:primary-signature -vv Dayglass.dmg
Dayglass.dmg: accepted
source=Notarized Developer ID
origin=Developer ID Application: Igor Ganapolsky (9GMM26JC5X)

$ codesign --verify --deep --strict --verbose=2 Dayglass.app
Dayglass.app: valid on disk
Dayglass.app: satisfies its Designated Requirement

$ codesign -dvv Dayglass.app
Identifier=com.iganapolsky.dayglass
Format=app bundle with Mach-O thin (arm64)
CodeDirectory v=20500 size=1188 flags=0x10000(runtime) hashes=26+7 location=embedded
Authority=Developer ID Application: Igor Ganapolsky (9GMM26JC5X)
Authority=Developer ID Certification Authority
Authority=Apple Root CA
Timestamp=Nov 20, 2026 at 12:31:48 PM
TeamIdentifier=9GMM26JC5X

$ xcrun stapler validate Dayglass.app
The validate action worked!

$ spctl --assess --type execute -vv Dayglass.app
Dayglass.app: accepted
source=Notarized Developer ID
origin=Developer ID Application: Igor Ganapolsky (9GMM26JC5X)
```

Both the DMG and the app inside carry a stapled notarization ticket. v2.4.1 needs an Apple silicon Mac and macOS 14 or later.

## Installer and quarantine

Neither `install.sh` nor the Homebrew cask removes the quarantine flag any more ([dayglass-mac PR 28](https://github.com/IgorGanapolsky/dayglass-mac/pull/28), [homebrew-dayglass PR 4](https://github.com/IgorGanapolsky/homebrew-dayglass/pull/4), both merged). The installer checks the SHA-256 against `SHA256SUMS` and refuses a build that fails `codesign --verify` or `spctl --assess`. The v2.4.1 `Install CLI.command` does not run `xattr`. Checked on the live `https://www.dayglass.io/install.sh` at 2026-11-20 18:30 UTC: no `xattr`; it still sent the PostHog install event at that time.
