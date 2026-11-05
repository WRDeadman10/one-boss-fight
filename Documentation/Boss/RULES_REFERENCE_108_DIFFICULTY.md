# Designer reference: normalized difficulty scales

`RPGBossDifficulty::Evaluate` maps one normalized difficulty input to damage, speed, and telegraph multipliers. The rule is unwired; a caller must choose a difficulty value and apply the returned scales.

| Parameter | Unit | Default | Valid domain |
|---|---|---:|---|
| `Difficulty01` | normalized scalar | none | finite, 0 to 1 inclusive |
| `DamageMin` / `DamageMax` | multiplier | 0.8 / 1.25 | finite; min > 0, max >= min, max <= 3 |
| `SpeedMin` / `SpeedMax` | multiplier | 0.9 / 1.2 | finite; min > 0, max >= min, max <= 2 |
| `TelegraphMin` / `TelegraphMax` | multiplier | 0.85 / 1.15 | finite; min > 0, max >= min, max <= 2 |

Each output is a linear interpolation from its configured minimum at difficulty 0 to maximum at difficulty 1. Outputs are multipliers; telegraph scale changes authored tell-rate only if a caller applies it.

Invalid input or any invalid configuration returns neutral scales `(1, 1, 1)`. Source: [`RPGBossDifficultyRules.h`](../../Source/OneBossFight/Player/RPGBossDifficultyRules.h:8), unit tests: [`RPGBossDifficultyRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossDifficultyRulesTests.cpp:7).
