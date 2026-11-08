# Queue AK — next-day controls, evidence and release audit (50 tasks)

Run in five-task batches. Post one X receipt per batch (maximum eight lines), then continue without waiting for Lead review. At the next mailbox cycle, hotfix any rejected item first. Claude builds, runs PIE/native tests and reviews; Codex owns offline work and scoped docs. Source changes require tests first and a `PRODUCTION CHANGE` label in the receipt. Never commit or push. Evidence-dependent rows record `WAITING ON <evidence>` and continue to the next row; they do not infer a pass.

Batch 1 = C01–C05, Batch 2 = C06–C10, Batch 3 = C11–C15, Batch 4 = C16–C20, Batch 5 = C21–C25, Batch 6 = C26–C30, Batch 7 = C31–C35, Batch 8 = C36–C40, Batch 9 = C41–C45, Batch 10 = C46–C50.

| ID | File(s) | Task and acceptance |
|---|---|---|
| AK-C01 | `Docs/BossCombatReview/Execution/Claude/P_C1006_GUARDCOUNTER/`, `Documentation/TEST_PLAN.md` | Check Lead C-1020 synthetic rerun on both routes; record R2 release, ER strong count, montage, hit kind/data and HP delta, or exact missing evidence. |
| AK-C02 | `Docs/BossCombatReview/Execution/Claude/P_C1006_GUARDCOUNTER/`, `Documentation/KNOWN_ISSUES.md` | Separate synthetic success from real guarded-contact evidence; KI-198 closes only if the named live gate is met. |
| AK-C03 | `Docs/BossCombatReview/Execution/Claude/P_C980_BACKSTEP/`, `Documentation/KNOWN_ISSUES.md` | Recheck corrected moving-case speed and last-input fields for both routes; KI-196 closes only from a valid rerun of the affected probes. |
| AK-C04 | `Documentation/Boss/CONTROLS_STATUS.md` | Refresh the owner table from C01–C03 with exact evidence IDs, no inferred physical latency or owner approval. |
| AK-C05 | `Documentation/Boss/AK_C01_C05_RUNTIME_ACCEPTANCE.md` | Publish the five-row evidence receipt with each route/gate and open owner. |
| AK-C06 | `Scripts/Editor/pie_lead_common.py`, `Scripts/Editor/test_pie_lead_common.py` | Test missing boss/player/component behavior and prove no implicit editor import in offline tests. |
| AK-C07 | `Scripts/Editor/pie_er_control_latency.py`, `Scripts/Editor/pie_er_air_restore.py` | Audit ported setup/finish parity with retained C-971/C-978 probes; report changed behavior or Lead smoke proof. |
| AK-C08 | `Scripts/Editor/pie_er_guard_counter.py` | Audit both synthetic/live cleanup paths and drawn-state retry bounds; add offline state tests only where useful. |
| AK-C09 | `Scripts/Editor/pie_er_air_hits.py`, `Docs/BossCombatReview/Execution/Claude/P_C992_AIRHITS/pie_er_air_hits.py` | Diff canonical reach probe against retained evidence; enumerate intentional shared-helper substitutions and any result-field drift. |
| AK-C10 | `Documentation/Boss/AK_C06_C10_PROBE_PORT_AUDIT.md` | Summarize helper tests, parity findings and Lead-only runtime gates. |
| AK-C11 | `Scripts/RunLeadPie.ps1`, `Scripts/Tests/TestRunLeadPieDryRun.ps1` | Add dry-run assertions for invalid route/env/timeout and no lock/output side effects. |
| AK-C12 | `Scripts/RunLeadPie.ps1` | Audit process cleanup on early exit, timeout and missing marker; fix with a Pester-free dry-run fixture if a reproducible bug exists. |
| AK-C13 | `Scripts/RunLeadPie.ps1` | Audit env restoration and route isolation (legacy clears H019; data selects G044); test with a pre-existing process env value. |
| AK-C14 | `Scripts/RunLeadPie.ps1` | Audit 8.3 script-path/quoted command handling and non-spaced project assumptions; document any fallback gate without launching UE. |
| AK-C15 | `Documentation/Boss/AK_C11_C15_RUNNER_AUDIT.md` | Publish runner contract, tested cases and live smoke dependency. |
| AK-C16 | `Source/OneBossFight/Tests/RPGGuardCounterRulesTests.cpp` | Review Lead native result for new edge tests when BUILD-256 exists; until then record static review and WAITING ON BUILD-256. If rejected, hotfix test expression before other work. |
| AK-C17 | `Source/OneBossFight/Tests/RPGAutomationTests.cpp` | Audit override kind tests against runtime identity/lifetime source and Lead compiler result. |
| AK-C18 | `Source/OneBossFight/Tests/RPGMontageUtilsTests.cpp` | Audit zero-slot, non-finite and multi-slot expectations against `RPGMontageUtils.cpp` and Lead run. |
| AK-C19 | `Source/OneBossFight/Combat/RPGMontageUtils.cpp`, `Documentation/KNOWN_ISSUES.md` | Source-review multi-slot semantics and package mutation; propose a production fix only with failing test evidence. |
| AK-C20 | `Documentation/Boss/AK_C16_C20_NATIVE_REVIEW.md` | Record test result IDs, compiler issues, and any real Source change separately. |
| AK-C21 | `Documentation/Boss/ER_PLAYER_CONTROLS_SPEC.md` | Reconcile saved optional montage-field status with current owner/Lead order; remove stale current-state sentences, retain history. |
| AK-C22 | `Documentation/Boss/GATE07_ANIMATION_REVIEW.md` | Cross-check four ER clip lengths and owner review state against the review pack and accepted mailbox IDs. |
| AK-C23 | `Documentation/Boss/OWNER_REVIEW_PACK.md` | Audit links to all four ER videos, strips and owner reel; run offline broken-link check for this page. |
| AK-C24 | `Documentation/Boss/AA_A08_NOTIFY_FRAMES_TABLE.md` | Compare notify/data claims to C-1003 saved T3D and C-1004 PIE; flag any unsupported active status. |
| AK-C25 | `Documentation/Boss/AK_C21_C25_OWNER_CONTENT_AUDIT.md` | Give one current owner/content gate summary, separating clip approval, saved wiring and package proof. |
| AK-C26 | `Source/OneBossFight/Player/RPGDodgeTiming.cpp` | Audit guard-contact monitor tick timing, suffix match and `Status.Blocking` precondition after C-1013. |
| AK-C27 | `Source/OneBossFight/Player/RPGDodgeTiming.cpp` | Audit strong montage override apply/start/restore/timeout path against Lead counter traces. |
| AK-C28 | `Source/OneBossFight/Player/RPGSwingTracker.cpp`, `Source/OneBossFight/Player/RPGHitIntake.cpp` | Trace counter montage kind/data into swing and hit attribution; distinguish source path from runtime proof. |
| AK-C29 | `Source/OneBossFight/Player/RPGBuildLoadout.cpp`, `Scripts/Editor/pie_er_guard_counter.py` | Audit `is_combat_enabled` as the synthetic draw gate and identify any false-ready state. |
| AK-C30 | `Documentation/Boss/AK_C26_C30_COUNTER_PATH_AUDIT.md` | Publish a source/evidence map and precise remaining counter failure stage. |
| AK-C31 | `Documentation/KNOWN_ISSUES.md` | Audit KI-190–KI-198 status against latest mailbox and raw receipts; change only rows with direct closure evidence. |
| AK-C32 | `Documentation/TEST_PLAN.md` | Remove duplicate or superseded control tests while preserving raw-result history and separate owner/runtime gates. |
| AK-C33 | `Documentation/PROJECT_STATE.md` | Refresh only current controls/queue handoff with accepted evidence and the active review owner. |
| AK-C34 | `Documentation/Boss/CONTROLS_STATUS.md` | Verify every number and named asset against a raw receipt or current saved readback. |
| AK-C35 | `Documentation/Boss/AK_C31_C35_STATUS_CENSUS.md` | Emit issue/test/doc census with corrected source links and no inferred closures. |
| AK-C36 | `Scripts/Tools/` offline checks, `Documentation/Boss/OWNER_REVIEW_PACK.md` | Run link validation and inventory missing owner-review media without modifying assets. |
| AK-C37 | `Docs/BossCombatReview/Execution/Claude/P_C1006_GUARDCOUNTER/` | Design a compact parser for counter trace markers; test it on retained logs and report absent fields explicitly. |
| AK-C38 | `Docs/BossCombatReview/Execution/Claude/P_C971_ERLATENCY/` | Recompute game-tick R2 boundary rows from raw lines; preserve timing uncertainty. |
| AK-C39 | `Docs/BossCombatReview/Execution/Claude/P_C992_AIRHITS/` | Reconcile air-hit HP deltas and hit kind/data on both routes with C-1004 accepted values. |
| AK-C40 | `Documentation/Boss/AK_C36_C40_EVIDENCE_TOOLS.md` | Publish parser/link-check results and exact raw provenance. |
| AK-C41 | `Scripts/Package.ps1`, `Scripts/MakeBenchKit.ps1` | Revisit KI-197 stage-root ambiguity without cleanup or packaging; map configuration sources. |
| AK-C42 | `Scripts/PackagedSmoke.ps1`, `Scripts/ShippingSmoke.ps1` | Verify what each smoke gate proves and whether it binds the same staged executable. |
| AK-C43 | `Docs/BossCombatReview/Execution/Codex/R6_PHASE1/receipt.json` | Recheck Phase 1 identity/hash chain and distinguish measured from predicted values. |
| AK-C44 | `Documentation/Boss/PERFORMANCE_DECISION_BRIEF_ROUNDS_1_6.md` | Reconcile target 60 FPS/p99 16.67 ms with current evidence; Phase 2 remains parked until owner direction. |
| AK-C45 | `Documentation/Boss/AK_C41_C45_RELEASE_EVIDENCE.md` | Publish packaging/performance gate map; do not claim a packaged 2060 Super pass. |
| AK-C46 | `Documentation/Boss/QUEUE_AK.md` | Census all 50 rows for duplicate work, stale asset names, blocked-only batches and missing acceptance. |
| AK-C47 | `Documentation/Boss/CONTROLS_STATUS.md`, `Documentation/Boss/OWNER_REVIEW_PACK.md` | Cross-check final owner-facing controls text and media links against the latest Lead review. |
| AK-C48 | `Documentation/KNOWN_ISSUES.md`, `Documentation/TEST_PLAN.md` | Reconcile issue closures and runtime test gates, preserving unresolved KI-196/KI-198 until direct proof. |
| AK-C49 | `Documentation/Boss/AK_C46_C50_HANDOFF.md` | Write next-lane handoff with accepted batches, rejected hotfixes, pending Lead build/PIE and owner gates. |
| AK-C50 | `Documentation/Boss/QUEUE_AK.md`, `Documentation/TASKS.md` | Close only completed rows; post one final five-task receipt and keep unrun work explicit. |

## Progress

- AK-C01–C05: Lead post-X-1428 draw-gated C-1020 rerun and corrected moving-case evidence pending; `CONTROLS_STATUS.md` records the current limits. Runtime acceptance batch remains open, owned by Lead evidence; no implied pass.
- AK-C06–C10: offline helper hardening and port audit complete; Lead runtime smoke remains an external acceptance gate. See `AK_C06_C10_PROBE_PORT_AUDIT.md`.
- AK-C11–C15: offline runner refusal/route/path audit and dry-run test complete; live lock/timeout/env smoke remains Lead-owned. See `AK_C11_C15_RUNNER_AUDIT.md`.
- AK-C16–C20: native test/source review complete statically; Lead build and exact native suites still pending under `ENGINE_LOCK`. See `AK_C16_C20_NATIVE_REVIEW.md`.
- AK-C21–C25: owner/content status, four ER row labels, lengths, T3D notify data and review-pack links audited; fresh default-wired PIE/package/Tier 2 appearance remain Lead gates. See `AK_C21_C25_OWNER_CONTENT_AUDIT.md`.
- AK-C26–C30: source-only guard arm → R2 override → swing/hit map complete; C-1020 draw-gated synthetic and live-contact Lead reruns remain open. See `AK_C26_C30_COUNTER_PATH_AUDIT.md`.
- AK-C31–C35: KI-190–KI-198 census, TEST_PLAN deduplication, current handoff and owner controls numbers reconciled. C-1024 corrected the initial backup-name misread: explicit C-1004 r5 receipts support about -22.4 AirHeavy HP on both routes. See `AK_C31_C35_STATUS_CENSUS.md`.
- AK-C36–C40: owner pack links/media inventory, guard-counter marker parser, R2 raw timing, and C-1004 air-hit HP audit complete offline. Parser isolated tests 2/2; 22 media paths present, broken_links=0. C-1024 clarified r5 provenance; see `AK_C36_C40_EVIDENCE_TOOLS.md`. Continuing C41–C45 without waiting for review.
- AK-C41–C45: package/kit stage roots, smoke executable binding, Round 6 Phase 1 receipt/archive hash and owner performance gate reconciled offline. KI-197 and Phase 2 remain open; no package or benchmark run. See `AK_C41_C45_RELEASE_EVIDENCE.md`. Continuing C46–C50 without waiting for review.
- AK-C46–C50: 50-row queue census and final owner/issue/test handoff complete offline. C-1024 r5 correction is reflected in owner pack with explicit source; link check remains broken_links=0. C01–C05 remains WAITING ON Lead runtime receipts; BUILD-256/native and default-wired PIE/package are external gates. See `AK_C46_C50_HANDOFF.md`.
