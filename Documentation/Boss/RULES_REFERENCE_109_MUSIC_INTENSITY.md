# Designer reference: health and phase music intensity

`RPGBossMusicIntensity::Evaluate` returns one normalized music intensity value. The rule is unwired and does not select tracks, change volume, or blend audio by itself.

| Parameter | Unit | Default | Valid domain |
|---|---|---:|---|
| `HealthFraction` | fraction of maximum health | none | finite, 0 to 1 inclusive |
| `Phase` | phase number | none | 1 or 2 |
| `PhaseTwoBoost` | normalized intensity | 0.25 | finite, 0 to 1 inclusive |
| Return value | normalized intensity | 0 for invalid input | 0 to 1 |

The formula is `clamp(1 - HealthFraction + (Phase == 2 ? PhaseTwoBoost : 0), 0, 1)`. Thus intensity rises as health falls, and phase two adds the configured boost before the result is clamped.

Invalid health, phase, or boost returns 0. Source: [`RPGBossMusicIntensityRules.h`](../../Source/OneBossFight/Player/RPGBossMusicIntensityRules.h:7), unit tests: [`RPGBossMusicIntensityRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossMusicIntensityRulesTests.cpp:6).
