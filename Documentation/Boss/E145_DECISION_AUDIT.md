# E145 — transient-world harness sufficiency

**Decision:** None is needed for pure model/rule tests; transient pack-target initialization is explicitly insufficient for actor-level health behavior. **Authority:** project owner if a future test architecture changes the harness boundary.

Native rule/model tests need no world. The executor lifecycle harness can test wrapper state with synthetic setup, but authored montage/contact proof requires real assets and an advancing animation world (`EXECUTOR_ABORT_WATCHDOG_HARNESS_DESIGN_D13.md`, “Harness feasibility and limits”). BUILD-195/196 established a separate limit: proof initialization with a pack target in a transient world fails `Framework.Boss.TargetHealth` even after dispatching target BeginPlay; C-778 ordered its removal. Keep the harness split explicit: pure/model and pack-free lifecycle cases are valid within their assertions; actor health, target-fault and authored contact outcomes require live PIE evidence or a separately approved viable fixture.

Static source/doc audit only; no build/tests run by Codex.
