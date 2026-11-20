<!-- Public copy of docs/PRIVACY-FACTS.md from the private IgorGanapolsky/dayglass repository. File and function references are to that source. -->

# Dayglass privacy facts

**Summary (for Setapp or the website):** Dayglass turns your meetings and screen into searchable notes, and keeps them on your Mac. Screen text is read on the Mac, and AI chat uses Apple's on-device model by default. Nothing leaves your Mac unless you switch on a cloud AI with your own key, or turn on search by meaning, which downloads a model once. Windows such as password managers and banking are skipped. This page cites the code behind every claim.

## What it records, and when

- **Screen.** During a meeting, every 5 seconds by default, it screenshots the meeting window (`DEFAULT_CAPTURE_INTERVAL` and `_capture_once` in `dayglass/engine.py`), only once macOS Screen Recording permission is granted. Outside a meeting it takes no screenshots unless the user sets `DAYGLASS_CAPTURE_ALL_DAY=1` (`capture_outside_meetings` in `dayglass/capture.py`). Since 2.4.1.
- **Hourly context, all day.** Once an hour a snapshot saves, without a picture outside meetings: the front app and window title, the list of open windows, recently changed file paths under project folders, and the working folders of running terminal sessions (`build_context` and `take_snapshot_now` in `dayglass/snapshots.py`). A private or personal front window is saved as `(private)`; windows, files and folders that match the private list are left out.
- **Screen text.** Apple's Vision framework reads the text on the Mac (`macos/dayglass_ocr.swift:1-9`). It is stored as read, with no password scrubbing (`dayglass/engine.py:231-258`).
- **Audio.** During a call it records the microphone and system audio in short chunks (`dayglass/meetings.py:3331-3361`). A call is detected automatically or started by hand (`dayglass/meetings.py:5382-5392`).
- **Transcript.** Each chunk is transcribed on the Mac, then its audio file is deleted unless a caller asks to keep it (`dayglass/meetings.py:3376-3392`).

## Where it is stored, and who can read it

- In `~/.dayglass`, or the folder named by `DAYGLASS_HOME` (`home_dir` in `dayglass/store.py`).
- The folder is created owner-only, mode 700 (`connect` in `dayglass/store.py`). An administrator, and any process running as that macOS user, can read it. The database is not encrypted by Dayglass; FileVault, if on, encrypts the disk.
- The local server listens on `127.0.0.1` only. It has no login or token: any process on the Mac can call it. It refuses requests whose `Host` is not a loopback address and requests from other web origins, which stops websites and DNS rebinding (`local_request_allowed` and `DayglassHandler.parse_request` in `dayglass/server.py`).
- Chat API keys you add go in the macOS Keychain (`dayglass/chat_engine.py:130-150`).

## What can leave the Mac

Nothing in normal use. The exceptions:

- **Cloud AI chat, if you choose it.** The default is Apple's on-device model (`dayglass/chat_engine.py:3`, `dayglass/chat_engine.py:81`). A cloud provider needs your key and your confirmation (`dayglass/chat_engine.py:258-264`). Chat then sends your question and matching meeting notes to that company (`dayglass/chat_engine.py:277-279`). `DAYGLASS_CHAT_LOCAL_ONLY=1` blocks this (`dayglass/chat_engine.py:247-250`).
- **Search by meaning, if you turn it on.** It is off by default (`dayglass/semantic_index.py:1`). Turning it on downloads about 200 MB from `huggingface.co`, once (`dayglass/semantic_index.py:46-58`, `dayglass/semantic_index.py:161-195`).
- **Local chat model.** Dayglass can ask your Ollama to download a 2 GB model (`dayglass/local_model.py:21-22`, `dayglass/local_model.py:86-100`).
- **Setapp licence.** The Setapp build checks access with Setapp's servers and grants nothing if they cannot be reached (`dayglass/setapp_vendor.py:13-14`, `dayglass/setapp_vendor.py:26`).
- **Analytics.** Events are saved on the Mac (`dayglass/analytics.py:24`). They go to PostHog only if someone sets a key, and none ships (`dayglass/analytics.py:42`, `dayglass/analytics.py:358-364`).
- **Feedback.** A vote goes to ThumbGate only with your consent and a key you set (`dayglass/feedback.py:478-481`).
- **Unexpected: IP lookup.** `dayglass privacy` and the privacy status endpoint look up your public IP on `api.ipify.org` (`dayglass/privacy_routing.py:222-249`, `dayglass/privacy_routing.py:354`). Capture does not do this.

## What is skipped automatically

- Before each screenshot, the front window's app and title are checked against a skip list (`dayglass/capture.py:284-285`). It covers 1Password, Bitwarden, Keychain Access, banking sites, payroll pages, WhatsApp, Telegram, Signal, and titles with "passwords" or "credentials" (`dayglass/capture.py:29-36`).
- **Unexpected:** the list also skips Google Meet and personal Teams windows, even in a meeting (`dayglass/capture.py:33`).
- A screenshot whose text matches a personal-surface pattern is deleted (`dayglass/engine.py:232-234`).

## Pause, delete, exclude

- **Stop a recording.** File menu "Stop Recording", or `dayglass stop` (`macos/main.swift:2329-2333`, `dayglass/cli.py:432`).
- **Pause capture.** Turning off Screen Recording in System Settings stops it (`dayglass/capture.py:278-279`).
- **Delete.** Screenshots beyond the newest 400 are deleted, and their text stays (`prune_frame_images` in `dayglass/store.py`, `IMAGE_KEEP_NEWEST` in `dayglass/engine.py`). Snapshot folders older than the retention setting, 30 days by default, are deleted (`DEFAULT_RETENTION_DAYS` and `prune_snapshots` in `dayglass/snapshots.py`).
- **Meetings.** In 2.4.1 and on `main` today, nothing deletes a meeting automatically and no per-meeting delete exists. Transcripts, speaker names, the Teams roster, captions and speaker samples stay until you run `dayglass forget-meetings --yes` or remove `~/.dayglass`. Screen frames and the text read off them are not touched by that command. Details in [MEETING-PARTICIPANT-DATA.md](MEETING-PARTICIPANT-DATA.md). A 90-day default and a per-meeting delete are planned; they are not in any release yet.
- **Screen text.** The text read off screenshots has no retention limit. It goes only when `~/.dayglass` is removed.
- **Exclude an app from search.** `DAYGLASS_SEARCH_EXCLUDE_APPS` replaces the hidden-apps list (`dayglass/store.py:688-691`, `dayglass/store.py:707-715`). It hides search results, not capture.

## What runs on the Mac

- Transcription: Apple's speech model on macOS 26 and later, with local Whisper as the fallback (`macos/livetranscribe.swift:1-2`, `dayglass/meetings.py:3636-3637`).
- Chat: Apple's on-device model, or Ollama or LM Studio on your Mac (`dayglass/chat_engine.py:281-285`).

## Not covered here

- **Private browser windows.** I found no code that skips them, though the pricing page says it does (`dayglass/web/pricing.html:590`).
- **Pause and delete.** I found no in-app screen pause, "delete everything" action, or capture exclusion. There is no in-app delete for a single meeting yet (planned, not in any release); deleting all meetings is `dayglass forget-meetings --yes`.
- **Audio.** I did not find the skip list applied to audio recording.
- **Encryption.** I found no database encryption in `dayglass/store.py`.
- **Updates and crash reports.** I found no update check or crash upload.
- **Not audited.** Pro licence and checkout calls, other modules' network calls, and what Apple, Ollama, Hugging Face, Setapp or a chosen AI company does with a request.
