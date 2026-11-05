# Designer reference: hysteretic gap-close gate

`RPGBossGapCloser::ShouldClose` decides whether range conditions allow a gap-closing action. It is unwired; the caller owns the chase state and starts/stops the action.

| Input | Unit | Default | Valid domain |
|---|---|---:|---|
| `bAlreadyClosing` | boolean | none | current chase state |
| `RangeCm` | centimeters | none | finite and non-negative |
| `EnterRangeCm` | centimeters | none | finite and non-negative |
| `ExitRangeCm` | centimeters | none | finite and at least `EnterRangeCm` |
| Return value | boolean | false for invalid input | true when chase should continue/start |

When not already closing, the rule returns true only when `RangeCm > ExitRangeCm`. During an active close, it remains true only while `RangeCm > EnterRangeCm`; equality at the enter range stops it. This creates hysteresis when exit range is larger than enter range.

Invalid numbers, negative ranges, or reversed thresholds return false. Source: [`RPGBossGapCloserRules.h`](../../Source/OneBossFight/Player/RPGBossGapCloserRules.h:7), unit tests: [`RPGBossGapCloserRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossGapCloserRulesTests.cpp:6).
