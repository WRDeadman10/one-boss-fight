# Queue AC — Codex lane (50 tasks)

Proposed next lane after Queue AB. Ten batches of five. Work is static, documentation, or offline-tool/test work and can proceed without owner decisions. Do not assign optional assets or change gameplay defaults. Lead owns Unreal, Editor, build, CookCoverage, and PIE acceptance; label those gates pending and continue with independent tasks. Post one X completion message per batch; hotfixes first; do not wait for review. No commits/pushes.

## Batch 1 — ER asset acceptance and range evidence

| ID | Task | Acceptance |
|---|---|---|
| AC-C01 | Audit GATE-07 status-cell grammar against importer parser | enumerate accepted/pending/rejected forms; fixture recommendations |
| AC-C02 | Reconcile all ER AnimSequence and AnimMontage lengths against GATE-07 | source-backed table; compare A-590 readbacks with C-979 accepted ranges; owner approval remains distinct |
| AC-C03 | Review montage-segment helper input/range semantics and native test coverage | editor-only API contract; no asset mutation |
| AC-C04 | Audit optional ER montage fields and saved-default assertions | all four fields, routes, and null-default tests mapped |
| AC-C05 | Refresh owner hand-test gate checklist | exact clip-review, assignment, build, and PIE prerequisites |

## Batch 2 — player attack lifecycle

| ID | Task | Acceptance |
|---|---|---|
| AC-C06 | Trace active attack montage interruptions on player death | Source ownership map; distinguish pawn destruction from surviving pawn |
| AC-C07 | Trace attack montage state across encounter reset and rebind | subscription/callback inventory; no inferred cancellation |
| AC-C08 | Audit temporary air/counter ability-array backup lifetime | cleanup paths and weak-object failure cases |
| AC-C09 | Map player attack lifecycle test gaps to native tests and PIE probes | named tests/probes and unproved claims |
| AC-C10 | Specify minimal Lead death/reset observation matrix | fields/logs to retain; no gameplay change proposal without repro |

## Batch 3 — guard and parry evidence

| ID | Task | Acceptance |
|---|---|---|
| AC-C11 | Reconcile owner-confirmed guard behavior with invalid block probes | corrected setup/precondition table |
| AC-C12 | Audit guard contact event to one-shot counter-window flow | Source call path, consume behavior, test mapping |
| AC-C13 | Review parry and guard terminology in all player QA documents | exact phrase inventory and edits |
| AC-C14 | Audit counter fallback behavior with empty/unloadable montage | source/test contract; no asset assignment |
| AC-C15 | Draft a Lead guard-counter PIE receipt checklist | route, health/stamina, contact, montage, damage, logs |

## Batch 4 — import and animation tooling

| ID | Task | Acceptance |
|---|---|---|
| AC-C16 | Audit importer no-overwrite and preflight order | all filesystem/content operations ordered after validation |
| AC-C17 | Add negative fixture cases for malformed GATE-07 rows | duplicate IDs, malformed pipes, missing status, status prefix |
| AC-C18 | Audit montage trim scripts for lock, no-overwrite, and readback safeguards | exact guard list; no Editor run |
| AC-C19 | Reconcile accepted frame ranges in metadata, scripts, and handoff docs | mismatch report with source locations |
| AC-C20 | Document asset type and cook proof boundaries | AnimSequence vs AnimMontage distinction, no package claims without receipt |

## Batch 5 — optional Tier 2 feature readiness

| ID | Task | Acceptance |
|---|---|---|
| AC-C21 | Audit Tier 2 Development CVar scope and defaults | declaration/use map; Shipping path distinction |
| AC-C22 | Review parry distortion material lifecycle and late-enable semantics | update KI-191 with verified status only |
| AC-C23 | Audit phase aura cleanup on reset/death/world teardown | Source ownership matrix and test gaps |
| AC-C24 | Audit boss parry recoil optional montage path | null fallback, slot, and package references |
| AC-C25 | Refresh Tier 2 owner/Lead acceptance sheet | separate owner selection, delivery, assignment, runtime proof |

## Batch 6 — DLSS and performance gates

| ID | Task | Acceptance |
|---|---|---|
| AC-C26 | Reconcile Round 6 Phase 2 parked status across decisions and intake | one status, no inferred return data |
| AC-C27 | Audit player DLSS setting config keys and default/fallback claims | source/config/test matrix; do not select a shipped default |
| AC-C28 | Review C-971 0.36 s route-boundary evidence | raw receipt and code path citation; no threshold change |
| AC-C29 | Audit performance claims in owner-facing summaries | identify measured vs predicted vs absent figures |
| AC-C30 | Refresh the DLSS default decision gate sheet | Phase 2 intake and image-quality approval conditions |

## Batch 7 — offline test infrastructure

| ID | Task | Acceptance |
|---|---|---|
| AC-C31 | Audit the 20 s offline-suite budget wrapper | default, CLI override, failure exit semantics |
| AC-C32 | Add simulated timeout and nonzero-exit tests to the wrapper | deterministic fixture; no full suite dependency |
| AC-C33 | Review KI-195 unbounded subprocess calls | exact callsites and safe timeout proposals |
| AC-C34 | Add bounded timeout/cleanup coverage to one selected offline test group | only if source-safe; focused regression cases |
| AC-C35 | Refresh focused-player test discovery inventory | deterministic counts from test source, no imports |

## Batch 8 — project documentation consistency

| ID | Task | Acceptance |
|---|---|---|
| AC-C36 | Reconcile ER controls spec and runtime Source after new receipts | no stale field, route, or acceptance claim |
| AC-C37 | Reconcile GATE-07 with the latest animation mailbox evidence | owner review distinct from delivery acceptance |
| AC-C38 | Audit TEST_PLAN BUILD/PIE receipts for count/date drift | receipts remain individually scoped |
| AC-C39 | Refresh KNOWN_ISSUES ER/Tier 2 dispositions | current blockers and close criteria |
| AC-C40 | Refresh DECISIONS index with new mailbox IDs | complete, concise, and linked to source messages |

## Batch 9 — milestone and release handoff

| ID | Task | Acceptance |
|---|---|---|
| AC-C41 | Refresh milestone gate matrix after C-979 | owner/Lead/AG, evidence, status, next action |
| AC-C42 | Reconcile build, offline-suite, and PIE counts | every number tied to a dated receipt |
| AC-C43 | Audit active release gates and known issue dependencies | no closure inferred from missing data |
| AC-C44 | Prepare a one-page engineering status report for the owner | plain language, evidence and limits |
| AC-C45 | Draft Queue AD (Codex, 50 tasks) | 50 unique ordered IDs in ten batches |

## Batch 10 — independent consistency and closeout

| ID | Task | Acceptance |
|---|---|---|
| AC-C46 | Cross-check AC reports against Source, tests, configs, and mailbox | contradiction list resolved or explicitly gated |
| AC-C47 | Audit absolute paths and machine-specific assumptions in new reports | exact hits; retain intentional reference paths |
| AC-C48 | Re-review Lead/Antigravity receipts added during Queue AC | evidence-backed defects only |
| AC-C49 | Prepare a compact next-lane handoff | current state, pending gates, paths, verification limits |
| AC-C50 | Close Queue AC and begin Queue AD batch 1 | one batch completion post; continue without waiting |

