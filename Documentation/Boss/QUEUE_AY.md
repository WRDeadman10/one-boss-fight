# Queue AY — Native red/green closure for eligible open issues

Authority: Claude C-1162. Fifty tasks in ten five-task batches. Prioritize open issues that can be reproduced, fixed, and proven with native automation. Use the C-1155 engine lock rules for every build/test launch; obtain the Lead acceptance build after each Source batch. Review is asynchronous: continue only with work that remains within these gates, and hotfix rejected items on the next cycle. Do not run PIE, cook, package, change assets, or alter owner-choice/package-gated features. For each proposed fix, preserve genuine pre-fix red evidence; if the failure is nondeterministic or the expected behavior needs an owner decision, stop that item and report it without shipping a guard.

## Batch 1 — five highest-impact candidate regressions

These are ranked among the open KI candidates that appear testable in native code; the first task in each lane must establish a deterministic, production-relevant red before any fix.

| ID | Candidate | Task and acceptance |
|---|---|---|
| AY-C01 | KI-175 — parry state across respawn/repossess | Build a same-component reuse lifecycle regression around `RPGPlayerParry::FState`; prove the old state changes a subsequent pawn-life window/cooldown result. If project lifecycle replaces the component or the expected behavior is not reproducible, retain that finding and do not add a speculative reset. |
| AY-C02 | KI-176 — parry refund when maximum stamina cannot be read | Add a pure/native regression for the actual missing-maximum fallback showing whether the bounded refund can exceed the pre-payment observed stamina; retain a pre-fix red before selecting the smallest safe fallback. |
| AY-C03 | KI-177 — parry recovery crossing a stance break | Extend the accepted transient-world fixture through the later recovery consumer. First report observed pending-state and subsequent-move effects; do not encode a failure or change recovery semantics until the expected boundary is confirmed. |
| AY-C04 | KI-154 — old-move parry result handling | Add native component-level regressions for Javelin, LowSweep, and Shockwave `Parried` branches, including single-consumption/counter outcomes. A test gap alone does not authorize changing already-correct behavior. |
| AY-C05 | KI-179 — executor watchdog lifecycle | Extend a transient-world fixture to advance the actual watchdog timer/tick and assert bounded completion/cleanup. Preserve the live proof separately; change production code only if the deterministic native regression exposes a defect. |

The ranked list is provisional to the available issue evidence. KI-180 already has a successful `MaximumHitBoundary` result in Lead BUILD-276 and is closed by the evidence note in this queue; it is not counted among the five candidates.

## Batch 2 — close evidence gaps and reconcile candidate status (C-1165 replan)

| ID | Task | Acceptance |
|---|---|---|
| AY-C06 | Record KI-175 lifecycle evidence and KI-176 actual-path fixture limitation. | No lifecycle or missing-maximum behavior is claimed without its required live/attribute reproduction. |
| AY-C07 | Reconcile KI-177 abort/rearm fixture observations with C-707's non-posture-breaking timing evidence. | Keep the later recovery consumer and intended composition unresolved. |
| AY-C08 | Reconcile KI-154 source branches and prior AX audit with available native tests. | Preserve shared `NotifyParried` dedupe; no live contact outcome or production defect is claimed. |
| AY-C09 | Record the KI-179 transient fixture's `NoSlotContribution` stop before watchdog timing. | Classify it as a fixture failure and specify a slot-contributing/ticking fixture prerequisite. |
| AY-C10 | Verify KI-180 `MaximumHitBoundary` in Lead BUILD-276 and update its issue status. | Cite the exact result and manifest-hash argument; do not claim gameplay reachability. |

## Batch 3 — KI-175 lifecycle guard, only if C01 is genuinely red

| ID | Task | Acceptance |
|---|---|---|
| AY-C11 | Implement the smallest reset/rebind state invalidation supported by the reproduced lifecycle. | No broad reset or new owner behavior is inferred. |
| AY-C12 | Add same-component stale-state red/green regression. | Fails before the guard and passes after it. |
| AY-C13 | Add fresh-component and ordinary cooldown positive controls. | Existing parry timing behavior is preserved. |
| AY-C14 | Check teardown/rebind ownership and duplicate reset delivery. | State is cleared once and no input/tag cleanup is lost. |
| AY-C15 | Build and run focused KI-175 automation under the lock protocol. | Raw red and green evidence retained; Lead acceptance remains separate. |

## Batch 4 — KI-176 bounded refund, only if C02 is genuinely red

| ID | Task | Acceptance |
|---|---|---|
| AY-C16 | Add an explicit pure rule for the unreadable-maximum fallback. | Invalid/non-finite inputs fail closed; refund cannot exceed the observed pre-payment bound. |
| AY-C17 | Route the unavailable-maximum branch through the tested rule. | Readable maximum continues to use the actual cap. |
| AY-C18 | Add missing-max red/green and readable-max controls. | Retain exact baseline red and fixed green. |
| AY-C19 | Cover retries and rejected writes without duplicate refund. | Existing bounded retry/clear semantics remain intact. |
| AY-C20 | Build and run focused stamina/parry automation. | Report exact cases and preserve logs; no PIE claim. |

## Batch 5 — KI-177 follow-through, only if expected behavior is clear

| ID | Task | Acceptance |
|---|---|---|
| AY-C21 | Decide from the fixture whether pending recovery reaches the next move. | Separate observed native state from the inferred Tick path. |
| AY-C22 | If and only if the observed next-move behavior violates the recorded recovery contract, add the red assertion. | No failure expectation is invented from stale fields alone. |
| AY-C23 | Implement the smallest abort/reset boundary guard after a genuine red. | Preserve intended parry recovery composition. |
| AY-C24 | Add abort/rearm and normal recovery controls. | Red/green and controls cover both paths. |
| AY-C25 | Build and run focused executor harness tests. | Retain evidence and identify any Lead-only remaining gate. |

## Batch 6 — KI-154 old-move parry result consumers

| ID | Task | Acceptance |
|---|---|---|
| AY-C26 | Add Javelin parry completion/counter regression. | One parry consumes the projectile once and increments only the parried counter. |
| AY-C27 | Add LowSweep parry duplicate-sample regression. | Later overlap samples do not add another result/counter. |
| AY-C28 | Add Shockwave parry single-resolution regression. | One resolved parry increments parried, not hit count. |
| AY-C29 | Verify HealPunish receives only the Javelin's terminal callback. | No invented HealPunish contact branch or duplicate reward. |
| AY-C30 | Run focused component automation and report remaining PIE-only contact proof. | Native correctness does not close live old-move contact evidence. |

## Batch 7 — KI-179 watchdog lifecycle coverage

| ID | Task | Acceptance |
|---|---|---|
| AY-C31 | Identify the exact watchdog-owned timer and executor terminal state. | Source map names scheduling, expiry, abort, and cleanup sites. |
| AY-C32 | Add a transient-world fixture that advances the real timer/tick. | Fixture proves timeout, not merely the pure timeout formula. |
| AY-C33 | Add normal completion and explicit abort controls. | Timeout cannot fire after cleanup or double-complete. |
| AY-C34 | Run the new harness against the unchanged production path first. | Any failure must reproduce the claimed watchdog defect, not fixture setup. |
| AY-C35 | Fix only a deterministic watchdog defect, otherwise close as coverage-only. | Keep prior live timeout evidence and native coverage distinct. |

## Batch 8 — KI-180 evidence and remaining robustness candidates

| ID | Task | Acceptance |
|---|---|---|
| AY-C36 | Verify `MaximumHitBoundary` result in Lead BUILD-276. | Exact test completion is cited; full-suite pass is not mislabeled as red/green evidence. |
| AY-C37 | Update KI-180 to native-test verified if BUILD-276 log confirms success. | Reachability remains unclaimed. |
| AY-C38 | Re-screen KI-181 score-underflow boundary for a deterministic native failure. | Do not alter score policy or selection semantics without a stated contract. |
| AY-C39 | Re-screen KI-155 profile starvation as proof-profile scope. | No product defect is inferred from invalid proof setup. |
| AY-C40 | Record excluded candidates requiring owner intent, PIE, package, or asset evidence. | No gated item enters AY implementation work. |

## Batch 9 — conditional hotfix/review follow-through

| ID | Task | Acceptance |
|---|---|---|
| AY-C41 | Read Claude/Lead feedback for the latest five-task batch. | Rejections and accepted items are mapped by task ID. |
| AY-C42 | Hotfix each rejected source item immediately. | Preserve accepted behavior and produce a targeted regression. |
| AY-C43 | Re-run the affected focused automation after a hotfix. | Exact exit/result evidence retained. |
| AY-C44 | Request or perform the Lead acceptance build per C-1162. | Build identity and suite result are explicit; engine lock is held. |
| AY-C45 | Continue next unblocked task without waiting for review. | No work crosses owner/PIE/package gates. |

## Batch 10 — final eligible-issue census and handoff

| ID | Task | Acceptance |
|---|---|---|
| AY-C46 | Re-scan KNOWN_ISSUES for eligible native red/green work. | Closed, intent-gated, package-gated, and PIE-only items remain separate. |
| AY-C47 | Reconcile fixed/native-verified statuses to accepted test receipts. | No status upgrade from source inspection alone. |
| AY-C48 | Reconcile TASKS and TEST_PLAN to the batch receipts. | Preserve Lead-owned rows and dated history. |
| AY-C49 | Validate the ten batches contain 50 unique ordered AY IDs. | Record the actual validation result. |
| AY-C50 | Write the closeout handoff and next dependency. | List fixed items, limits, test evidence, Lead review state, and no commit/push. |

## Batch 1 status

Claude accepted the queue and Batch 1 in C-1163. Lead's Mid01 dodge PIE was inconclusive and the lock was released in C-1164; its optional range-band follow-up remains deferred until after AY Batch 1. KI-180's existing boundary test passed in Lead BUILD-276 (`B_C1161_GENGUARDS/suite.log`, `MaximumHitBoundary`); a status update is included in AY-C37. The five Batch 1 candidates were statically preflighted; regression evidence and blockers are in `AY_C01_C05_NATIVE_PREFLIGHT.md`. No package/runtime/owner-choice work is part of this queue.

AY-C01–C05 native preflight is recorded in `AY_C01_C05_NATIVE_PREFLIGHT.md`. No product defect was proven; Claude accepted this outcome in C-1165 and identified the local 493/494 as an invocation/environment issue fixed by the required `-DD27jManifestHash` argument in the Lead runner. The watchdog experiment stopped at `Framework.Playback.NoSlotContribution` before timing and was reverted. The five candidates now require the live or fixture evidence listed in `KNOWN_ISSUES.md`; no guard is authorized by source inspection alone. Batch 2 was replanned and completed as an evidence/status reconciliation in `AY_C06_C10_EVIDENCE_REPLAN.md`. Claude replaced AY-C11–C15 with Lead-PIE-backed driver tasks in C-1166; later queue slots await follow-up assignments.

## AY-C11–C15 status (C-1166 / C-1167)

Replacement batch: C11 Mid01 dodge band READY (`AY_C11_MID01_DODGE_RANGE.md`); C12 respawn probe hotfix READY after C-1171's setup-only 0/1 (`AY_C12_PARRY_RESPAWN_PROBE.md`); C14 owner Video 3 capture plan READY (`AY_C14_OWNER_VIDEO3_PREP.md`). C-1170 resolves C13 as N/A because `L_SevarogArena` lacks the F5 framework-boss PIE fixture needed for KI-177; the pack-only posture hook is not substituted. C15 batch receipt/contracts are ready in `AY_C11_C15_DRIVER_PREP.md`; Lead ordered C12 rerun then C14 video 3. Codex performed no PIE/engine operation for this follow-up.
