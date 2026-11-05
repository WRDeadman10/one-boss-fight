# S39 — Route and selection glossary

| Term | Meaning in this project |
|---|---|
| Legacy route | Existing default startup/attachment path when no encounter definition is selected. It remains the fallback and parity control. |
| Selected/data route | Opt-in startup path that validates an `URPGEncounterDefinition`, prepares the typed definitions, and activates the registered subset for the world. |
| Selection request | A nonempty selection supplied to the runtime. A missing or invalid requested definition fails closed; it must not silently fall back to legacy. |
| Encounter definition | Authored asset naming the boss/player definition slots, initial transition phase, encounter identity, and canonical manifest hash. |
| Boss/player definition | Typed configuration for one role. Player leaves classified `NOT-COMPARABLE` on the TargetOnly path are not evidence of runtime player parity. |
| Slot | Stable role-specific name used to identify a boss or player definition reference in the encounter asset. |
| PhaseTwo | The G044 phase-transition record chosen by C-824. Its name does not say that combat starts in phase two. |
| Preflight | Validation/preparation stage before activation. A refusal is a hard error; it is not a partial success or permission to attach the legacy bundle. |
| Activation | Runtime operation that configures/registers the selected subset and reports its result. `ActivatedRegisteredSubset` and `LegacyNoSelection` are distinct outcomes. |
| Participant / role | Runtime boss or player actor associated with a role and selected definition slot; parity evidence records actor identity and generation/reset state. |
| A5 parity pair | One fresh-process legacy control and one fresh-process selected-data run using matching driver inputs and identities. Both per-arm checks and receipt comparison are needed. |
| Run receipt | Structured record of route, run identity, terminal result, checks, activation, participants, components, observables, and their evidence references. |
| Comparator report | Deterministic PASS/FAIL/INCONCLUSIVE result from paired receipts. A PASS under declared WARN rules is not proof that every raw number is equal. |
| WARN | A declared stochastic, sampled, or boundary-sensitive difference retained in the report while its scenario rule passes. WARN is not a hidden mismatch waiver. |
| Shipping selector | Owner-approved Blueprint setter route (J049=A). It is separate from the Development console variable and benchmark command-line selector; no current content caller was found in C-876. |
| A7 release gates | Owner evidence gates before legacy retirement; passing A5 parity alone does not close them. |

Primary references: `Documentation/Boss/G044_ENCOUNTER_SELECTION_PIE_EXPECTED.md`, `Documentation/Boss/P15_A7_PARITY_SUMMARY_DRAFT.md`, and `Documentation/Boss/S36_A5_PARITY_OPERATOR_RUNBOOK.md`.
