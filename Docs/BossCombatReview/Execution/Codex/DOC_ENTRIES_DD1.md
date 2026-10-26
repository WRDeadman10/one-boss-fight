# X-T12 staged project-document entries

2026-10-26. **Not applied.** Claude owns the four project docs. Read their existing headers/tails; use formats below. Maximum KI id currently108 (rows are not numerically ordered); KI109..112 were unused at this read, not permanently reserved. Recheck for concurrent claims before pasting. Test table has7 columns; its existing late BUILD-03 and SCRATCH-A rows have only5 cells. Proposed replacements below restore7 cells while preserving IDs; do not append duplicate IDs. New DD1-01..04 were unused at this read. DECISIONS uses dated sections, no numeric ids. PROJECT_STATE gotchas use bullets.

All Execution paths below are relative to project root. Raw hash/evidence index is in Codex/OWNER_PACKAGE_DD1_STEP1.md. Dates/counts belong to frozen runs, not every later binary. Do not silently convert proposed test criteria to PASS.

## Documentation/DECISIONS.md

Add a dated section before its final Open section (not into an unrelated historic decision):

### DD1 catalog contract (2026-10-26, implemented scope; full acceptance pending)

| Item | Decision |
|---|---|
| Complete startup source | auto publishes one complete valid data epoch or one complete legacy compatibility epoch with reason; legacy loads no catalog; strict data failure publishes no epoch and disables consumers. No per-lookup data/legacy mixing. Development source changes affect next session only; Shipping source/test controls compiled out, uses auto. Spec STEP1_SPEC_v3_AMENDMENTS; Catalog.cpp Context.Publish/Initialize. |
| Epoch lifetime | A game-instance subsystem owns immutable copied values and reference leases; consumers carry that epoch. No mutable global current epoch/global LIFO restore. Real GI ordering/travel/concurrent teardown-equip proof remains open; pure contexts are not accepted as that witness. |
| Existing three-build contract | Stable BuildId drives new catalog paths; legacy slots0/1/2 pinned independently of UI order. Legacy enum99 still maps to Dex. Fourth fixture shares Sword; new-weapon/P8 canary not demonstrated. |
| Validation acceptance boundary | Full-path load and wiring-text checks are currently bounded installed-content validation, not fixed expected ABI/typed-role closure. Condition1 remains open; exact readback and tests specified in Execution/Codex/TYPED_ABI_CLOSURE_TEST_SPEC.md. |
| Promotion gate | Codex accepts bounded three-build editor compatibility WITH CONDITIONS. Step2/3 patches are unapplied incomplete scaffolds; missing typed adapters/importer/fixtures and owner scope approval still required. No P1 start, G4/G5, pack edits, commits or pushes authorized by this milestone. |
| Packaged result | Development cold source=data witnessed; both data and legacy logs contain19 material errors and log checker fails. Shipping content/liveness/debug-off does not directly attest selected data source. Keep catalog loading separate from whole-package quality/performance acceptance. |

## Documentation/KNOWN_ISSUES.md

Append rows to its existing5-column table (before any future prose section):

| ID | Area | Description | Workaround | Status |
|---|---|---|---|---|
| KI-109 | DD1 packaging | Shipping catalog source selection has no direct runtime provenance witness because logs and source/test cvars are compiled out. Seven staged assets, liveness and CheckShippingBinary pass would not prove source=data. Development cold publication is independently witnessed (archived data log9e0ec499...). | Keep Shipping source verdict INCONCLUSIVE; use Development proof for that bounded milestone. Owner-approved read-only Shipping provenance or explicit acceptance of weaker inference needed for direct Shipping criterion. See Execution/Codex/CATALOG_PACKAGED_PROOF.md. | Open evidence gap, not a reproduced load failure |
| KI-110 | Capture tooling | Claude's HighResShot capture attempts in this PIE environment yielded black/placeholder frames; script RESULT/quota did not prove usable images. Standing-editor CaptureLoop.ps1 PrintWindow produced actual frame files in C148, but framing/visible hand release remain unverified and camera correction pending. | Capture standing editor via CaptureLoop with flag tags and wall/sim telemetry; validate nonblank/nonidentical images and actual coverage/framing. Missing hooks must fail, not substitute False/0. No claim HighResShot fails universally. | Open tooling/framing verification |
| KI-111 | Scratch proof | E010 run2 had empty task report after fixed5s, cause unknown; runs3-6 passed20/20 with bounded polling. Run4 repeats root tasks, consistent with UE Looped tree execution; does not prove explicit RestartLogic. | Poll with bounded diagnostics; keep scratch out of product/gate. Do not relax single-start transaction requirements based on id1/id2-only assertions. | Open unexplained first-run timing; feasibility witnessed |
| KI-112 | DD1 validation | Catalog ItemBaseClass comes from declared data/actual item class, AbilityClass only requires UClass and combined exported property text can satisfy wiring checks without role-correct typed edges. Three installed bundles work; arbitrary new/untrusted bundles are not fully validated. | Trusted authoring boundary only pending native fixed ABI/role validation plus meaningful negative tests. Readback batch X140; test spec Execution/Codex/TYPED_ABI_CLOSURE_TEST_SPEC.md; no guessed topology or pack edits. | Open acceptance condition1 |

Do not close KI080 on the basis of catalog cold-load proof. No new material-error root cause is asserted here.

## Documentation/TEST_PLAN.md

Replace existing BUILD-03 row by this7-cell row after checking latest text:

| Test ID | Area | Procedure | Pass criteria | Build | Result | Evidence |
|---|---|---|---|---|---|---|
| BUILD-03 | DD1 catalog compatibility | pie_combat_catalog.py plus Catalog.Context/Validation/LegacyParity/Resolution automation; fresh legacy/data/fourth/strict-invalid sessions | Three legacy values/words/order/equip outcomes unchanged; fourth stable id selects/defer/reset/respawn using existing Sword; no mixed epoch; late cvar cannot mutate; unbound shared style ambiguous | Frozen final WP15 | Catalog91/91 in full gate40/40; automation41/41 on recorded binary, not all later binaries | Execution/Claude/Evidence/exports/gate_step1_final_2026-10-26.txt d97d839d...; Saved/rebuild_step1_wp15.txt; remaining spec conditions in Execution/Codex/STEP1_ACCEPTANCE_REVIEW.md |

Add new rows with the same7-column format (not another header in target):

| DD1-01 | Typed reference closure | TYPED_ABI_CLOSURE_TEST_SPEC.md:5 positive/12 negative cases using actual native ancestry/property-role pins | Role-correct full identity/ancestry, negative reaches intended resolving stage; complete publication/failure; no text-membership false pass | Pending future reviewed patch | NOT RUN / implementation open | Exact readback request X140; PROMOTION_STEP1_TYPED_ABI_HOLD.md; no patch claimed |
| DD1-02 | Real GI lifetime and ordering | Instrument actual publish-before-first-consumer; same-GI travel; two real GIs while one tears down and other equips | Correct retained/fresh epoch identities, no mixed world context or dangling references; actual equip continues in surviving GI | Pending Claude fixture | NOT RUN / condition2 open | Pure FContext tests and fresh PIE recreation are bounded substitutes only, not acceptance evidence |
| DD1-03 | Constrained selector and focus | Actual1080p and constrained viewport render/input; all keyboard/mouse/focus paths; missing/broken icon and overflow | First3 positions unchanged; fourth visible in acceptance viewport; hidden rows unavailable to actual input/focus; once-only diagnostic and identifiable text fallback | Pending Claude driver | NOT RUN / condition3 open | Formula-only RowVisible checks do not close real viewport/focus criterion |
| DD1-04 | Cold packaged catalog | Package.ps1 Development, explicit7 package manifest check, fresh PackagedSmoke and archived source log; separate Shipping checks | Development source=data with new epoch/no missing required dependency; Shipping provenance separately observed or explicitly INCONCLUSIVE; material errors never hidden | Archived Development run2026-10-26 | Development publication witnessed; packaged log checker FAIL on materials; Shipping selection unproved | data log9e0ec499..., legacy8e549091...; manifest162e2db0...; CATALOG_PACKAGED_PROOF.md |

Existing SCRATCH-A should retain its scratch-only status; if normalizing its short row, use build=G3 scratch, result=runs3-6 20/20 reported/raw reviewed, evidence=E010 and SCRATCH_ROUTE_A_REVIEW.md. No production transaction/clean process exit/one-start guarantee implied.

## Documentation/PROJECT_STATE.md gotchas

Add current dated bullets near the recent-state gotchas, leaving historical baseline sections intact:

- DD1(2026-10-26): current catalog modes latch per game instance before consumers. Source switch/test controls are Development only; Shipping uses auto and has no runtime log. A stage manifest and smoke/debug-name pass do not attest Shipping source=data. Step1 remains ACCEPT WITH CONDITIONS; see Execution/Codex/STEP1_ACCEPTANCE_REVIEW.md.
- Catalog structural negatives can short-circuit at the pinned three-build contract. To test resolving validation, use an extra structurally valid nonlegacy bundle and assert its exact resolving field; C140 fixes the old wrong-style test trap. Typed ABI closure remains open.
- Capture(2026-10-26): use existing CaptureLoop.ps1 in the standing editor with phase flag/wall-sim correlation; HighResShot was black in these attempts. Existing tracker hooks are GetPosition/IsActiveWindow/GetPhaseName, not guessed alternatives with hasattr fallback. Frame quantity alone is not usable capture/visible release proof.
- Scratch route(a): EnemyInfo must be supplied before BeginPlay on the test actor. First post-rebuild fixed5s empty report remains unexplained; use bounded polling. Immediate task completion in default Looped BT may repeat; integer reservation diagnostics are not exactly-once product transactions.
- Staged patches under Execution/Codex are not live Source: step2/3 git apply checks do not mean built, runtime-tested or ready to replace attachment/animation metadata. Only Claude builds/runs; owner accepts scope and commits. Preserve unrelated dirty source and keep preimages for the owned delta.

## TASKS.md coordination note for Claude

The existing Boss combat improvement program row/dashboard is the master status. Update it in place after review to mention bounded step1 acceptance with conditions1-3 open and Development cold-load witness, step2/3 scaffold HOLD, P1 held; do not add a duplicate master task or count X-T9 HOLD as completion. Codex has not edited TASKS or any of the four target docs.
