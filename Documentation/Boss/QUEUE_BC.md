# Queue BC: Codex lane (owner order 2026-11-10)

Queue BC follows Queue BB's five-task cadence: complete an offline-capable batch, record evidence, post one `X-` message, read Claude's last verdict at the next cycle, hotfix rejected items, and continue without waiting. Lead owns engine builds, PIE, authored-asset readback, Shipping builds, and profiler captures. Never write pack assets or commit/push.

## Batch 1 — source/test contracts (BC-X01–X05)

| ID | Task | Acceptance |
|---|---|---|
| BC-X01 | Sweep every AreaEffect numeric field for NaN/Infinity and just-outside bounds | Native validation cases; no asset loading |
| BC-X02 | Sweep every ChannelDrain numeric field for NaN/Infinity and just-outside bounds | Native validation cases; no asset loading |
| BC-X03 | Cover mutually exclusive add-on / defensive-card validator combinations | Native cases for AreaEffect+ChannelDrain and defensive conflicts |
| BC-X04 | Add default-off compatibility checks for the compiled MoveCard snapshot | Defaults preserved and copied optional payloads remain disabled |
| BC-X05 | Review the BB property tests for deterministic assertions and fixture-only dependencies | File:line matrix; no transient worlds or asset loads |

## Batch 2 — Sevarog proof boundaries (BC-X06–X10)

| ID | Task | Acceptance |
|---|---|---|
| BC-X06 | Inventory current C-1256a/C-1258a/C-1262a proof artifacts | Hash/path inventory; do not open or change Lead-owned raw evidence |
| BC-X07 | Cross-check Sevarog MoveCard authoring manifest against accepted C-1254 rows | Offline row-level reconciliation; no asset authoring |
| BC-X08 | Audit Sevarog live-driver fail-closed checks against the latest documented API | File:line audit and bounded test gaps |
| BC-X09 | Audit retry/watchdog terminal-state rules against native test coverage | Transition matrix with uncovered cases |
| BC-X10 | Refresh the Sevarog proof boundary checklist with any verified changes | Links and scope remain distinct for source/build/PIE/asset |

## Batch 3 — framework boss lifecycle audits (BC-X11–X15)

| ID | Task | Acceptance |
|---|---|---|
| BC-X11 | Trace native framework boss spawn ownership and teardown | Source-backed lifecycle map; no runtime claim |
| BC-X12 | Audit controller possession/unpossession paths | Failing scenario and file:line evidence |
| BC-X13 | Audit health/death idempotence and repeated-death guards | Source/test gap list; no gameplay changes |
| BC-X14 | Audit HUD health binding options for `IRPGNativeBossHealth` | Minimal interface proposal with compatibility scope |
| BC-X15 | Audit encounter completion/retry integration points | Signal/owner map and missing transitions |

## Batch 4 — Greystone asset readiness (BC-X16–X20)

| ID | Task | Acceptance |
|---|---|---|
| BC-X16 | Recheck child BP and wrapper package presence before dependent work | Read-only path receipt; mark dependent rows blocked if absent |
| BC-X17 | Review wrapper verification driver path allowlist and refusal behavior | Offline source contract or precise audit |
| BC-X18 | Review wrapper notify comparison coverage for timing/track identity | Document unobservable UE Python fields and readback boundary |
| BC-X19 | Audit Greystone startup switch reset and normal-pawn fallback | Source matrix; do not launch editor |
| BC-X20 | Reconcile Greystone CookCoverage roots with approved package paths | Config diff report; no cook run |

## Batch 5 — damage/parry contracts (BC-X21–X25)

| ID | Task | Acceptance |
|---|---|---|
| BC-X21 | Map framework outgoing damage rejection reasons | Resolver policy table with file:line references |
| BC-X22 | Map native-health incoming damage behavior | Adapter contract and explicit pack-path differences |
| BC-X23 | Audit parry event key dedupe across shared hit groups | Source/test boundary report |
| BC-X24 | Audit i-frame monitor teardown retry behavior | State transition table; add tests only for deterministic pure rules |
| BC-X25 | Audit player parry teardown retry behavior | State transition table; add tests only for deterministic pure rules |

## Batch 6 — offline validators and evidence (BC-X26–X30)

| ID | Task | Acceptance |
|---|---|---|
| BC-X26 | Inventory validators used by the Sevarog/Greystone lane | Command/path inventory with no execution of engine tools |
| BC-X27 | Add malformed-input contract coverage to one safe offline validator | Focused offline tests and syntax check |
| BC-X28 | Add path traversal/identity coverage to one offline evidence reader | Focused offline tests; no touching captured evidence |
| BC-X29 | Audit report links for BB Codex batches 1–8 | Broken-link list or zero result |
| BC-X30 | Reconcile TASKS and TEST_PLAN status for BB Codex batches 1–8 | Exact status map; preserve Lead-owned gates |

## Batch 7 — documentation and source safety (BC-X31–X35)

| ID | Task | Acceptance |
|---|---|---|
| BC-X31 | Audit new C-1274 fields for disabled-default compatibility | Source comparison and test coverage matrix |
| BC-X32 | Audit effect-only card validation and compile paths | Source path map with edge cases |
| BC-X33 | Audit channel interrupt/cleanup call sites | Abort/EndPlay table with file:line evidence |
| BC-X34 | Audit temporary movement-speed restoration ownership | External-change and teardown scenario map |
| BC-X35 | Refresh known-issues entries for verified Batch BB findings | Preserve owner/Lead decision gates and source provenance |

## Batch 8 — quality gates (BC-X36–X40)

| ID | Task | Acceptance |
|---|---|---|
| BC-X36 | Audit the native test inventory for test hooks exposed through UFUNCTION | Reflected-surface inventory scoped to named classes |
| BC-X37 | Propose Shipping-safe guard patterns for identified test hooks | Minimal code options; no implementation without test/BuildTool evidence |
| BC-X38 | Audit current engine lock documentation and scripts for consistency | Static consistency matrix; never acquire or remove a lock |
| BC-X39 | Review build/test command documentation for stale Rebuild.ps1 guidance | File:line evidence and safe command correction proposal |
| BC-X40 | Add offline source checks for forbidden asset-write/save calls in read-only drivers | Focused script contract tests |

## Batch 9 — maintenance queue follow-through (BC-X41–X45)

| ID | Task | Acceptance |
|---|---|---|
| BC-X41 | Inspect Claude feedback for BC-X01–X40 and record disposition | Hotfix rejected rows first; no waiting for a review cycle |
| BC-X42 | Fix any bounded source/doc contract defects found in BC-X41 | Scoped diff and focused offline verification |
| BC-X43 | Audit newly received Lead evidence references without editing raw evidence | Read-only receipt/path inventory and limitations |
| BC-X44 | Sync accepted BC progress to TASKS/TEST_PLAN/PROJECT_STATE | Matching status, evidence path, and remaining gate |
| BC-X45 | Draft Queue BD with 50 five-task items from verified, owner-independent backlog | `QUEUE_BD.md` with scope and acceptance per task |

## Batch 10 — closeout (BC-X46–X50)

| ID | Task | Acceptance |
|---|---|---|
| BC-X46 | Audit BB/BC report links and local evidence-path references | Link/path report; no edits to evidence |
| BC-X47 | Reconcile open framework HUD/death integration blockers | Owner/Lead gate summary with source evidence |
| BC-X48 | Reconcile Greystone wrapper and CookCoverage blockers | Asset-presence status and exact pending Lead action |
| BC-X49 | Summarize verified defects, risks, and unresolved claims | Every item has source/evidence reference and scope |
| BC-X50 | Publish BC closeout handoff and next-batch action | Docs synchronized, no commit/push |

## Standing limits

- No Lead review wait; check at the next batch cycle and hotfix bounded rework immediately.
- Do not run Unreal, build, cook, PIE, Shipping, package, or profiler work without the required engine protocol and Lead ownership.
- Never infer authored asset/runtime behavior from source or synthetic tests. Keep raw Lead evidence immutable.
- Keep owner-selected gameplay values and other owner-only choices blocked until supplied.
