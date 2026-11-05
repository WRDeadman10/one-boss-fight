# Designer reference: first-hit parry combo abort

`RPGBossComboAbort::ShouldAbort` decides whether an already active combo is canceled by a parry. It is a decision helper only; the caller owns combo state and cleanup.

| Input | Unit | Default | Meaning |
|---|---|---|---|
| `bComboActive` | boolean | none | Current combo state |
| `AcceptedHits` | count | none | Hits already accepted in this combo |
| `bFirstHitParried` | boolean | none | Whether the first combo hit was parried |
| Return value | boolean | false | True only for an active combo, zero accepted hits, and a parried first hit |

The helper does not validate or clamp the count; it requires `AcceptedHits == 0`. Any other combination returns false, including inactive combo state, an accepted earlier hit, or no first-hit parry. There are no time or numeric parameters. Source: [`RPGBossComboAbortRules.h`](../../Source/OneBossFight/Player/RPGBossComboAbortRules.h:7), unit tests: [`RPGBossComboAbortRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossComboAbortRulesTests.cpp:6).
