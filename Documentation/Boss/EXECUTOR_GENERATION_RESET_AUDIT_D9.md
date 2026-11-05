# Executor generation reset audit (Queue D D9, 2026-11-03)

## Pure model contract and tests

`FRPGBossMoveModel::ResetGeneration` requires initialization and a strictly newer generation; it aborts the owned attack, closes any open window, clears per-generation clocks/state, and preserves the monotonic instance counter. `FBossMoveModelGeneration` (`Tests/RPGBossMoveModelTests.cpp`) verifies active-generation reset, old-token rejection, successful new-generation start with increasing instance ID, and rejection of a generation rewind. Model-level reset semantics are covered.

## Executor wrapper order

`URPGFrameworkMoveExecutor::Rearm` first checks initialized/game-thread state, then calls `StopOwned(0)` and clears `OwnedMontage`, and only after that asks the model to `ResetGeneration` (`Boss/RPGFrameworkMoveExecutor.cpp:96–105`). On successful reset it clears abort/finish/watchdog and per-card fields, clears `Token`, and disables ticking. `RecoverAfterAbort` is a separate same-generation path (`:107–113`) requiring initialized + aborted + not finished + idle, then clears local abort/finish fields and token. `Abort` is idempotent after a clean finish/earlier abort and stops owned montage/tick (`:579–603`); `EndPlay` routes through `Abort`.

## Wrapper test coverage and finding

The inspected `RPGFrameworkRuntimeTests.cpp` creates a bare executor only for isolated preview-refusal cleanup, but does not call `Initialize`, `Rearm`, or `RecoverAfterAbort` on a valid actor/animation fixture. Pure model tests do not exercise montage/component side effects.

**Potential failed-Rearm mutation:** an invalid or non-increasing generation is rejected by `Model_.ResetGeneration`, but `Rearm` stops the owned montage and clears `OwnedMontage` before receiving that refusal. If called while a live card is playing with an invalid generation, it may interrupt playback while leaving the model in its prior active generation. This ordering deserves a wrapper regression and Lead review; no reachable caller or live failure is asserted by this source audit.

## Transition matrix

| Request | Intended source guard | Existing test | State/side-effect check needed |
|---|---|---|---|
| Rearm with newer generation | Stop owned montage; reset model; clear component state; disable tick. | Pure model test only. | Verify exactly one abort/close, old token rejected, new token generation and monotonic instance count, no owned montage/tick. |
| Rearm with equal/older generation | Model rejects monotonicity. | Pure model rewind test. | Confirm rejected wrapper call leaves active montage/model/tick intact; current order stops montage first. |
| Recover after abort | Only initialized, aborted, not finished, idle. | No valid executor wrapper test found. | Verify old token cannot affect subsequent same-generation instance and cleanup remains idempotent. |
| Recover before abort / after finish | Return false. | No wrapper test found. | Confirm no flags/token/montage/tick mutate on refusal. |
| Abort twice / EndPlay after finish | Idempotent cleanup. | Static test hook/source review only in inspected file. | Verify runtime montage, motion lock, held target, resolver tags, and tick are each released once. |

## Bounded fixture recommendation

Use a transient executor fixture with synthetic card metadata and valid actor/target/animation dependencies. Start one card; call `Rearm` with the current/older generation and assert exact refusal plus unchanged active playback/model state; then call with a newer generation and verify orderly teardown/reset. Separately exercise same-generation `RecoverAfterAbort`, and EndPlay while active. If safe fixture construction is blocked by actual asset/slot requirements, document that exact blocker and keep model tests clearly scoped.

## Verification boundary

Read-only source/test inspection. No source/test code changed; no test/build/Editor/PIE/package run occurred. Failed-Rearm ordering is a potential component-side effect, not a reproduced production defect.
