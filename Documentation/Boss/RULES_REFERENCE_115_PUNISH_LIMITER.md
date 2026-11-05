# Designer reference: per-fight punish-use budget

`RPGBossPunishLimiter` stores a small use count and answers whether another punish-window use is allowed. It is unwired; the caller owns the state and must reset it at the correct encounter boundary.

| State/input | Unit | Default | Valid domain |
|---|---|---:|---|
| `FState.Uses` | uses | 0 | non-negative and less than the budget to permit a use |
| `MaxUses` | uses per reset period | none | integer 1 to 100 inclusive |
| `CanUse` result | boolean | true for fresh state and valid budget | false at/over budget or invalid state/budget |
| `RecordUse` result | boolean | none | true only when it increments an allowed use |

`RecordUse` increments by one only when `CanUse` is true. At the cap, it returns false and leaves the count unchanged. `Reset` sets the count to zero; no timer or automatic per-fight reset exists, so call `Reset` when a new fight begins.

Invalid budgets and negative/corrupt use counts fail closed. Source: [`RPGBossPunishLimiterRules.h`](../../Source/OneBossFight/Player/RPGBossPunishLimiterRules.h:7), unit tests: [`RPGBossPunishLimiterRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossPunishLimiterRulesTests.cpp:6).
