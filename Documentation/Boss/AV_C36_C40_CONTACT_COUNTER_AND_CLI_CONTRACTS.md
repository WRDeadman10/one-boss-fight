# AV-C36–C40 — contact counters and CLI receipt contract

## Completed offline

- A successful `PARRY_CONTACT` now requires its preceding attempt to have `opened=true`.
- Successful contacts are unique per tracker instance, player parried counters are contiguous, and attempt/contact chronology is checked.
- Attempt and contact counter values must be nonnegative; attempt positions must be finite; unknown sources remain rejected.
- The JSON receipt exposes a typed `parry_contacts` array with instance, move, source, timestamp, player counter values and supplemental sweep delta. Existing total counts remain cross-checked against the summary.
- Handoff refreshed through C-1126: AU-C15 and AU-C19 have Lead witnessed passes; candidate readability remains for the owner; BUILD-270 and natural parry rerun remain Lead-owned.

## Verification and scope

`python -m unittest Scripts.Tools.test_fight_capture_receipt -q`: 20 passed. Combined AU/AV regression set: 99 passed. Python syntax and scoped `git diff --check` pass. All added evidence is synthetic/offline. Codex did not open Lead run folders or run Unreal, Editor, PIE, build, cook, package, commit or push.
