# Framework executor damage accounting

The executor keeps actor-lifetime contact/damage totals and separate per-card contact state. Read the counters with their owner and reset boundary; do not sum cumulative `CARD_END` values as if each were a card delta.

## Counter scope

| Counter | Scope / reset | Meaning |
|---|---|---|
| `HitsAccepted` | Executor lifetime; initialized to 0 with the component, not reset by `StartCard` or `Rearm`. | Count of accepted resolver outcomes across attacks and generations. |
| `HitsGuarded` | Executor lifetime; same reset boundary. | Accepted contacts observed as guarded. These can still apply chip damage if the profile enables it. |
| `HitsParried` | Executor lifetime; same reset boundary. | Resolver `Parried` outcomes. Kept separate from accepted-hit count. |
| `AppliedDamage` | Executor lifetime; same reset boundary. | Sum of actual resolver `HPApplied`, including chip-adjusted applied amount, not nominal card damage. |
| `CardAcceptedHits`, `CardParriedHits` | Reset for each `StartCard` (`RPGFrameworkMoveExecutor.cpp:128`). | Current-card contact decision used for completion/fatigue/combo semantics; not the public lifetime totals. |
| Boss `ExpectedTargetHP` | Initialized from target health at encounter start and reset at `RestartEncounter`; decremented when the framework executor (or the boss's I-frame proof probe) records actual applied damage. | Expected target health used by the boss invariant; it is not a standalone source attribution ledger. |

The lifetime fields are declared in `RPGFrameworkMoveExecutor.h:41-59`; increments occur on accepted contacts in `RPGFrameworkMoveExecutor.cpp:291,413`. `CARD_END` formats `HitsAccepted` and `AppliedDamage` directly (`:206`), so those two fields are cumulative executor totals at that card boundary. `FrameworkProof invariant` reports the target's before/after and expected health plus the same lifetime total accepted/damage values (`RPGFrameworkBossCharacter.cpp:615`). A restart advances the generation but preserves executor totals (`RPGFrameworkMoveExecutor.cpp:96-107`; `FRAMEWORK_BOSS_RESET_GUIDE_S145.md`).

## Reconciled retained example

Evidence: `Docs/BossCombatReview/Execution/Claude/B_AWR004/pie_run1/editor_raw.log`.

| Evidence | Values | Check |
|---|---:|---|
| Initial target HP (`invariant`, line 2002) | 800 | Starting point |
| Accepted hit records (lines 1628 and 1900) | 35 + 35 HP | Two accepted contacts |
| Final target HP (`invariant`, line 2002) | 730 | `800 - 730 = 70` |
| Lifetime accepted/applied (`invariant`, line 2002) | 2 / 70 | Matches two hit records and health delta |
| `RESULT` (`line 2003`) | 2 accepted hits, 3 attacks | Third attack slot did not add damage; attack count is not accepted-hit count |
| `CARD_END` rows (lines 1728, 1851, 2000) | 1/35, 1/35, 2/70 | Cumulative executor totals, not per-card deltas; card 2 contributes no accepted hit |

For a general reconciliation, sum actual `hpApplied` over damage records for the run/generation, compare that sum to the corresponding target-health delta, and compare to executor lifetime values only after accounting for any earlier generations and any non-card probes. Do not add the `CARD_END` totals across cards. A nonzero `RejectedDuplicate`, rejected, or zero-application outcome contributes zero applied damage. Other actors can change target health outside this executor; a mismatch is evidence to investigate, not permission to relabel the difference as executor damage.

## Source references

- Counter declarations and read-only accessors: `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.h:41-59`.
- Reset/start/increment/logging: `RPGFrameworkMoveExecutor.cpp:96-128,206,286-291,408-413`.
- Boss invariant and target-health expectation: `RPGFrameworkBossCharacter.cpp:615-623`; restart expectation reset: `:861`.
- Generation reset semantics: [FRAMEWORK_BOSS_RESET_GUIDE_S145.md](FRAMEWORK_BOSS_RESET_GUIDE_S145.md).
