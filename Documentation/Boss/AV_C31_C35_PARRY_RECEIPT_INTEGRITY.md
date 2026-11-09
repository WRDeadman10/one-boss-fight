# AV-C31–C35 — parry attempt and contact receipt integrity

## Completed offline

- The full-fight driver timeout is now `timeout_no_live_tracker_window`; the parser still accepts historical `timeout_no_live_a4` rows.
- Receipt diagnostics reject duplicate parry attempts for the same tracker instance and discontinuous press-counter sequences.
- Every reported successful contact must match a preceding attempt by instance, move, source, player press count, and pre-contact parry count.
- Refreshed Queue AV, task status, project state, and test plan against C-1124–C-1126. Lead's BUILD-270/parry rerun and BoostLite capture remain pending; AU-C15/AU-C19 outcomes and the readability risk are recorded without owner decisions.

## Verification and scope

`python -m unittest Scripts.Tools.test_fight_capture_receipt -q`: 18 passed. Combined AU/AV regression set: 97 passed. Python syntax and scoped `git diff --check` pass. No Lead run folder was accessed for this change; no Unreal, Editor, PIE, build, cook, package, commit or push was run by Codex.
