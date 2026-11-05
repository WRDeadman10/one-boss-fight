# Cue jitter seeded-property audit (Queue D104)

**Scope:** static source/test comparison for deterministic per-cue time jitter. Helper is documented unwired; no tests were run.

`Source/OneBossFight/Player/RPGBossCueJitterRules.h:8-17` rejects negative cue index, nonfinite base/jitter/safe endpoints, negative jitter/safe minimum, or reversed safe interval by returning 0. It hashes `(Seed,CueIndex)` into a local `FRandomStream`, samples an offset in `[-JitterSeconds,+JitterSeconds)`, adds it to base, then clamps to the safe interval. No shared stream or mutable sequence state is retained, so same input tuple is repeatable and cue order cannot consume another cue's random draw.

`Source/OneBossFight/Tests/RPGBossCueJitterRulesTests.cpp:9-15` samples 1000 cue indices under one fixed seed, asserting every result lies within [.8,1.2] and each repeated identical tuple matches exactly; it also checks a negative safe minimum returns 0.

Gaps: no direct different-seed or different-index inequality assertion; no exact safe endpoint clamp cases; no nonfinite or negative jitter/base/cue-index tests; invalid input's zero sentinel is not disambiguated when zero itself lies in the safe interval. The test proves deterministic repeatability for sampled tuples, not statistical uniformity or runtime cue association. A separate `RPGBossTrack::ReactionDelaySeconds` property suite in `RPGFrameworkRuntimeTests.cpp:549-560` is distinct from this cue jitter helper and must not be conflated with it.
