# BK-46–50 — integration and Queue BK status

## Task status

| Task | Status | Evidence / dependency |
|---|---|---|
| BK-46 — locked build + pinned suite | Waiting on Lead | C-1293 assigns the engine to Claude's X26 live matrix. No explicit engine release is in the mailbox; Codex did not build or launch PIE. |
| BK-47 — focused offline contracts | Complete | `test_bk2_x26_driver_contract.py` 4/4; `test_c1278_x26_acceptance_contract.py` 2/2; `test_verify_c1278_x26_live_log.py` 13/13 after enum-format hotfix. Total 19/19. |
| BK-48 — reconcile X26 live log | Reconciled; Lead review pending | All five C-1293 per-arm logs are present and were independently rechecked; see the table below. No arm passes the full matrix; arm B is incomplete. |
| BK-49 — seed next engineering batch | Waiting on Lead scope | C-1286's remaining items are live/engine acceptance steps already owned by Claude (Greystone retarget/readback/pairing, X26, selected-route BE, LevelStart, Shipping/UHT). No additional independent Codex engineering seed was assigned; no speculative queue was created. |
| BK-50 — source/test/receipt index | Status index prepared | This report indexes present completion and external dependencies. Queue BK is not represented as fully closed while BK-46 awaits locked build/release and BK-48 awaits Lead review. |

## BK-48 evidence received and independently rechecked

The five C-1293 arm folders now exist under `Docs/BossCombatReview/Execution/Claude/P_C1292_X26_{A..E}`. I read their `status.txt` and `data.log` files, then ran the verifier in-process against each exact log without writing over the Lead's existing `x26_verify.json` receipts. Results below are source observations, not Lead acceptance:

| Arm | Lead status file | Verifier rows | Reconciliation |
|---|---|---|---|
| A | `finished=True route_verified=True` | 0/7 pass | S7 release/sample appears at 0.815 s; at 0.827 s the boss fails on target HP actual=100 vs expected=800, before the +0.75 s resolve. A combat-style change follows immediately; its causal link is unproven. No S7 resolve/damage/snare or phase rows. |
| B | `finished=False route_verified=True` | 0/7 pass | Incomplete run; repeated S6 setup at 120 cm is logged, but no S6 hit, phase rows, S7 resolve, or S8 channel rows. |
| C | `finished=True route_verified=True` | 2/7 pass | S7 dodge-out rows pass: release at 0.819 s; resolve at 1.5796 s, 594.596 cm from center, `inside=0`. Phase, S6, and S8 rows are absent. |
| D | `finished=True route_verified=True` | 0/7 pass | One S3 hit leaves expected target HP=745; target HP later reads 100 and autonomous selection fails. No phase-gate or X26 card evidence. |
| E | `finished=True route_verified=True` | 0/7 pass | Test-health hook logs 0.5 but the old card-start reset restores boss health to max; one S3 hit leaves expected target HP=745, later target HP reads 100, and autonomous selection fails. No phase-gate or X26 card evidence. |

Rechecking uncovered a verifier parsing defect: `RPGFrameworkMoveExecutor.cpp` formats `ERPGDamageOutcome` with `UEnum::GetValueAsString`, which yields values such as `ERPGDamageOutcome::Accepted`; the verifier only accepted bare `Accepted`. `verify_c1278_x26_live_log.py` now accepts both spellings, with a regression test. Focused verifier suite passes 13/13. This parser hotfix does not change any of the five arm results above because their remaining required phase/card evidence is absent (and B is incomplete). The existing Lead receipts were left untouched.

## A-827 source hotfix (offline; runtime pending)

Antigravity's read-only review identified two test-bridge defects in `RPGFrameworkBossCharacter.cpp`: standalone test actors were excluded from the neutral phase gate, and `StartTestCardAtIndex` reset a health fraction set for the phase-two probe. The same card-start health reset existed in `StartComboForTest`. The source hotfix now runs the shared neutral phase/transition logic for standalone test actors while returning before the production autonomous selector, preserves an explicit test health fraction through the next successful test card or combo start, and resets that one-shot state on initialization/restart. `StartSelectedCardForTest` also emits the selector's candidate/refusal traces and advances the diagnostic sequence.

Added offline source-contract coverage in `test_bk2_x26_driver_contract.py`; BK-2 driver, C1278 acceptance, and live-log verifier contracts pass 22/22. The source fix does not establish a successful X26 arm or constitute a native build/PIE validation. The separate player target-health drift from 800/745 to 100 is not explained by these source findings: in arm A it occurs before delayed S7 resolution, and a combat-style log follows the mismatch. Do not infer that the adjacent combat-style message caused the HP change. C-1293 still owns the engine. No Lead review or engine release was received in this cycle.

Antigravity A-828 identified the exact source cause in `RPGFrameworkProofFixture.cpp`: the pack equips `BP_CombatComponent_C.CurrentCombatStyle` about 9.4 seconds after PIE begins and resets player health/max to 100/120. The fixture waits for `PackStyleKnown` before setting target health, but the standalone PIE driver did not. The driver now polls that same component/property before spawning and initializing the test boss, logs readiness, and fails closed after 30 seconds. `spawn_live_boss` also rechecks readiness before initializing the test target. The target-health invariant remains unchanged.

The focused BK-2/C1278 driver, acceptance and live-log verifier contracts now pass 23/23; driver and test Python files compile. This is offline source validation only. C-1293 still owns PIE/build confirmation; no live X26 result is claimed.

## Mailbox and runtime checkpoint

Mailbox history through A-827 contains no Lead verdict on BK-41–45 and no new engine-release instruction. X26 files now exist locally as described above, so BK-48 has an independent evidence reconciliation but remains unaccepted pending Lead review. C-1293 remains the last engine ownership instruction. The Editor process and C-1155 lock files were absent on a read-only local check; this does not replace the required Lead release.

No commit, push, build, Editor launch, PIE run, or live acceptance is claimed.
