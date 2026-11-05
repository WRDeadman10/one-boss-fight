# E127 — bleed saturation reachability

**Decision:** None required for the current defensive saturation. **Authority:** project owner if future gameplay design changes proc-count or threshold behavior.

`RPGBleedRules::Apply` validates nonnegative proc state, resets buildup on one threshold crossing, increments only while `Procs < MAX_int32`, and caps the next threshold at `ThresholdMax` (`RPGBleedRules.h:56-70`). C-757 selected saturation at the integer maximum; the focused regression is `RPGCodexTests.cpp:97-99`. Runtime bleed state is reset during initialization and generation restart (`RPGFrameworkBossCharacter.cpp:79,865-874`). Ordinary fights cannot approach the counter limit, and saturation preserves a valid proc outcome without signed overflow. D93's historical reachability concern is closed. No need to change UI, telemetry, or proc semantics. Static review only; no tests run by Codex.
