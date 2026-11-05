# E143 — executor hit-counter external contract

**Decision needed:** whether `AcceptedHits`, `GuardedHits`, and `ParriedHits` are internal proof/combo counters or a stable external API contract. **Authority:** project owner for any external consumer or telemetry promise.

`ApplyHit` updates counters only after resolver outcomes: Accepted increments accepted/card counts and optionally guarded; Parried increments the separate parried count; other outcomes do not (`RPGFrameworkMoveExecutor.cpp:282-300`). Accessors expose accepted, guarded, and parried counts (`RPGFrameworkMoveExecutor.h:41-46`); boss combo/fatigue logic consumes related counts. Pure resolver tests do not prove executor-level contact/counter ordering. A real executor witness still needs authored montage/window contact; C-778 forbids another pack-target transient test route. Until ownership is decided, do not advertise these counters as a general external API.

Static source/doc audit only; no build/tests run by Codex.
