# Selector/start snapshot test-gap audit (Queue D D2, 2026-11-03)

## Scope and result

Compared every field of `FRPGBossDecisionSnapshot` against selector preprocessing, `FRPGBossMoveModel::IsEligible/Start`, production `StartCard` callers, and the inspected automation fixtures. The shared predicate protects most inputs and existing model tests cover many refusal boundaries. Two specific test gaps remain: malformed `ConeHoldSlackDegrees` is not explicitly validated by the model domain gate, and no inspected test invokes the `UActorComponent` executor wrapper. This is a source/test audit only; it does not establish exploitability or runtime behavior for the slack case.

## Field-by-field coverage

| Snapshot field | Selector/start use | Current test coverage inspected | D2 finding |
|---|---|---|---|
| `EncounterId`, `Generation` | Model identity must match initialized encounter/generation. | `FBossMoveModelEligibility` rejects wrong encounter and generation; generation reset tests exercise new epoch. | Covered at model layer; no executor wrapper parity assertion. |
| `TargetId`, `bTargetValid` | Model requires both a valid-target flag and nonzero ID. Executor also requires a live weak target after initialization. | `FBossMoveModelEligibility` tests false flag and zero ID. | Value-model check covered; live target/component precondition is wrapper-only. |
| `FrameId` | Model rejects a non-increasing frame after the first start. | `FBossMoveModelGeneration` rejects same-frame restart, then accepts next frame. | Boundary covered for start after abort; selector and wrapper same-frame path is not integrated. |
| `PhaseId` | Compared to card phase in shared predicate. | `FBossMoveModelEligibility` rejects another phase. | Covered at model layer. |
| `ClockSeconds` | Finite/nonnegative domain; after a start, model rejects time regression. Selector uses it for cooldown and `NoteStarted` ignores invalid values. | `FBossMoveModelEligibility` tests NaN; model tests exercise monotonic restart. No selector test was found for invalid clock interaction with cooldown. | Domain and basic monotonic behavior covered separately; selector-to-start boundary not integrated. |
| `RangeCm` | Finite [0,1e6], card min/max; selector uses range preference only after eligibility. | `FBossMoveModelEligibility` tests 19/401 refusal and inclusive 20/400 edges; infinity domain refusal. | Model boundaries covered; selected card is not passed through executor fixture. |
| `SignedYawDegrees` | Finite [-180,180], cone check; selector stores per-card cone-memory slack. | Eligibility tests reject ±60.01 and -181; `FBossMoveSelectorStartConeSlack` tests 44/47/49 and zero-hysteresis behavior. | Core cone and hysteresis boundaries covered; wrapper replay assertion is absent. |
| `ConeHoldSlackDegrees` | Selector overwrites it to either configured hysteresis or zero (`RPGBossMoveSelector.cpp:41–48`); normal production path copies the chosen trace to start (`RPGFrameworkBossCharacter.cpp:518–519`). | Selector test checks zero and six-degree trace values; no direct model test for negative, NaN, or infinite slack was found. | Candidate domain gap: `IsEligible` clamps with `Max(0, slack)` but the shown snapshot-domain condition does not explicitly reject non-finite/oversized slack. Add tests first; any runtime correction requires separate review. |
| `VerticalDeltaCm` | Finite [0,1e6]; a positive card limit rejects strictly above the limit. | `FBossMoveModelVerticalSeparation` tests equal, just-above, far-above, negative, NaN, and infinity. | Covered at model layer. |
| `bNeutral` | Model requires neutral and idle state. | `FBossMoveModelEligibility` checks false neutral; model start tests cover double start/busy state. | Value and model-state tests exist; executor state checks remain untested. |

Selector context and candidate configuration do not pass to `StartCard`: candidate cooldown/weights/pattern multipliers affect choice; `ConeHysteresisDegrees` is the only context value copied into the model snapshot as cone slack. `PreferredAggroBand` and behavioral flags affect score only. Start therefore rechecks eligibility, not score, cooldown, repeat history, or tie selection.

## Wrapper fixture boundary

`URPGFrameworkMoveExecutor` derives from `UActorComponent`. Its public `Initialize` needs a boss, resolved dependencies, target pawn, and encounter/generation; the production `StartCard` additionally checks initialization/abort/owner/target/idle/finished state, `ValidatePlaybackCard`, then the shared model predicate. Existing tests use synthetic compiled card metadata and value-only `FRPGBossMoveModel`; none in the inspected tests constructs the executor. Do not call that gap “impossible to test”: a separate Editor automation fixture may create transient actor/component dependencies, but it must avoid pack assets and must tear down its world-owned objects safely.

## Bounded follow-ups

- D3 should specify direct malformed-slack model cases (negative, NaN, positive infinity, and a very large finite value) and expected stable behavior before implementation. Keep test and code decisions separate; this audit alone does not authorize a source fix.
- A later executor test should cover one valid same-snapshot start, one model refusal with exact token and unchanged idle model, invalid playback metadata, and uninitialized or finished wrapper state. If a transient actor fixture cannot meet the component's documented preconditions safely, record the exact constructor/initialization blocker and retain model-layer tests.
- Keep the cone trace-to-start value assertion separate from executor success: the former proves data transfer in a pure fixture; only the latter can exercise wrapper-owned validation.

## Verification boundary

Inspected source and existing automation test declarations read-only. No project source or test files were changed, and no test/build/Editor/PIE/package run was performed. This report records test presence and gaps; it is not a test result or a diagnosis that malformed slack occurs in production.
