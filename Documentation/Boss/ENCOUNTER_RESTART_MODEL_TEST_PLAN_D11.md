# Encounter restart model test plan (D11)

## Scope

Source and automation-test review of `FRPGBossMoveModel::ResetGeneration`. This is a pure-model plan; it does not claim executor, montage, actor, or live restart behavior. Relevant implementation is `Source/OneBossFight/Player/RPGBossMoveModel.cpp:11-15, 50-56, 91-105, 125-147` and the value/state members in `RPGBossMoveModel.h:47-72`.

## Reset contract and state disposition

| State | Required after a successful generation reset | Source behavior / test requirement |
|---|---|---|
| Encounter identity | Retained | Reset changes `Epoch`, not `Encounter`; a snapshot from another encounter must fail with `MoveModel.Generation`. |
| Epoch/generation | Set to the strictly newer requested value | `ResetGeneration` rejects zero/equal/older values; test generation getter and refusal token. |
| Active state/card/windows | Idle, no current card, zero open windows | `CloseAndClear` closes each currently open window before emitting `Aborted`, then clears windows/card and sets Idle. Exercise Committed, Active, and Recovery states, including zero and multiple open windows. |
| Callback acceptance | Old generation token rejected; no callback can change the new state | Assert `AcceptsCallback=false`; invoke stale `Abort`, wall-clock `Advance`, and observed-local advance both before and after a new-generation start; require `MoveModel.StaleCallback` and no emitted events/state mutation. |
| Current token | May retain its old value internally, but must not be accepted while Idle or after epoch advances | Do not require token memory to be zeroed; test public acceptance and behavior. |
| Local time, clock mode, last clock | Not explicitly reset by `ResetGeneration`; next valid `Start` resets local time to zero and clock mode to Unset and writes the new snapshot clock | Test that the first next-generation attack starts at local zero with either clock mode selectable. Do not assert hidden values between reset and next start. |
| Start frame / monotonic history | `LastStartFrame`, `LastClock`, and `bHasStarted` are retained; `NextInstance` is never reset | Test a new start uses a later frame and nondecreasing clock, and its instance ID exceeds the pre-reset one. Define a separate contract decision before changing same-frame/clock history. |
| Event output | Successful reset emits only cleanup events for the interrupted attack, in order; reset while already Idle emits none | Assert exact Close event identity/window and local time, then Aborted token/local time. Repeated reset must not duplicate cleanup. |

## Existing coverage

- `FBossMoveModelGeneration` in `Tests/RPGBossMoveModelTests.cpp:136-153` covers active-token reset, stale `AcceptsCallback`, post-reset start with monotonically increasing instance, delayed old wall tick with no events, and rewind refusal.
- `FBossMoveModelCrossing` covers normal window edges; it does not currently establish reset cleanup for multiple simultaneously open windows.
- The encounter loop test `Tests/RPGBossEncounterLoopTests.cpp:78-96, 97+` starts with an open window, resets generation, and checks Close-before-Aborted, then continues a generation-two loop. This is a pure model/selector integration test.

## Gaps to add as model tests

1. Table-driven reset from Committed, Active with one open window, Recovery, and Idle. Check state, open-window count, card/token callback acceptance, ordered events, and repeated reset. Validated windows are non-overlapping, so a multiple-open-window case is not a valid card fixture.
2. Equal, older, and zero generation refusal must leave the active token, state, open-window count, and event output unchanged, with `MoveModel.Generation`.
3. After generation advance, stale `Abort`, `Advance`, and `AdvanceObservedLocal` must each refuse with `MoveModel.StaleCallback`, emit no events, and preserve a later generation's active token/state.
4. A stale-generation snapshot must fail `IsEligible` and `Start` with `MoveModel.Generation`; no instance ID is consumed and the current generation remains startable.
5. Verify the first valid next-generation start begins at local zero, accepts either clock mode, uses monotonic instance identity, and honors the retained frame/clock monotonicity contract.

The current tests already cover items 2 (rewind only), a subset of 3 (old `Advance` after the new start), and part of 4 through eligibility tests. These are proposed additions, not reported test results. No build, automation run, or Editor run was performed for D11.
