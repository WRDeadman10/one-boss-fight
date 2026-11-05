# Designer reference: consecutive pattern detection

`RPGBossPatternDetect` remembers the current pattern identity and its consecutive observation count. It is a pure helper: the caller decides when to observe, what counts as a pattern, and what action follows a detected repeat.

| Input | Unit | Default | Valid domain |
|---|---|---|---|
| `Pattern` | `FName` identifier | none | must not be `NAME_None` |
| `RequiredRepeats` | consecutive observations | none | integer 2 to 100 inclusive |
| `FState.LastPattern` | `FName` identifier | `NAME_None` | internal state |
| `FState.Consecutive` | observations | 0 | internal state; bounded to 100 on each valid observation |

The first observation of a pattern sets the count to 1. Repeating the same name increments the count (capped at 100); observing a different name starts a new streak at 1. `Observe` returns true once the streak reaches `RequiredRepeats`, and continues returning true while the streak remains at or above that threshold.

An empty pattern or an invalid threshold resets all state and returns false. There is no time window, decay, weighting, or built-in action. Source: [`RPGBossPatternDetectRules.h`](../../Source/OneBossFight/Player/RPGBossPatternDetectRules.h:8), unit tests: [`RPGBossPatternDetectRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossPatternDetectRulesTests.cpp:6).
