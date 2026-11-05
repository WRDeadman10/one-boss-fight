# Player death during parry audit (Queue D29)

Scope: source-only trace of player death/unpossess while a parry window, owned tag, or optional stamina settlement is active. No tests, build, Editor, or PIE run.

## Lifecycle and callback paths

- The parry component has no timer or death/unpossess delegate. It samples world time in `IsWindowOpen`; its only periodic work is component Tick, which retries input binding, clears the owned tag once the window is closed, and settles a pending stamina cost (`Source/OneBossFight/Player/RPGPlayerParry.cpp:24-42,111-116`). There is no delayed parry callback that can later restore input or reopen a window.
- `Press` has no owner-health, `Status.Dead`, or possession check before charging stamina and calling the pure window rule (`RPGPlayerParry.cpp:64-108`). With the default zero cost, a still-live component can open a new timed window after death if its bound input callback remains callable. Whether the pack disables input or removes/replaces the pawn on death is not established by this native source review.
- `EndPlay` makes bounded stamina/tag cleanup attempts, then calls `Super`; it does not unbind the Enhanced Input action or reset `RPGParry::FState` (`RPGPlayerParry.cpp:182-186`; binding at `:45-60`). Thus teardown cleanup is tied to component destruction, not death/unpossession. Existing KI-175 separately covers possible state retention if the same pawn/component is reused across respawn/repossess; this audit does not duplicate that issue.
- At contact, `URPGDamageResolver` requires readable positive target health and absence of `Status.Dead` before computing invulnerability/parry eligibility (`Source/OneBossFight/Player/RPGDamageResolver.cpp:141-154`). A dead target therefore rejects before parry notification or damage; no stale parry callback can award a parry/refund after that gate. Lethal accepted damage is recorded as lethal at the contact site (`:154-163`); subsequent death handling is pack-owned in this audit's player scope.

## Coverage and disposition

- Pure tests cover window/cooldown schedules and the resolver decision for a dead target (`Source/OneBossFight/Tests/RPGParryTests.cpp:9-40,42-62`). They do not instantiate the parry component, kill/unpossess a player during an open window, invoke the lingering input binding, or inspect tag/stamina cleanup.
- No stale timer callback exists in the reviewed parry component. The source-visible boundary is instead conditional: death does not itself close the time window or suppress `Press`; correctness therefore depends on the pack disabling/removing input or destroying the pawn/component. Verify that lifecycle and tag behavior in a focused runtime test before changing production code. No runtime defect is claimed.
- Existing evidence establishes pure-rule behavior only; it does not prove death/unpossess teardown or current pack behavior.
