# E132 — enrage ramp reset ownership

**Decision:** None is required for the current stateless helper. **Authority:** project owner must approve the clock origin and reset semantics before any runtime integration.

`RPGBossEnrage::Progress` derives clamped progress solely from elapsed seconds and a valid config; `DamageScale` and `SpeedScale` recompute from those arguments on each call (`RPGBossEnrageRules.h:8-32`). It has no stored start time or reset API. Existing E16/E26 tests cover ramp endpoint and deterministic repeated values (`RPGBossQueueEBoundaryTests.cpp:87-107`). The unwired helper cannot decide whether future elapsed time starts at encounter, phase, or attack. Keep that caller-owned question out of the current pure rule.

Static source/doc audit only; no build/tests run by Codex.
