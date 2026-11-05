# E134 — punish limiter design approval

**Decision:** No approval is required while the limiter remains unwired. **Authority:** project owner must approve max-use semantics and encounter reset scope before a caller is added.

`RPGBossPunishLimiter` is a stateless-with-respect-to-time count helper: it permits a use only for `0 <= Uses < MaxUses <= 100`, increments on an accepted use, and resets the count (`RPGBossPunishLimiterRules.h:8-18`). It has no clock/cooldown contract; defensive-card cooldown is a separate rule. Tests exercise cap and corrupt-state behavior (`RPGBossPunishLimiterRulesTests.cpp:9-16`, `RPGBossQueueEBoundaryTests.cpp:306-308`). The helper is explicitly unwired, so neither rate limiting nor a design approval is implied by its tests.

Static source/doc audit only; no build/tests run by Codex.
