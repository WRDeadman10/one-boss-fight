# E136 — retreat vertical gate

**Decision:** None is required for the current unwired helper. **Authority:** project owner if a runtime retreat feature needs a vertical constraint.

`RPGBossRetreat::ShouldRetreat` accepts range, close-range threshold, threat, and threat threshold; it has no vertical coordinate/distance input (`RPGBossRetreatRules.h:8-14`). Existing source and tests establish strict range and inclusive threat behavior, not a 3D retreat gate (`RPGBossRetreatRulesTests.cpp:9-11`; `RPGBossRetreatCloseBoundaryMutationTests.cpp:10-17`). The helper is unwired. Do not add a vertical parameter or claim vertical behavior without a concrete caller requirement and owner approval.

Static source/doc audit only; no build/tests run by Codex.
