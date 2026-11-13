# Queue BK — Engineering Work (`BK-01..BK-50`)

Successor to `QUEUE_BJ.md`, rewritten per Claude C-1286/C-1288. Ten batches of five engineering tasks, grouped around the eight Lead-seeded lanes. Each batch reports file/line, test names, and receipt path. Build plus pinned suite only under both C-1155 locks when absent and Claude has released the engine; no commit or push by Codex. Per C-1293, BK-06..20 completed first, then BK-01..05 starts while Claude runs X26 live validation. Do not use Unreal until Claude releases the editor.

## Batch 1 — BK-1 Grey root-motion retarget tool (`BK-01..05`, active per C-1293)
| ID | Engineering task | Acceptance |
|---|---|---|
| BK-01 | Inventory dodge montage sequence references from `URPGDodgeTiming`, `GA_Player_Dodge`, and weapon ability montage arrays | Source-derived exact referenced sequences and consumers; no guessed asset set |
| BK-02 | Add a non-destructive `*_RM` retarget mode for only inventoried sequences | Existing sources/assets remain untouched; outputs are separate assets |
| BK-03 | Emit root-XY proof manifest per source/output pair | Source/output paths, displacement, ratio, and validation status recorded |
| BK-04 | Add safe montage duplication/repoint step for affected `_Grey` montages | Duplicated montage segments reference `_RM` sequences; originals preserved |
| BK-05 | Add offline contracts for selection, non-destructive outputs, manifest, and repoint mapping | Contracts cover wrong/unreferenced sequence refusal and never save editor assets |

## Batch 2 — BK-2 X26 driver inputs and phase test hook (`BK-06..10`, active)
| ID | Engineering task | Acceptance |
|---|---|---|
| BK-06 | Add `SEVAROG_LIVE_CARDS` comma/plus parser and allowlisted move IDs | Default card list unchanged; invalid/duplicate IDs fail before PIE |
| BK-07 | Add a Shipping-excluded boss test health-fraction bridge | Standalone test actor only; validates finite `(0,1]`, logs old/new/max, cannot mutate production route |
| BK-08 | Apply `SEVAROG_LIVE_BOSS_HEALTH_FRACTION` through the bridge and allow normal phase logic to consume it | No fabricated phase transition; driver waits for ordinary transition before starting requested card |
| BK-09 | Add S6/S7/S8 per-card in-band spawn placement | S6 90–150, S7 300–900, S8 220–620 cm; actual planar readback logged and validated |
| BK-10 | Add source-contract coverage for environment parsing, Shipping guard, health hook, and range placement | Contract checks default compatibility and refusal cases; no editor execution |

## Batch 3 — BK-2 S7 variant and C1278 verifier (`BK-11..15`)
| ID | Engineering task | Acceptance |
|---|---|---|
| BK-11 | Add S7 dodge-out variant scheduled at release + 0.3 seconds | Moves target outside snapshot radius before resolve; records requested and actual displacement |
| BK-12 | Add offline verifier CLI for `C1278_X26_LIVE_CHECK_ACCEPTANCE_TABLE.md` | One PASS/FAIL per matrix row with exact matching source log lines |
| BK-13 | Verify phase refusal and unlock/candidate rows | S6/S8 phase refusal, one phase transition, post-transition candidates checked in order |
| BK-14 | Verify S6 hit count and S7 release/resolve/damage/snare rows | Single accepted S6 scythe group; S7 stationary and dodge-out cases distinguish damage/snare behavior |
| BK-15 | Verify S8 cadence, cone-miss, and heal-cap rows | Five exact ticks at 0.467–1.267; inside and escape cases checked against table |

## Batch 4 — BK-2 verifier test hardening (`BK-16..20`)
| ID | Engineering task | Acceptance |
|---|---|---|
| BK-16 | Add synthetic passing fixtures for each C1278 row | Fixtures contain exact C++ log shapes and produce matching row receipts |
| BK-17 | Add negative fixtures for missing/duplicate phase and bad ranges | Failures identify row and preserve offending/missing evidence |
| BK-18 | Add negative S6/S7 damage, resolve, and snare fixtures | Wrong hit count, outside damage, early resolve, or failed restore reject |
| BK-19 | Add negative S8 cadence/cone/heal fixtures | Wrong count/time, healing on miss, or heal-cap breach reject |
| BK-20 | Publish BK-2 receipt and run focused offline contracts after engine release | File/line, exact test names, command and actual outcome; no live claim without Lead log |

## Batch 5 — BK-3 BE selected-route live verifier (`BK-21..25`)
| ID | Engineering task | Acceptance |
|---|---|---|
| BK-21 | Parse the BF-X05 selected-route acceptance sheet into explicit verifier predicates | Each sheet requirement maps to stable row ID and source line |
| BK-22 | Verify build/map/definition/config/route identity header | All fields present and consistent for a single run |
| BK-23 | Verify one terminal/HUD/victory/retry cycle and participant generation | Event order and generation linkage are enforced |
| BK-24 | Verify stale-generation callback refusal and default-off pack regression | Required refusal and untouched pack route are evidenced in matching log lines |
| BK-25 | Add synthetic verifier contracts and a machine-readable receipt format | Passing and failing fixtures; no live acceptance inferred |

## Batch 6 — BK-4 selector diagnostics and BK-5 generation fence (`BK-26..30`)
| ID | Engineering task | Acceptance |
|---|---|---|
| BK-26 | Add test-first selector diagnostic coverage for early binding failure | Test proves diagnostic cannot remain empty/stale after refusal |
| BK-27 | Implement diagnostic reset/population at every early failure path | Stable reason and binding identity exposed without changing selection behavior |
| BK-28 | Add same-actor two-generation owned-tag delayed-removal regression | Old cleanup cannot remove new generation's tag |
| BK-29 | Implement generation fence for delayed owned-tag removal | Mismatched generation is a no-op; matching generation cleans up once |
| BK-30 | Add focused native test/report and source guards for BK-26..29 | Test names and shipping surface are explicit; wait for locked build |

## Batch 7 — BK-6 performance attribution (`BK-31..35`)
| ID | Engineering task | Acceptance |
|---|---|---|
| BK-31 | Implement default-off runtime perf CVar and scoped counter storage | No work/counter logging while disabled |
| BK-32 | Count selected framework work by CPU/GPU attribution category | Categories have documented units and no proxy estimate presented as target hardware |
| BK-33 | Add one-line summary with run/build identity and sample window | Summary is machine-readable and absent when feature disabled |
| BK-34 | Add native counter-math tests | Accumulation, reset, zero samples, and overflow/bounds behavior covered |
| BK-35 | Add perf receipt schema and target-device/proxy distinction | RTX 2060 Super target remains distinct from any proxy result |

## Batch 8 — BK-7 Shipping runner (`BK-36..40`)
| ID | Engineering task | Acceptance |
|---|---|---|
| BK-36 | Build one-command Lead runner around task-specific stage path | Refuses if C-1155 locks/editor ownership are absent or conflicting |
| BK-37 | Integrate `CheckShippingBinary` with same-build identity | Exact staged binary, hash, size, and build ID captured |
| BK-38 | Integrate UHT reflection dump and binary scan receipts | Inputs/outputs/exits bound to same build ID |
| BK-39 | Define Shipping receipt schema with artifact lineage | Stage, UAT, source revision, target/config, scans and reflection linked |
| BK-40 | Add offline Shipping receipt validator | Missing/mixed build identity fails closed; does not claim smoke or provenance beyond supplied evidence |

## Batch 9 — BK-8 PIE driver safety (`BK-41..45`)
| ID | Engineering task | Acceptance |
|---|---|---|
| BK-41 | Add common final `RESULT` formatter for PIE drivers | Every terminal success/failure path emits exactly one final result |
| BK-42 | Add Enhanced Input mapping readiness wait helper | First release event cannot raise before mapping readiness; timeout is bounded and reported |
| BK-43 | Migrate the C-1283 warm-up pattern to drivers that inject key releases | Existing timing and input intent remain intact |
| BK-44 | Add offline source-contract scan for `Scripts/Editor/pie_*.py` | Identifies missing result paths and unsafe early `SetKeyDown False` |
| BK-45 | Add focused contracts for formatter and readiness timeout | Normal ready, delayed ready, missing mapping, and exception outcomes covered |

## Batch 10 — Integration and queued remainder (`BK-46..50`)
| ID | Engineering task | Acceptance |
|---|---|---|
| BK-46 | Run one locked build and pinned suite for BK-2 driver/C++ source batch | Both C-1155 locks absent before acquisition; DD27j hash pinned; actual exits recorded |
| BK-47 | Run focused offline verifier/driver contracts for BK-2 | Exact command and pass/fail counts recorded |
| BK-48 | Reconcile Lead X26 live log against verifier output | Every PASS cites matching log line; discrepancies remain FAIL/unknown |
| BK-49 | Prepare next five-task engineering batch from remaining C-1286 seeds | No audits or mailbox-reconciliation tasks; no new queue without engineering acceptance |
| BK-50 | Close Queue BK with source/test/receipt index | Completed, waiting-on-Lead, and blocked tasks separated; no commit/push by Codex |

## Progress

- BK-01..05 source phase authored: exact quick/full roll references were inventoried; a read-only-by-default, explicit-`--write` isolated `_RM` retarget and montage-copy tool was added, with root XY manifest and no-overwrite/no-delete guards. Offline contract 5/5 and Python compilation pass. No asset/editor/build/PIE operation was performed while Claude holds the engine. Actual retarget outputs, montage readback, and RM4 live displacement remain pending a released editor window.
- BK-21..25 complete at verifier/source level: converted the BF-X05 selected-route sheet into nine predicates and added a fail-closed JSON receipt checker plus synthetic regression set (11/11). Python compilation and doc links pass. It records `live_run_verified=false`; no live acceptance is implied. Lead log transcription/live route evidence remains pending.
- BK-06..BK-15 complete: driver controls, test health hook, card placement, dodge-out variant, and C1278 verifier. Driver build and DD27j-pinned suite passed; bounded S1 PIE self-test passed. Lead's S1–S8 live acceptance remains pending.
- BK-16..BK-20 complete: positive row fixtures, negative phase/S6/S7/S8 cases, and JSON receipt contract; focused contracts pass 18/18.
- BK-26..30 source work complete: selector refusal diagnostics are synchronized and refreshed on early failures; owned-tag retry callbacks carry the acquisition generation and refuse stale generations. Offline contract 5/5 and scoped diff check pass; native automation/build remain pending a Lead release. Report: `Documentation/Boss/BK_26_30_SELECTOR_DIAGNOSTICS_TAG_GENERATION_FENCE.md`.
- BK-31..35 source/tooling complete with explicit limits: default-off Development-only inclusive executor CPU scope, saturating counter helper and native counter test authored, machine-readable receipt schema/verifier, and GPU frame-global/component separation. Offline source guard 4/4 and receipt contracts 6/6 pass. Native build/test/benchmark remain pending Lead release; project build ID and GPU component attribution are explicitly unresolved. Report: `Documentation/Boss/BK_31_35_FRAMEWORK_PERF_ATTRIBUTION.md`.
- BK-36..40 source/tooling complete: preflight-only-by-default locked Shipping runner, exact caller-supplied reflection-dump invocation, same-build-ID artifact receipt, binary/source guard integration, and fail-closed receipt validator. Runner contract 5/5 and receipt/hash tests 5/5; PowerShell syntax and schema JSON parse. No build/stage/reflection/scan was run. Approved UHT dump invocation and Lead engine release remain required. Report: `Documentation/Boss/BK_36_40_SHIPPING_PIPELINE.md`.
- BK-41..45 source/tooling complete: added shared one-shot RESULT/readiness helpers; migrated ten input/reach drivers (nine ER probes plus `pie_remains.py`) to readiness-gated input and single terminal results. Helper tests pass 13/13 and scanner tests 3/3; Python compilation passes. The scanner reports 139 runtime-driver candidates / 136 heuristic findings (129 missing recognized RESULT markers, 7 direct key-up calls without recognized readiness markers), explicitly as follow-up inventory rather than runtime proof. No Editor/PIE run while Claude owns the engine. Report: `Documentation/Boss/BK_41_45_PIE_DRIVER_SAFETY.md`.
- BK-46..50 checkpoint: BK-47 offline contracts pass 19/19 after a verifier hotfix (driver 4/4, C1278 acceptance 2/2, live-log verifier 13/13). Five X26 arm logs are now present and independently reconciled in `Documentation/Boss/BK_46_50_INTEGRATION_STATUS.md`; only arm C's S7 dodge-out rows pass (2/7), arm B is incomplete, and no arm passes the matrix. BK-46 locked build/DD27j suite remains held by C-1293 engine ownership. BK-49 has no independent engineering seed beyond Claude's live/engine-owned run order, so no speculative queue was created. BK-50 status index prepared; Queue BK remains open pending Lead review/release and external evidence.
- Continue in five-task batches; check Lead feedback each cycle and hotfix rejected work without waiting before advancing. BK-01 asset execution remains parked until Claude releases the editor.
