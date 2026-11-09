# AV-C41–C45 — parry result outcomes and receipt failure behavior

## Completed offline

- Parses `no_contact`, `window_refused`, `unexpected_parried_delta`, and `interrupted` outcomes; unknown or malformed outcomes fail closed.
- No-contact receipts require unchanged player parry counters and must agree with an opened attempt. Refused attempts must have `opened=false`; successful contacts cannot also claim refusal/no-contact for the same instance.
- Timeout slots remain unique and must point to a recorded `parry_watch` action.
- Subprocess coverage verifies malformed parry result logs exit nonzero with no success-shaped stdout.
- Refreshed queue/test handoffs against mailbox through C-1126. There is no newer Claude verdict after X-1601; Lead's BUILD-270/parry rerun and BoostLite capture remain outstanding.

## Verification and scope

`python -m unittest Scripts.Tools.test_fight_capture_receipt -q`: 22 passed. Combined AU/AV regression set: 101 passed. Python syntax and scoped `git diff --check` pass. No Unreal, Editor, PIE, build, cook, package, commit or push was run by Codex.
