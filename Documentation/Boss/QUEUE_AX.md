# Queue AX — open KI offline source audits

**Authority:** Claude C-1147 says continue with an open-KI offline batch. Batch 1 audited KI-154; Batch 2 audits KI-155 proof-profile candidate budget. C-1150 separately authorizes a Source-test for the data-route attach witness only after Lead's BUILD-274 result; the attach source and test remain untouched pending that result. No code fix is proposed in this offline audit. No Unreal, build, PIE, commit or push.

## Batch 1 — audit four old-move Parried results

| Task | Work | Acceptance |
|---|---|---|
| AX-C01 | Trace javelin resolver outcome through projectile completion and owner counter. | Exact source path and counter accessor cited; runtime status kept separate. |
| AX-C02 | Trace low-sweep resolver outcome, per-sweep suppression and counter. | Exact source path shows one count and no repeated contact after Parried. |
| AX-C03 | Trace shockwave outcome, one-resolution guard and counter. | Exact source path shows Parried increments its own counter without counting a hit. |
| AX-C04 | Trace HealPunish's role in javelin callback/counter; distinguish it from the projectile's hit resolver. | No separate HealPunish contact path is invented; callback and accessor are cited. |
| AX-C05 | Check test/evidence coverage and identify any historical TEST_PLAN wording that predates J7. | Generic outcome tests are not passed off as old-move contact tests; the report marks the historical note as pre-J7; PIE gate stays open. |

## Findings

- **AX-C01:** `RPGBossJavelin.cpp:137-158` calls the shared damage resolver and routes `Parried` to `Finish(Parried)`; `Finish` reports exactly once to its `URPGBossHealPunish` owner (`:83-95`). `HealPunish.cpp:197-205` increments the parried-projectile counter; getter `RPGBossHealPunish.h:126-136`.
- **AX-C02:** `RPGBossLowSweep.cpp:77-83,136-154` refuses subsequent samples after the first parry, resolves the contact, then sets `bParriedCounted` and increments `ParriedCount`; getter `RPGBossLowSweep.h:75-80`.
- **AX-C03:** `RPGBossShockwave.cpp:112-139` marks the player outcome resolved before the resolver branch; `Parried` increments `ParriedCount`, not `HitCount`; getter `RPGBossShockwave.h:80-89`.
- **AX-C04:** HealPunish owns projectile lifecycle/counters, while the javelin owns overlap/resolution; there is no distinct HealPunish hit branch. The callback is `ReportJavelin` (`RPGBossHealPunish.h:146-147`).
- **AX-C05:** `RPGAutomationTests.cpp:174-192` covers the pure resolver decision and parry-over-guard priority. The searched native tests do not invoke the three component/projectile result branches or assert these counters. Adapter tests cover config/lifecycle, not contact outcomes. C-683's compile confirmation and source audit do not establish live contact behavior. `TEST_PLAN.md` line 936 describes pre-J7 behavior; I left the historical row untouched and clarify the superseding source state here.

## Validation and limits

Read-only source/document review only; no tests were added or run, and no source code changed. KI-154 remains open until Lead PIE contacts exercise each relevant old move and verify counters. Report: `Documentation/Boss/AX_C01_C05_KI154_OLD_MOVE_PARRY_AUDIT.md`.

## Batch 2 — KI-155 proof-profile candidate-budget validation

| Task | Work | Acceptance |
|---|---|---|
| AX-C06 | Inspect the pure `PhasePoolCannotStarve` rule and its cardinality/zero-cooldown assumptions. | Rule and edge behavior are cited; score penalties are not described as eligibility filters. |
| AX-C07 | Trace where `ResolveProfile` applies cooldown-starvation validation. | Phase membership and the exact branch gate are cited. |
| AX-C08 | Compare profile-integration tests with pure helper tests. | Coverage gaps are called out without passing helper tests off as profile validation. |
| AX-C09 | Inspect the parry-recovery gating profile generator's candidate count/cooldowns/readback. | Proof setup is distinguished from a general authoring-time validator. |
| AX-C10 | Reconcile KI-155's open status and the runtime/proof boundary. | Report identifies the single-pool validation gap as a source finding and does not claim runtime failure or authorize a fix. |

Findings and source line references: `Documentation/Boss/AX_C06_C10_KI155_PROFILE_BUDGET_AUDIT.md`. No code/test/runtime changes; implementation remains a Lead/owner disposition decision.

## Batch 3 — open tooling and release KI source audit

| Task | Work | Acceptance |
|---|---|---|
| AX-C11 | Trace evidence-pack output-directory creation vs destination-collision validation. | Failure side effects and ordering are cited; no cleanup/fix is run. |
| AX-C12 | Trace source-manifest behavior for roots without a `Source` directory. | Empty-success path is confirmed from source, without generating a manifest. |
| AX-C13 | Inspect malformed-JSON handling in KI-166's listed CLIs. | Uncaught parse paths and available diagnostics are accurately scoped. |
| AX-C14 | Trace absolute-path and raw-row output in KI-167's listed reports. | Concrete disclosure paths are listed; no logs are run or shared. |
| AX-C15 | Re-check KI-168 console control definitions and guard locations. | Source visibility is distinguished from packaged binary proof. |

Findings: `Documentation/Boss/AX_C11_C15_TOOLING_AND_SHIPPING_SOURCE_AUDIT.md`. Source-only; no fixes, tests, logs, packaged binaries, or editor runs.

## Batch 4 — KI-169–173 source and gate audit

| Task | Work | Acceptance |
|---|---|---|
| AX-C16 | Recheck KI-169's suspected editor-property spelling without loading/saving the asset. | Treat the property name as unverified pending reflection/readback. |
| AX-C17 | Inspect KI-170's script source and preserve its parse-check-before-execution gate. | No script execution or asset authoring. |
| AX-C18 | Inspect KI-171's indentation issue and preserve its parse-check/Editor gates. | No script execution or asset authoring. |
| AX-C19 | Trace KI-172 pending native hit queue, reset path, and reset-counter call sites. | State whether generation is stored/queue cleared, but do not claim reproduction or change production code. |
| AX-C20 | Trace KI-173 next-tick riposte callback state guard and reset cleanup. | Identify the request/generation gap while preserving the required ordering-test and intent gate. |

Findings: `Documentation/Boss/AX_C16_C20_KI169_C173_GATE_AUDIT.md`. No script execution, asset operation, tests, or production change.

## Batch 5 — KI-172/173 generation-guarded test-first proposal

| Task | Work | Acceptance |
|---|---|---|
| AX-C21 | Reuse the participant-generation identity pattern from `RPGPackParryContact` as the proposal basis. | Encounter generation and per-operation callback identity are distinguished. |
| AX-C22 | Specify KI-172 reset-before-next-tick native regression ordering and observable state. | Old-generation hit must have zero side effects; same-generation and fresh-generation controls are required. |
| AX-C23 | Propose the narrow KI-172 pending-record generation guard and reset cleanup only after the test fails. | No production implementation is made; timer scheduling and hit merge semantics stay covered. |
| AX-C24 | Specify KI-173 abort/reset/rearm/new-riposte callback ordering and observables. | Stale callback must not start clips or clean up/mutate a newer request. |
| AX-C25 | Propose KI-173 request serial plus encounter generation guard and reconcile the reproduction gate. | Test-first sequence and acceptance criteria are documented; KI statuses remain unchanged. |

Proposal: `Documentation/Boss/AX_C21_C25_KI172_173_GENERATION_FIX_PROPOSAL.md`. Source-only design; no implementation, tests or runtime claim.

## Batch 6 — KI-179–183 execution and gate recheck

| Task | Work | Acceptance |
|---|---|---|
| AX-C26 | Reconcile watchdog execution code and existing harness limitations. | Tick-dependent runtime behavior is not presented as automation coverage. |
| AX-C27 | Recheck the reactive-dodge maximum-counter fix and native test execution evidence. | Rule arithmetic, boundary assertion, and gameplay reachability are distinguished. |
| AX-C28 | Audit subnormal-score handling and current zero-score tie behavior. | Tested selector semantics are reported; no epsilon or product-policy assumption is introduced. |
| AX-C29 | Reconcile KI-182's single-reset closure against the optional repeated-reset evidence. | The unrun x3 case and release-policy separation remain explicit. |
| AX-C30 | Reconcile the Shipping selection API, its source guards, caller search, and proof gate. | API allowance is not presented as an exercised Blueprint caller or package proof. |

Findings: `Documentation/Boss/AX_C26_C30_KI179_C183_EXECUTION_AND_GATE_RECHECK.md`. No production changes, package inspection, or new runtime run.

## Batch 7 — runtime-coverage and stale-status reconciliation

| Task | Work | Acceptance |
|---|---|---|
| AX-C31 | Compare the KI-179 pure watchdog-rule test with runtime TickComponent behavior and coverage classification. | Pure math coverage is not presented as an observed watchdog lifecycle. |
| AX-C32 | Identify a bounded KI-181 all-zero score/tie-band regression case. | Test intent is proposed without changing selection semantics or code. |
| AX-C33 | Reconcile KI-182 S27 x3 driver readiness with the actual Lead-run receipt status. | Expected cycles/checks are documented separately from unrun runtime results. |
| AX-C34 | Separate KI-183 transient native setter tests from actual Blueprint callers and Shipping/package proof. | Native test use is not passed off as a real Shipping caller. |
| AX-C35 | Reconcile KI-188's open label with the accepted root-anchored ignore fix and permanent-loss record. | Active recurrence issue is closed while unrecovered-content impact remains explicit. |

Findings: `Documentation/Boss/AX_C31_C35_RUNTIME_COVERAGE_AND_STALE_STATUS.md`. No runtime/build/package/assets.

## Batch 8 — KI-189–193 evidence reconciliation

| Task | Work | Acceptance |
|---|---|---|
| AX-C36 | Recheck KI-189's optional Tier 2 soft-load timing and default-off path against current source. | Synchronous first-use possibility is separated from default-path loading and measured hitch evidence. |
| AX-C37 | Reconcile KI-190's owner policy question with Freeze wording, current rows, and retained Strength evidence. | No choice, owner response, or option-dependent tuning is inferred. |
| AX-C38 | Reconcile KI-191 lifecycle, visibility, failed paired captures, owner showcase, first-use, and package gates. | Showcase delivery and static hypotheses do not become a visual verdict, cause, or owner disposition. |
| AX-C39 | Recheck KI-192 route identity and bounded PIE/package status against C-1099/C-1100. | Only a same-run activation witness identifies true legacy; package remains separate. |
| AX-C40 | Reconcile KI-193 source defaults, C-1042 default-wired hit evidence, and package requirements. | Source/PIE are not promoted to cook or packaged-runtime proof. |

Findings: `Documentation/Boss/AX_C36_C40_KI189_193_EVIDENCE_RECONCILIATION.md`. Offline source/document review only; no tests or engine operations.

## Batch 9 — KI-194–198 evidence reconciliation

| Task | Work | Acceptance |
|---|---|---|
| AX-C41 | Reconcile KI-194's C-978 post-air ground restoration result with lifecycle and post-wiring boundaries. | Tested route sequence is separated from death/reset/rebind and default-wiring proof. |
| AX-C42 | Recheck KI-195's timeout helper, remaining direct subprocess calls, and reported test scope. | Every retained direct call has an explicit bound; targeted tests are not described as a full-suite run. |
| AX-C43 | Reconcile KI-196's C-1076 moving-dodge evidence with C-1099 route provenance and C-1104 scope. | DATA-default tested PIE cases remain separate from legacy parity and packaged proof. |
| AX-C44 | Compare KI-197's current Package/bench-kit source defaults and Lead gate with TEST_PLAN wording. | Identify stale source-default statements; preserve the TEST_PLAN edit authorization gate. |
| AX-C45 | Reconcile KI-198's accepted C-1047 result with older unchecked TEST_PLAN rows. | DATA-default PIE proof and package gate are separated; stale rows are reported without editing TEST_PLAN. |

Findings: `Documentation/Boss/AX_C41_C45_KI194_198_EVIDENCE_RECONCILIATION.md`. Offline source/document review only; TEST_PLAN left unchanged under its authorization gate.
