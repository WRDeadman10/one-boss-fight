# Designer reference: time based enrage

`RPGBossEnrage` is a header-only, unwired rule. It calculates bounded multipliers from elapsed fight time; it does not start a timer or change a boss by itself.

| Parameter | Unit | Default | Valid domain |
|---|---|---:|---|
| `RampSeconds` | seconds | 120 | finite and greater than 0 |
| `MaxDamageScale` | multiplier | 1.5 | finite, 1 to 3 inclusive |
| `MaxSpeedScale` | multiplier | 1.25 | finite, 1 to 2 inclusive |
| `ElapsedSeconds` input | seconds | none | finite; zero or less keeps baseline |

Progress is `clamp(ElapsedSeconds / RampSeconds, 0, 1)`. Damage and speed scale linearly from 1 to their configured maxima. At or beyond `RampSeconds`, both outputs stay at the maximum. The two channels use the same progress but separate maxima.

Invalid configuration returns progress 0 and both multipliers 1. Non-finite or non-positive elapsed time also gives baseline output. `FConfig::IsValid()` exposes configuration validation; callers should validate before adopting a profile.

This rule is not wired into combat and has no effect on the current boss. Source: [`RPGBossEnrageRules.h`](../../Source/OneBossFight/Player/RPGBossEnrageRules.h:8), unit tests: [`RPGBossEnrageRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossEnrageRulesTests.cpp:6).
