# Mutation thought experiment: boundary gaps (R66–R70)

Read-only audit. Each mutation below appears able to survive the current focused tests because the exact input is absent. The proposed assertions are additions only; none were added or run in this audit.

| Rule and source operator | Mutation not distinguished by current focused test | Small test that would catch it |
|---|---|---|
| `RPGBossGapCloserRules.h:11`, start condition `RangeCm > ExitRangeCm` | Flip `>` to `>=`; current start cases use 500 and 601 against 600, so both operators produce the same results (`RPGBossGapCloserRulesTests.cpp:10–11`). | Assert `ShouldClose(false, 600., 250., 600.)` is false; also keep 601 true. |
| `RPGBossRetreatRules.h:12`, close gate `RangeCm < CloseRangeCm` | Flip `<` to `<=`; current range values are 100 and 200 against 150, with no exact close boundary (`RPGBossRetreatRulesTests.cpp:9–11`). | Assert `ShouldRetreat(150., 150., .8)` is false while 149.999 retreats. |
| `RPGBossFeintRules.h:11`, cap validation `MaxChance > 1.` | Flip `>` to `>=`; tests use default .45 and invalid 4, not the valid maximum 1 (`RPGBossFeintRulesTests.cpp:10–12`). | Assert `Chance(.15, .15, .6, .05, 1.) == 1.` and that the config is accepted. |
| `RPGBossStaggerResistRules.h:11`, phase selection `Phase == 1` | Replace `==` with `<=`; the only unknown phase tested is 3, so phase 0 would expose this change (`RPGBossStaggerResistRulesTests.cpp:10`). | Assert `Scale(0, .8, 1.6) == 1.`. |
| `RPGBossPoiseRegenRules.h:11`, invalid ramp `RampSeconds <= 0.` | Flip `<=` to `<`; tests exercise positive ramp values only (`RPGBossPoiseRegenRulesTests.cpp:10–14`). | Assert zero ramp returns the documented fail-closed zero, e.g. `Rate(10., 1., 1., 0., 1.5) == 0.`. |
| `RPGBossParryFeedbackRules.h:10`, `bOutcomeParried && !bAlreadyEmitted` | Change `&&` to `==`; existing cases true/false, false/false, true/true all keep their results, leaving false/true untested (`RPGBossParryFeedbackRulesTests.cpp:9–10`). | Assert `ShouldEmit(false, true)` is false. |
| `RPGBossStuckRecoveryRules.h:10`, cap validation `MaxAttempts <= 8` | Flip `<=` to `<`; tests cover 1, 2, and 9 but not the valid upper edge 8 (`RPGBossStuckRecoveryRulesTests.cpp:9–12`). | Assert `CanRecover(true, false, 0, 8)` is true. |
| `RPGBossDifficultyRules.h:13`, ordered endpoints `DamageMax >= DamageMin` | Flip `>=` to `>`; defaults are unequal and the only invalid config raises the speed max (`RPGBossDifficultyRulesTests.cpp:10–15`). | Set `DamageMax = DamageMin`; assert `IsValid` and `Evaluate(1., C).Damage == C.DamageMin`. |
| `RPGBossDesperationRules.h:11`, `StartFraction > 1.` | Flip `>` to `>=`; tests use .35 and omit the allowed exact upper endpoint (`RPGBossDesperationRulesTests.cpp:10–15`). | Assert `WeightMultiplier(0., 1., 1.8) == 1.8`; a simple half-health assertion would be inconclusive because invalid config also falls back to 1. |
| `RPGBossStrafeResumeRules.h:10`, positive remaining budget `> 0.` | Replace `>` with `!=`; current tests cover .5 and 0 but no negative finite budget (`RPGBossStrafeResumeRulesTests.cpp:10–12`). | Assert `ShouldRestart(true, false, -.1)` is false. |

These are proposed mutation tests, not runtime findings. The source and focused test files were inspected; no tests were run.
