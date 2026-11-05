# Designer reference: one-shot parry feedback gate

`RPGBossParryFeedback::ShouldEmit` decides whether a resolved parry should produce its one-shot player-facing feedback. It is unwired and does not play audio, animation, or effects.

| Input | Unit | Default | Meaning |
|---|---|---|---|
| `bOutcomeParried` | boolean | none | Final outcome of the contact |
| `bAlreadyEmitted` | boolean | none | Whether feedback was already emitted for this event |
| Return value | boolean | false | True for a parry that has not emitted feedback |

The result is `bOutcomeParried && !bAlreadyEmitted`. The helper stores no state; caller code must record the one-shot flag after emitting. Every other combination returns false. Source: [`RPGBossParryFeedbackRules.h`](../../Source/OneBossFight/Player/RPGBossParryFeedbackRules.h:7), unit tests: [`RPGBossParryFeedbackRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossParryFeedbackRulesTests.cpp:6).
