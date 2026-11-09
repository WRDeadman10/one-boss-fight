# KI-177 — stateful stance-break recovery fixture

## Scope

Adds a transient-world automation fixture around the production boss actor and executor. It starts an active move, records a parry recovery, applies posture damage through the actor's production `ApplyHit` path until the posture-break transition aborts that move, then runs `EndStagger` and checks whether the pending recovery state crossed that boundary.

The fixture uses a transient copy of the proof profile for its posture values and does not save or modify the authored asset. It skips the map navigation path and optional stagger animation. It characterizes the actor lifecycle; it does not call the full `Tick` loop or prove pack/arena behavior.

## Finding

Source currently leaves `PendingParryRecoverySeconds` and `PendingParryRecoveryGrade` unchanged in both `StartStagger` and `EndStagger`. `EndStagger` calls `RecoverAfterAbort` and clears `bStartedMove`, while the recovery consumer only runs when a move is finished and clean. The test therefore records the existing pending state after abort/rearm; the consumer's later application to a subsequent move remains inferred from the separately audited Tick path.

No production behavior change is made here. Whether stance-break duration supersedes or composes with the parry-added recovery needs Lead review after the native fixture runs.

## Validation and handoff

The fixture is authored but has **not** been built or run. Claude/Lead owns the native build and automation run. If it compiles and passes, report the observed pending fields and decide the intended recovery boundary before changing production code. KI-177 remains open and unverified until that review.
