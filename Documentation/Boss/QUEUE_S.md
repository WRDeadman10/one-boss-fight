# Queue S — after A5 parity (50 tasks)

Written by the lead (Claude), 2026-11-05, after A5 live parity (31 drivers), BUILD-222, owner decisions J049 = A and A7 = B.
Rules unchanged: C-797 (5-task batches, one X- per batch or Source change, roll to Queue T at S45), C-820 (no re-check/status-only
tasks; "WAITING ON LEAD: <item>" then the next task), C-829 (lead HOTFIX first), C-871 compile checklist (grep every name/include
against its declaration, count #if/#endif, Shipping-only paths compile too), offline suite green before every X- touching tools.
A task is DONE only with an executing test, a tool run with counts, a lead-run result, or a measured artifact.

## S01–S10 Shipping-build hygiene (found today: BUILD-222 Shipping package failed on CVarCueMode)
| ID | Task | Acceptance |
|---|---|---|
| S01 | DONE — Source CVar guard audit, including macro-generated perf CVar path; one known CueMode use was already fixed by Lead | `Documentation/Boss/S01_S05_SHIPPING_GUARD_BATCH.md`; explicit scan 35 declarations / 0 Shipping uses |
| S02 | CODEX SOURCE REVIEW DONE — no further unguarded CVar use found; Lead's guarded CueMode fallback preserves default 0 | No Codex Source change; Lead Shipping package compile is still the acceptance gate |
| S03 | DONE — offline checker and 3 seeded contract cases | `Scripts/Tools/check_shipping_guards.py`, `Scripts/Tools/test_check_shipping_guards.py`; normal + `-I` tests 3/3 |
| S04 | DONE — editor/dev-automation runtime symbol audit; guarded editor API sites and automation test seams documented | `Documentation/Boss/S01_S05_SHIPPING_GUARD_BATCH.md`; no Source change required |
| S05 | DONE — packaged CVar/default behavior and player effect inventory; corrected unsupported assumption for Legend/Build | `Documentation/Boss/S01_S05_SHIPPING_GUARD_BATCH.md`; no behavior change |
| S06 | DONE — Lead closed the real cook census at 3/3 roots present; 78/156 uncooked `/Game` references are editor-only skeleton references. Comparator now has a tested folder-scoped allowlist. | `Documentation/Boss/S06_S10_SHIPPING_PACKAGE_GATES.md`, `Documentation/Boss/H2_G044_CONTENT_COOK_CENSUS_EXPECTED.md`; C-878/X-1256 |
| S07 | PREPARED — Shipping smoke expected sheet, including startup/debug criteria and limits | `Documentation/Boss/S06_S10_SHIPPING_PACKAGE_GATES.md`; LEAD-RUN |
| S08 | PREPARED — one-run Development selected-route smoke sheet, no performance claim | `Documentation/Boss/S06_S10_SHIPPING_PACKAGE_GATES.md`; LEAD-RUN |
| S09 | DONE — KI-185 records BUILD-222 failure, guard audit, and pending compile/smoke/cook gates | `Documentation/KNOWN_ISSUES.md`; cites C-877 |
| S10 | DONE — batch report posted as X-1254 | `Documentation/Boss/S06_S10_SHIPPING_PACKAGE_GATES.md` |

## S11–S20 Reference study (Track D, real measurements only)
| ID | Task | Acceptance |
|---|---|---|
| S11 | INCONCLUSIVE — surveyed combat footage for priority 7 Bloodflame grab; no distinct grab/skewer confidently identified, so no timing fabricated and ledger remains null | `Documentation/Boss/S11_S14_D3_FRAME_RESTORATION.md`; lead closed D3 at 5/10 measured |
| S12 | DONE — restored six missing canonical PNGs for D3 priority 8 from registered 59.9401 fps WebM | hashes + source times + contact sheet in `Docs/BossCombatReview/Execution/Claude/D3/evidence/`; ledger values unchanged |
| S13 | DONE — restored six missing canonical PNGs for D3 priority 9 | same |
| S14 | DONE — restored six missing canonical PNGs for D3 priority 10 | same |
| S15 | DONE — priorities 2–5 evidence-first reviewed; all remain unmeasured/withdrawn because the available footage did not establish the required attack identities and boundaries | `Documentation/Boss/S15_D3_CLIP_AUDIT.md`; ledger null timing/frame fields retained with withdrawal notes |
| S16 | DONE — sync-only run over the authoritative D3 ledger; 10 rows, 5 measured, 5 withdrawn/null, no incomplete measured rows; audit found only P1/P6's 12 canonical PNG references absent | `Documentation/Boss/S16_S18_D3_LEDGER_AND_CARD_COMPARISON.md` |
| S17 | DONE — comparison table covers only the five measured rows and records confidence; no matching authored Ember Warden MoveCard timing specs are available, so numerical deltas are unavailable | same; do not substitute attack-tracker defaults for MoveCard data |
| S18 | DONE — no tuning proposal is evidence-supported until matching MoveCard timings exist; review cites the measured frame IDs and records the exact missing source | same |
| S19 | DONE — clarified D5 scope and added links to its generated manifest, expected procedure, MoveCard schema, and the separate S16–S18 timing comparison; all 4 relative links resolve | `Documentation/Boss/D5_G044_LEGACY_DEFAULT_AUDIT.md` |
| S20 | DONE — batch receipt posted as X-1257 | `Documentation/Boss/S16_S18_D3_LEDGER_AND_CARD_COMPARISON.md` |

## S21–S30 Data route maturity (A7-B preparation, no legacy removal)
| ID | Task | Acceptance |
|---|---|---|
| S21 | DONE — receipt parser adds typed exact observables for explicitly labeled health/posture/damage values in check messages across all registered drivers; documented historical coverage across 31 drivers and fixture tests | `Documentation/Boss/S21_GAMEPLAY_VALUE_OBSERVABLES.md`; focused tests 17/17 (including registration coverage) |
| S22 | DONE — regenerated all 31 available `_d5`/`_t1` arm receipts from existing raw logs in a temp directory and re-ran parity comparison: 31 PASS, 0 FAIL, 0 INCONCLUSIVE; 62 typed gameplay observables per arm matched | `Documentation/Boss/S21_GAMEPLAY_VALUE_OBSERVABLES.md` |
| S23 | DONE — one-command 31-pair runner with default dry list, fresh A4/A5 arm runners, failure-continuing summary table, and explicit `-Execute` gate | `Scripts/RunA5ParityNightly.ps1`, `Documentation/Boss/S23_A5_PARITY_NIGHTLY_RUNNER.md`; dry list 31 commands; parser clean; focused tests 17/17 |
| S24 | DONE — comparator emits a full G044-shaped manifest from source-cited legacy defaults; verifies all boss leaves and refuses overwrite | unique temp dry-run: 424 fields, 214 MATCH, 0 MISMATCH, 210 player NOT-COMPARABLE; `Documentation/Boss/S24_S25_LEGACY_BASELINE_AUTHORING.md` |
| S25 | DONE — exact-field intentional tuning allowlist; stale/unknown entries refused, unlisted mismatch remains nonzero | comparator fixture suite 6/6; `Scripts/Tools/compare_manifest_to_legacy_defaults.py` |
| S26 | DONE — JSON schema and runtime validator require exact field/value/reason/owner-approval records; stale, duplicate, incomplete or value-drifted approvals refuse | comparator focused suite 8/8; `Scripts/Tools/intentional_tuning.schema.json` |
| S27 | DONE LOCALLY — opt-in repeated death/respawn x3 pair runs four contexts × three cycles in legacy and selected-data arms; LEAD-RUN still required | driver fixture 1/1; Python compile + PowerShell parse pass; `Scripts/RunA5DeathResetX3.ps1`; no Unreal/PIE claim |
| S28 | DONE — source-backed tick-state read inventory beyond tracker, explicit dependencies and presentation-only reads distinguished | `Documentation/Boss/S27_S29_RESPAWN_AND_TICK_ORDER_AUDIT.md` |
| S29 | DONE — test-first flagged proposals for dynamic Encounter/Phases, clip-swap/death and cosmetic track ordering; no unsupported tick edge added | proposal table in `Documentation/Boss/S27_S29_RESPAWN_AND_TICK_ORDER_AUDIT.md` |
| S30 | DONE — batch handoff posted | X-1259 |

## S31–S40 Documentation and handover
| ID | Task | Acceptance |
|---|---|---|
| S31 | DONE — evidence-backed milestone dashboard added to PROJECT_STATE and TASKS; A5 31/31, BUILD-222 463/463, D5 214/0/210, D3 5 measured + 5 withdrawn, and A7 gates match TEST_PLAN | percentages scoped to named evidence; no overall completion claim |
| S32 | DONE — BUILD-218..222 and 31-pair A5 evidence index added to `Documentation/TEST_PLAN.md` | all five evidence-directory links resolve |
| S33 | DONE — one-line index added for every Claude message C-833 through C-877 in `Documentation/DECISIONS.md` | 45 entries |
| S34 | DONE — closed KI-184 against BUILD-221/C-864/C-865 test and paired evidence; KI-185 remains closed with C-878 evidence | closed rows cite BUILD/C ids |
| S35 | DONE — Antigravity evidence handover maps A5 parity, D1, D5, T1 and G2 with source paths and warns against guessing a canonical ledger mapping | `Documentation/Boss/S31_S35_ANTIGRAVITY_LEDGER_HANDOVER.md` |
| S36 | DONE — pair execution, receipt generation/comparison, report interpretation, and D6b/c/d/O4 WARN rules documented; added MakeBenchKit local-dependency regression test (2/2; full offline suite 185 passed, 1 skipped) | `Documentation/Boss/S36_A5_PARITY_OPERATOR_RUNBOOK.md`; `Scripts/Tools/test_make_bench_kit_dependencies.py` |
| S37 | DONE — new encounter authoring sequence, D5 scope, phase/default/approval limits documented | `Documentation/Boss/S37_NEW_ENCOUNTER_DESIGNER_GUIDE.md` |
| S38 | DONE — G2 select/explicit-clear command, refusal tokens, limits, and unresolved owner evidence documented | `Documentation/Boss/S38_ENCOUNTER_SELECTION_OPERATOR_GUIDE.md` |
| S39 | DONE — route/selection/glossary terms defined with project references | `Documentation/Boss/S39_ROUTE_SELECTION_GLOSSARY.md` |
| S40 | DONE — handoff posted as X-1261; accepted by C-886 | `Documentation/TEAM_MAILBOX.md` |

## S41–S50 Close-out
| ID | Task | Acceptance |
|---|---|---|
| S41 | DONE — Round 4 owner report template separates six run rows and leaves all measured fields blank until owner evidence arrives | `Documentation/Boss/S41_ROUND4_OWNER_REPORT_TEMPLATE.md` |
| S42 | DONE — play-test intake records feel, responsiveness, readability, and reproducible examples | `Documentation/Boss/S42_PLAYTEST_FEEDBACK_TEMPLATE.md` |
| S43 | DONE — A7-B residual risks and evidence-based exit rules recorded | `Documentation/Boss/S43_A7_RESIDUAL_RISK_REGISTER.md` |
| S44 | DONE — C-791 audit found and fixed early profile save; remaining reviewed setup scripts comply with enum/path/map/pre-save lessons | `Documentation/Boss/S44_UE_PYTHON_LESSON_REVIEW.md`; no Editor run |
| S45 | DONE — Queue T drafted with 50 unique, bounded IDs in ten five-task batches | `Documentation/Boss/QUEUE_T.md`; handoff X-1262 |
| S46 | Final consistency pass of the docs touched in S31–S39 | no contradictions |
| S47 | Offline suite timing: keep discovery under 10 s | measured |
| S48 | Archive superseded Boss docs into Documentation/Archive (move, no delete) with an index | index |
| S49 | Mailbox digest of C-833..C-877 decisions for the owner | half page |
| S50 | Queue S closed; continue at T001 | X- line |

