# E147 decision audit: selector memory lifetime

`FRPGBossMoveSelector::Reset` clears per-card cooldown clocks, repeat history, started-count seed offset, and cone-inside memory. Encounter generation reset calls the selector reset before evaluating the lower clock of the next generation. Within a generation, `NoteStarted` records only real starts; completion does not erase cooldown/repeat history. `SELECTOR_REPEAT_MEMORY_LIFECYCLE_AUDIT_D6.md` maps the current behavior and coverage.

The current rule is explicit enough for existing encounter semantics; no new policy is required. Whether memory should survive actor/component replacement is a lifecycle/product decision not established by these pure selector APIs. Owner decides if that replacement behavior becomes a shipped contract; Lead owns implementation review.

Verification: static source/test inspection only; no tests/build/Editor run.
