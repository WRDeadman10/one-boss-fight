# E129 — unknown phase policy

**Decision:** None required while the pure helper remains unwired. **Authority:** project owner if phase representation or runtime application changes.

`RPGBossStaggerResist::Scale` accepts finite phase scales in `[0,3]`, returns phase-one/phase-two values for IDs 1/2, and neutral scale `1` for every other integer or invalid scale (`RPGBossStaggerResistRules.h:8-12`). Existing tests exercise phase 3 and phase 0 with non-default scales (`RPGBossStaggerResistRulesTests.cpp:9-12`; `RPGBossStaggerResistUnknownPhaseMutationTests.cpp:10-14`). The helper is documented unwired, so this fallback is not yet a production phase-enum policy. Keep neutral fallback unless an owner-approved phase schema/wiring proposal requires a different behavior.

Static source/doc audit only; no build or tests run by Codex.
