# Designer reference: parry hit-stop duration

`RPGBossHitStop::Seconds` maps parry grade to a bounded pause duration. The rule is unwired; it does not apply global or local time dilation.

| Parameter | Unit | Default | Valid domain |
|---|---|---:|---|
| `PerfectSeconds` | seconds | 0.12 | finite; at least `GoodSeconds`; no greater than `MaxSeconds` |
| `GoodSeconds` | seconds | 0.08 | finite; between `PerfectSeconds` and `LateSeconds` |
| `LateSeconds` | seconds | 0.04 | finite and non-negative; no greater than `GoodSeconds` |
| `MaxSeconds` | seconds | 0.20 | finite and non-negative; must be at least `PerfectSeconds` |
| `Grade` input | enum | none | Perfect, Good, Late, or other |

Perfect, Good, and Late return their matching configured durations. The default ordering is Perfect > Good > Late. `None` and other unsupported grades return 0.

An invalid configuration returns 0 for every grade. The configured maximum is the cap; the rule does not impose an additional fixed upper limit. Source: [`RPGBossHitStopRules.h`](../../Source/OneBossFight/Player/RPGBossHitStopRules.h:7), unit tests: [`RPGBossHitStopRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossHitStopRulesTests.cpp:6).
