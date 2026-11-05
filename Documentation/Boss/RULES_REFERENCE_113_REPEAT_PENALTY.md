# Designer reference: recent-repeat weight penalty

`RPGBossRepeatPenalty::Weight` exponentially reduces a base selection weight for repeated use. It is unwired; it does not track history or select a move.

| Input | Unit | Default | Valid domain |
|---|---|---:|---|
| `BaseWeight` | selection weight | none | finite and non-negative |
| `RepeatCount` | repeat count | none | integer 0 to 100 inclusive |
| `PerRepeatScale` | multiplier per repeat | 0.7 | finite, 0 to 1 inclusive |
| Return value | selection weight | 0 for invalid input | 0 to `BaseWeight` |

The formula is `BaseWeight × PerRepeatScale^RepeatCount`. Zero repeats preserve the base weight; a scale of zero clears the weight after the first repeat; a scale of one applies no penalty. The result is clamped to the base-weight range.

Invalid inputs return 0. A caller must define how it counts repeats and when that memory resets. Source: [`RPGBossRepeatPenaltyRules.h`](../../Source/OneBossFight/Player/RPGBossRepeatPenaltyRules.h:7), unit tests: [`RPGBossRepeatPenaltyRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossRepeatPenaltyRulesTests.cpp:6).
