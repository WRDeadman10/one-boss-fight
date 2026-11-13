# Queue BI — Codex Residual Source and Evidence Work (`BI-X01..X50`)

Successor to `QUEUE_BF.md`, drafted after BF-X41–X45. Work in five-task batches: inspect Claude feedback each cycle, hotfix rejected work immediately, and continue without waiting for review. This is an offline/source/docs queue; no Engine/Editor/build/runtime/package/asset work is authorized by the queue. Do not duplicate Antigravity's active `QUEUE_BH_AG.md`. Lead and Owner gates are explicit blockers. User commits; no commit or push.

## Batch 1 — evidence receipt contracts (`BI-X01..X05`) — COMPLETE (draft only; no runner adoption)

Report: `Documentation/Boss/BI_X01_X05_BENCHMARK_RECEIPT_SCHEMA.md`; proposal: `Documentation/Boss/BENCHMARK_RUN_RECEIPT_V1.schema.json`.

| ID | Task | Acceptance |
|---|---|---|
| BI-X01 | Audit BF/BE run receipt field consumers | Field-to-source table; missing identity fields explicit |
| BI-X02 | Draft versioned immutable benchmark receipt JSON schema | Required/optional types and fail-closed rules |
| BI-X03 | Add offline schema fixture plan for missing build/session/hash | Negative/positive cases only; no captured evidence |
| BI-X04 | Map benchmark summary writer versus receipt proposal | Exact field parity and gaps |
| BI-X05 | Batch receipt and Lead adoption gates | No claim that proposal is implemented or accepted |

## Batch 2 — source telemetry and performance candidate follow-up (`BI-X06..X10`) — COMPLETE (offline static audit)

Report: `Documentation/Boss/BI_X06_X10_PERFORMANCE_CANDIDATES.md`.

| ID | Task | Acceptance |
|---|---|---|
| BI-X06 | Reconcile combat allocation candidates against active call paths | Complete: call paths and event/tick cadence distinctions documented; runtime costs unmeasured |
| BI-X07 | Audit diagnostic log category and Shipping guards | Complete: source boundary recorded; Shipping retention not inferred |
| BI-X08 | Specify minimal profiler counters for combat candidates | Complete: proposed per-run counters documented; no profiler run |
| BI-X09 | Compare performance report target wording across docs | Complete: 60 FPS / p99 target and 120 FPS stretch kept distinct |
| BI-X10 | Batch report and unmeasured-cost boundary | Complete: no profiling or optimization change |

## Batch 3 — Sevarog Niagara spec/evidence gate (`BI-X11..X15`) — COMPLETE (offline source/docs audit)

Report: `Documentation/Boss/BI_X11_X15_SEVAROG_AURA_SOURCE_GATE.md`.

| ID | Task | Acceptance |
|---|---|---|
| BI-X11 | Reconcile BB-A24 and BC-A26 bounds/sprite proposals | Complete: Ember authored facts separated from Sevarog proposals |
| BI-X12 | Audit aura reference/type and excluded historical assets | Complete: exact type/path distinctions; no asset change |
| BI-X13 | Draft Lead readback checklist for candidate bounds/spawn/scalability | Complete: fixed bounds, particle cap, and runtime fields distinguished |
| BI-X14 | Map phase-two prewarm/attach/reset source lifecycle | Complete: source-only map; no runtime claim |
| BI-X15 | Batch report with unresolved Owner/Lead gates | Complete: candidate selection remains Owner-owned |

## Batch 4 — SFX option/evidence intake (`BI-X16..X20`) — COMPLETE (offline static audit)

Report: `Documentation/Boss/BI_X16_X20_SFX_OWNER_PICK_INTAKE.md`; proposal schema: `Documentation/Boss/SFX_OWNER_PICK_INTAKE_V1.schema.json`.

| ID | Task | Acceptance |
|---|---|---|
| BI-X16 | Inventory current SFX manifests and explicit Owner pick slots | Complete: per-scope source, pick state, and reel status table |
| BI-X17 | Draft machine-readable Owner pick intake shape | Complete: pending/selected/none; no choice populated |
| BI-X18 | Audit option path mapping versus current specs | Complete: Wave/Cue distinction and stale/abbreviated paths recorded |
| BI-X19 | Map approved-pick prerequisites to safe authoring/wiring gates | Complete: Owner pick, exact asset reconciliation, Lead review, then authorized implementation |
| BI-X20 | Batch receipt and blockers | Complete: no pick inferred; docs only; media and disk existence not independently verified |

## Batch 5 — framework live-acceptance readiness (`BI-X21..X25`) — COMPLETE (record reconciliation)

Report: `Documentation/Boss/BI_X21_X25_FRAMEWORK_ACCEPTANCE_READINESS.md`.

| ID | Task | Acceptance |
|---|---|---|
| BI-X21 | Reconcile BE-X01..X20 source status with Lead map acceptance | Complete: source/Development and saved/live states separated |
| BI-X22 | Audit terminal HUD/death/retry evidence checklist | Complete: selected-route cycle and replacement-generation evidence listed |
| BI-X23 | Review nav diagnostic receipt against source contract | Complete: route/generation, path result, terminal positions required |
| BI-X24 | List unresolved selected-route gates and owners | Complete: Lead/Owner gates retained |
| BI-X25 | Batch report and next proof ordering | Complete: no PIE or result inference |

## Batch 6 — Greystone authoring and motion evidence (`BI-X26..X30`) — COMPLETE (static source/docs/mailbox audit)

Report: `Documentation/Boss/BI_X26_X30_GREYSTONE_MOTION_EVIDENCE_AUDIT.md`.

| ID | Task | Acceptance |
|---|---|---|
| BI-X26 | Reconcile C-1285/C-1282 and current author scripts | Complete: wrapper readbacks separated from unrecorded `_RM` outputs and paired motion proof |
| BI-X27 | Audit rollback/readback source boundaries after BF-X31..35 | Complete: rig/retargeter persistence and created-output cleanup documented |
| BI-X28 | Specify paired root-motion capture receipt identity | Complete: shared setup, transforms, root/pelvis and capsule fields listed |
| BI-X29 | Map mannequin-default and package gates | Complete: mannequin default and package smoke remain separate |
| BI-X30 | Batch report and blocked actions | Complete: Lead/Owner boundaries preserved |

## Batch 7 — offline tool robustness (`BI-X31..X35`) — COMPLETE (read-only parser/portability audit)

Report: `Documentation/Boss/BI_X31_X35_OFFLINE_TOOL_PORTABILITY_AUDIT.md`.

| ID | Task | Acceptance |
|---|---|---|
| BI-X31 | Audit queue validator parsing boundaries | Complete: hardcoded supported queue formats and limits documented |
| BI-X32 | Review evidence manifest portability behavior | Complete: path, symlink, encoding, hash, and resolution boundaries mapped |
| BI-X33 | Draft fixture matrix for platform-dependent path cases | Complete: synthetic Windows/POSIX cases specified; no fixture run |
| BI-X34 | Audit doc-link checker behavior for file URLs/anchors | Complete: limited syntax, all-scheme skip, and no anchor validation documented |
| BI-X35 | Batch report; add only bounded offline fixes if evidenced | Complete: no safe change made without focused verification; report records candidates |

## Batch 8 — Shipping and package evidence readiness (`BI-X36..X40`) — COMPLETE (static audit only)

Report: `Documentation/Boss/BI_X36_X40_SHIPPING_PACKAGE_READINESS.md`.

| ID | Task | Acceptance |
|---|---|---|
| BI-X36 | Reconcile Development reflection contracts with Shipping request | Complete: source guards contrasted with missing Shipping UHT/reflection proof |
| BI-X37 | Audit Shipping stage freshness and package identity checklist | Complete: current reread finds required launcher/manifests/stamp present; stamps/mtime are not identity proof |
| BI-X38 | Draft package intake artifact checklist | Complete: provenance, binary/manifests, map/route/config, reflection, scans and smoke bound to one package |
| BI-X39 | Reconcile current disabled defaults/guard scope | Complete: targeted shared defaults and Development override guards recorded; no edits |
| BI-X40 | Batch report and Lead action list | Complete: static audit only; no build or package run |

## Batch 9 — project status synchronization (`BI-X41..X45`) — COMPLETE (documentation/mailbox only)

Report: `Documentation/Boss/BI_X41_X45_STATUS_SYNC_AND_NEXT_QUEUE.md`; successor proposal: `Documentation/Boss/QUEUE_BJ.md`.

| ID | Task | Acceptance |
|---|---|---|
| BI-X41 | Compare TASKS and PROJECT_STATE active-queue statements | Complete: active BI status aligned; old next-batch phrases identified as historical |
| BI-X42 | Reconcile TEST_PLAN status for BF/BE open gates | Complete: historical Shipping-guard wording superseded; Lead proof remains open |
| BI-X43 | Update the batch's current status ledger | Complete: report paths and stage blocker linked |
| BI-X44 | Check Claude/Antigravity feedback and hotfix bounded rejects | Complete: no post-X-1905 verdict/reject; AG BI queue closed |
| BI-X45 | Draft next queue only from verified residual gaps | Complete: QUEUE_BJ.md, ten batches; offline evidence/doc scope |

## Batch 10 — closeout (`BI-X46..X50`) — COMPLETE

Closeout: `Documentation/Boss/BI_X46_X50_CLOSEOUT.md`.

| ID | Task | Acceptance |
|---|---|---|
| BI-X46 | Reconcile all BI batch reports and queue rows | Complete: 50 IDs reconciled across ten batches |
| BI-X47 | Summarize unmeasured performance work and target gate | Complete: target/proxy separation preserved; no new measurement |
| BI-X48 | Summarize Owner and Lead blockers | Complete: current owners and unresolved Shipping provenance recorded; prior launcher-absence claim corrected |
| BI-X49 | Reconcile documentation consistency | Complete: `python Scripts/Tools/check_doc_links.py`, exit 0, `broken_links=0`; no test suite |
| BI-X50 | Publish closeout and handoff | Complete: QUEUE_BJ and QUEUE_BJ_AG paths handed off |

## Global boundaries

No changes to owner-selected values, runtime defaults, authored assets, or active Lead evidence. Read-only audits can be completed independently; source/test edits require a bounded defect and focused offline verification. Never represent a proposal, source-ready state, proxy result, or missing record as live/package acceptance. Queue BI is closed; successor Codex queue: `Documentation/Boss/QUEUE_BJ.md`.
