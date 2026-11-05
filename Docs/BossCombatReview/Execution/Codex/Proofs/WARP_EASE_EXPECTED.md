# WarpEaseInOut live proof

## Setup

Run `make_warp_ease_profile.py` in the Unreal Editor. It creates a copied ANM006 card/profile/map, changes only the card's `WarpEaseInOut` value, and refuses existing destinations. Run the source ANM006 map as the linear control and the generated `L_SevarogFrameworkProofWarpEaseR1` map as the eased case with the same target start and profile timing. The editor run belongs to Claude.

## PASS

- Both runs emit `[FrameworkProof] warp_summary` for the same card and comparable target conditions.
- Eased run emits `[FrameworkProof] warp_ease on=1` (`RPGFrameworkMoveExecutor.cpp:454`).
- Compare total `movedCm` from `warp_summary` across linear/eased runs: equal within 2 cm when neither run emits `warp_blocked`. The endpoint and total budget should match; intermediate `warp_step` distances may differ because easing redistributes displacement over time.
- Both runs stay within `maxDistanceCm` and `maxAngleDeg` in the summary.

## Control

Use the unchanged ANM006 linear-warp map with the same target start, card, and timing; it must not emit `warp_ease on=1`.

## Validator

`python -I Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py <editor_raw.log>`

## FAIL

- Missing `warp_ease on=1`, mismatched final total displacement beyond 2 cm in unblocked runs, or either total exceeds its configured budget.
- Any `warp_blocked` invalidates the equality comparison and requires a clean geometry run; it is not evidence that easing changed the total-distance rule.
