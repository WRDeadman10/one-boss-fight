# Queue BF — Codex engineering follow-through

Successor to Queue BE. Work in five-task batches: inspect current Lead feedback, apply bounded hotfixes immediately, complete offline/source work, record exact evidence and continue without waiting for review. Lead owns UE editor/build/PIE, saved asset authoring, Shipping/UHT/package proof, and live acceptance. Preserve default-off routes and owner-approved values. Do not commit or push.

## Batch 1 — framework route acceptance support (BF-X01–X05) — SOURCE/TEST READY; Lead live acceptance pending

| ID | Task | Scope | Acceptance |
|---|---|---|---|
| BF-X01 | Reconcile live route questions against the BE framework checklist | TEST_PLAN, BE-X01–X20 reports | Exact Lead-owned proof rows; no implied pass |
| BF-X02 | Audit framework selection refusal telemetry for actionable reason codes | selection subsystem/tests | Source-backed table and bounded gaps |
| BF-X03 | Add deterministic native cases for generation replacement and stale callbacks | framework tests | Old generation cannot complete/rebind replacement |
| BF-X04 | Audit HUD/music unbind behavior across EndPlay and replacement | HUD/audio source/tests | Lifecycle matrix; only add pure deterministic coverage |
| BF-X05 | Prepare a concise selected-framework live acceptance sheet | report/TEST_PLAN | Exact route, actor, generation, outcome, retry and reset fields |

## Batch 2 — navigation and autonomous driver resilience (BF-X06–X10)

**COMPLETE — OFFLINE/SOURCE READY; live route acceptance remains Lead-owned.** Report: `Documentation/Boss/BF_X06_X10_NAVIGATION_DRIVER.md`; contract: `Scripts/Tools/test_bf_x06_x10_navigation_driver_contract.py` (6/6).

| ID | Task | Scope | Acceptance |
|---|---|---|---|
| BF-X06 | Audit autonomous driver termination on missing selector result | Sevarog driver/tests | Every exit has bounded cleanup and explicit status |
| BF-X07 | Add offline contract cases for card/time caps and cleanup paths | driver contract | Limit and cleanup boundaries covered |
| BF-X08 | Audit navigation summary identity against selected actor/generation | controller/driver | Source map and mismatch refusal coverage |
| BF-X09 | Check path-result diagnostics for stale or duplicate completion | navigation source/tests | Single terminal result per request; no per-frame logging |
| BF-X10 | Refresh the Lead navigation checklist from verified API/source | report/TEST_PLAN | Recast, projection, route and terminal position fields remain separate |

## Batch 3 — Shipping reflection and build evidence (BF-X11–X15)

**COMPLETE — DEVELOPMENT REFLECTION SOURCE READY; Lead Shipping/UHT/package proof remains open.** Report: `Documentation/Boss/BF_X11_X15_SHIPPING_REFLECTION.md`; reflection contract: `Scripts/Tools/test_bf_x11_x15_shipping_reflection_contract.py` (3/3); C-1155 build 0, pinned suite 509/509.

| ID | Task | Scope | Acceptance |
|---|---|---|---|
| BF-X11 | Re-scan named combat headers for unguarded test-only reflected functions | resolver/framework/dodge/parry headers | Exact declaration inventory |
| BF-X12 | Compare guarded declarations with definitions and native registration | named source/test files | Parity matrix; no Shipping claim |
| BF-X13 | Harden reflection contract against a deliberately unguarded fixture | offline contract | Fixture rejected and restored within temp directory |
| BF-X14 | Audit C-1155 runners for lock-owner-safe cleanup on failure | Scripts/Editor | Static failure-path map; no engine invocation |
| BF-X15 | Update Shipping/UHT checklist with exact Lead artifact paths | TEST_PLAN/report | UHT, build target, hash and reflection result fields |

## Batch 4 — move-card validation boundaries (BF-X16–X20)

**COMPLETE — source/preflight/native coverage ready.** Focused preflight 3/3; C-1155 Development build 0; DD27j-pinned suite 509/509. No assets. Lead live asset/PIE acceptance remains separate.

| ID | Task | Scope | Acceptance |
|---|---|---|---|
| BF-X16 | Enumerate every MoveCard numeric validator field and boundary | card/profile rules/tests | Source-to-test coverage matrix |
| BF-X17 | Add finite-value checks for any uncovered authored field | rules/native tests | NaN/Infinity rejected; defaults unchanged |
| BF-X18 | Audit optional AreaEffect and ChannelDrain copied-data semantics | card model/executor | Disabled default and immutable snapshot preserved |
| BF-X19 | Add regressions for malformed phase/additional-phase combinations | card/profile tests | Invalid/mixed phase inputs fail closed |
| BF-X20 | Reconcile card validation contract with authoring dry-run output | author script/report | Exact authored IDs and refusal reasons; no saves |

## Batch 5 — status effects and owned cleanup (BF-X21–X25)

**COMPLETE — read-only source/test audit.** No bounded pure retry-rule gap found; live-actor reuse risk is recorded for focused follow-up. No build/PIE/runtime claim.

| ID | Task | Scope | Acceptance |
|---|---|---|---|
| BF-X21 | Map outgoing and incoming damage rejection precedence | resolver/health adapter | File:line policy table |
| BF-X22 | Audit hit identity and duplicate suppression for multi-target results | resolver/executor/tests | Distinct target/hit-group cases identified |
| BF-X23 | Audit retry timers for cancellation and owner destruction | cleanup helpers/callers | Weak lifetime and teardown matrix |
| BF-X24 | Check live-actor encounter reuse against cleanup ownership | encounter lifecycle | Explicitly document if no generation identity is available |
| BF-X25 | Add pure-rule coverage for any bounded retry-state gap | cleanup tests | Normal schedule preserved; invalid inputs safe |

## Batch 6 — Sevarog card evidence and counterplay (BF-X26–X30)

**COMPLETE — static/source and mailbox-metadata audit.** Saved-asset and live S1–S8 acceptance remain Lead-owned; no raw outputs were opened and no runtime result is claimed. Report: Documentation/Boss/BF_X26_X30_SEVAROG_CARD_AND_LIVE_EVIDENCE_AUDIT.md. Continuing BF-X31–X35.

| ID | Task | Scope | Acceptance |
|---|---|---|---|
| BF-X26 | Reconcile accepted S1/S2 ranges with current dry-run manifest | authoring source/report | Only approved rows and values; no asset edits |
| BF-X27 | Audit S6–S8 phase pools and effect damage budgets | card/profile rules | Source/test crosswalk; no value changes |
| BF-X28 | Review ChannelDrain counterplay exemption reasons | profile validator/tests | Narrow cone/fixed facing accepted; full-cone tracking remains rejected |
| BF-X29 | Inventory Lead live card evidence by path/run/build/hash/status | mailbox/TEST_PLAN metadata | Do not open raw outputs or infer unseen results |
| BF-X30 | Refresh S1–S8 live acceptance questions | checklist/TEST_PLAN | Reach, contact, phase, effect and recovery rows separated |

## Batch 7 — Greystone authoring and motion gates (BF-X31–X35)

**COMPLETE — static source/docs audit.** Wrapper identity/refusal, owned cleanup limits, configured root-motion repair, paired capture fields, and open package/default-player gates are recorded. No test or engine operation. Report: Documentation/Boss/BF_X31_X35_GREYSTONE_AUTHORING_AND_MOTION_GATES.md. Continuing BF-X36–X40.

| ID | Task | Scope | Acceptance |
|---|---|---|---|
| BF-X31 | Audit Greystone wrapper readback refusal and package identity | author/readback scripts | Exact source/target identity; no saves |
| BF-X32 | Check cleanup paths remove only assets created by the current run | author scripts/contracts | Existing/reference assets are never deleted |
| BF-X33 | Reconcile C-1285 root-motion diagnosis with approved source flags | decision/checklist/source | Root cause wording and evidence limits match Lead record |
| BF-X34 | Prepare paired mannequin/Greystone live capture schema | TEST_PLAN/report | Same montage, transform, root displacement and result fields |
| BF-X35 | Audit package/default-player gates after authored wrappers | docs/config inventory | Mannequin default stays explicit until owner gate closes |

## Batch 8 — offline tooling and evidence integrity (BF-X36–X40)

**COMPLETE — queue/evidence tooling audit.** Queue malformed-row fixtures 4/4; evidence-manifest suite 4 passed / 1 symlink fixture skipped because Windows denied symlink creation; doc links 0 broken. Current runner receipts have explicit provenance gaps. Report: Documentation/Boss/BF_X36_X40_QUEUE_AND_EVIDENCE_TOOLING_AUDIT.md. Continuing BF-X41–X45.

| ID | Task | Scope | Acceptance |
|---|---|---|---|
| BF-X36 | Audit queue validator coverage for duplicate IDs and batch counts | queue validator/tests | Ten groups of five required |
| BF-X37 | Add a malformed Markdown-table fixture to queue validation | validator/offline tests | Invalid row is rejected without modifying source |
| BF-X38 | Audit evidence manifest path containment and symlink handling | manifest reader/tests | Traversal and identity cases fail closed |
| BF-X39 | Compare run receipts for required build/hash/lock fields | receipt validator/docs | Missing required provenance is reported precisely |
| BF-X40 | Inventory documentation links for BE and BF reports | doc link tool/reports | Broken-link list or zero count |

## Batch 9 — performance and owner gates (BF-X41–X45)

**COMPLETE — read-only performance/source/owner-gate audit and successor queue drafted.** Report: `Documentation/Boss/BF_X41_X45_PERFORMANCE_AND_OWNER_GATES.md`; successor: `Documentation/Boss/QUEUE_BI.md`. No tests, engine, benchmark or profiler operation.

| ID | Task | Scope | Acceptance |
|---|---|---|---|
| BF-X41 | Inventory unmeasured combat-path allocation/string candidates | source/performance report | Candidate list only; no cost claim |
| BF-X42 | Audit existing 2060 Super performance receipt schema | PERFORMANCE_LOG/TEST_PLAN | p99, frame time, build/map/device and warm-up fields present |
| BF-X43 | Map optional Niagara bounds and sprite budgets to authored defaults | config/docs | No runtime performance inference |
| BF-X44 | Reconcile pending owner A/B/C picks and content authoring gates | mailbox/decision docs | Exact decision owner and blocked downstream work |
| BF-X45 | Draft the next queue from only verified residual gaps | QUEUE_BG.md | Fifty scoped tasks in ten groups of five |

## Batch 10 — closeout and handoff (BF-X46–X50)

**COMPLETE — source/live and owner gates reconciled without upgrading provisional evidence.** Report: `Documentation/Boss/BF_X46_X50_CLOSEOUT.md`. Queue BF closed (50/50); next Codex lane: `Documentation/Boss/QUEUE_BI.md`.

| ID | Task | Scope | Acceptance |
|---|---|---|---|
| BF-X46 | Reconcile framework source readiness against Lead live verdicts | report/TEST_PLAN | Source and live status distinct |
| BF-X47 | Reconcile S1–S8 authoring and combat evidence | report/KNOWN_ISSUES | No provisional row described as accepted |
| BF-X48 | Reconcile Greystone wrappers, root motion and default route | report/DECISIONS | Owner/Lead gates remain visible |
| BF-X49 | Reconcile Shipping, package and performance open gates | TEST_PLAN/TASKS | Exact evidence owner and build target |
| BF-X50 | Publish final queue receipt with batch dispositions | TASKS/PROJECT_STATE | Ten-batch status, evidence paths, no commit/push |

## Global gates

Use the task-specific C-1155 locked runner for authorized engine work; do not overlap Lead engine use. Default route and owner-approved values remain unchanged. Source tests, Development builds, live PIE, saved assets, Shipping/UHT, package and performance evidence are separate claims. Owner commits; no commit or push.
