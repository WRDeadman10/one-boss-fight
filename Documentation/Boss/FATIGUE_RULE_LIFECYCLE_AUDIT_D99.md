# Fatigue rule lifecycle audit (Queue D99)

**Scope:** static source/test mapping for fatigue's consecutive-whiff count and rate scale. No code or tests changed/run.

## Rule and caller lifecycle

`Source/OneBossFight/Player/RPGBossFatigueRules.h:8-15` validates nonnegative count/grace, finite reduction in [0,1], and floor in (0,1]. Counts at/below grace return 1; each further whiff subtracts the configured amount until the floor. Invalid input returns -1.

`Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:579-590` updates once after a started card is finished and executor-clean, guarded by `bFatigueFinishedCardSeen`. If fatigue is enabled (`FatigueFloor > 0`), any contact resets `FatigueWhiffs` to zero; a no-contact finished card increments it once, then emits the derived scale. The latch is cleared on card start at `:800,816`. Phase transition resets both count and latch at `:411`; encounter restart resets both at `:863`. `:521` also clears the finished-card latch when transitioning out of a branch (the count is not reset there).

## Existing test coverage

`Source/OneBossFight/Tests/RPGBossFatigueRulesTests.cpp:9-23` checks bounded monotonic output over counts 0..999, first-two-whiffs grace, negative-count rejection, and invalid zero floor. `Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp:237-249` checks profile-level enablement and rejection of partial/out-of-range configuration.

## Gaps

No stateful boss lifecycle fixture asserts that a completed no-contact card increments only once, a contact card resets the streak, an aborted/unclean card does not count, or phase/restart clears it. The pure-rule test does not pin exact grace+1, exact floor-reaching count, zero reduction, or floor 1. Caller code evidence maps the intended behavior but does not establish runtime event ordering or actual contact aggregation semantics; the framework helper is opt-in.
