# Designer reference: reaction-based feint chance

`RPGBossFeint::Chance` maps the player's measured reaction time to a probability of a feint. It is unwired and does not roll randomness or select a feint.

| Parameter | Unit | Default | Valid domain |
|---|---|---:|---|
| `PlayerReactionSeconds` | seconds | none | finite and non-negative; values outside the band clamp |
| `FastReactionSeconds` | seconds | 0.15 | finite and non-negative |
| `SlowReactionSeconds` | seconds | 0.6 | finite and greater than fast threshold |
| `MinChance` | probability | 0.05 | finite and non-negative |
| `MaxChance` | probability | 0.45 | finite; at least minimum and at most 1 |
| Return value | probability | 0 for invalid input | from configured minimum to maximum |

The reaction time is normalized across the fast/slow band and clamped to 0–1. Slow reactions receive `MinChance`; fast reactions receive `MaxChance`; intermediate values interpolate linearly, so faster reactions never reduce feint chance.

Invalid inputs return 0. Source: [`RPGBossFeintRules.h`](../../Source/OneBossFight/Player/RPGBossFeintRules.h:7), unit tests: [`RPGBossFeintRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossFeintRulesTests.cpp:6).
