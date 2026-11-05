# Combined opt-in proof sequence plan (R21–R25)

The driver calls the existing `Docs/BossCombatReview/Execution/Claude/F4/run_pie.ps1` wrapper, which writes `current_map.txt`, `current_log.txt`, optional console/overlay settings, then launches `F4/drive_pie.py`. The driver defaults to printing the sequence. Claude can use `--execute` to launch it from a console session; each case is a separate PIE/editor process because `drive_pie.py` ends PIE and quits the editor after one proof result.

## Order

1. Warp linear control, then WarpEaseInOut. Same card family and conditions; compare final total distance before any other movement hook is enabled.
2. Strafe stuck recovery in its collision cage. It runs alone because the walls intentionally change movement.
3. Yaw probe with cone hysteresis off, then on. The same 5-degree probe isolates the effect of the profile's 6-degree hysteresis.
4. Guard chip with real block input. No parry hook is enabled, so the guarded-damage ratio is isolated.
5. Parry recovery with repeated real parry input. No blocking or guard-chip profile is active.
6. Telegraph fair scale on its copied profile, with no other timing feature enabled.
7. Aggro switch after the synthetic dodge-rate sequence. No fatigue or cone probe is active.
8. Fatigue after a target-shift schedule is calibrated from the selected card's active/recovery times. Shift the target out during each active window and back before the next decision; the script refuses to execute the full batch until this command is supplied.
9. Player stamina and overlay together. Overlay is observational; the same real parry input drives stamina and supplies visible `Parry`/`Grade` data.

Each map is reloaded in a fresh editor run and each feature profile is isolated. Expected-log files in this folder define per-case PASS/FAIL. Preserve each generated `editor_raw.log`; run `python -I Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py <editor_raw.log>` after each run. For a telemetry-presence report against a case sheet, run `python -I Scripts/Tools/proof_report.py <editor_raw.log> <feature_EXPECTED.md>`. Its PASS/FAIL covers required token presence only; lines without a registered token and all numeric/gameplay relationships remain manual review. The owner/Claude chooses when to execute; Codex only prepared this plan.

## Invocation

- Print plan: `python -I Docs/BossCombatReview/Execution/Codex/Proofs/drive_opt_in_features.py`
- Execute after fatigue schedule calibration: `python -I Docs/BossCombatReview/Execution/Codex/Proofs/drive_opt_in_features.py --execute --fatigue-console "rpg.BossProofTargetShift <seconds:dx,dy,dz|...>"`
