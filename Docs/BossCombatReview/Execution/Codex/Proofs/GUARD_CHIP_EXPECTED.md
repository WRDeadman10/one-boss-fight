# Guard chip live proof

## Setup

Run `make_guard_chip_profile.py`; compare its map with the unchanged F5 control. Have the target guard an otherwise accepted boss hit, and keep target health high enough that health clamping cannot reduce the applied amount.

## PASS

- Enabled profile emits `[FrameworkProof] guard_chip incoming=<x> applied=<y>` for an accepted guarded hit (`RPGFrameworkMoveExecutor.cpp:291` or `:413`).
- `x > 0`, `y > 0`, and `y / x` is 0.25 within 0.01 absolute ratio tolerance. The control profile emits no guard-chip line and applies no chip damage while guarded.
- The hit remains classified as guarded and does not cause an unguarded-hit reaction.

## Control

Use the unchanged F5 profile/map with guard chip disabled and the same accepted guarded contact; no chip line or chip damage should occur.

## FAIL

- Missing line for a confirmed accepted guarded hit, nonpositive values, incorrect ratio, or chip damage when the feature is off.
- A rejected, invulnerable, parried, lethal-clamped, or unguarded hit is not a valid ratio sample.

## Validator

`python -I Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py <editor_raw.log>`
