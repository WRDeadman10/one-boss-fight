# Queue X — proposed Codex lane after Queue W

Draft by Codex for Claude review, 2026-11-06. Work pattern: batches of five, one mailbox post per batch; read mailbox tail at each cycle; continue to the next unblocked batch without waiting for review; take rejected items as immediate hotfixes. No commits/pushes by Codex. Any Editor/build/PIE, package, owner choice, asset save, or destructive action remains with its designated Lead/owner.

Status: X-C001–X-C005 complete locally. UE 5.5 source confirms the factory creates a one-sequence montage; `create_tier1_art_assets.py` now defaults to dry run and refuses the incomplete A2 assembly. Focused safety suite 7/7. No asset save or Editor run. Next X-C006–X-C010.

## Batch 1 — Tier 1 authoring safety and A2 correctness

| ID | Task | Acceptance |
|---|---|---|
| X-C001 | Reproduce W-C046's montage-source finding against UE 5.5.4 API declarations | API/source evidence note; no Editor run |
| X-C002 | Prepare a dry-run/explicit-execute contract for `create_tier1_art_assets.py` | proposal and safe refusal cases; no asset write |
| X-C003 | Specify three-clip A2 montage segment/section requirements from the installed API | source-backed sequence table and expected duration formula |
| X-C004 | Strengthen offline guard coverage for writer execution gates and every save call | synthetic source fixtures; no live content test claim |
| X-C005 | X-C001..004 receipt and W-C046 finding disposition check | one batch post; preserve Lead verdict |

## Batch 2 — content writer contracts

| ID | Task | Acceptance |
|---|---|---|
| X-C006 | Inventory all project Python asset writers and save call sites | path/line inventory; writer vs read-only classification |
| X-C007 | Audit namespace/path anchoring on each writer | findings only; no script execution |
| X-C008 | Audit overwrite/refuse behavior on each writer | exact code paths; identify missing guard fixtures |
| X-C009 | Compare writer reports against actual validation assertions | claim-to-check table; unsupported claims labeled |
| X-C010 | Batch receipt | one concise post and hand off any proposed source fixes |

## Batch 3 — tool validation contracts

| ID | Task | Acceptance |
|---|---|---|
| X-C011 | Recheck V-A054 `PrimaryAutomationTest` registration mapping after disposition | registration evidence or updated finding |
| X-C012 | Audit `test_requirements_coverage_matrix.py` fixtures for false-pass paths | bounded mutation matrix; no edits to AG files |
| X-C013 | Cross-check test registration claims against C++ implementation macros | exact source path and test name table |
| X-C014 | Review requirements matrix status/category semantics | mismatches or explicit no-finding report |
| X-C015 | Batch receipt | one post; update unresolved findings |

## Batch 4 — G044 and parity evidence durability

| ID | Task | Acceptance |
|---|---|---|
| X-C016 | Reconcile G044 typed paths against current native defaults | cited current-vs-manifest table |
| X-C017 | Audit D5/legacy baseline for numeric token coverage gaps | synthetic fixtures and explicit limits |
| X-C018 | Check parity pair receipts for path/build identity consistency | receipt-to-log hash audit; no rerun |
| X-C019 | Review warning-only comparison rules for hidden gameplay mismatches | counterexamples or clear scope note |
| X-C020 | Batch receipt | one post with unclosed rows retained |

## Batch 5 — benchmark readiness, offline

| ID | Task | Acceptance |
|---|---|---|
| X-C021 | Re-audit Round 6 kit manifest against current required support files | static checker result and exact missing/extra paths |
| X-C022 | Compare kit `BUILD_INFO` identity to staged executables and telemetry scripts | hash/build ID table; no game launch |
| X-C023 | Review Round 6 receipt schema against the README fields | required/optional mapping and missing-field fixtures |
| X-C024 | Check Round 6 stop conditions and retained failure folders | source-only control-flow audit |
| X-C025 | Batch receipt | state that physical run still needs Lead/owner |

## Batch 6 — performance evidence analysis

| ID | Task | Acceptance |
|---|---|---|
| X-C026 | Audit returned Round 6 bundle when available | hash/identity checked intake; otherwise WAITING ON LEAD and continue |
| X-C027 | Independently recompute per-mode summary from raw runs | reproducible table or documented missing inputs |
| X-C028 | Cross-check active DLSS mode witnesses against treatment labels | every treatment has a matching log witness or fails intake |
| X-C029 | Separate measured FPS, p99, GPU time, and prediction values across docs | no inferred measurement; citations per field |
| X-C030 | Batch receipt | state owner image-quality gate separately |

## Batch 7 — combat timing evidence

| ID | Task | Acceptance |
|---|---|---|
| X-C031 | Intake Lead's six latency sessions after R6 (or continue if absent) | route/FPS/action identity and run-independent comparisons |
| X-C032 | Audit montage observation delay versus game tick cadence | instrumentation limit quantified only from logs |
| X-C033 | Intake paired telegraph captures for A1–A6 | measured, inconclusive, and unrun states kept distinct |
| X-C034 | Reconcile hit-stop/shake/audio captures with the source matrix | event-by-event source/log/capture trace |
| X-C035 | Batch receipt | no reaction or feel claim without evidence |

## Batch 8 — selected route release gates

| ID | Task | Acceptance |
|---|---|---|
| X-C036 | Reconcile packaged selector/first-caller evidence when Lead returns it | source/build/log identity checked |
| X-C037 | Audit cooked content manifest and selected definition closure | package paths resolved; no asset mutation |
| X-C038 | Review refusal/visual recovery receipt for both routes | explicit pass/fail/unrun checks |
| X-C039 | Verify legacy fallback and selected-route policy text across release docs | no contradictory default/retirement statement |
| X-C040 | Batch receipt | A7 remains open until every named gate has evidence |

## Batch 9 — issue and owner-decision closure

| ID | Task | Acceptance |
|---|---|---|
| X-C041 | Refresh KI-190 after owner/Lead decision or leave open | exact approved choice plus real loadout receipt, else no status change |
| X-C042 | Refresh Tier 2 art brief after owner selection or deferral | no look-changing execution before explicit choice |
| X-C043 | Reconcile owner decision table against mailbox and DECISIONS index | each choice/default/source agrees |
| X-C044 | Review P35 cleanup references without deleting/moving files | per-candidate referencer evidence and owner gate retained |
| X-C045 | Batch receipt | only owner may close owner-gated decisions |

## Batch 10 — release documentation and roll

| ID | Task | Acceptance |
|---|---|---|
| X-C046 | Refresh current residual risk register from evidence completed in X batches | every status has a source; unresolved gates retained |
| X-C047 | Cross-check witness ledger against new evidence and citation lines | validator pass plus semantic exceptions list |
| X-C048 | Reconcile PROJECT_STATE, TASKS, TEST_PLAN, KNOWN_ISSUES, DECISIONS | no contradictory current state; historical snapshots labeled |
| X-C049 | Write a release-owner handover with decisions and gates | one-page summary; no completion percentage without defined basis |
| X-C050 | Draft the next 50-task lane from remaining concrete gaps | ten batches of five, file targets, acceptance, Lead review |

Claude review is requested for this proposal. The queue does not authorize production/source edits beyond the named tasks or any owner-gated action.
