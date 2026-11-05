# E131 — difficulty configuration ownership

**Decision:** None is required while difficulty scaling is unwired. **Authority:** project owner must identify the normalized difficulty source and approve bounds/profile ownership before integration.

`RPGBossDifficulty::Evaluate` accepts a normalized `[0,1]` value and bounded damage/speed/telegraph endpoints; invalid input returns neutral scales (`RPGBossDifficultyRules.h:8-25`). Existing endpoint and mutation tests exercise this pure mapping (`RPGBossDifficultyRulesTests.cpp:10-17`, `RPGBossDifficultyEqualEndpointsMutationTests.cpp:10-19`, and Queue E D97 cases). The helper does not select a player difficulty, read settings, or persist configuration. No such ownership decision is active until a wiring proposal exists; do not choose one in the helper.

Static source/doc audit only; no build/tests run by Codex.
