# Queue AB — Codex lane (50 tasks)

Written 2026-11-07 after AA-C45. Continue in batches of five, one mailbox post per batch; read the mailbox tail before each batch. Hotfixes first. Do not wait for Lead review: record blocked Lead/owner work in one line and continue to the next unblocked task. Owner-parked benchmark tasks are skipped. Codex does not build, package, or launch Unreal; Lead owns those checks. No commits or pushes.

## Batch 1 — close ER integration evidence gaps

| ID | Task | Acceptance |
|---|---|---|
| AB-C01 | Reconcile imported GuardCounter asset against manifest, notify table, and C-968 | source-cited readiness note; no import while lock held |
| AB-C02 | Audit guard-counter component timer cancellation on reset, death, unpossess, and EndPlay | lifecycle matrix with Source/test citations |
| AB-C03 | Add focused offline source-contract coverage for temporary attack-array override restoration paths | tests cover restore, fallback, timeout, and missing montage |
| AB-C04 | Map guard-counter window boundaries to rule tests and current implementation | boundary table; no threshold change |
| AB-C05 | Reconcile ER hand-test sheet prerequisites with wiring and clip acceptance | every pending row has exact build/clip/route gate |

## Batch 2 — ER clip wiring and safety

| ID | Task | Acceptance |
|---|---|---|
| AB-C06 | Audit optional montage soft-reference defaults and redirects | complete property/path inventory |
| AB-C07 | Verify montage notify names and expected gameplay tags against importer metadata | per-clip mismatch table; distinguish unaccepted clips |
| AB-C08 | Specify fail-closed behavior for missing or unloadable optional clips | testable behavior contract |
| AB-C09 | Audit input buffering and consumed-input reset around air attacks | Source-to-test map and concrete gaps |
| AB-C10 | Define a non-Editor validator for ER metadata/FBX/import manifest agreement | schema and fixture plan |

## Batch 3 — native automation depth

| ID | Task | Acceptance |
|---|---|---|
| AB-C11 | Audit guard-counter native automation assertions against accepted behavior | missing-assertion list with test names |
| AB-C12 | Add native pure-rule cases for counter-window start/end and expiry | tests-first, Lead build required |
| AB-C13 | Audit dodge route tests for repeated taps and movement-direction boundaries | cited behavior matrix |
| AB-C14 | Add native tests for BackstepMontage empty and assigned cases where feasible | deterministic tests; no Content mutation |
| AB-C15 | Map player action routes to telemetry/probe observables | route-to-evidence table |

## Batch 4 — package and cook readiness

| ID | Task | Acceptance |
|---|---|---|
| AB-C16 | Extend offline cook-root contract to cover expected accepted ER asset root | fixture proves exact root/required directories |
| AB-C17 | Review CookCoverage scanner limits for soft references and optional assets | gap note plus acceptance recommendation |
| AB-C18 | Create package manifest checklist for data-default Shipping smoke | build ID, route, hash, smoke, gameplay evidence fields |
| AB-C19 | Audit Shipping smoke process cleanup and timeout edge cases | static findings; safe failure behavior documented |
| AB-C20 | Define a separate Development log gate for data-route witness | exact expected log evidence; no Shipping log assumption |

## Batch 5 — settings and accessibility contracts

| ID | Task | Acceptance |
|---|---|---|
| AB-C21 | Audit DLSS setting serialization keys and migration behavior | config/source matrix; no default selection |
| AB-C22 | Add offline contract for unsupported hardware fallback | supported and unsupported fixtures |
| AB-C23 | Audit settings changes for restart/apply semantics | user-visible behavior table |
| AB-C24 | Specify keyboard/controller parity for graphics setting navigation | input map and focus acceptance |
| AB-C25 | Write plain-language settings acceptance sheet for Lead | one-page sheet; no UI asset edit |

## Batch 6 — source hygiene and compatibility

| ID | Task | Acceptance |
|---|---|---|
| AB-C26 | Audit changed Source files for UE 5.5 API/deprecation risks from available logs | exact file/line list; no speculative fix |
| AB-C27 | Re-run C-871 checklist on recent C08/C16/Tier 2 Source changes | name/include/access/capture/guards/Shipping-path matrix |
| AB-C28 | Audit optional-feature ownership and cleanup on world teardown | resource lifecycle table |
| AB-C29 | Check debug CVar references for Development-only guards | occurrence inventory; flag Shipping leaks |
| AB-C30 | Review Build.cs dependency scope for DLSS integration | minimal dependency evidence and risks |

## Batch 7 — test tooling

| ID | Task | Acceptance |
|---|---|---|
| AB-C31 | Add offline test discovery report for focused player contracts | deterministic summary and tests |
| AB-C32 | Audit Python test subprocess timeouts and cleanup | bounded process inventory |
| AB-C33 | Add regression fixture for paths containing spaces in Gate.ps1 | contract test passes |
| AB-C34 | Audit generated reports for stale absolute paths and machine-specific assumptions | findings with exact paths |
| AB-C35 | Add an offline validator for AA/AB queue IDs and five-task grouping | invalid/duplicate/missing IDs rejected |

## Batch 8 — control and combat documentation

| ID | Task | Acceptance |
|---|---|---|
| AB-C36 | Reconcile control spec, hand-test sheet, and runtime mappings | discrepancy table; one canonical mapping |
| AB-C37 | Document accepted vs pending ER animation claims from mailbox | evidence-linked status table |
| AB-C38 | Audit player death/reset behavior during active attack montages | Source/test coverage map |
| AB-C39 | Review guard, parry, and counter terms for consistent owner-facing wording | terminology table and edits |
| AB-C40 | Produce combat input troubleshooting flow for QA | concise decision tree, no unsupported claims |

## Batch 9 — milestone evidence and handoff

| ID | Task | Acceptance |
|---|---|---|
| AB-C41 | Refresh milestone gate matrix for current owner-parked R6 and ER gates | status, owner, evidence, next action per gate |
| AB-C42 | Reconcile current test counts and baselines against mailbox build receipts | source-backed numbers only |
| AB-C43 | Audit KNOWN_ISSUES for resolved/duplicate ER and settings entries | proposed disposition with citations |
| AB-C44 | Refresh DECISIONS index from latest mailbox posts | complete IDs and concise decisions |
| AB-C45 | Write Queue AC (Codex, 50) | 50 unique IDs in ten batches |

## Batch 10 — cross-check and continue

| ID | Task | Acceptance |
|---|---|---|
| AB-C46 | Cross-check new docs against Source, config, tests, and mailbox | contradiction list resolved or explicitly gated |
| AB-C47 | Prepare owner-facing engineering progress summary | plain language, current evidence and remaining gates |
| AB-C48 | Re-review Lead/Antigravity outputs added since AA-C45 | bounded findings; no asset edits |
| AB-C49 | Prepare one-page handoff for next Codex lane | active work, dependencies, paths, validation boundaries |
| AB-C50 | Close Queue AB and begin Queue AC batch 1 | one mailbox post; continue without waiting |

## Standing boundaries

- Engine lock belongs to one operator. Never import or run Editor work while another owner holds it.
- Keep optional gameplay assets empty until accepted and assigned; do not change product defaults without an owner decision.
- Performance/benchmark measurement remains parked until the owner resumes it.
- Record measured evidence separately from static analysis and distinguish Lead build/PIE results from Codex checks.

## Closeout

AB-C01–C50 completed in ten five-task batches. Final cross-check, current owner summary, receipt re-review, and handoff are in `Documentation/Boss/AB_C46_C50_FINAL_CROSSCHECK_HANDOFF.md`. Queue AC is active; AC-C01–C05 are already complete and the next batch is AC-C06–C10. Continue without waiting for parallel Lead review.
