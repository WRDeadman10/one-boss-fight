# Designer reference: deterministic cue timing jitter

`RPGBossCueJitter::Time` offsets one cue's base time with deterministic seeded jitter, then clamps it to a safe interval. It is unwired; a caller owns cue playback and seed lifecycle.

| Input | Unit | Default | Valid domain |
|---|---|---:|---|
| `Seed` | integer seed | none | any `int32` |
| `CueIndex` | cue index | none | integer, non-negative |
| `BaseSeconds` | seconds | none | finite; may lie outside safe interval |
| `JitterSeconds` | seconds | none | finite and non-negative |
| `SafeMin`, `SafeMax` | seconds | none | finite; minimum >= 0; maximum >= minimum |
| Return value | cue time in seconds | 0 for invalid input | clamped to safe interval |

The same seed and cue index produce the same offset. The base time receives a deterministic offset in the requested jitter range and the result is clamped to `[SafeMin, SafeMax]`. Identical seeds across actors will repeat the same cue-index pattern unless the caller gives each actor a distinct seed.

Invalid inputs return 0. Since 0 may also be a valid clamped cue time, callers should validate their parameters separately when that distinction matters. Source: [`RPGBossCueJitterRules.h`](../../Source/OneBossFight/Player/RPGBossCueJitterRules.h:7), unit tests: [`RPGBossCueJitterRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossCueJitterRulesTests.cpp:6).
