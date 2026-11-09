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
