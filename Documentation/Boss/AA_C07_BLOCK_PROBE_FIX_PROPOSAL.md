# AA-C07 — Block probe fix proposal

## Scope

Probe-only change. Do not change guard gameplay, damage, input mappings, or ability behavior: the owner confirms L1 blocking works (C-953).

## Proposed v5 changes

1. Treat player viability as a precondition: require health and stamina above zero before starting either arm; report and abort an arm if the values become invalid. Keep the existing per-tick refill only as a labeled test control.
2. Keep player and boss animation observations separate. Require an observed player equip/combat transition before a guard arm; never use a boss montage as proof of player weapon state.
3. Log the specific authoritative tag checks used by `RPGBossDamage::HasTag` (`Status.Blocking`, `State.Blocking`, `Ability.Parry`, `Ability.Block`, `Status.ParryActive`) alongside the broad owned-tag dump. Record both input delivery and state samples on a common game-time timeline.
4. Add an optional Development-only framework-hook run using `rpg.BossProofPlayerGuard=3` (mapped combat toggle followed by the real `IA_Block` action) where the fixture is present. Keep the independent gamepad and direct-action arms so the three paths remain distinguishable. If the fixture/hook is absent, report unsupported and do not claim a failed block.
5. Test-first: add offline coverage for precondition rejection, actor-vs-boss montage attribution, and tag-sample formatting; run syntax/fixture checks before handing the script to the Lead. Lead performs the live PIE run and supplies the log for acceptance.

## Acceptance evidence

The report must show a living player, a player-side combat/equip observation, the selected input path, and explicit guard tag samples. A missing action or tag is a probe result only; no game-side fix follows without separately reviewed gameplay evidence.

## Status

Proposal only. The current v4 remains unchanged until the test-first implementation is ready. No Source/Config/Content gameplay changes are proposed.
