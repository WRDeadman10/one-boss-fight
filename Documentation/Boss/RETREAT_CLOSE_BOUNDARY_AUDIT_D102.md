# Retreat close-boundary audit (Queue D102)

**Scope:** static review of the pure retreat gate and existing boundary tests. No tests run; helper is documented unwired.

`Source/OneBossFight/Player/RPGBossRetreatRules.h:8-14` returns false for nonfinite inputs, negative range/close range, threat outside [0,1], or threshold outside [0,1]. Otherwise retreat requires strict `RangeCm < CloseRangeCm` and inclusive `Threat01 >= ThreatThreshold`. There is a single close-range limit, not independent min/max range fields, and no vertical position/distance parameter; vertical gating cannot be claimed for this helper.

`Source/OneBossFight/Tests/RPGBossRetreatRulesTests.cpp:9-11` covers an interior close range, a farther range, threat below/equal threshold, threat above 1, and negative range. `RPGBossRetreatCloseBoundaryMutationTests.cpp:10-17` checks 149.999 is inside and exact 150 is excluded when close range is 150.

Gaps: no adjacent representable values around the range threshold, no configurable threat-threshold adjacent/equality test beyond the default `.5`, and no nonfinite/negative close-range or NaN/negative threat cases. No vertical behavior is expressible in the current signature. Caller/runtime integration remains unproved because the helper is explicitly unwired.
