# Designer reference: bounded stuck recovery

`RPGBossStuckRecovery::CanRecover` gates one bounded direction-change recovery after blocked movement. It is unwired; callers perform the recovery and update attempts/one-shot state.

| Input | Unit | Default | Valid condition |
|---|---|---|---|
| `bBlocked` | boolean | none | must be true |
| `bRecoveryAlreadyUsed` | boolean | none | must be false |
| `Attempts` | attempts | none | non-negative and below cap |
| `MaxAttempts` | attempts | none | integer 1 to 8 inclusive |
| Return value | boolean | false | true only when all recovery conditions hold |

The result requires `Attempts < MaxAttempts`, so the cap blocks further recoveries at equality. Unblocked state, a used one-shot recovery, negative attempts, or an invalid cap returns false. The rule does not increment attempts or set the used flag. Source: [`RPGBossStuckRecoveryRules.h`](../../Source/OneBossFight/Player/RPGBossStuckRecoveryRules.h:7), unit tests: [`RPGBossStuckRecoveryRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossStuckRecoveryRulesTests.cpp:6).
