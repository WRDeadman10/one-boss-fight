# Queue BK-06–BK-10 — X26 driver support

**Status:** Lead's aggregate X26 C1278 matrix is complete across R3 and R4: all seven table checks pass, plus the S7 dodge-out mode (8/8 evidence rows including the variant). AG independently verified the build and R4 receipts in A-840. The separate deferred framework-selection live arm (BK-3) and S4→S5 120 cm boundary issue remain open; no authored card values changed.
**Authority:** Claude C-1286 and C-1288; acceptance predicates: `Documentation/Boss/C1278_X26_LIVE_CHECK_ACCEPTANCE_TABLE.md`.

## Work completed

- BK-06: `Scripts/Editor/pie_sevarog_framework_live.py:25-45` accepts `SEVAROG_LIVE_CARDS` as comma/plus-separated IDs, rejects duplicates/unknown values before PIE, and preserves the four-card default.
- BK-07/08: `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.h:35-39` and `.cpp:200-218` add a Shipping-disabled, standalone test actor health-fraction setter. The driver applies `SEVAROG_LIVE_BOSS_HEALTH_FRACTION` after test initialization and allows the ordinary phase-tick logic to run before card requests (`pie_sevarog_framework_live.py:332-353`). It does not directly latch Phase 2 or fabricate a transition log.
- BK-09: `pie_sevarog_framework_live.py:292-329` positions S6/S7/S8 at 120/600/400 cm respectively and checks/logs actual distance against each authored spec band. S7's optional `SEVAROG_LIVE_S7_DODGE_OUT=1` variant moves 500 cm at release + 0.3 seconds and records actual displacement (`:650-675`).
- BK-10: `Scripts/Tools/test_bk2_x26_driver_contract.py` checks driver controls and source guard; four focused source assertions pass.
- C-1288 also ordered the verifier work now present at `Scripts/Tools/verify_c1278_x26_live_log.py`: separate P1/P2/S6/S7a/S7b/S8a/S8b PASS/FAIL rows with matching lines, phase pool cardinality, S6 in-band distance, S7 center sample and release/resolve card times, stationary/dodge-out S7 modes, inside/cone-escape S8 modes, and optional JSON receipt. Synthetic regression tests are in `Scripts/Tools/test_verify_c1278_x26_live_log.py`.

## Validation

- `python -m unittest Scripts.Tools.test_bk2_x26_driver_contract Scripts.Tools.test_verify_c1278_x26_live_log Scripts.Tools.test_c1278_x26_acceptance_contract` — **12 passed** for driver/verifier implementation; after edge-case hardening, the same command passes **18 tests**.
- `python -m py_compile Scripts/Editor/pie_sevarog_framework_live.py Scripts/Tools/verify_c1278_x26_live_log.py` — passed.
- `git diff --check -- <BK-2 changed paths>` — passed.
- C-1155 run `Docs/BossCombatReview/Execution/Codex/BK2_X26_DRIVER/Run_20261110_213723/`: Development build exit 0; pinned DD27j suite **509/509**, exit 0, hash `cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec`; bounded PIE reports `SPAWN_PASS=True`, `S1_IN_BAND_STARTED=True`, `CARD_WINDOW_ELAPSED=True`, `SELF_TEST_FINISHED=True`, `NO_ASSET_SAVES=1`. C-1155 locks released; editor closed. This proves bounded S1 driver readiness only, not the Lead's X26 live acceptance matrix.
- The first PIE run exposed an asynchronous `PENDING` navigation result; driver now polls for the terminal result. A second run exposed that controller possession is not reflected by the Python bridge, so the driver records it as unexposed rather than inferring failure or claiming a match. Navigation itself reached `Success` before the S1 request.

## Remaining in BK-2

The current C++ `area_effect_snare state=Ended` receipt omits its instance id, so the verifier reports it as an uncorrelated cleanup line rather than claiming it belongs to the S7 instance. The C++ release/resolve logs include local card time so the verifier can check the 0.800 release and >=1.550 resolve. Synthetic hardening now covers each table row, missing/duplicate/out-of-order phase transitions, bad S6 range/hit counts, S7 wrong damage/early resolve/missing restoration, S8 cadence/cone-miss damage/heal cap, and JSON receipt output. Lead live matrix remains pending and must be checked against the verifier without upgrading unknown evidence.

## X26 R3 live matrix and follow-up (2026-11-11)

The five fresh, no-save receipts are `Docs/BossCombatReview/Execution/Codex/P_C1297_X26R3_A..E/`. AG independently checked them against `C1278_X26_LIVE_CHECK_ACCEPTANCE_TABLE.md` in A-835:

- Arm A: X26-S7a and X26-S7b pass.
- Arm B: X26-S6, X26-S8a, and X26-S8b pass.
- Arm C: X26-S7a and X26-S7-dodge-out pass.
- Arms D and E: X26-P1 passes; Arm E X26-P2 **fails** because the first selected card starts before the phase latch and the one-shot driver makes no later selector call.

Therefore seven checks are witnessed and X26-P2 remains open. S6 and S8 have disjoint authored range bands; valid P2 evidence requires distinct post-transition selector decisions at both bands (115 cm and 400 cm). The opt-in driver now waits for the actual Phase_2 getter before placing the player and requesting each decision. Its C++ phase getter is editor-only. No new Development build or live rerun is claimed for this follow-up; the prior recovery build remains 511/511.

The S4-to-S5 refusal in Arm A is a separate range-boundary issue, not part of the C1278 X26 matrix: S4's 120 cm warp standoff equals S5's narrowed 120 cm maximum, so floating-point residual sometimes triggers `MoveModel.Range`. No card values were changed; preserve as a follow-up unless separately authorized.

AG's independent receipt review is recorded in A-840. The BK-3 deferred framework-selection live arm remains unrun/open and is not implied by X26 acceptance.

Offline P2 verifier coverage now requires two distinct post-transition selector sequences, S6 and S8 candidates, at least three eligible unique candidates, exactly one phase transition, and no `NoCandidate` refusal. Lead-owned fixture contracts pass: `test_verify_c1278_x26_live_log.py` 18/18; all `test_verify_*.py` 37 passed, 1 skipped; `test_bk2_x26_driver_contract.py` 11/11; all `test_b*_contract.py` 137/137. These are offline results, not live P2 acceptance.

## X26 R4 phase-gate acceptance (2026-11-11)

After a fresh C-1155 Development build and pinned DD27j suite (exit 0; 511/511; locks released), Lead ran `P_C1297_X26R4_E/` with the opt-in Phase_2 probes. The driver finished with `route_verified=true`, `timed_out=false`, and no asset saves. Its verifier receipt marks X26-P1 and X26-P2 PASS; other rows are absent in this P1/P2-only arm and are not part of its verdict. The P2 evidence contains one Phase_1→Phase_2 transition at 125/250 health, distinct post-transition S6 and S8 decisions at the 115 cm and 400 cm bands, and corresponding card starts. Together with R3's seven accepted table checks, all seven table checks pass; the S7 dodge-out mode also passes (8/8 rows including the variant). AG independently verified the build and R4 receipt in A-840. The BK-3 deferred framework-selection live arm remains open separately. Build receipt: `Docs/BossCombatReview/Execution/Codex/B_C1297_PHASE2_BUILD_1127Z/`; live receipt: `Docs/BossCombatReview/Execution/Codex/P_C1297_X26R4_E/`.
