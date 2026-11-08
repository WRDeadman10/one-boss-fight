# Queue AJ — C-998 override hotfix verification audit

Scope: source-level verification of the C-998 classification hotfix while Lead owns build/native execution and the two-route PIE rerun. No Unreal, build, PIE, asset, or package operation by Codex.

## Batch 1 — AJ-C01–AJ-C05

| ID | Task | Acceptance | Status |
|---|---|---|---|
| AJ-C01 | Audit temporary override lifetime and array restoration | Apply, playback, timeout, interruption, and EndPlay cleanup are source-mapped | Complete |
| AJ-C02 | Audit exact montage-to-kind classification timing | SwingTracker and OnHit consume the same active montage identity; deferred hit finalization retains the captured kind | Complete |
| AJ-C03 | Audit canonical AttackData normalization | Kind-to-data mapping and asset path agree with the existing pack hit-intake contract | Complete; object load still needs Lead runtime verification |
| AJ-C04 | Trace corrected kind/data through the attack row | AttackData, kind, table posture/health multiplier, and owner of health application are distinguished | Complete |
| AJ-C05 | Audit native coverage and refresh verification handoff | Tests and documentation match source; Lead-only build/PIE dependencies remain explicit | Complete |

## Batch 1 result

`AJ_C01_C05_OVERRIDE_HOTFIX_AUDIT.md` finds the hotfix's state and data flow internally consistent by source inspection. It also records the untested canonical-asset load and the absence of a component-level native lifecycle fixture. No tests/build/Editor/PIE operation was run by Codex. Lead's C-998 build/native run and two-route PIE check remain authoritative.

## Batch 2 — AJ-C06–AJ-C10 (C-1003 follow-through)

| ID | Task | Acceptance | Status |
|---|---|---|---|
| AJ-C06 | Manually review changed native test expressions against UE test overloads | C2665 cause/fix and remaining typed comparisons documented | Complete; corroborated by BUILD-249 |
| AJ-C07 | Trace pack-boss health damage versus project hit-record/table flow | Source boundary and Lead's -16/-22.4 observed comparison recorded | Complete |
| AJ-C08 | Reconcile notify AttackData rule to latest Lead direction | AirHeavy + GuardCounter strong; AirLight unset; saved readback pending | Complete as direction/status only; no asset edit |
| AJ-C09 | Refresh C-998/C-1003 status across gates, test plan and KI-193 | Classification closed by BUILD-249; health delta remains open | Complete |
| AJ-C10 | Record exact owner, follow-up acceptance, and evidence boundary | Antigravity asset edit and Lead readback/PIE stay explicit | Complete |

Batch evidence: `AJ_C06_C10_DAMAGE_OWNER_AND_TEST_OVERLOAD_AUDIT.md`. No asset, test, build, Editor, PIE, package, or commit operation by Codex.

## Batch 3 — AJ-C11–AJ-C15 (A-607 evidence review)

| ID | Task | Acceptance | Status |
|---|---|---|---|
| AJ-C11 | Verify the raw saved T3D proof at `Saved/C1003_t3d` | Correct notify subobject owns Strong AttackData on AirHeavy and GuardCounter | Complete |
| AJ-C12 | Verify AirLight remains unset and notify is still active | Serialized active trace exists; no AttackData override line | Complete |
| AJ-C13 | Cross-check the Lead asset readback against the five montage lengths | Saved-montage lengths/readback match C-1003 report; do not treat this as PIE | Complete |
| AJ-C14 | Refresh docs from assigned to asset-edit-complete state | Readback complete; damage rerun still open | Complete |
| AJ-C15 | Define final Lead runtime acceptance and evidence capture | Both-route control and ER damage deltas with raw logs required | Complete |

Batch report: `AJ_C11_C15_C1003_SAVED_ASSET_EVIDENCE_AUDIT.md`. Raw T3D supports the requested saved properties; this does not prove the live hit damage delta.

## Batch 4 — AJ-C16–AJ-C20 (C-1003 Queue AB target correction)

| ID | Task | Acceptance | Status |
|---|---|---|---|
| AJ-C16 | Check A-607's Queue AB retarget claim against the remaining task rows | A36–A50 reviewed for retired boss assets | Complete |
| AJ-C17 | Preserve historical completed tasks without treating retired assets as active targets | No repeat or Ember Warden acceptance claim attached to Greystone/Sevarog audits | Complete |
| AJ-C18 | Retarget the remaining arena LOD task to the active Ember Warden combat arena | Task names active target and evidence boundary | Complete |
| AJ-C19 | Remove unsupported “without hitching” acceptance language | Static property readback separated from measured runtime | Complete |
| AJ-C20 | Record the queue correction and next active lane | Report identifies C-1003/A-607 source and remaining boundaries | Complete |

Batch report: `AJ_C16_C20_QUEUE_AB_RETARGET_AUDIT.md`.

## Batch 5 — AJ-C21–AJ-C25 (C-1004 guard-counter live-hit probe)

| ID | Task | Acceptance | Status |
|---|---|---|---|
| AJ-C21 | Trace the source event that arms guard counter and its timing | Probe waits for the actual successful-guard log, not a montage/timing guess | Complete by source inspection |
| AJ-C22 | Author the Lead-run real-input PIE driver | L1 is held while Ember Warden AI swings; R2 is tapped immediately after confirmed guard contact | Complete locally; not run |
| AJ-C23 | Capture the guard-counter hit record and boss health | Probe reports hit kind, AttackData, record count, and before/after HP from the live intake | Complete locally; Lead PIE pending |
| AJ-C24 | Preserve route and owner-approval boundaries | Legacy/data selection is explicit; probe never assigns or saves montage properties | Complete locally |
| AJ-C25 | Document the Lead handoff and evidence limits | Run instructions, paired raw log requirement, and no-contact failure semantics are recorded | Complete locally |

Batch report: `AJ_C21_C25_GUARD_COUNTER_PROBE.md`. The driver is authored but has not been executed; Lead's live hit is still pending, as is owner clip approval and saved-field assignment.

## Batch 6 — AJ-C26–AJ-C30 (guard-contact hook reachability)

| ID | Task | Acceptance | Status |
|---|---|---|---|
| AJ-C26 | Census all successful-guard notification call sites | Exact call sites and owning source path are recorded | Complete |
| AJ-C27 | Identify the C++ host of the framework executor | Do not assume the arena Blueprint uses the framework executor without runtime/readback proof | Complete by source inspection |
| AJ-C28 | Reconcile L1 mapping evidence with the probe input path | Preserve the input-dump evidence and verify active ER context in the run | Complete |
| AJ-C29 | Define how missing hook evidence is interpreted | No source log/component is an evidence gap, not a demonstrated counter defect | Complete |
| AJ-C30 | Refresh probe and Lead handoff with route-reachability limits | Runtime output logs executor presence and keeps both route results pending | Complete locally |

Batch report: `AJ_C26_C30_GUARD_HOOK_REACHABILITY_AUDIT.md`. Source confirms the successful-guard notifier is called only by the framework move executor; the arena Blueprint's component/attack-route reachability is not established by available source. Continue the next static batch without waiting for Lead.

## Batch 7 — AJ-C31–AJ-C35 (probe evidence and cleanup audit)

| ID | Task | Acceptance | Status |
|---|---|---|---|
| AJ-C31 | Match probe confirmation strings to the source log text | Both guard and counter acceptance triggers use exact current C++ strings | Complete |
| AJ-C32 | Verify hit-record telemetry is reflected to Unreal Python | `GetRecordLines` and hit-count calls are source-exposed and read-only | Complete by source inspection |
| AJ-C33 | Audit key release and PIE cleanup paths | Held L1/R2/combat keys are released on normal, timeout, and error exits | Complete by code review |
| AJ-C34 | Audit active-log rotation/new-file handling | New logs are tailed from their beginning; fix any missed-event case | Complete; offset fallback fixed |
| AJ-C35 | Refresh the acceptance record and current status | No runtime claim; revised log-tail limitation and validation are documented | Complete locally |

Batch report: `AJ_C31_C35_PROBE_EVIDENCE_AND_CLEANUP_AUDIT.md`. A log created or rotated after PIE startup previously defaulted to EOF and could hide the guard diagnostic; the probe now tails a previously unseen log from byte zero. Continue AJ-C36–C40 without waiting for Lead.

## Batch 8 — AJ-C36–AJ-C40 (owner/runtime acceptance boundary)

| ID | Task | Acceptance | Status |
|---|---|---|---|
| AJ-C36 | Compare the probe setup with the owner hand-test prerequisites | Health/stamina, facing, actual blocked contact, and player response requirements remain explicit | Complete by documentation review |
| AJ-C37 | Reconcile owner approval, saved montage assignment, and Lead execution gates | No gate is treated as implied by asset delivery or script readiness | Complete |
| AJ-C38 | Verify GuardCounter notify AttackData status from available proof | Saved StrongMeleeAttackData is distinguished from a live hit record/HP result | Complete |
| AJ-C39 | Check that the expected montage and fallback branches are stated correctly | Empty/unavailable montage remains pack strong fallback; assigned montage is owner-gated | Complete by source/doc review |
| AJ-C40 | Publish one acceptance boundary for the Lead and owner | Both-route runtime, source hook reachability, clip approval, and saved assignment remain separately tracked | Complete locally |

Batch report: `AJ_C36_C40_OWNER_AND_RUNTIME_ACCEPTANCE_AUDIT.md`. The hand-test sheet remains authoritative for owner-visible health/stamina/animation observations; the scripted source diagnostics supplement those checks and do not replace owner approval.

## Batch 9 — AJ-C41–AJ-C45 (C-1004 air-hit status reconciliation)

| ID | Task | Acceptance | Status |
|---|---|---|---|
| AJ-C41 | Scan current C-998/C-1003 status claims for C-1004 drift | Stale -16/pending rerun claims are distinguished from historical snapshots | Complete |
| AJ-C42 | Reconcile AA-A08 and GATE-07 against C-1004 | Both-route -16/-22.4 results and owner-review boundary agree | Complete |
| AJ-C43 | Update KI-193 to its remaining gates | Air-hit runtime is closed; owner review/assignment and cook/package remain open | Complete |
| AJ-C44 | Reconcile controls spec and TEST_PLAN | Current air result and guard-counter separate gate are explicit | Complete |
| AJ-C45 | Publish the status correction and supporting source receipt | C-1004/A-607 are cited; no new run is claimed | Complete locally |

Batch report: `AJ_C41_C45_C1004_STATUS_RECONCILIATION.md`. No runtime action was performed; the changes reconcile documents to Claude's C-1004 PIE report.

## Batch 10 — AJ-C46–AJ-C50 (C-1006 rejected-driver hotfix)

| ID | Task | Acceptance | Status |
|---|---|---|---|
| AJ-C46 | Fix the reported indentation/syntax failure and parse the driver | `ast.parse` passes on the actual driver | Complete; syntax-only check |
| AJ-C47 | Replace keyboard R setup with the known combat-entry tag path | Uses `Ability.EnterCombat`, 900 cm placement, and per-tick refill | Complete by code review |
| AJ-C48 | Verify L1/R2 evidence and input cleanup remain intact | Only real gamepad inputs are sent; held inputs are released in cleanup | Complete by code review |
| AJ-C49 | Add the requested opt-in GuardCounter montage runtime assignment | `ER_GC_ASSIGN=1` assigns transiently in PIE; no asset save path | Complete by code review |
| AJ-C50 | Reconcile C-1006/C-1007 status and prepare Lead rerun handoff | Both routes remain unrun by Codex; no-contact is an X-1415 reachability finding, not a pass | Complete locally |

Batch report: `AJ_C46_C50_C1006_DRIVER_HOTFIX.md`. X-1418 handed the corrected driver to Claude for both-route Lead rerun. Codex performed the explicit AST parse and scoped whitespace check only; no Unreal/PIE/build/test/asset operation.
