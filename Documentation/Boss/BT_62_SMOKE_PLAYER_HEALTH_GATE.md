# BT-62 — Smoke Player Health Acceptance Gate

Date: 2026-11-16 18:00 UTC
Status: source change prepared; awaiting fresh bound build/suite before runtime use.

The BT-62 board acceptance criteria require player health to read back as 800/800. The existing Smoke driver observed Starter, Sevarog max health, selected-card telemetry, suppression, and actor census, but it did not parse or require the route's `PlayerHealthReady` current/max health values. That omission could allow the Smoke readiness path to pass without proving the owner's approved player health.

Codex updated `Scripts/Editor/pie_sevarog_arena_route_acceptance.py` to parse the logged `outcome=PlayerHealthReady hp=... max_hp=...` fields, place both values in the receipt, and require both to equal 800.0 in the Smoke criteria and readiness predicate. Missing, unreadable, or different values fail closed. Updated `Scripts/Tools/test_c1619_sevarog_arena_route_contract.py` with source assertions for those fields; no tests were run.

This changed the acceptance-driver hash bound by C-1155. Before any route Smoke or BT-63 asset write, refresh the Development build and complete DD27j suite with the current driver hash, then use the resulting receipt for subsequent gates. BT-63's separate source-review fixes remain pending. No Unreal process, asset operation, build, suite, PIE, commit, or push occurred for this source edit. Raw BehaviorTree attack-task tick count remains `BLOCKED_NOT_INSTRUMENTED`.

## C-1155 Smoke result (2026-11-16 UTC)

Run: Saved/SevarogArenaRoute/Run_20261116_204412_a65c9e15. Runner returned SMOKE_PASS_LIFECYCLE_UNTESTED; receipt acceptance.json reports
esult=PASS, accepted=false. Observed Starter loadout, one framework boss and zero pack bosses, Sevarog max health 1500, player current/max health 800/800, production tick-selected card Move_Sevarog_Swing3_Slow, suppressed pack actor with BeginPlay=0 and no active montage, and zero pack boss HUD widgets. DefaultGame.ini restored byte-for-byte; Editor exited, 2/2 C-1155 locks released. This does not complete acceptance: boss-death lifecycle was not exercised in Smoke and RAW_BEHAVIOR_TREE_TICK_COUNTER_NOT_INSTRUMENTED remains blocked. No build/package/asset save.
