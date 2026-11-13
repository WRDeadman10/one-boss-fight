# Queue BE — Codex five-task batches

Successor to Queue BD, scoped to verified open source, documentation, and offline-tool work. Keep every finding tied to source or a cited report; metadata references do not replace evidence. Do not edit pack or content assets, choose owner gameplay values, perform Lead acceptance, or run the engine. If a task needs unavailable runtime/asset/owner input, record the exact blocker and continue within the batch.

## Batch 1 — framework health and encounter lifecycle

| ID | Task | Files | Acceptance |
|---|---|---|---|
| BE-X01 | Trace framework native health mutation and death transition | `RPGFrameworkBossCharacter.*`, `RPGFrameworkMoveExecutor.*` | Function/call graph with file:line; distinguish framework from pack health |
| BE-X02 | Map pack HUD creation/read assumptions against framework boss | `UI/RPGBossHud.*`, framework boss sources | Existing/missing binding matrix; no integration claim |
| BE-X03 | Trace encounter completion, music, victory and retry notification ownership | encounter/player/game-state sources | State/event ownership table and exact absent edges |
| BE-X04 | Audit generation/reset guards across proof and production routes | framework boss, encounter subsystem, related tests | Compare route state machines and existing tests; no runtime claim |
| BE-X05 | Draft the minimum Lead acceptance matrix for framework integration | `NEW_BOSS_CHECKLIST.md`, report | Observable outcomes, fixture, cleanup and route identity; no implementation |

## Batch 2 — Sevarog range and combo evidence contracts

| ID | Task | Files | Acceptance |
|---|---|---|---|
| BE-X06 | Reconcile latest Sevarog card metadata with source authoring tables | Sevarog authoring script, `TEST_PLAN.md`, C-1265/C-1266 references | Row-to-source map; preserve reported-vs-verified labels |
| BE-X07 | Audit trace driver component discovery and failure exits | `pie_sevarog_clip_frames.py`, `run_c1265b_clip_trace.ps1` | Static failure-path matrix and safe no-save contract |
| BE-X08 | Review full-clip trace sampling versus active-window sampling | trace driver, C-1269 metadata only | Identify observable/schema limitations; do not open raw output |
| BE-X09 | Map selector combo continuation and per-card/lifetime accounting | `RPGFrameworkMoveExecutor.*`, Sevarog card/profile sources | Source-backed counter and transition table |
| BE-X10 | Refresh Sevarog live gates after C-1266/C-1269 | `KNOWN_ISSUES.md`, `TEST_PLAN.md`, report | Keep approach, S1/S2, S5 chain and route scopes distinct |

## Batch 3 — Greystone wrapper and readback safety

| ID | Task | Files | Acceptance |
|---|---|---|---|
| BE-X11 | Audit montage wrapper metadata copied from source | `RPGMontageWrapperLibrary.*`, tests | Field-by-field copy/validation table, including notify timing |
| BE-X12 | Review wrapper path and skeleton refusal contracts | wrapper source/tests | Enumerate tested and untested rejection cases |
| BE-X13 | Audit script save/reload/readback and created-only rollback | `author_greystone_player.py`, wrapper verifier | Static control/data-flow; no execution or asset load |
| BE-X14 | Reconcile approved quick-roll route with driver inputs | `SWITCH_PLAN.md`, Greystone drivers | One-tap/directional mapping and explicit prohibited full-roll route |
| BE-X15 | Map remaining child-BP and package-proof dependencies | Greystone docs, CookCoverage config | File/path inventory; no content or package claim |

## Batch 4 — status and tag cleanup resilience

| ID | Task | Files | Acceptance |
|---|---|---|---|
| BE-X16 | Trace owned invulnerability-tag add/remove/retry lifecycle | `RPGIFrameMonitor.*`, cleanup helpers | Ownership and retry state table |
| BE-X17 | Trace owned parry-tag cleanup and EndPlay behavior | `RPGPlayerParry.*`, cleanup helpers | State/call-site matrix; separate retry from confirmed success |
| BE-X18 | Audit deferred cleanup identity and stale-owner handling | cleanup helpers and tests | Identify stale generation/weak-owner boundaries |
| BE-X19 | Inventory native tests for reset, retry, and EndPlay paths | relevant `Source/.../Tests` | Exact test-name-to-path matrix; don't run native suite |
| BE-X20 | Add a bounded pure policy regression only if a source gap is isolated | rules/tests; report | Test fails before/fixes after; no Unreal dependency or runtime assertion |

## Batch 5 — validator and receipt contracts

| ID | Task | Files | Acceptance |
|---|---|---|---|
| BE-X21 | Audit A5 receipt schema/type validation and error reporting | A5 validator/tests | Malformed shape matrix; fixture-only tests if authorized by gap |
| BE-X22 | Check manifest canonical-path and duplicate identity behavior | evidence manifest tools/tests | Path/identity table; source logs untouched |
| BE-X23 | Audit Markdown link scanner supported forms and blind spots | checker/tests | Positive/negative syntax table with bounded fixtures if needed |
| BE-X24 | Review task-queue parser for duplicate IDs, ordering and acceptance text | queue checker/tests | Contract matrix and reproducible fixture findings |
| BE-X25 | Refresh safe offline versus engine command index | `OFFLINE_VALIDATOR_COMMANDS.md` | Every command labeled, no generic engine command presented as authorized |

## Batch 6 — reflected test surface and shipping boundaries

| ID | Task | Files | Acceptance |
|---|---|---|---|
| BE-X26 | Inventory test-facing reflected functions in selected combat classes | resolver/framework/parry headers | Header-level declaration map |
| BE-X27 | Compare Development guards and Shipping implementation stubs | matching headers/CPP | Exact compile/body table; no stripping claim |
| BE-X28 | Check Editor module isolation for montage wrapper test APIs | `OneBossFightEditor` build/source files | Module boundary matrix; no UHT/build |
| BE-X29 | Compare test registration names with source test inventory | native test files | Exact names/case; no engine test execution |
| BE-X30 | Update Lead UHT/Shipping proof checklist for known open declarations | `TEST_PLAN.md`, checklist | Binary/symbol/map evidence fields, owner clearly identified |

## Batch 7 — performance evidence and observability

| ID | Task | Files | Acceptance |
|---|---|---|---|
| BE-X31 | Reconcile final target and proxy wording across release docs | `DECISIONS.md`, `PERFORMANCE_LOG.md`, `TEST_PLAN.md` | 1080p/60 FPS/p99 and RTX 2060 Super consistent; no new metric |
| BE-X32 | Audit current performance receipt required identity fields | performance tools/reports | Build/package/hardware/config/sample identity matrix |
| BE-X33 | Map live driver terminal counters to failure reasons | C-1262a driver/receipt source | Counter-to-outcome table; no raw evidence |
| BE-X34 | Inventory combat telemetry allocation candidates without cost claims | resolver/executor source | Source locations only; no benchmark |
| BE-X35 | Reconcile parked Phase 2 and latest Phase 1 proxy status | performance docs and mailbox references | Keep parked/not-run, proxy/final, and measured/target distinct |

## Batch 8 — project documentation and milestone coherence

| ID | Task | Files | Acceptance |
|---|---|---|---|
| BE-X36 | Reconcile queue completion lines against reports | `TASKS.md`, batch reports | Exact report/status map; no unsupported completion |
| BE-X37 | Check TEST_PLAN suite ownership and hash references | `TEST_PLAN.md`, runner source | Latest Lead and Codex receipts distinct; source-pinned hash |
| BE-X38 | Review PROJECT_STATE current milestone/open-gate summary | `PROJECT_STATE.md` | Cite current supporting rows and flag stale claims |
| BE-X39 | Reconcile KNOWN_ISSUES resolved/open scope with current receipts | `KNOWN_ISSUES.md`, `TEST_PLAN.md` | No closure beyond verified scope |
| BE-X40 | Check build/Editor instructions against C-1155 | onboarding/runbook docs | Static command audit; no engine/locks |

## Batch 9 — review and incoming evidence intake

| ID | Task | Files | Acceptance |
|---|---|---|---|
| BE-X41 | Inspect Claude feedback on BE-X01–X40 | mailbox history | Record accepted/reworked/rejected items |
| BE-X42 | Hotfix bounded review rejects before other work | reviewed files | Focused patch and scoped verification; continue if none |
| BE-X43 | Inventory new Lead evidence references without opening raw outputs | mailbox, `TEST_PLAN.md` | Path/status/hash/route metadata only |
| BE-X44 | Sync accepted BE status into task and milestone docs | `TASKS.md`, `TEST_PLAN.md`, `PROJECT_STATE.md` | Matching status and open gates |
| BE-X45 | Build next queue from verified open work | new `QUEUE_BF.md` | Ten batches of five, scoped files and acceptance |

## Batch 10 — closeout and handoff

| ID | Task | Files | Acceptance |
|---|---|---|---|
| BE-X46 | Audit new report and queue links | BE artifacts, link checker | Missing-reference list or zero result |
| BE-X47 | Summarize framework health/HUD/death decisions still open | framework reports, checklist | Lead/owner choices separated from Codex tasks |
| BE-X48 | Summarize Sevarog and Greystone evidence gates | Sevarog/Greystone reports | Source, live, saved asset and package claims distinct |
| BE-X49 | Reconcile accepted facts, defects, risks and hypotheses | BE reports, issue docs | Every item sourced and scoped |
| BE-X50 | Publish final BE handoff | `TASKS.md`, `TEST_PLAN.md`, `PROJECT_STATE.md` | Queue status synced; no commit or push |

## Standing limits

- Lead owns acceptance builds, full PIE, asset-authoring runs, UHT/Shipping proof, cook and package acceptance unless a newer explicit mailbox order assigns a scoped self-test.
- Any authorized engine use follows C-1155 with the task-specific runner, both locks, no existing UnrealEditor process, owner-token-safe cleanup and pinned DD27j hash for suites.
- Do not inspect raw Lead evidence unless specifically assigned. Preserve pack assets and all uncommitted work. The owner commits; no commit or push.
