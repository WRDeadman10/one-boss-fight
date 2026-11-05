# Designer reference: low health weight ramp

`RPGBossDesperation::WeightMultiplier` returns a bounded multiplier based on the boss's health fraction. A caller may use it to adjust selection weights; this helper does not choose a move or change health.

| Parameter | Unit | Default | Valid domain |
|---|---|---:|---|
| `HealthFraction` | fraction of maximum health | none | finite, 0 to 1 inclusive |
| `StartFraction` | fraction of maximum health | 0.35 | finite, greater than 0 through 1 inclusive |
| `MaxMultiplier` | weight multiplier | 1.5 | finite, 1 to 3 inclusive |
| Return value | weight multiplier | 1 | 1 to configured maximum |

At or above `StartFraction`, the result is 1. Below it, the result increases linearly as health falls; zero health reaches `MaxMultiplier`. The progress calculation clamps to 0–1, so valid inputs never exceed the configured maximum.

Any non-finite input, health outside 0–1, start fraction outside `(0, 1]`, or maximum multiplier outside `[1, 3]` returns 1 (unchanged weight). Source: [`RPGBossDesperationRules.h`](../../Source/OneBossFight/Player/RPGBossDesperationRules.h:8), unit tests: [`RPGBossDesperationRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossDesperationRulesTests.cpp:7).
