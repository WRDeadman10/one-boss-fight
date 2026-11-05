# E128 — poise regeneration integration status

**Decision:** No integration decision is active; the rule remains explicitly unwired. **Authority:** project owner must approve any runtime wiring or authored values.

`RPGBossPoiseRegen::Rate` is documented “Unwired by design” and computes a bounded rate from base, post-hit delay, ramp duration, and max scale (`RPGBossPoiseRegenRules.h:6-19`). Existing tests cover representative delay/ramp behavior and zero-ramp refusal (`RPGBossPoiseRegenRulesTests.cpp:8-17`, `RPGBossPoiseRegenZeroRampMutationTests.cpp:6-16`). No runtime consumer or profile integration is part of this task. Do not infer a regeneration rate or enable it from these tests; owner approval is the gate if implementation is proposed.

Static source/doc audit only; no build or tests run by Codex.
