# Selector-to-start parity regression map (Queue D D1, 2026-11-03)

## Result

The production normal path preserves the selector's model snapshot, copying the selected trace's cone slack before `StartCard`. `StartCard` re-runs the shared move-model predicate and adds playback/state validation. Combo starts bypass selector choice/cooldown/repeat scoring, use the route's current or fresh snapshot, and abandon the combo on model refusal. After a successful combo start, the actor still calls `Selector.NoteStarted`, updating cooldown clock, repeat history, and tie offset for future normal selections. I found no source-level mismatch that justifies changing runtime code. The useful test gap is narrower: current pure tests exercise `FRPGBossMoveModel::Start`, not the `URPGFrameworkMoveExecutor::StartCard` wrapper and its preconditions/extra playback validation. That wrapper coverage needs a separate, deliberately designed fixture before implementation. See the D15 audit for route-by-route memory behavior.

## Predicate and data flow

| Route or check | Current source | Test evidence inspected | Finding / limit |
|---|---|---|---|
| Candidate eligibility | `Player/RPGBossMoveSelector.cpp:41–48` applies per-card cone memory and calls `Model.IsEligible`. | `Tests/RPGBossMoveSelectorTests.cpp` covers filter and scoring behavior. | Shared predicate; selector context changes only snapshot cone slack before evaluation. |
| Shared range/phase/cone/domain predicate | `Player/RPGBossMoveModel.cpp:16–44`. | `Tests/RPGBossMoveModelTests.cpp` and selector tests. | Selection and start share this model contract. |
| Normal chosen-card snapshot | `Boss/RPGFrameworkBossCharacter.cpp:455`, `:518–521`. | `StartConeSlack` checks the trace's hysteresis slack; `PureSelectorModelRestart` passes slack to `Model.Start`. | Production copies selected slack into the same snapshot before wrapper start. |
| Wrapper start conditions | `Boss/RPGFrameworkMoveExecutor.cpp:120–126`. | No executor-level wrapper test was found in the inspected test files. | In addition to model eligibility, wrapper checks card validity, initialization, abort/owner/target/idle/finished state, playback-card validity, and then model eligibility. |
| Combo continuation | `Boss/RPGFrameworkBossCharacter.cpp:787–800`. | `RPGBossComboFallbackTests.cpp` verifies model refusal and ordinary-selector fallback. | Bypasses selector choice/cooldown/repeat scoring, uses the current gate snapshot, then records successful start with `NoteStarted` at `:799`; refusal leaves selector memory unchanged. |
| Delayed combo start | `Boss/RPGFrameworkBossCharacter.cpp:803–815`. | No test in the inspected pure test files executes the actor timer route. | `StartComboCard` calls `MakeSnapshot()` at wake; successful start records `NoteStarted` at `:815`, while refusal ends combo without that update. Requires a separate world/actor fixture to exercise directly. |
| Caller movement policy | `Boss/RPGFrameworkBossCharacter.cpp:465–484`. | Existing movement/range rule tests cover pure portions only. | Range-band walk/reposition are caller policy, not duplicate `StartCard` eligibility. This audit makes no live movement claim. |

## Existing regression coverage and bounded next work

- `FBossMoveSelectorStartConeSlack` (`OneBossFight.Framework.Selector.StartConeSlack`) checks entry/hold/exit slack and the strict zero-hysteresis case.
- `FBossEncounterPureLoopRestart` (`OneBossFight.Framework.EncounterLoop.PureSelectorModelRestart`) selects, copies trace slack, calls the pure model `Start`, and covers reset/stale-generation behavior. It does not instantiate `URPGFrameworkMoveExecutor`.
- `FBossComboFallbackAfterModelRefusal` (`OneBossFight.Framework.Combo.FallbackAfterModelRefusal`) covers the pure model refusal followed by ordinary selection; no actor or timer is exercised.
- The existing S1 audit remains the broad source comparison. This D1 refresh incorporates the S2/S5 pure coverage, C-727 fallback test, and current post-Queue-C callsites; it does not re-run those tests or claim a current build.

## D2 fixture design requirements

Before adding an executor-level test, D2 should establish a bounded component construction strategy that does not require pack assets: construct an initialized executor with synthetic compiled metadata and valid owner/target components, or document why the wrapper is not safely instantiable in engine-free automation. If feasible, exercise (a) selected same snapshot succeeds, (b) omitted positive cone slack refuses at the exact exit edge, (c) invalid playback metadata refuses before model mutation, and (d) uninitialized/finished state fails with the state token. Tests must assert executor/model state remains idle on every refusal. Claude owns build and suite execution.

## Verification boundary

Source and test files were inspected read-only. No C++ or test source was changed; this D1 deliverable is documentation-only. No test, build, Unreal Editor, PIE, or packaging run was performed. This is a source-level coverage map, not a claim of runtime parity or current suite health.
