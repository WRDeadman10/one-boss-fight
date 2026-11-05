# Cone-slack start-route test plan (Queue D D3, 2026-11-03)

## Purpose

Specify deterministic tests for the selected trace's cone slack at selection and start, and for direct malformed snapshots. This is a test plan, not authorization to change runtime semantics. D2 found that `IsEligible` explicitly validates clock, range, yaw, and vertical separation but does not explicitly validate `ConeHoldSlackDegrees`; the selector itself uses finite positive context values and the resolved profile limits configured hysteresis to 0–40 degrees.

## Existing basis

- `RPGBossFrameworkProfile.cpp:131` rejects non-finite profile hysteresis, values below 0 or above 40, and positive values outside F5 (`Framework.Profile.ConeHysteresis`).
- `RPGBossMoveSelector.cpp:41–48` writes either the finite positive context value for a remembered candidate or zero into the evaluation snapshot; it stores the used value in the trace.
- `RPGFrameworkBossCharacter.cpp:518–519` copies the chosen trace's value into the normal start snapshot before `StartCard` re-evaluates the shared model predicate.
- `RPGBossMoveModel.cpp:26–44` validates other snapshot domains, then computes the cone exit using `Max(0, ConeHoldSlackDegrees)` without an explicit finite/range check for slack.
- `FBossMoveSelectorStartConeSlack` already covers 44° entry, 47° retained at six degrees of full-cone slack, 49° refusal, and zero-hysteresis strict behavior for a 90° card.

## Proposed test matrix

Use a synthetic compiled card with a 90° full cone and the existing 50–150 cm range; fresh model and selector per independent case. The acceptance expectations below are proposed from the profile/config contract and require Lead review before a code change.

| Case | Selection/setup | Start snapshot | Proposed expected result |
|---|---|---|---|
| Zero slack | yaw 47°, no hysteresis context | exact trace slack 0 | Selector reports `MoveModel.Cone`; direct model check refuses. |
| Entry then held edge | yaw 44° first, 47° next with 6° configured slack | copy trace value 6° with same yaw/identity/frame/clock | model start accepts; confirms selected eligibility is preserved. |
| Omit selected slack | same eligible held decision | force slack 0 while retaining yaw 47° | start refuses `MoveModel.Cone`; remains Idle with no token/event. |
| Negative slack | direct model snapshot | -0.01° | Proposed `MoveModel.SnapshotDomain`; current code clamps to zero, so this locks down a deliberate contract decision. |
| NaN slack | direct model snapshot | quiet NaN | Proposed `MoveModel.SnapshotDomain`; do not rely on platform-specific `Max` NaN ordering. |
| Positive infinity slack | direct model snapshot | +infinity | Proposed `MoveModel.SnapshotDomain`; current expression may broaden the exit edge without a finite guard. |
| Profile maximum | configured 40° and candidate already remembered | 40° | selector carries exactly 40°; start accepts at corresponding inclusive exit boundary. |
| Above profile maximum direct value | direct model snapshot | 40.01° | Proposed `MoveModel.SnapshotDomain` for consistent model-level boundary; requires Lead confirmation because direct snapshot API currently has no documented upper bound. |
| Selector context invalid | context NaN or infinity | selector-produced snapshot | Current selector treats it as off/zero; assert strict cone refusal outside the original cone and trace slack zero. |

For all refusal cases, assert output token is cleared, output events are empty, and model state remains Idle. For the positive case, assert the started token matches the initialized encounter/generation and model state becomes Committed/Active according to the card's authored start. Do not use `FRPGBossMoveModel::Start` alone to claim wrapper validation; executor `StartCard` needs a separate fixture task.

## Test placement and review sequence

1. Add direct malformed-slack tests beside `FBossMoveModelEligibility` in `Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp` only after the Lead selects the intended domain and refusal token.
2. Extend `FBossMoveSelectorStartConeSlack` in `Source/OneBossFight/Tests/RPGBossMoveSelectorTests.cpp` only for profile-valid context behavior; direct invalid profile values belong to profile validation fixtures.
3. Add a separate executor-level automation fixture for `StartCard`; do not conflate it with the pure model matrix.
4. Claude runs the focused and full framework suite after any C++ change and records exact build/run identity. The present document claims no execution.

## Verification boundary

This is a source-derived test plan. No source/test code changed and no tests, build, Editor, PIE, or packaged run occurred. The proposed upper bound/refusal token for directly supplied slack is an explicit Lead-review item, not an established current contract.
