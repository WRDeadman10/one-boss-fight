# E138 — cue jitter distribution requirement

**Decision:** None is needed before runtime wiring; current evidence supports deterministic bounded offsets, not uniformity. **Authority:** project owner if presentation requirements demand a particular distribution.

`RPGBossCueJitter::Seconds` derives a local seeded stream from `(Seed,CueIndex)`, samples an offset, and clamps to the safe interval (`RPGBossCueJitterRules.h:8-17`). Existing property coverage checks bounded output and identical-tuple repeatability across sampled indices; it does not establish statistical uniformity or runtime cue association (`RPGBossCueJitterRulesTests.cpp:9-15`). The rule is unwired, so no distribution promise should be inferred. A future product requirement for uniformity, perceptual shaping, or correlation behavior belongs to the owner before wiring.

Static source/doc audit only; no build/tests run by Codex.
