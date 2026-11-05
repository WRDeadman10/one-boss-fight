# Executor invalid-start refusal audit (Queue D D8, 2026-11-03)

## Refusal order and existing test boundary

`URPGFrameworkMoveExecutor::StartCard` in `Boss/RPGFrameworkMoveExecutor.cpp:120–126` rejects a null card with `Framework.Playback.State`, assigns `Card=NextCard`, then checks initialization/abort/owner/target/idle/finished state with the same token. It next runs `ValidatePlaybackCard` and shared `Model_.IsEligible`. `ValidatePlaybackCard` (`:61–68`) distinguishes unresolved preview from invalid sequence telemetry/playback setup. `Tests/RPGFrameworkRuntimeTests.cpp:102,115,138` exercises static playback validation for resolved cards and preview refusal, not the stateful component `StartCard` wrapper.

Later start failures occur after more state changes: play rate and watchdog fields are computed, component ticking is enabled, and the model reserves a token before montage playback. A failed montage calls `Abort`; these transitions are outside the pure model and static card validator fixtures inspected here.

## Review finding

**Potential state-mutation-on-refusal:** the wrapper writes its `Card` member before the initialized/aborted/owner/target/idle/finished guard. Thus a non-null card passed to a rejected start can replace the member used by the `Start()` convenience method, which delegates to `StartCard(Card, ...)`. This differs from the pure model contract, where a rejected `Start` clears output token/events and leaves the model idle. Whether that component field change is a reachable user-visible defect depends on how callers retry; this source audit does not claim a reproduced failure. The smallest regression should snapshot the prior card, induce a rejected non-null start in a transient fixture, and verify subsequent default `Start()` still uses the prior accepted card—or establish the desired API contract before changing code.

## Refusal and mutation matrix

| Input/state | Current check | Test evidence inspected | State/mutation question |
|---|---|---|---|
| Null card | `Framework.Playback.State` before member assignment. | No wrapper test found. | Card member unchanged. |
| Not initialized, aborted, invalid owner/target, non-idle, or finished | `Framework.Playback.State` after assigning `Card`. | No `StartCard` wrapper tests found. | **Card member is changed before refusal.** |
| Unresolved preview or invalid playback shape | `Framework.Playback.UnresolvedPreview` / `Framework.Playback.SequenceTelemetryOnly`. | Static `ValidatePlaybackCard` tests exercise representative cases. | Wrapper order and component/model state are not tested. |
| Model-ineligible snapshot | Shared `MoveModel.*` token after playback validation. | Pure model/selector tests cover individual predicates; not the component call. | Confirm token/output/model idle and member behavior in wrapper fixture. |
| Fatigue/telegraph/watchdog refusal | Specific profile or watchdog token after pre-check computations. | Source tracing only. | Verify no tick/timer/resource leak and whether member/derived play rate remains changed. |
| Missing sequence/animation dependency drift | `Framework.Playback.DependencyDrift` after enabling tick. | No wrapper test found. | Tick must be disabled on refusal or contract must explain cleanup. |
| Model start or montage-play failure | Model reservation then `Framework.Playback.StartFailed`/abort path. | Model-level failure tests exist; no component playback test found. | Verify token/model cleanup, tick/montage teardown, and member retry semantics. |

## Bounded fixture recommendation

Use synthetic compiled cards and a transient actor/component fixture without pack assets. Record the initially accepted card, submit a different non-null card under a guard-rejected state, assert exact token and no tick/model transition, then call default `Start()` after the fixture reaches valid state and verify which card is used. Add one preview refusal and one model refusal; inspect `IsIdle`, `DidFinish`, `ActiveCard`, tick state, model token/state, and output log association. If the transient fixture cannot provide a valid mesh animation instance/slot graph safely, keep the static validator tests and record the exact blocker; do not claim wrapper coverage.

## Verification boundary

Read-only source/test inspection. No implementation or test code changed, and no automation test/build/Unreal Editor/PIE/package run occurred. The member-mutation observation is a source-level potential issue pending a reachable retry test and Lead review.
