# Queue AD-C31–C35 — performance evidence and owner gates

Date: 2026-11-07. Read-only receipt/source audit plus documentation corrections. No Round 6 Phase 2 run, game launch, Unreal, build, or device benchmark was performed.

## AD-C31 — Round 6 Phase 1 / Phase 2 status and surviving evidence

The Phase 1 archive exists at `D:\BenchTransfer\R6b\bench_results_GANPATIGAMERBOI_20261106_150650.zip`, size 1,543,766 bytes. Its SHA-256 **matches** both the Lead intake and receipt: `342582190518453db5fa6739e7ce08478682b28c5becc8c7fb3cd00ec3f10a8e`. Extracted raw files remain under `Saved/bench_return/round6_20261106/`; the `runs` folder contains 22 directories across the Phase 1 series, older G4 data, preflight, and warm-up runs. The validated receipt selects 13 measured Phase 1 runs: four TSR anchors and three trials each for Quality, Balanced, and Performance. It excludes the aborted 14:47:53 anchor and both warm-ups. Receipt: `Docs/BossCombatReview/Execution/Codex/R6_PHASE1/receipt.json` (SHA-256 `91e0b7094e2e2728c2718d254df64cffdec14ab6f828ea5a771705472d598cbf`); displayed medians: `report.md`; recomputed summary text: `Saved/bench_return/round6_20261106/summary_table.txt` (SHA-256 `3d27257ef953b977e9f1776ac28cbefb08233ef6d73814900a093253925c44b1`).

I ran `python Scripts/Tools/round6_benchmark_report.py Docs/BossCombatReview/Execution/Codex/R6_PHASE1/receipt.json`; it accepts the 13-row Phase 1 receipt and emits the documented medians. The raw phase-1 archive's source identity is BUILD-240 Development, selected data route, RTX 3060 proxy, driver 610.88, and 1920×1080. C-951 accepts the Phase 1 performance evidence and selects Performance/50% as a **Phase 2 experiment base**. The separate Phase 2 return archive is absent from `D:\BenchTransfer\R6b`; C-954 later orders benchmarking parked / Phase 2 not run. The default decision remains open; there is no Phase 2 measurement.

## AD-C32 — Phase 2 authorization and image-quality requirements

The original C-951 order released `-Round6Tuning` with `-BestDlssMode Performance -BestDlssScreenPercentage 50 -TsrAnchorScreenPercentage 72.886896 -Phase1Accepted -OwnerImageQualityAccepted`. `Scripts/RunPerfExperiments.ps1` checks that tuning has a chosen mode, positive primary fraction, and both Boolean switches; it then creates the planned 16-run treatment/anchor sequence. These command-line switches are operator-supplied assertions, not machine-verifiable owner authorization. C-954 supersedes the earlier release: benchmark testing is parked and Phase 2 has not run. A new explicit owner un-park instruction is required before execution. For a future result, retain current build/mode/fraction/fight-start witnesses, the complete raw 16-run bundle, and a separate owner image-quality disposition of the actual treatment results. A Phase 2 experiment selection alone cannot change the shipped default.

## AD-C33 — DLSS player preference / fallback source audit

`Config/DefaultEngine.ini` registers `/Script/OneBossFight.RPGDLSSGameUserSettings`. `RPGDLSSGameUserSettings.h` persists `DLSSPlayerMode` as a `Config` property defaulting to `Off`, labeled “Off (TSR).” `SetDLSSPlayerMode` applies then calls `SaveSettings`; overridden `ApplySettings` reapplies after the base implementation. Application checks both general DLSS support and requested-mode support. The pure resolver maps Off, unsupported, and unknown modes to TSR; supported DLAA/Quality/Balanced/Performance map through to the plugin. Fallback does not overwrite the saved preference, so an unsupported user's choice can apply on a supported device later. `RPGDLSSPlayerSettingsRulesTests.cpp` expresses the supported/unsupported mapping; `test_dlss_player_settings_contract.py` checks configuration/wiring. This audit did not run those tests or establish settings-menu exposure, packaged plugin support, real-device persistence, or visual quality. Current default remains Off/TSR; C-954 explicitly defers the shipped-mode decision.

## AD-C34 — performance-brief number provenance

Cross-checked `PERFORMANCE_DECISION_BRIEF_ROUNDS_1_6.md` against `PERFORMANCE_LOG.md`, the Phase 1 intake/receipt, `W_C041_OWNER_GAME_SUMMARY.md`, and the Round 4/5 source references. Updated the Round 6 row and owner summary: the older brief's “no returned Round 6 result bundle” statement was stale. Current classifications are:

- Rounds 1, 2, 4, and 5 retain their original source-cited limitations; Round 2 is unstable/directional, Round 3 has no attributable result, and Round 5 mode logs later confirmed active NGX witnesses.
- Round 6 Phase 1 medians are measured (13 receipt runs): TSR 26.66 FPS / 45.7 ms p99; Quality 29.82 / 42.1; Balanced 33.56 / 37.6; Performance 35.19 / 35.9. The receipt additionally records GPU averages of 36.2 / 32.2 / 28.5 / 27.1 ms, respectively. All modes miss 60 FPS average and 16.67 ms p99.
- Round 6 Phase 2 tuning results are absent/parked, not predicted or measured. Performance/50% is only the owner-selected experiment base.
- The 60 FPS / p99 ≤16.67 ms release values remain a target; 120 FPS remains stretch. No current performance claim promotes a prediction or experiment base to a shipped setting.

## AD-C35 — KI-192 C-971 exact route evidence

Updated KI-192 with the exact 0.36 s row from `Docs/BossCombatReview/Execution/Claude/P_C971_ERLATENCY/SUMMARY.md` and both raw probe line exports. At 0.36 s, legacy selected `ChargedAttack_Montage` at 356.63 ms with tick 31.64 ms; selected data chose `Ability_E_Anim_Montage` at 393.00 ms with tick 27.80 ms. The report records 0.34/0.35/0.70 s montage choices as matching between routes. These remain game-tick-bounded observations, do not establish physical input latency or a cause, and are independent of C-980's invalid moving-dodge classification. No threshold change is recommended from this one sampled run.

## Sources and related updates

Owner decisions C-949, C-951, and C-954 are in `Documentation/TEAM_MAILBOX.md`; the final park order controls current status. Updated `ROUND6_PHASE1_INTAKE.md`, `PERFORMANCE_LOG.md`, `PERFORMANCE_DECISION_BRIEF_ROUNDS_1_6.md`, `W_C041_OWNER_GAME_SUMMARY.md`, and KI-192. No Round 6 phase 2 values or owner decision were invented.
