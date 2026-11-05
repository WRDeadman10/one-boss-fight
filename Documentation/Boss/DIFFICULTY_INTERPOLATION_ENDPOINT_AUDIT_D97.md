# Difficulty interpolation endpoint audit (Queue D97)

**Scope:** static source/test review of the pure difficulty scalar mapper. The header calls it unwired. No tests run.

`Source/OneBossFight/Player/RPGBossDifficultyRules.h:8-19` accepts only finite `Difficulty01` in [0,1] and a valid config. Config endpoints must be finite, positive, ordered (`Max >= Min`), with maxima bounded: damage <=3, speed <=2, telegraph <=2. Invalid input returns default neutral scales of 1. Valid input uses `FMath::Lerp(min,max,Difficulty01)` independently for damage, speed, and telegraph.

Tests in `Source/OneBossFight/Tests/RPGBossDifficultyRulesTests.cpp:10-17` cover valid defaults; difficulty 0 low damage endpoint; difficulty 1 high endpoints for all three outputs; 1000 monotonic/bounded interior samples; NaN difficulty neutral fallback; and rejection of speed max above its cap. `RPGBossDifficultyEqualEndpointsMutationTests.cpp:10-19` proves equal damage endpoints are valid and constant at difficulty 1.

Gaps: no equal-endpoint check for speed/telegraph or at difficulty 0/interior; no adjacent representable checks around difficulty 0/1; negative, >1, and infinite difficulty values are not directly asserted (NaN is). Config tests do not cover nonfinite/zero minima or equality for all fields. Source arithmetic is bounded by config maxima and input [0,1], so no output overflow is apparent for valid config. No evidence here establishes runtime wiring, normalization source, or product-selected difficulty values.
