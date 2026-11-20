<!-- Public copy of docs/MEETING-PARTICIPANT-DATA.md from the private IgorGanapolsky/dayglass repository. File and function references are to that source. -->

# What Dayglass keeps about meeting participants

Dayglass records calls, so it keeps data about the other people in them, not only about you. This page says what it keeps, for how long, whether it builds a voice model, and how to delete it. Every claim cites the code. It sits next to [PRIVACY-FACTS.md](PRIVACY-FACTS.md).

All of it lives in `~/.dayglass` (or `DAYGLASS_HOME`), mostly in `dayglass.sqlite` (`dayglass/store.py:61-65`, `dayglass/store.py:178`). Nothing below is sent off the Mac by the recording path.

## What it keeps about other people

| Data | Where | Code |
| --- | --- | --- |
| Words everyone said, transcribed from mic and system audio, with time and source | `audio_chunks` table | `dayglass/store.py:216-225` |
| Full meeting transcript, summary, and action items | `meetings` table | `dayglass/store.py:238-247` |
| The speaker name given to each live transcript turn, and how it was decided | `live_turn_speakers` table | `dayglass/live_stt.py:43-49` |
| Names of everyone shown in a Teams call window, with first and last time seen, and a bot flag | `teams_participants` table | `dayglass/teams_roster.py:30-35`, `dayglass/teams_roster.py:141-150` |
| Who Teams showed as speaking, sampled over time, with the other candidates | `teams_speaker_samples` table | `dayglass/teams_roster.py:36-41`, `dayglass/teams_roster.py:151-154` |
| Teams live caption text with the speaker's name | `teams_captions` table | `dayglass/teams_captions.py:38-44` |
| Calendar subject, organizer, and meeting link | `calendar_events` table | `dayglass/store.py:288-300` |
| Names, roles, and notes about people in recurring meetings, if you write them | `meeting_profiles.json` | `dayglass/prep.py:206-215` |
| Text vectors of transcript chunks, if search by meaning is on (vectors of words, not of voices) | `audio_vectors` table | `dayglass/semantic_index.py:273-283` |

Screenshots and their on-screen text can also show participants' names and faces. Those are covered in [PRIVACY-FACTS.md](PRIVACY-FACTS.md).

## How long audio and transcripts are kept

- **Audio.** Each chunk is written as a WAV under `~/.dayglass/audio` (`dayglass/meetings.py:3338-3349`). It is deleted right after it is transcribed, unless a caller asks to keep it (`dayglass/meetings.py:3376-3392`). The background recorder never asks (`dayglass/daemon.py:134`), and no caller in `dayglass/` passes `keep_audio=True`. A chunk that failed to record is deleted too (`dayglass/meetings.py:3370-3372`).
- **Transcripts, speaker names, Teams roster, speaker samples, and captions.** Kept for 90 days by default, then deleted (`DEFAULT_MEETING_RETENTION_DAYS` and `prune_meeting_data` in `dayglass/store.py`). The server runs this once a day from the same maintenance pass that prunes snapshot folders (`run_maintenance` in `dayglass/snapshots.py`). It deletes `meetings` rows whose start and end are both older than the window, `audio_chunks` older than the window with their `live_turn_speakers` names, `teams_captions` and `teams_speaker_samples` older than the window, and `teams_participants` names last seen before it, then runs `VACUUM`. `DAYGLASS_MEETING_RETENTION_DAYS` sets another number of days; `0` keeps everything until you delete it. Test: `tests/test_meeting_retention_delete.py`.
- The 30-day retention setting covers snapshot folders only (`prune_snapshots` in `dayglass/snapshots.py`). Meeting retention does not delete screen frames or their text; see [PRIVACY-FACTS.md](PRIVACY-FACTS.md).
- This retention is on `main` after Dayglass 2.4.1. In 2.4.1 and earlier, transcripts and participant tables have no retention limit.

## Does speaker matching build a voice model?

Not in Dayglass's own code. Speakers are named from text and screen signals only: the Teams call window's tiles and People pane, who is muted, the calendar, `meeting_profiles.json`, and names said in the transcript (`dayglass/teams_roster.py:1-13`, `dayglass/meetings.py:707-723`). No speaker embedding, voiceprint, or diarization model is computed or stored, and no table holds voice features.

Two caveats:

- `dayglass/anythingllm_steal.py:83-88` defines a "Full Diarization (Voiceprint Clustering)" mode. It is only a label used in summary headings (`dayglass/anythingllm_steal.py:272`, `dayglass/anythingllm_steal.py:291`). No code clusters voices.
- Transcription runs in Apple's SpeechTranscriber (`macos/livetranscribe.swift:192`) or a local `whisper-cli` (`dayglass/meetings.py:3636-3637`). Dayglass asks neither for speaker identity. What those engines do internally is **unknown** from this code.

## How to delete it

### One meeting

Open the meeting in Dayglass and click **Delete meeting** next to **Copy Transcript**, then click again to confirm (`modalDeleteMeetingBtn` and `deleteCurrentModalMeeting` in `dayglass/web/index.html`). The same delete from the command line:

```bash
dayglass delete-meeting <meeting id> --yes
```

Both call `delete_meeting` in `dayglass/store.py`, through `POST /api/meetings/<id>/delete` with `{"confirm": true}` for the button (`dayglass/server.py`). It deletes the meeting row and, between that meeting's start and end: the transcript chunks and their audio files, speaker names, Teams captions and speaker samples, screen frames and their images, and hourly snapshots. A Teams roster name is deleted only if it was seen during this meeting and at no other time. It then runs `VACUUM`; if the running server holds the database at that moment, the rows are still gone and the next daily pass vacuums. A meeting that is still recording is refused. Test: `tests/test_meeting_retention_delete.py`.

The button and `delete-meeting` are on `main` after Dayglass 2.4.1; they are not in 2.4.1.

### All meetings

```bash
dayglass forget-meetings --yes
```

It deletes every row in `audio_chunks`, `meetings`, `live_turn_speakers`, `teams_participants`, `teams_speaker_samples`, `teams_captions`, rebuilds the transcript search index, runs `VACUUM` so deleted text does not linger in free pages, and removes `audio/` and `meeting_profiles.json` (`forget_meeting_data` in `dayglass/store.py`). This command is in 2.4.1. Screen history stays. Without `--yes` it only says what it would delete. Deleting from `audio_chunks` also removes the matching `audio_vectors` rows (`dayglass/semantic_index.py:276-281`). It acts on `DAYGLASS_HOME`, so quit Dayglass first, or stop the server with `launchctl bootout gui/$(id -u)/com.iganapolsky.dayglass-server`, so it does not write while you delete.

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

- Retention and the per-meeting delete button are not in a released build yet (2.4.1 has only `dayglass forget-meetings`).
- There is no in-app "delete all meetings" button; that is the CLI only.
- Retention is set with an environment variable, not in Settings.
- No notice to other participants. Teams captions are shown only to you, and Teams does not tell others (`macos/teamscaptions.swift:6`).
- The database is not encrypted (see [PRIVACY-FACTS.md](PRIVACY-FACTS.md)).
