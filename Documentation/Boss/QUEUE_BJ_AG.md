# Queue BJ-AG — Independent combat-source audit and bounded offline fixes (`BJ-A01..A50`)

Assigned to Antigravity by the interim Lead while Claude is offline. Ten batches of five. Start with Batch 1; report once after each five tasks and continue to the next batch without waiting for review. This is offline C++/test-source work. No Unreal Editor, engine, build, PIE, packaged run, asset, config-default, Owner-pick, commit, or push operation. Keep findings tied to current file:line and a concrete input/state. Fix only a self-contained source defect with a focused offline/native test; otherwise document the bounded follow-up for Lead.

## Batch 1 — incoming damage and parry (`BJ-A01..A05`)
| ID | Task | Acceptance |
|---|---|---|
| BJ-A01 | Audit resolver precedence for invalid, stale, duplicate, and i-frame hits | Ordering table and edge conditions |
| BJ-A02 | Audit parry window/cost/grade boundaries | Concrete finite and boundary cases |
| BJ-A03 | Audit pack parry observer identity/deduplication | Generation and duplicate paths traced |
| BJ-A04 | Compare resolver/parry tests against source branches | Missing cases named; no duplicate tests |
| BJ-A05 | Batch receipt and fix only a proven pure-rule defect | Focused test source; commands/results if run |

## Batch 2 — dodge and owned i-frame lifecycle (`BJ-A06..A10`)
| ID | Task | Acceptance |
|---|---|---|
| BJ-A06 | Audit dodge input activation ordering and invalid input handling | Source branch map |
| BJ-A07 | Audit owned i-frame add/remove/retry and reset paths | Owner identity and cleanup states mapped |
| BJ-A08 | Audit swing/tracker window resets on montage/instance changes | Stale callback case considered |
| BJ-A09 | Compare rule/native tests against identified lifecycle branches | Exact missing or already-covered cases |
| BJ-A10 | Batch receipt and bounded offline fixes | No live actor/timer claims |

## Batch 3 — player hit intake and combat state (`BJ-A11..A15`)
| ID | Task | Acceptance |
|---|---|---|
| BJ-A11 | Audit hit intake validation and accepted-key spending | Rejection/acceptance ordering |
| BJ-A12 | Audit bleed and damage-scale finite/bounds rules | Inputs, outputs, and clamping documented |
| BJ-A13 | Audit posture/stamina/parry-reward failure boundaries | No double-spend or invented gameplay rule |
| BJ-A14 | Cross-check native tests for hit intake and bleed adapters | Test-to-branch map |
| BJ-A15 | Batch receipt and bounded offline fixes | Focused regression evidence only |

## Batch 4 — encounter selection and generations (`BJ-A16..A20`)
| ID | Task | Acceptance |
|---|---|---|
| BJ-A16 | Audit selection inputs and fallback/default precedence | Explicit selection vs config default separated |
| BJ-A17 | Audit binding generation advancement and stale callbacks | Replacement actor/state traced |
| BJ-A18 | Audit restart/retry cleanup and idempotence | Duplicate/failed reset cases |
| BJ-A19 | Compare activation/restart tests to lifecycle branches | Test gaps with exact evidence |
| BJ-A20 | Batch receipt and bounded offline fixes | No default/config edits |

## Batch 5 — move cards, selection and combos (`BJ-A21..A25`)
| ID | Task | Acceptance |
|---|---|---|
| BJ-A21 | Audit card numeric/phase/slot validation against consumers | No schema-only conclusion |
| BJ-A22 | Audit weighted selector cooldown/repeat/tie behavior | Deterministic tie and invalid candidate states |
| BJ-A23 | Audit combo graph validation and abort fallback | Cycles, stale edges, and phase changes traced |
| BJ-A24 | Compare card/selector/combo tests against branches | Precise missing boundary cases |
| BJ-A25 | Batch receipt and bounded offline fixes | No asset authoring |

## Batch 6 — move executor, montage and interruption (`BJ-A26..A30`)
| ID | Task | Acceptance |
|---|---|---|
| BJ-A26 | Audit executor state transitions and terminal callbacks | Each state has one valid completion/abort path |
| BJ-A27 | Audit montage notify timing fallback and backward seeks | Invalid/duplicate windows and fallback mapped |
| BJ-A28 | Audit watchdog, abort cleanup, and late callback identity | Stale instance cannot complete current move |
| BJ-A29 | Compare executor/timing tests with source transitions | Branch-to-test matrix |
| BJ-A30 | Batch receipt and bounded offline fixes | No live montage claim |

## Batch 7 — target, trace and navigation rules (`BJ-A31..A35`)
| ID | Task | Acceptance |
|---|---|---|
| BJ-A31 | Audit target selection invalidation and controller ownership | World/actor/generation mismatch cases |
| BJ-A32 | Audit approach, leash, stuck recovery and bounds rules | Finite, vertical, and timeout edges |
| BJ-A33 | Audit trace/damage attribution and duplicate contacts | Self-hit and target-contact ordering |
| BJ-A34 | Compare focused navigation/trace tests to contracts | Live-only gaps clearly labeled |
| BJ-A35 | Batch receipt and bounded offline fixes | No PIE or geometry acceptance |

## Batch 8 — phase, effects and cleanup (`BJ-A36..A40`)
| ID | Task | Acceptance |
|---|---|---|
| BJ-A36 | Audit phase transition and reset ordering | Cancellation/terminal paths traced |
| BJ-A37 | Audit optional AreaEffect/ChannelDrain default-off admission | Mutual exclusion and rejected hit boundaries |
| BJ-A38 | Audit temporary movement/tag cleanup ownership | Timer, EndPlay, stale owner paths |
| BJ-A39 | Compare tests to each proven source branch | Pure-rule versus runtime gap distinguished |
| BJ-A40 | Batch receipt and bounded offline fixes | Defaults and assets unchanged |

## Batch 9 — UI, startup, guards and test quality (`BJ-A41..A45`)
| ID | Task | Acceptance |
|---|---|---|
| BJ-A41 | Audit native boss health/HUD and terminal event idempotence | Health, death, victory and retry source flow |
| BJ-A42 | Audit startup route/legacy parity controls and guard scope | Defaults remain unchanged |
| BJ-A43 | Audit Shipping/editor-only declaration guards in scoped headers | No build/UHT claim |
| BJ-A44 | Audit source tests for weak assertions and tautologies | Exact assertion and tested state |
| BJ-A45 | Batch receipt; classify code fixes vs Lead/Owner gates | Current mailbox checked; no assumptions |

## Batch 10 — consolidation (`BJ-A46..A50`)
| ID | Task | Acceptance |
|---|---|---|
| BJ-A46 | Deduplicate findings across prior nine batch reports | One finding per root cause |
| BJ-A47 | Verify each proposed fix is in scope and evidence-backed | No speculative runtime or design changes |
| BJ-A48 | Reconcile changed source/tests/docs against exact task rows | Paths and outcomes complete |
| BJ-A49 | Prepare Lead review/hotfix index | Rejected/uncertain items isolated with reproduction |
| BJ-A50 | Closeout and next-step handoff | No commit/push; no new queue without Lead review |

## Global acceptance

Before changing code, check the current mailbox and project instructions. Preserve other agents' edits. Findings must include file:line, input/state, severity, and source/test evidence. Any implemented fix must remain offline-source scoped and include a focused regression test; record the actual command/result. Anything requiring assets, Owner choices, defaults, Editor, live actors, Shipping, packaging, performance hardware, or architectural direction remains a Lead/Owner gate.
