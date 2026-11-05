# E142 — executor window-count observability

**Decision:** No public telemetry promise is established. **Authority:** project owner if external diagnostics are expected to depend on `OpenWindowCount` semantics.

The move model owns the open-window set and clears it through terminal cleanup; executor exposes `OpenWindowCount()` as a read-only accessor (`RPGBossMoveModel.h:73-76`, `RPGBossMoveModel.cpp:125-149`, `RPGFrameworkMoveExecutor.h:90`). Existing model tests assert close/abort events and idle state, while the executor harness checks cleanup and retry; no public document establishes the count as a stable external contract. Treat it as test/diagnostic observability until the owner requests a telemetry contract.

Static source/doc audit only; no build/tests run by Codex.
