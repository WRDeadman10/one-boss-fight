# Stagger resistance unknown-phase audit (Queue D95)

**Scope:** static comparison of the pure phase-scale helper with current tests. It is documented as unwired. No tests were run.

`Source/OneBossFight/Player/RPGBossStaggerResistRules.h:8-12` accepts finite phase scales in [0,3], otherwise returns neutral 1. It returns the phase-one value only for integer 1, phase-two only for integer 2, and neutral 1 for every other `int32` phase. Thus zero, negatives, and large/unknown phase IDs are all fail-neutral. The helper returns a scale; this alone does not prove how any runtime consumer applies it.

`Source/OneBossFight/Tests/RPGBossStaggerResistRulesTests.cpp:9-12` covers default phase 1 and 2, unknown phase 3, explicit phase-one override, and an invalid upper scale fallback. `Source/OneBossFight/Tests/RPGBossStaggerResistUnknownPhaseMutationTests.cpp:10-14` explicitly covers phase zero with non-default values, preventing accidental default-value-only success.

Coverage gaps: negative and `MAX_int32` phase IDs are not directly asserted; scale endpoints 0 and 3, negative/NaN/infinite overrides, and each phase's invalid-override combination are not individually covered. Code inspection shows the range/finite guard applies uniformly before phase selection. No test establishes production wiring, phase enum validity, or application direction (more/less posture per hit); documented unwired status remains authoritative.
