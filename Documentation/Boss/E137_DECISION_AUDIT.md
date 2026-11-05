# E137 — gap-closer live proof gate

**Decision:** No runtime proof gate is active while the rule remains unwired. **Authority:** project owner must approve any wiring and its live movement proof criteria.

`RPGBossGapCloser::ShouldClose` is a pure strict-threshold predicate; it does not execute movement or verify an endpoint (`RPGBossGapCloserRules.h:8-13`). E104/E105 and the existing boundary tests cover helper thresholds, while the D103 report explicitly leaves action execution, vertical distance, and runtime wiring unproved (`RPGBossGapCloserRulesTests.cpp:10-14`; `RPGBossGapCloserExitBoundaryMutationTests.cpp:10-16`). Current scope ends at helper correctness. If wiring is proposed, owner approval must set an authored/live movement proof bar before implementation is called ready.

Static source/doc audit only; no build/tests run by Codex.
