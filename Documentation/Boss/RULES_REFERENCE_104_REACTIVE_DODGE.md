# Designer reference: reactive dodge chance

`RPGBossReactiveDodge` calculates a deterministic chance for a boss to evade a heavy player attack based on recent player hits. It does not generate a random number or perform a dodge; the caller supplies the roll and handles the result.

| Parameter | Unit | Default | Valid domain |
|---|---|---:|---|
| `HitsToStart` | recent hit count | 2 | integer 0 to 100 inclusive |
| `BaseChance` | probability | 0.05 | finite, 0 to `MaxChance` |
| `ChancePerHit` | probability per hit | 0.1 | finite and non-negative |
| `MaxChance` | probability | 0.65 | finite, 0 to 1 inclusive |
| `RecentHits` input | hit count | none | integer; must meet `HitsToStart` |
| `Roll` input | probability sample | none | finite, 0 inclusive to 1 exclusive |

Only heavy attacks are eligible. At/above the hit threshold, chance is `clamp(BaseChance + (RecentHits - HitsToStart + 1) * ChancePerHit, 0, MaxChance)`. With defaults, the second recent hit gives 0.15; further hits rise by 0.1 until the 0.65 cap. `ShouldDodge` succeeds only when `Roll < Chance`.

Light attacks and counts below threshold have zero chance. Invalid configuration yields zero chance; invalid, negative, or `Roll >= 1` samples fail closed. This helper is unwired and has no current combat effect. Source: [`RPGBossReactiveDodgeRules.h`](../../Source/OneBossFight/Player/RPGBossReactiveDodgeRules.h:8), unit tests: [`RPGBossReactiveDodgeRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossReactiveDodgeRulesTests.cpp:7).
