<!-- Public copy of docs/PRIVACY-FACTS.md from the private IgorGanapolsky/dayglass repository. File and function references are to that source, as of commit 467a332 (the v2.4.1 build). -->

# Dayglass privacy facts

Code references in this page are to the private Dayglass source at commit `467a332`, the v2.4.1 build, by file and function or constant name. Where a name could not be checked at that commit, the claim says "not verified".

**Summary (for Setapp or the website):** Dayglass turns your meetings and screen into searchable notes, and keeps them on your Mac. Screen text is read on the Mac, and AI chat uses Apple's on-device model by default. Nothing leaves your Mac unless you switch on a cloud AI with your own key, or turn on search by meaning, which downloads a model once. Windows such as password managers and banking are skipped. Each claim below names the file and function or constant behind it, at commit `467a332`; the few claims I could not trace are marked "not verified".

## What it records, and when

- **Screen.** During a meeting, every 5 seconds by default, it screenshots the meeting window (`DEFAULT_CAPTURE_INTERVAL` and `_capture_once` in `dayglass/engine.py`), only once macOS Screen Recording permission is granted. Outside a meeting it takes no screenshots unless the user sets `DAYGLASS_CAPTURE_ALL_DAY=1` (`capture_outside_meetings` in `dayglass/capture.py`). Since 2.4.1.
- **Hourly context, all day.** Once an hour a snapshot saves, without a picture outside meetings: the front app and window title, the list of open windows, recently changed file paths under project folders, and the working folders of running terminal sessions (`build_context` and `take_snapshot_now` in `dayglass/snapshots.py`). A private or personal front window is saved as `(private)` (the string is in `dayglass/snapshots.py`; I did not trace which function writes it, so the rule for files and folders being left out is not verified).
- **Screen text.** Apple's Vision framework reads the text on the Mac (`VNRecognizeTextRequest` in `macos/dayglass_ocr.swift`). The text body is stored as read: `_capture_once` in `dayglass/engine.py` inserts the raw OCR output. A separate headline and summary come from `sanitize_frame` (`dayglass/sanitizer.py`); what that function removes was not audited.
- **Audio.** During a call it records the microphone and system audio in short chunks (`record_sources` and `record_chunk` in `dayglass/meetings.py`). A call is detected automatically (`detect_active_meeting` in `dayglass/meetings.py`) or started by hand ("Record Now" in the File menu, `macos/main.swift`).
- **Transcript.** Each chunk is transcribed on the Mac, then its audio file is deleted unless a caller asks to keep it (`transcribe_recordings` in `dayglass/meetings.py`). If transcription raises, or the app is killed before that delete runs, the WAV stays in `~/.dayglass/audio` until a later pass removes it. I read this from the code and did not test it.

## Where it is stored, and who can read it

- In `~/.dayglass`, or the folder named by `DAYGLASS_HOME` (`home_dir` in `dayglass/store.py`).
- The folder is created owner-only, mode 700 (`connect` in `dayglass/store.py`). An administrator, and any process running as that macOS user, can read it. The database is not encrypted by Dayglass; FileVault, if on, encrypts the disk.
- The local server listens on `127.0.0.1` only. It has no login or token: any process on the Mac can call it. It refuses requests whose `Host` is not a loopback address and requests from other web origins, which stops websites and DNS rebinding (`local_request_allowed` and `DayglassHandler.parse_request` in `dayglass/server.py`).
- Chat API keys you add go in the macOS Keychain (`_SecurityKeychain` in `dayglass/chat_engine.py`, through Security.framework).

## What can leave the Mac

Nothing in normal use. The exceptions:

- **Cloud AI chat, if you choose it.** The default is Apple's on-device model (`PROVIDERS` and the module docstring in `dayglass/chat_engine.py`). A cloud provider needs your key and your confirmation (`_confirmed_for_call` in `dayglass/chat_engine.py`). Chat then sends your question and meeting notes to that company; exactly which notes are included was not verified. `DAYGLASS_CHAT_LOCAL_ONLY=1` blocks this (`_stay_on_mac` in `dayglass/chat_engine.py`).
- **Search by meaning, if you turn it on.** It is off by default (`is_enabled` in `dayglass/semantic_index.py` returns false when no saved setting exists). Turning it on downloads a model from `huggingface.co` (`HF_REPO` and `HF_COMMIT` in `dayglass/semantic_index.py`); the download size is not verified, and I did not check whether it happens only once.
- **Local chat model.** Dayglass can ask your Ollama to download a 2 GB model (`STARTER_MODEL` and `STARTER_MODEL_SIZE` in `dayglass/local_model.py`, `_pull` posts to `/api/pull` on local Ollama).
- **Setapp licence.** The Setapp build checks access with Setapp's servers and grants nothing if they cannot be reached (`check_application_access` and the module docstring in `dayglass/setapp_vendor.py`).
- **Analytics.** Events are saved on the Mac (`analytics_events` table, module docstring of `dayglass/analytics.py`). They go to PostHog only if someone sets a key, and none ships (`DEFAULT_POSTHOG_PROJECT_KEY = ""` in `dayglass/analytics.py`).
- **Feedback.** A vote goes to ThumbGate only with your separate cloud consent (`consent_thumbgate_cloud` in the `dayglass/feedback.py` docstring; `_sync_vote_to_thumbgate_cloud`, `THUMBGATE_HOSTED_ORIGIN`). That a key is also required was not verified.
- **Unexpected: IP lookup.** `dayglass privacy` and the privacy status endpoint look up your public IP on `api.ipify.org` (`check_anonymity`, called by `privacy_status`, in `dayglass/privacy_routing.py`; the `dayglass privacy` command in `dayglass/cli.py`; `/api/privacy` in `dayglass/server.py`). Capture does not do this.

## What is skipped automatically

- Before each screenshot, the front window's app and title are checked against a skip list (`is_private_window`, called by `get_frontmost_window`, both in `dayglass/capture.py`). The list is `PRIVATE_MARKERS` in `dayglass/capture.py`. It covers 1Password, Bitwarden, Keychain Access, banking sites, payroll pages, WhatsApp, Telegram, Signal, and titles with "passwords" or "credentials".
- **Unexpected:** the list also skips Google Meet and personal Teams windows, even in a meeting (`PRIVATE_MARKERS`: "google meet", "meet.google.com", "teams.live.com").
- A screenshot whose text matches a personal-surface pattern is deleted (`is_personal_surface` in `dayglass/sanitizer.py`, used by `_capture_once` in `dayglass/engine.py`).

## Pause, delete, exclude

- **Stop a recording.** File menu "Stop Recording", or `dayglass stop` ("Stop Recording" in `macos/main.swift`, `stopRecordingFromMenu`; the `stop` subcommand in `dayglass/cli.py`).
- **Pause capture.** Turning off Screen Recording in System Settings stops it (`has_screen_capture_permission` in `dayglass/capture.py`).
- **Delete.** Screenshots beyond the newest 400 are deleted, and their text stays (`prune_frame_images` in `dayglass/store.py`, `IMAGE_KEEP_NEWEST` in `dayglass/engine.py`). Snapshot folders older than the retention setting, 30 days by default, are deleted (`DEFAULT_RETENTION_DAYS` and `prune_snapshots` in `dayglass/snapshots.py`).
- **Meetings.** In 2.4.1 and on `main` today, nothing deletes a meeting automatically and no per-meeting delete exists. Transcripts, speaker names, the Teams roster, captions and speaker samples stay until you run `dayglass forget-meetings --yes` or remove `~/.dayglass`. Screen frames and the text read off them, calendar events and the `turn_reactions` table are not touched by that command. Details in [MEETING-PARTICIPANT-DATA.md](MEETING-PARTICIPANT-DATA.md). A 90-day default and a per-meeting delete are planned; they are not in any release yet.
- **Screen text.** The text read off screenshots has no retention limit. It goes only when `~/.dayglass` is removed.
- **Exclude an app from search.** `DAYGLASS_SEARCH_EXCLUDE_APPS` replaces the hidden-apps list (`DEFAULT_SEARCH_EXCLUDED_APPS` and `search_excluded_apps` in `dayglass/store.py`). It hides search results, not capture.

## What runs on the Mac

- Transcription: live transcription uses Apple's SpeechAnalyzer on macOS 26 and later (`macos/livetranscribe.swift`). The recorded-chunk path in `transcribe_audio` (`dayglass/meetings.py`) tries the bundled `whisper-cli` first and falls back to Apple's `SFSpeechRecognizer`.
- Chat: Apple's on-device model, or Ollama or LM Studio on your Mac (`LOCAL_PORTS` in `dayglass/chat_engine.py`: 11434 for Ollama, 1234 for LM Studio).

## Not covered here

- **Private browser windows.** I found no code that skips them, though the pricing page says it does (`dayglass/web/pricing.html`, the sentence listing "private browser windows").
- **Pause and delete.** I found no in-app screen pause, "delete everything" action, or capture exclusion. There is no in-app delete for a single meeting yet (planned, not in any release); deleting all meetings is `dayglass forget-meetings --yes`.
- **Audio.** I did not find the skip list applied to audio recording.
- **Encryption.** I found no database encryption in `dayglass/store.py` (`connect`).
- **Updates and crash reports.** I found no update check or crash upload.
- **Not audited.** Pro licence and checkout calls, other modules' network calls (for example `dayglass/drex_max.py`, which reads `DREX_SYSTEMONE_URL`, and `dayglass/aaif_agent_standards.py`, which names `api.dayglass.io` fast and frontier endpoints; whether it makes a call was not traced), and what Apple, Ollama, Hugging Face, Setapp or a chosen AI company does with a request.
