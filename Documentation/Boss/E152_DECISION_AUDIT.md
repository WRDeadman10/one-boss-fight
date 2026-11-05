# E152 decision audit: leash overflow policy

Queue E's D37 reference is detector-edge coverage, not leash radius; the matching source audit is D40. Queue E is corrected.

`RPGBossLeashRules::IsOutsideArena` validates all position/center components and radius for finiteness, returns outside on invalid input, then uses planar distance and strict `>` against positive radius. Equality is inside. It does not square radius or manually accumulate squared coordinates, so there is no radius-squaring overflow path in this helper. The actor-level transition remains a separate runtime proof boundary.

No designer policy is needed for this pure helper. Any change to invalid-input behavior or vertical-distance semantics needs owner approval; runtime transition acceptance is Lead-owned proof. Static inspection only; no tests/build/Editor run.
