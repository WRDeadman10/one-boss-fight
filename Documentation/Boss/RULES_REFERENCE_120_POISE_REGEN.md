# Designer reference: delayed poise-regeneration ramp

`RPGBossPoiseRegen::Rate` returns a poise-per-second rate after a post-hit delay. It is unwired; a caller owns the timer and applies the resulting rate.

| Parameter | Unit | Default | Valid domain |
|---|---|---:|---|
| `BasePerSecond` | poise/second | none | finite, 0 to 1,000,000 inclusive |
| `SecondsSinceHit` | seconds | none | finite and non-negative |
| `DelaySeconds` | seconds | none | finite, 0 to 1,000,000 inclusive |
| `RampSeconds` | seconds | none | finite, greater than 0 through 1,000,000 inclusive |
| `MaxScale` | multiplier | 1.0 | finite, 1 to 3 inclusive |
| Return value | poise/second | 0 for invalid input or before delay | base rate through `BasePerSecond × MaxScale` |

Before the delay expires the rate is zero. At the exact delay boundary it starts at the base rate, then rises linearly to the maximum scale over `RampSeconds`; later it stays at the cap. A `MaxScale` of 1 disables the ramp and leaves the rate at its base after the delay.

Invalid inputs return 0. Source: [`RPGBossPoiseRegenRules.h`](../../Source/OneBossFight/Player/RPGBossPoiseRegenRules.h:7), unit tests: [`RPGBossPoiseRegenRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossPoiseRegenRulesTests.cpp:6).
