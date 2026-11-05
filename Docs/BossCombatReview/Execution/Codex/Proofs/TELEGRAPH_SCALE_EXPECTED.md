# Parry-fair telegraph scale live proof

## Setup

Run `make_telegraph_scale_profile.py`; compare the copied F5 map with its unchanged control. Use the same card and record its authored `ActiveStartSeconds`, `PlayRate`, and `RecoveryEndSeconds`.

## PASS

- Enabled run emits `[FrameworkProof] telegraph_scale card=<id> rate=<r>` and `playback_start ... rate=<r>` with matching rates (`RPGFrameworkMoveExecutor.cpp:139–172`).
- The rate is `min(authoredRate, ActiveStartSeconds / 0.325)` and no lower than 40% of authored rate (`RPGBossParryFairRules.h:10–24`, `RPGBossTelegraphScaleRules.h:10–20`). If the required scale is below that floor, the proof is invalid because the card should refuse as unachievable.
- Control profile emits no `telegraph_scale` and starts at authored rate.
- After natural completion or abort, require `[FrameworkProof] telegraph_restore card=<id> rate=<authoredRate>` from `RestoreCardPlayRate()` and compare it with the authored card rate (`RPGFrameworkMoveExecutor.cpp:569–578`). This token reads the active montage rate after `Montage_SetPlayRate` restores it.
- Treat the control playback rate as an explicit numeric baseline for the *same card*: record its authored `PlayRate` and control `playback_start rate`; require equality. Compare enabled `telegraph_scale` and `playback_start` against that baseline, and require the enabled arm's later `telegraph_restore rate` to return to the baseline. Do not accept cleanup-only evidence as restoration.

## Control

Use the unchanged F5 profile/map and same card as the control; it emits no `telegraph_scale` and keeps the authored start rate.

## Recorded comparison

For `Move_Sevarog_SwingSlow_F5`, control and enabled `playback_start` both report rate `1`; enabled also reports scale rate `1`, then `pie_enabled_run2_restore` reports restored rate `1` (`B_TELEGRAPH/pie_control/editor_raw.log:1584`; `pie_enabled/editor_raw.log:1582,1585`; `pie_enabled_run2_restore/editor_raw.log:1582,1585,1792`). This card did not require a slowdown, so it is a useful baseline/restoration case. For `Move_Sevarog_AntiGreed_F5`, control starts at rate `1`; enabled scale and start both report `0.769231`, then the enabled rerun restores rate `1` (`pie_control:1816`; `pie_enabled:1811,1814`; `pie_enabled_run2_restore:1804,1807,1906`). The enabled rerun therefore supplies both the changed play rate and restoration evidence; the control's gate-off path intentionally emits no `telegraph_restore` token.

## FAIL

- Enabled rate is not the computed minimum/floor, start log disagrees with scale log, control is slowed, or `telegraph_restore` is missing/mismatches the authored rate after cleanup.

## Validator

`python -I Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py <editor_raw.log>`
