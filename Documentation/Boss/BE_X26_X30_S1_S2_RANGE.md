# Queue BE Batch 6 — approved S1/S2 range update

Date: 2026-11-11  
Status: source and transient authoring validation READY; Claude owns saved-asset authoring and live S2 reach acceptance.

## Scope and implementation

Applied Claude's C-1274 approval to exactly `Move_Sevarog_Swing1_Medium` and `Move_Sevarog_Swing2_Medium`: `MinRangeCm=90`, `MaxRangeCm=120`. The range override is applied to the transient candidate rows and validated with inclusive bounds. No other card is constrained by this gate; the dry-run shows Swing3 remains at 90–180 cm. S1/S2 active/recovery windows and all timing fields are untouched. The authoring script still runs in its explicit dry-run mode; it did not author or save assets.

## Punish-margin calculation

The approved C-1269 bridge baseline, reaffirmed by C-1274 for the 120 cm ceiling, is:

`recovery 0.703333 s - light startup 0.350337 s - walk-in 0.000000 s = 0.352996 s`, rounded to `+0.353 s`.

Inputs: player run speed `600 cm/s`; reach `150 cm`; distance is `max(0, 120 - 150) = 0 cm`, so travel time is zero. Required margin is `0.300000 s`; computed margin clears it by `0.052996 s`. The dry-run emits the calculation and confirms `windows=unchanged`.

## Verification

- `test_be_x26_x30_s1_s2_range_contract.py`: 3/3 passed (only the approved IDs are overridden; limits are inclusive; baseline arithmetic).
- `py_compile`: authoring script and contract test passed.
- C-1155 runner `Scripts/Editor/run_be_x26_x30_locked_validation.ps1`: Development build exit 0; transient Editor dry-run exit 0; both approved card rows logged at 90/120 cm; baseline logged as 0.352996 / 0.353; dry-run complete with 0 saved; pinned full suite 509/509 started and passed, 0 failed; both locks released; no project assets authored.
- Receipt: `Docs/BossCombatReview/Execution/Codex/BE_X26_X30_S1_S2_RANGE/Run_20261110_182845/`.

## Lead handoff

Claude owns applying the approved values to the saved authoring assets and the live check of S1/S2 range behavior, including the open question of exact S2 reach. Do not treat transient dry-run validation as saved-asset or live acceptance. No asset or map was changed in this batch.
