# Designer reference: close-range threat retreat

`RPGBossRetreat::ShouldRetreat` returns whether a threatened boss should back away from a close target. It is unwired; the caller decides how and how far to retreat.

| Input | Unit | Default | Valid domain |
|---|---|---:|---|
| `RangeCm` | centimeters | none | finite and non-negative |
| `CloseRangeCm` | centimeters | none | finite and non-negative |
| `Threat01` | normalized threat | none | finite, 0 to 1 inclusive |
| `ThreatThreshold` | normalized threat | 0.5 | finite, 0 to 1 inclusive |
| Return value | boolean | false | true only when close and threat is at/above threshold |

The target must be strictly closer than `CloseRangeCm`, and `Threat01 >= ThreatThreshold`. Equality at the close-range limit does not retreat; equality at the threat threshold does.

Invalid inputs return false. Source: [`RPGBossRetreatRules.h`](../../Source/OneBossFight/Player/RPGBossRetreatRules.h:7), unit tests: [`RPGBossRetreatRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossRetreatRulesTests.cpp:6).
