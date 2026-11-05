# E135 — reactive dodge attempt budget

**Decision:** No retry-budget policy is active; the pure rule has no attempt state. **Authority:** project owner if a runtime dodge consumer is proposed.

`RPGBossReactiveDodge::Chance` and `ShouldDodge` are stateless functions of attack kind, recent-hit count, config, and roll; there is no per-attack retry counter or generation input (`RPGBossReactiveDodgeRules.h:6-25`). E26/E76 cover the maximum hit-count edge and the minimum-int refusal (`RPGBossQueueEBoundaryTests.cpp:245-247,317-319`). The helper is explicitly unwired. The unrelated boss dodge-history/aggro observation state is not an attempt budget. No retry policy should be added or inferred without an owner-approved runtime design.

Static source/doc audit only; no build/tests run by Codex.
