# C-1138 matched-range parry-close driver

Date: 2026-11-09  
Scope: Lead-requested driver-only adjustment for a matched-range A/B. No gameplay Source changes and no Unreal/Editor/build/PIE activity by Codex.

## Driver changes

- `FIGHT_PARRY_ONLY=1` now uses the same 115–125 cm control band and >130 cm reposition guard as `PARRY_ONLY_CONTROL=1`. Both modes share the same helper, start placement, movement thresholds, and range log; the control mode still sends no parry or attack input. The parry mode's 260 cm approach path is removed.
- The read-only pack-tag snapshot records `Status.ParryActive`, `Status.Blocking`, `State.Blocking`, `Ability.Parry`, `Ability.Block`, and `Status.Invulnerable` as true/false/UNKNOWN on parry attempts, observed damage drops, and montage contact samples.
- `PACK_IMPACT_SAMPLE` records montage/move/instance, expected contact marker, sampled montage position, player HP and tag snapshot at each timing marker available from the C-1132 hit observations. The driver's exposed native/runtime interfaces do not expose the pack Blueprint `SM_ImpactDecision` result, so `pack_impact_outcome=UNKNOWN` is explicit; no impact outcome is inferred from resolver counters. `PLAYER_HIT` also captures tags with the actual sampled HP decrease.

## Lead run interpretation

Run `PARRY_ONLY_CONTROL=1` and `FIGHT_PARRY_ONLY=1` after resetting to the same baseline, build, map, route and player health. Compare each real damage/contact window by montage position, player HP, range and `player_status_tags`. `ParriedCount=0` is expected for pack boss contacts because the native resolver owns project A4/A5/A6 geometry only. A no-damage event with active `Status.ParryActive` is evidence that the pack suppressed damage, but pack reward/recoil is still unknown unless the pack itself exposes a response log/state. Mark missing contact or missing impact signal inconclusive.

## Validation limits

The initial C-1138 post only ran Python syntax compilation. C-1139 updated the stale offline source contract to assert the shared range-step helper and no-input control behavior; the full offline driver suite then passed 39/39, Python compilation and scoped diff check passed. Lead owns the control/dodge captures and the subsequent matched-range parry-close run. No runtime result is claimed here.
