# Queue Z — proposed Codex follow-on lane

Draft: 2026-11-06. Ten batches of five, intended to start after Y046–Y050 and Lead review. Follow the standing cadence: inspect the mailbox each cycle; execute one batch; post a single batch receipt; continue to the next unblocked batch without waiting; address rejected items as hotfixes on the next cycle. Claude owns all Unreal Editor, PIE, build, package, and live-performance execution. This queue proposes read-only source/evidence audits and documentation; it authorizes no asset, default, or owner-gated change.

Acceptance for each audit task: a concise report with exact source/evidence paths and hashes where artifacts are involved; separate measured, source-configured, historical, proposed, and unknown claims; state limits; no unsupported runtime inference. Existing closed reports should be extended only when a substantive correction is found.

## Batch 1 — boss rule and phase authority

Status (2026-11-06): Z001–Z005 complete locally; see `Z001_Z004_BOSS_RULE_LIFECYCLE_AUDIT.md`. Static source/test inventory only; no tests were executed. Continuing to Batch 2 without waiting for review.

| ID | Task | Target / acceptance |
|---|---|---|
| Z001 | Trace boss phase transition authority | `RPGBossCombatComponent` phase source and tests; diagram the one-way latch/reset paths and list untested branches. |
| Z002 | Audit boss death/respawn health ownership | health application and reset code; separate initial spawn, death, and reset semantics with citations. |
| Z003 | Cross-check posture break thresholds | posture rules, data defaults and unit tests; table each threshold/reset action and any mismatched documentation. |
| Z004 | Review boss attack cancellation lifecycle | executor/tracker source and tests; enumerate cancel, death, stagger and teardown cleanup obligations. |
| Z005 | Batch receipt | index Z001–Z004 findings, unknowns, and continuation; make no gameplay change. |

## Batch 2 — player action and input lifecycle

Status (2026-11-06): Z006–Z010 complete locally; see `Z006_Z009_PLAYER_ACTION_LIFECYCLE_AUDIT.md`. Retained D5 PIE evidence is historical; key mappings and live/package outcomes remain limited as stated. Continuing to Batch 3 without waiting for review.

| ID | Task | Target / acceptance |
|---|---|---|
| Z006 | Map shared input bindings to action outcomes | input config, Enhanced Input setup, current dodge audit; table every shared key/action and evidence class. |
| Z007 | Reconcile dodge montage/i-frame windows | dodge source, authored montage data and retained PIE receipts; distinguish configured windows from measured contact behavior. |
| Z008 | Trace parry-to-riposte eligibility | parry, hit-intake and riposte source/tests; sequence acceptance gates and identify missing negative cases. |
| Z009 | Audit stamina payment and regeneration ordering | swing tracker/rules and stamina driver; report cost/fallback/regeneration invariants and real-loadout gaps. |
| Z010 | Batch receipt | link all player-action findings and any owner/Lead dependency; do not tune values. |

## Batch 3 — target validity and boss decision context

Status (2026-11-06): Z011–Z015 complete locally; see `Z011_Z014_TARGET_SELECTOR_RANGE_AUDIT.md`. Framework proof-lane rules are kept separate from legacy pack AI; retained R2 evidence supports calibrated cards only. Continuing to Batch 4 without waiting for review.

| ID | Task | Target / acceptance |
|---|---|---|
| Z011 | Review target invalidation paths | awareness/target selection source and proofs; cover dead, destroyed, off-arena and missing targets. |
| Z012 | Audit weighted action selection filters | selector rules/tests; map range, phase, cooldown and availability filters with boundary coverage. |
| Z013 | Reconcile authored attack ranges to reach evidence | attack tables, calibrated card evidence and current design docs; mark old vs calibrated cards distinctly. |
| Z014 | Trace no-valid-action recovery | selector/executor fallback and tests; document retry/yield/fail states and untested combinations. |
| Z015 | Batch receipt | summarize Z011–Z014 and preserve all runtime unknowns. |

## Batch 4 — encounter registration and reset

Status (2026-11-06): Z016–Z020 complete locally; see `Z016_Z019_ENCOUNTER_RESET_CLEANUP_AUDIT.md`. C915 selected and legacy bundles each retain 20/20 reset cycles; teardown and Blueprint/package boundaries remain limited as stated. Continuing to Batch 5 without waiting for review.

| ID | Task | Target / acceptance |
|---|---|---|
| Z016 | Trace encounter world registration | activation/registration source and tests; state required ordering and rollback points. |
| Z017 | Audit player possession/rebind epochs | reset/rebind source and C915 receipts; distinguish single-cycle proof from repeated-respawn evidence. |
| Z018 | Review scope cleanup on EndPlay | typed feedback, time dilation, tag, sound mix and aura lifecycle; provide a push/pop/restore table backed by code/tests. |
| Z019 | Cross-check encounter state persistence boundary | SaveGame/config/source inventory and G4 report; list exactly what persists and what is intentionally runtime-only. |
| Z020 | Batch receipt | deliver a concise lifecycle diagram and unresolved Lead-run proof list. |

## Batch 5 — combat readability and player information

Status (2026-11-06): Z021–Z025 complete locally; see `Z021_Z024_TELEGRAPH_HUD_CAMERA_ACCESSIBILITY_AUDIT.md`. Source timing, tick-driven HUD authority, camera safeguards, historical CAM/HUD evidence and accessibility boundaries are classified separately. Continuing to Batch 6 without waiting for review.

| ID | Task | Target / acceptance |
|---|---|---|
| Z021 | Build source-to-telegraph inventory | boss attack data, animation notifies, presentation hooks; classify visible cues by move and evidence type. |
| Z022 | Cross-check HUD state against combat authority | health/posture/stamina UI source and tests; map values, update events and stale-state risks. |
| Z023 | Audit camera collision and arena framing | camera settings/source, arena constraints and retained evidence; separate authored values from measured readability. |
| Z024 | Review accessibility/input feedback claims | control hints, color/contrast/scaling settings and UI source; flag unsupported usability claims and missing evidence. |
| Z025 | Batch receipt | link inventory and list unmeasured visual/accessibility claims without proposing look changes. |

## Batch 6 — content authoring and reference integrity

Status (2026-11-06): Z026–Z030 complete locally; see `Z026_Z029_CONTENT_SAFETY_REFERENCE_AUDIT.md`. Reconciled existing static writer heuristics, synchronous soft-load sites, cooked vendor mounts and conflicting dated reference-census counts. No asset operation was run. Continuing to Batch 7 without waiting for review.

| ID | Task | Target / acceptance |
|---|---|---|
| Z026 | Review content-writer execution gates | `Scripts/Editor` writers and safety inventory; classify dry-run, existence, assertion and save guards with exact paths. |
| Z027 | Audit soft-reference load timing risks | Source/Blueprint properties and prior runtime evidence; list synchronous first-use loads and unknown hitch measurements. |
| Z028 | Review Content naming and mount boundaries | Content tree, config roots and pack integration docs; list concrete outliers and preserve third-party ownership. |
| Z029 | Reconcile redirector/reference integrity claims | retained Editor census and source docs; distinguish project, third-party and historical scans by date/scope. |
| Z030 | Batch receipt | provide a no-write content safety summary; do not launch Editor or run asset writers. |

## Batch 7 — performance evidence and telemetry contracts

Status (2026-11-06): Z031–Z035 complete locally; see `Z031_Z034_BENCHMARK_TELEMETRY_CONTRACT_AUDIT.md`. Corrected stale PERF-01 120 FPS acceptance to the binding 60 FPS / 16.67 ms target; R4/R5 remain historical misses and R6 identity/run evidence is absent. Continuing to Batch 8 without waiting for review.

| ID | Task | Target / acceptance |
|---|---|---|
| Z031 | Review benchmark sample/discard semantics | benchmark collector and summarizer; specify sample inclusion, warm-up removal, percentile convention and units. |
| Z032 | Reconcile performance thresholds to decisions | DECISIONS, gate checklist and runbooks; list target hardware/resolution/FPS/p99 rules and cite every active threshold. |
| Z033 | Audit graphics mode witness collection | DLSS/TSR configuration and log parser; enumerate expected active-mode tokens and false-positive paths. |
| Z034 | Review R6 kit schema/provenance contract | BUILD_INFO, manifests, kit guide and identity report; specify minimum source/package/executable/manifest/log binding. |
| Z035 | Batch receipt | state precisely which telemetry can and cannot certify target performance. |

## Batch 8 — automation and comparator correctness

Status (2026-11-06): Z036–Z040 complete locally; see `Z036_Z039_COMPARATOR_REQUIREMENTS_SHIPPING_AUDIT.md`. Matrix matching remains 5/82 exact registration/source pairs; G044 numeric source-token and parity health false-passes remain; two identical staged Shipping executables pass the scanner's three-token check, with package-wide coverage/provenance still open. No tests or Unreal/build/package operation. Continuing to Batch 9 without waiting for review.

Status (2026-11-06): Z036–Z040 complete locally; see `Z036_Z039_COMPARATOR_REQUIREMENTS_SHIPPING_AUDIT.md`. Matrix matching remains 5/82 exact registration/source pairs; G044 numeric source-token and parity health false-passes remain; two identical staged Shipping executables pass the scanner's three-token check, with package-wide coverage/provenance still open. No tests or Unreal/build/package operation. Continuing to Batch 9 without waiting for review.

| ID | Task | Target / acceptance |
|---|---|---|
| Z036 | Reconcile requirements matrix mapping after owner review | CSV, registration scanner and matrix validator; report fixed mappings, intentionally grouped suites and remaining UNKNOWN rows. |
| Z037 | Re-review G044 comparator after source-token fix | tool/tests and current D5 manifest; confirm the synthetic 2000/1800 counterexample is rejected if the owning lane changed it. |
| Z038 | Re-review parity health metric after structured-observable work | schema/comparator/tests; check equal-timing/unequal-health fixture and preserve route identity controls. |
| Z039 | Audit Shipping symbol-scan coverage | symbol checker/tests and compiled artifacts supplied by Lead; enumerate scan scope, encodings and unverified binaries. |
| Z040 | Batch receipt | distinguish static/tool regression evidence from actual Shipping or runtime acceptance. |

## Batch 9 — evidence and documentation quality

Status (2026-11-06): Z041–Z045 complete locally; see `Z041_Z044_OWNER_CITATION_STATUS_ARCHIVE_AUDIT.md`. Corrected three stale evidence-index line anchors, updated the owner handover to C-936, and recorded current ledger/message mismatch plus index-coverage limits. C-936 directs Codex to finish this in-progress batch and stop; Batch 10 is not started.

| ID | Task | Target / acceptance |
|---|---|---|
| Z041 | Audit owner-facing numbers in release docs | current owner handover, P15, briefs and risk register; source or label each number as proposal/unknown. |
| Z042 | Cross-check evidence citation anchors | current reports/receipts and citation tools; verify cited file/line identity without promoting evidence class. |
| Z043 | Reconcile date/status snapshots | TASKS, PROJECT_STATE, TEST_PLAN, known issues, decisions and mailbox; label historical states and list current conflicts. |
| Z044 | Review evidence archive index coverage | `Docs/BossCombatReview/Execution` index/readmes; identify unindexed high-value receipts without moving files. |
| Z045 | Batch receipt | provide a navigation index and unresolved citation/date issues; no archive migration. |

## Batch 10 — release evidence and next-lane closeout

Disposition (2026-11-06): Not started under C-936, which directs Codex to stop after completing the already active Z041–Z045 batch. Do not continue this draft queue unless Claude or the owner authorizes new work.

| ID | Task | Target / acceptance |
|---|---|---|
| Z046 | Reconcile release checklist with current gate receipts | A7/R6/test plan; status every requirement only to evidence actually supplied. |
| Z047 | Audit source-to-binary provenance on the next Lead package | source revision, build record, launcher/inner binary, manifest and run outputs; report exact chain breaks. |
| Z048 | Review unclosed technical risks after W/Y verdicts | residual risk register and mailbox; convert accepted/rejected findings into evidence-backed current states. |
| Z049 | Refresh owner handover with exact next actions | decision/evidence owner, artifact path and closure criterion for every open gate. |
| Z050 | Batch receipt and next-lane proposal | close Z progress, list accepted/reworked items, and draft another ten five-task lane only if useful. |

This is a draft for Lead review. Owner decisions, cleanup, visual changes, production defaults, Editor/PIE/build/package runs, and live measurements remain with their designated owner/Lead process.
