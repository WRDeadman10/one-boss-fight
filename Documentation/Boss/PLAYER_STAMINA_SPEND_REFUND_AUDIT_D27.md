# Player stamina spend/refund audit (Queue D27)

Scope: source inventory of maintained player-side stamina mutations, separating direct parry cost from melee differential adjustments and pack-owned baseline costs. No Source changes or test/build/Editor/PIE run.

## Maintained C++ mutation points

### Parry press: `URPGPlayerParry`

- Cost defaults to zero. A development CVar may supply a proof cost when the configured value is zero (`Source/OneBossFight/Player/RPGPlayerParry.cpp:13-15,69-78`). Nonfinite/negative cost is refused; zero cost bypasses attribute access.
- For positive cost, the component reads current `Attribute.Stamina`, requires `RPGParryCost::CanPress`, then writes the full cost before calling the pure window/cooldown rule (`:80-95`). A failed read/insufficient balance/write returns without opening the window. The exact-cost/refusal rule coverage is in `RPGParryCostTests.cpp:8-30` and `RPGParryTests.cpp:42-58`.
- If cooldown refuses after the cost was written, it saves the pre-press value and attempts to restore it (`:95-108,147-157`). Failed restoration stays pending for later component ticks and bounded EndPlay retries (`:30-42,182-186`). This is snapshot restoration, not a compensating-delta ledger; no concurrent attribute-mutation fixture exists.
- An accepted charged press remains pending until the parry window closes. A resolver-confirmed parry marks the pending attempt (`RPGPlayerParry.cpp:138-145`); on close, the component refunds half the paid cost, capped at readable maximum stamina (`:158-170`). Whiffs retain full cost. If current stamina cannot be read, it retries up to five times; after the retry limit pending bookkeeping is cleared. If the max read fails, the source fallback adds half cost without a cap (low unverified KI-176). Refund write failures retry up to five attempts, then clear pending state; EndPlay also attempts bounded completion (`:147-185`).
- `RPGParryCostRules.h:15-27` defines the pure charge/half-refund arithmetic; `RPGParryCostTests.cpp:21-30` covers half refund, whiff full cost, zero-floor, max cap, and invalid inputs. These tests do not exercise component read/write failure retries.

### Melee attack: `URPGSwingTracker`

- The maintained tracker observes pack montage starts, classifies melee swings, and looks up a weapon/kind row (`Source/OneBossFight/Player/RPGSwingTracker.cpp:214-247`). It treats the pack's `GE_MeleeAttackCost` baseline as 15 via `PackStaminaCost` (`RPGSwingTracker.h:53-59`); that base payment is pack-owned and not performed by this tracker.
- If table costs are enabled and the row cost is nonnegative, it computes only the difference from the assumed pack cost (`RPGSwingTracker.cpp:248-266`; `RPGSwingRules.h:45-56`). A positive difference is limited to the current stamina; a negative difference refunds the cheaper-cost amount. `AddStamina` requires readable current and max stamina and clamps the write to `[0, max]` (`RPGSwingTracker.cpp:204-212`).
- The initial current-stamina read used to bound extra cost ignores its success flag and starts from zero (`:258-261`). If a positive adjustment cannot be read/written, no extra mutation is recorded and the pack baseline remains; a negative adjustment also does nothing if either read or the write fails. There is no retry, saved pre-charge snapshot, or later rollback for this differential. The tracker records `StaminaExtra`/`StaminaExtraTotal` only after `AddStamina` succeeds (`:261-269`).
- Pure tests cover positive differential, negative refund, baseline equality, current-stamina clamp, and no-floor behavior (`RPGAutomationTests.cpp:568-578`; duplicate rule checks `RPGCodexTests.cpp:110-112`). They do not test attribute adapter failures, pack baseline mismatch, interrupted montages, or runtime payment timing.

## Other inspected paths and boundaries

The full `Source/OneBossFight` search found no other maintained `Attribute.Stamina` writes or direct `StaminaCost` mutation path. `RPGHitIntake` reads/logs table cost data, and combat debug displays stamina; neither performs the mutation. Pack abilities and Gameplay Effects may spend stamina outside these C++ files. This audit does not inventory or claim their complete behavior beyond the pack-owned melee baseline used by the swing tracker.

## Summary

Maintained code has two player-side paths: direct optional parry charge/refund with cooldown rollback and bounded retries, and a melee-table differential layered over the pack's assumed 15-point cost with no differential retry/rollback. KI-176 remains the unverified uncapped parry fallback. Attribute component failures, simultaneous external stamina changes, and pack-owned non-melee ability costs need isolated/live evidence; no new defect is asserted from this source inventory.
