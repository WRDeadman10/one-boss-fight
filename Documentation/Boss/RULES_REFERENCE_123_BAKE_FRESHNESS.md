# Designer reference: baked-animation fingerprint freshness

`RPGBossBakeFreshness::IsFresh` compares a current animation-source fingerprint with the fingerprint stored alongside baked hit samples. It is unwired and does not calculate either fingerprint or rebuild the samples.

| Input | Unit | Default | Valid condition |
|---|---|---|---|
| `CurrentSourceFingerprint` | 64-bit fingerprint | none | nonzero |
| `BakedSourceFingerprint` | 64-bit fingerprint | none | nonzero |
| Return value | boolean | false | true only when both are nonzero and equal |

Matching nonzero values are fresh. A mismatch is stale; either zero value is treated as missing/unknown and returns false. The helper does not distinguish stale from missing data. Source: [`RPGBossBakeFreshnessRules.h`](../../Source/OneBossFight/Player/RPGBossBakeFreshnessRules.h:7), unit tests: [`RPGBossBakeFreshnessRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossBakeFreshnessRulesTests.cpp:6).
