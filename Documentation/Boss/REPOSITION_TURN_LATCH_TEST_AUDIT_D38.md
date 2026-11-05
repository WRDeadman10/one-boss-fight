# Reposition turn-latch test audit (Queue D38)

Scope: direction memory, exact deadband, zero-yaw/reached-target behavior, reversal, and reset coverage. Static source/test review only; no tests run.

## Source contract

- `StepYawLatched` returns current yaw unchanged on committed/bad/nonpositive rate or delta-time. It computes shortest angular delta; if target is within this tick's step it returns the normalized target and clears `Dir`. Otherwise it derives direction, but preserves prior direction when direction reverses inside the back-axis band `abs(Delta) >= 180 - HysteresisDeg` (default 30 degrees), and counts actual direction changes (`Source/OneBossFight/Player/RPGBossTrackRules.h:12-29`). Thus the exact default latch threshold is 150 degrees inclusive; a real crossing below 150 degrees releases it.
- Actor integration uses the helper only for the no-candidate reposition turn when configured (`Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:468-479`). It logs turn start/end and resets latch at end; restart, death, and failure also reset it (`:861-863,879,888`). `rpg.BossProofTurnLatch 0` is the unlatched comparison control (`:40,471-475`).

## Existing tests and gaps

- `OneBossFight.Framework.Runtime.TurnLatch` tests 40 alternating +170/-170 targets with the latch on/off, a clear reversal at -90 degrees, target arrival within one step, committed hold, and zero rate (`Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp:473-490`). These cover representative behavior, not the exact deadband boundary.
- Missing explicit cases: target exactly 150 degrees from the back axis and adjacent representable angles on either side; exact zero yaw/delta and normalized ±180 wrap; nonfinite current/target/hysteresis inputs; zero/negative Dt; state preservation in all refusal paths; lifecycle reset assertions for end/restart/death/failure. The current zero-rate assertion checks unchanged yaw but not latch counters/state.
- Existing cases support representative latch retention/release and counting, but no independent test asserts reset of `LastDir`/`Flips` at each actor lifecycle boundary. The source reset sites are not actor-level tested here.

No source mismatch is established. Suggested focused additions are pure boundary mutation cases for 150°/adjacent floats and zero/wrap, plus a small state equality assertion for refusal/reset; keep actor lifecycle wiring distinct from the pure math rule.
