<!-- Public copy of docs/MEETING-PARTICIPANT-DATA.md from the private IgorGanapolsky/dayglass repository. File and function references are to that source, as of commit 467a332 (version string 2.4.1; see the note below). -->

# What Dayglass keeps about meeting participants

Dayglass records calls, so it keeps data about the other people in them, not only about you. This page says what it keeps, for how long, whether it builds a voice model, and how to delete it. Code references are to the private Dayglass source at commit `467a332`, version string 2.4.1 (the tag `v2.4.1` is not in the private clone, so that this commit produced the shipped DMG is not shown here), by file and table or function name; a claim I could not trace says "not verified". It sits next to [PRIVACY-FACTS.md](PRIVACY-FACTS.md).

All of it lives in `~/.dayglass` (or `DAYGLASS_HOME`), mostly in `dayglass.sqlite` (`home_dir` and `connect` in `dayglass/store.py`). Nothing below is sent off the Mac by the recording path.

## What it keeps about other people

| Data | Where | Defined in |
| --- | --- | --- |
| Words everyone said, transcribed from mic and system audio, with time and source | `audio_chunks` table | `dayglass/store.py` (`CREATE TABLE IF NOT EXISTS audio_chunks`) |
| Full meeting transcript, summary, and action items | `meetings` table | `dayglass/store.py` (`CREATE TABLE IF NOT EXISTS meetings`) |
| The speaker name given to each live transcript turn, and how it was decided | `live_turn_speakers` table | `dayglass/live_stt.py` |
| Names of everyone shown in a Teams call window, with first and last time seen, and a bot flag | `teams_participants` table | `dayglass/teams_roster.py` |
| Who Teams showed as speaking, sampled over time, with the other candidates | `teams_speaker_samples` table | `dayglass/teams_roster.py` |
| Teams live caption text with the speaker's name | `teams_captions` table | `dayglass/teams_captions.py` |
| Calendar subject, organizer, and meeting link | `calendar_events` table | `dayglass/store.py` (`calendar_events`) |
| Names, roles, and notes about people in recurring meetings, if you write them | `meeting_profiles.json` | `dayglass/prep.py` (`_load_recurring_meeting_profiles`) |
| Text vectors of transcript chunks, if search by meaning is on (vectors of words, not of voices) | `audio_vectors` table | `dayglass/semantic_index.py` (`audio_vectors`) |

Screenshots and their on-screen text can also show participants' names and faces. Those are covered in [PRIVACY-FACTS.md](PRIVACY-FACTS.md).

## How long audio and transcripts are kept

- **Audio.** Each chunk is written as a WAV under `~/.dayglass/audio` (`record_sources` in `dayglass/meetings.py`). It is deleted right after it is transcribed, unless a caller asks to keep it (`transcribe_recordings` in `dayglass/meetings.py`). The background recorder passes `keep_audio=False` (`dayglass/daemon.py`). `git grep keep_audio=True` over `dayglass/` at that commit finds nothing. A chunk that failed to record is deleted too (`record_sources`). If transcription raises, or the app is killed before the delete in `transcribe_recordings`, the file stays in the audio folder; nothing at 467a332 removes it except `dayglass forget-meetings` or deleting the folder. Read from the code, not tested.
- **Transcripts, speaker names, Teams roster, speaker samples, and captions.** No retention limit. In 2.4.1 and on `main` today they stay until you run `dayglass forget-meetings --yes` or remove `~/.dayglass`. A 90-day default is planned; it is not in any release yet.
- The 30-day retention setting covers snapshot folders only (`prune_snapshots` in `dayglass/snapshots.py`). Meeting retention does not delete screen frames or their text; see [PRIVACY-FACTS.md](PRIVACY-FACTS.md).
- **Exported markdown copies.** When a meeting ends, Dayglass writes a markdown copy (summary, action items, full transcript) to `~/.dayglass/exports/meetings`, or to the folder in `DAYGLASS_EXPORT_DIR` if set. It may also write copies to `DAYGLASS_SECONDARY_EXPORT_DIR`, to `DAYGLASS_WORK_VAULT_DIR` (`Meetings/Recorded`), and to `Meetings` folders of Obsidian vaults it finds or is configured for (`_export_meeting_markdown` in `dayglass/meetings.py`). Nothing in Dayglass deletes these files, and `dayglass forget-meetings` does not touch them. Delete them yourself.
- **Reactions.** Thumbs and other reactions on transcript turns are saved in the `turn_reactions` table with a short text snippet (`dayglass/store.py`). `dayglass forget-meetings` does not clear that table.

## Does speaker matching build a voice model?

Not in Dayglass's own code. Speakers are named from text and screen signals only: the Teams call window's tiles and People pane, who is muted, the calendar, `meeting_profiles.json`, and names said in the transcript (`dayglass/teams_roster.py`; the speaker-naming code in `dayglass/meetings.py` was not traced to a function). No speaker embedding, voiceprint, or diarization model is computed or stored, and no table holds voice features.

Two caveats:

- `dayglass/anythingllm_steal.py` defines a "Full Diarization (Voiceprint Clustering)" mode. I read it as only a label used in summary headings; I did not verify at this commit that no code clusters voices.
- Transcription runs in Apple's SpeechAnalyzer (`macos/livetranscribe.swift`), `SFSpeechRecognizer`, or a local `whisper-cli` (`transcribe_audio` in `dayglass/meetings.py`). Dayglass asks neither for speaker identity. What those engines do internally is **unknown** from this code.

## How to delete it

### One meeting

There is no way to delete a single meeting in 2.4.1 or on `main` today. A per-meeting delete (an app button and a command) is planned; it is not in any release yet. Until it exists, the only built-in deletes are the all-meetings command below and removing `~/.dayglass`.

### All meetings

```bash
dayglass forget-meetings --yes
```

It deletes every row in the six tables listed in `MEETING_DATA_TABLES` (`audio_chunks`, `meetings`, `live_turn_speakers`, `teams_participants`, `teams_speaker_samples`, `teams_captions`), rebuilds the transcript search index, runs `VACUUM` so deleted text does not linger in free pages, and removes `audio/` and `meeting_profiles.json` (`forget_meeting_data` in `dayglass/store.py`). This command is in 2.4.1. It does not remove `calendar_events` (calendar subject, organizer and meeting link), the `latest-meeting.png` copy, exported markdown, or `turn_reactions`. Screen history stays. Without `--yes` it only says what it would delete. Deleting from `audio_chunks` also removes the matching `audio_vectors` rows (a trigger in `dayglass/semantic_index.py`). It acts on `DAYGLASS_HOME`, so quit Dayglass first, or stop the server with `launchctl bootout gui/$(id -u)/com.iganapolsky.dayglass-server`, so it does not write while you delete.

To delete everything, screenshots included, remove `~/.dayglass` (or your `DAYGLASS_HOME`) after quitting.

### Proof, run on a throwaway folder

`scripts/prove_forget_meetings.sh` seeds a temporary `DAYGLASS_HOME` with one test meeting and runs the command. It never touches `~/.dayglass`. Output from 20 Nov 2026:

```text
seeded /tmp/dayglass-forget-proof.3pcRRA
before: audio_chunks=1 meetings=1 live_turn_speakers=1 teams_participants=1 teams_speaker_samples=1 teams_captions=1
sys_test.wav
$ DAYGLASS_HOME=/tmp/dayglass-forget-proof.3pcRRA python -m dayglass forget-meetings
Would delete meeting and participant data in /tmp/dayglass-forget-proof.3pcRRA. Re-run with --yes.
$ DAYGLASS_HOME=/tmp/dayglass-forget-proof.3pcRRA python -m dayglass forget-meetings --yes
Deleted from /tmp/dayglass-forget-proof.3pcRRA:
  audio_chunks: 1 rows
  meetings: 1 rows
  live_turn_speakers: 1 rows
  teams_participants: 1 rows
  teams_speaker_samples: 1 rows
  teams_captions: 1 rows
  removed /tmp/dayglass-forget-proof.3pcRRA/audio
  removed /tmp/dayglass-forget-proof.3pcRRA/meeting_profiles.json
after: audio_chunks=0 meetings=0 live_turn_speakers=0 teams_participants=0 teams_speaker_samples=0 teams_captions=0
ls: /tmp/dayglass-forget-proof.3pcRRA/audio: No such file or directory
ls: /tmp/dayglass-forget-proof.3pcRRA/meeting_profiles.json: No such file or directory
```

The real `~/.dayglass/dayglass.sqlite` had the same modification time and size before and after the run (`1795189169 270336`).

## Gaps

- There is no retention limit and no per-meeting delete. A 90-day default and a per-meeting delete are planned and not in any release yet; 2.4.1 has only `dayglass forget-meetings`.
- Exported markdown copies of meetings, the `turn_reactions` table, the `calendar_events` table (subject, organizer, link) and the `latest-meeting.png` copy are not removed by `dayglass forget-meetings`.
- There is no in-app "delete all meetings" button; that is the CLI only.
- No notice to other participants. Teams captions are shown only to you, and Teams does not tell others (comment at the top of `macos/teamscaptions.swift`).
- The database is not encrypted (see [PRIVACY-FACTS.md](PRIVACY-FACTS.md)).
