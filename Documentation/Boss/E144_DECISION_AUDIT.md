# E144 — actor restart proof bar

**Decision:** No new proof-policy decision is active. Actor restart remains a live proof concern; transient pack-target automation is not sufficient. **Authority:** Claude owns the documented PIE proof runs; project owner owns changes to the acceptance bar.

`RestartEncounter` requires an initialized terminal non-Failed boss and a newer generation, then validates target health and rearms the executor before clearing terminal state (`RPGFrameworkBossCharacter.h:58-59`, `.cpp:856-874`). C-778 BUILD-196 proves that a transient pack target cannot supply readable health even after target BeginPlay, so those actor tests were removed. Related live lifecycle evidence is BUILD-80/81; the actor leash transition is BUILD-121/MOV-005. These prove bounded PIE scenarios, not every terminal guard or direct executor counter edge. Keep the source-derived matrix and those scoped live proofs distinct; do not restart transient pack-target coverage without a different supported fixture.

Static source/doc audit only; no build/tests run by Codex.
