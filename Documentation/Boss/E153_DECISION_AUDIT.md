# E153 decision audit: bleed threshold rounding

Queue E's D38 reference is reposition turn-latch coverage, not bleed threshold behavior. The relevant rule is `RPGBleedRules::Apply` and its finite-input hardening audit D91; Queue E is corrected.

`Apply` accumulates `float` buildup and procs when `Buildup >= Threshold`; after a proc it sets buildup to zero and raises threshold with `Min(Threshold + ThresholdIncrease, ThresholdMax)`. Therefore threshold comparison and increment use ordinary float arithmetic with no explicit decimal rounding or epsilon. Existing exact-threshold tests assert the comparison boundary; no cross-platform bitwise rounding contract is established.

No owner decision is needed for existing code behavior. If balance data requires decimal quantization or cross-platform deterministic threshold arithmetic, the owner must specify that contract first; Lead reviews its implementation. Static inspection only; no tests/build/Editor run.
