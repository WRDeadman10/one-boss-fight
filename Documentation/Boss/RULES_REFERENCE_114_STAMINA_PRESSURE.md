# Designer reference: low-stamina pressure

`RPGBossStaminaPressure::Pressure` returns an urgency value as the player's stamina falls below a threshold. It is unwired; callers decide how this value changes selection weights or behavior.

| Parameter | Unit | Default | Valid domain |
|---|---|---:|---|
| `StaminaFraction` | fraction of maximum stamina | none | finite, 0 to 1 inclusive |
| `LowThreshold` | fraction of maximum stamina | 0.4 | finite, greater than 0 through 1 inclusive |
| `MaxPressure` | urgency scale | 1.0 | finite, 0 to 3 inclusive |
| Return value | urgency scale | 0 for invalid input | 0 to `MaxPressure` |

The formula is `clamp((LowThreshold - StaminaFraction) / LowThreshold, 0, 1) × MaxPressure`. At or above the threshold pressure is 0; at zero stamina it reaches the configured maximum. At half the default threshold, it is half the maximum.

Invalid inputs return 0. Source: [`RPGBossStaminaPressureRules.h`](../../Source/OneBossFight/Player/RPGBossStaminaPressureRules.h:7), unit tests: [`RPGBossStaminaPressureRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossStaminaPressureRulesTests.cpp:6).
