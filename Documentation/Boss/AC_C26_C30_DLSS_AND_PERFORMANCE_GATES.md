# AC-C26–C30 — DLSS and performance gates

Date: 2026-11-07. Read-only source, receipt, and documentation audit. No benchmark, hardware run, game/Editor, build, test, or package operation.

## C26 — Round 6 Phase 2 state

C-954 records the owner's order that benchmark testing is parked, Phase 2 has not run, and the shipped DLSS default remains undecided until testing resumes. C-951 selected Performance at primary 50% as an **experiment base**, not a shipped default. No Phase 2 return bundle/results are recorded. The intake remains blank; prior “awaiting” wording should not imply an active benchmark task. `ROUND6_PHASE2_INTAKE.md`, `ROUND6_PHASE2_DEFAULT_DECISION.md`, and the owner summary now say **PARKED / NOT RUN**, preserving the return checklist without scheduling a run.

## C27 — DLSS setting source/config/test matrix

| Concern | Source-backed state | Limit |
|---|---|---|
| Registration | `Config/DefaultEngine.ini:80` selects `/Script/OneBossFight.RPGDLSSGameUserSettings`. | No packaged settings UI is established by this setting. |
| Preference key/default | `RPGDLSSGameUserSettings.h:10-27`: enum Off, DLAA, Quality, Balanced, Performance; Config property `DLSSPlayerMode` defaults Off (TSR). | Does not prove pre-existing user INI migration or engine-level serialization behavior for corrupt enum values. |
| Persistence | `SetDLSSPlayerMode` writes the selected value, applies it, then `SaveSettings`; `ApplySettings` reapplies after superclass (`.cpp:57-68`). | Selection is immediate, not a staged Apply/Cancel form. Restart/driver behavior is unmeasured. |
| Support/fallback | `.cpp:70-86` asks DLSS support and requested-mode support; pure resolver returns TSR for Off/unsupported/unknown. Fallback selects plugin Off and writes UE TSR anti-aliasing mode. Unsupported preference is not overwritten. | Source branch is not a hardware proof; device/driver application and active-upscaler readback remain Lead gates. |
| Tests | `RPGDLSSPlayerSettingsRulesTests.cpp` covers native mapping; `Scripts/Tools/test_dlss_player_settings_contract.py` checks config/default/apply/support/fallback contracts. | No test run in this audit; these contracts do not prove a packaged menu, persistence on device, or visual quality. |

No graphics default is chosen here. TSR remains the current behavior/default pending owner decision after measurement and image review.

## C28 — C-971 0.36 s route-boundary receipt

The retained `Docs/BossCombatReview/Execution/Claude/P_C971_ERLATENCY/SUMMARY.md` and route logs record PIE on legacy and selected-data at about 35 FPS, tick intervals about 25–32 ms. At requested R2 hold 0.36 s, legacy selected `ChargedAttack_Montage` (356.63 ms observed; tick 31.64 ms); data selected `Ability_E_Anim_Montage` (393.00 ms; tick 27.80 ms, see `probe_data_lines.txt`). At 0.34 and 0.35 s both routes selected Ability_E; at 0.70 s both selected ChargedAttack. This is a real route-observation split in the retained run. It is game-tick-bounded, not physical controller latency and does not establish why the routes differ. C-944/C-945 and the input mapping establish the intended 0.35 s charge mapping; the callback in `RPGDodgeTiming.cpp:489-520` handles a triggered R2 tap/strong replay and is not itself the hold-threshold implementation. Keep KI-192 open; do not tune from one sampled boundary run.

The moving-dodge observations in this same probe must be excluded from moving classification pending the C-980 corrected movement-input rerun (KI-196); this does not invalidate the independently logged R2 holds.

## C29 — owner-facing performance claims

| Claim | Classification | Current evidence boundary |
|---|---|---|
| Round 4 route performance: 27.29/27.10 average FPS and 42.88/42.85 ms p99 | Measured historical | BUILD-222, RTX 3060 proxy; relative route comparison passed, absolute target failed. |
| Round 5 DLSS Performance: 38.1 average FPS / 31.9 ms p99 | Measured historical | BUILD-224 selected route, RTX 3060 proxy; still misses 60 FPS / 16.67 ms. Does not choose a default or prove visual acceptability. |
| Round 6 mode/tuning outcome | Absent | No return bundle or rows. Protocol and selected Performance/50% base are not results. |
| `predicted_gpu_saving_ms` | Prediction/input | Explicitly distinct from measured GPU-average delta in the report schema/audits; no prediction is promoted as captured FPS/p99 or saved milliseconds. |
| Project target | Acceptance target | Packaged 1920x1080, average >=60 FPS and whole-frame p99 <=16.67 ms on RTX 2060 Super; RTX 3060 proxy only where owner-approved. 120 FPS is stretch. |

`W_C041_OWNER_GAME_SUMMARY.md` and `PERFORMANCE_DECISION_BRIEF_ROUNDS_1_6.md` already separate these measured, absent, and target figures. Their Round 6 language has been refreshed from “next step” to owner-parked. No benchmark has been run.

## C30 — Phase 2 decision gate

`ROUND6_PHASE2_DEFAULT_DECISION.md` is the owner/Lead sheet. It now preserves the following gates without authorizing a run: owner must un-park testing; validate the exact kit/build identity and complete return bundle; corroborate active mode, fraction, route, and fight-start witnesses; compare valid measurements to the TSR anchor under the existing drift/regression limits; obtain owner image-quality acceptance for the exact measured configuration; then separately review supported-device fallback and packaged behavior. Until these gates are satisfied and the owner decides, keep the shipped default unchanged (TSR). Phase 1/2 Performance/50% selection is not approval to ship that mode.

