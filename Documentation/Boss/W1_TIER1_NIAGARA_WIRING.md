# C-917 W1: opt-in Tier 1 Niagara wiring

Status: source and test changes authored; Lead build/native suite and live visual checks remain pending.

`URPGBossShockwave::Launch()` can spawn one optional `ShockwaveVFX` at the existing wave origin. `URPGPlayerParry::NotifyParried()` can spawn one optional `ParrySparkVFX` at the player chest transform; the damage resolver invokes it once for an accepted parry contact. Both soft references default empty, so the current visual paths remain unchanged. The OneBossFight module already depends on Niagara (`OneBossFight.Build.cs`).

When the authored field is empty, Development-only CVar `rpg.Art.Tier1` (default 0) selects the built-in preview assets. The CVar is excluded from Test and Shipping configurations:

- `/Game/OneBossFight/VFX/NS_Boss_ShockwaveRing.NS_Boss_ShockwaveRing`
- `/Game/OneBossFight/VFX/NS_Combat_ParrySpark.NS_Combat_ParrySpark`

An authored soft reference takes priority and remains usable in every configuration. `rpg.Art.Tier1` is compiled only for Development, so preview paths cannot be selected in Test or Shipping. Spawn counters are exposed on both components for event-level checks. Soft asset resolution currently uses `LoadSynchronous()` at the first opted-in event; KI-189 tracks the possible one-time hitch.

## Offline verification

- Native test `OneBossFight.Art.Tier1Visual.SelectionAndDefaults` checks empty/default-off, opt-in fallback selection, authored override priority, and Shipping switch absence.
- `Scripts/Tools/test_tier1_visual_wiring_contract.py` checks one spawn call per event handler, spawn counter updates only after a component is returned, optional empty fields, and the Shipping CVar guard.
- No Unreal build/automation or live PIE visual run has been executed by Codex.

## Lead checks after build

1. With both fields empty and `rpg.Art.Tier1 0`, run one A6 wave and one successful parry; each component's additional visual counter stays unchanged and the existing path remains visible.
2. With both fields empty and `rpg.Art.Tier1 1` in Development, repeat each event; the relevant counter advances exactly once per event and the corresponding Tier 1 asset appears at the documented origin.
3. In a test definition with one authored soft path, keep `rpg.Art.Tier1 0`; the authored path still spawns once. Confirm the Shipping build has no `rpg.Art.Tier1` CVar and only authored paths can select an effect.
4. Retain raw logs, component counter snapshots, asset identities, build identity, and screenshots for both routes. No live acceptance is claimed until those checks run.
