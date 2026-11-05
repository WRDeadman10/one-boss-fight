# H019 / C-804 live reset-order observation

## Setup

Run `run_pie.ps1 -OutDir <fresh evidence directory>` with the editor idle. The driver opens `/Game/OneBossFight/Levels/L_SevarogArena`, begins PIE, waits 10 seconds for the pack warm-up, wakes the pack boss, enters player combat, and starts an A4 action. After 0.8 s of the active action it calls the existing `RPGCombatDebug.debug_set_player_health(0.0)` hook, matching `Scripts/Editor/pie_player_death_reset.py`'s hook and timing pattern. Source review of `RPGCombatDebug.cpp:493-501` shows this helper only writes `Attribute.Health`; unlike `DebugKillBoss` at `RPGCombatDebug.cpp:410-415`, it does not explicitly activate `Ability.Dead`. The pack-side death/respawn response therefore remains an observation of the real PIE run. The driver also enables `rpg.Debug 2`, which `pie_debug_overlay.py` uses for the on-screen overlay and once-per-second `LogRPGDebug` lines; it is diagnostic setup, not the death trigger. No component properties are set in PIE.

## Control

Observe player health, the `Status.Dead` tag when queryable, A4 state, original/replacement pawn names and all four `[EncounterLifecycle]` tokens in the raw editor log. The driver leaves PIE running for six seconds after a differently named pawn appears, then ends PIE and quits. It does not invoke `restart_encounter_for_test`, alter selection, or perform rebind behavior.

## PASS

The raw log shows accepted A4 start, health before/after the zero write, health/death-tag samples, a changed pawn name, and timestamps/generation/reset-count values for whichever lifecycle tokens actually occur. The complete observed order and elapsed times can be reconstructed from the `timestamp=` fields. `result.json` reports a clean editor exit and raw-log SHA-256.

## FAIL

Map/setup failure, absent boss/debug component, no new pawn within 30 seconds, driver exception, timeout, or missing/stale raw log makes the run inconclusive. Do not infer an absent token from an incomplete run. No expected reset order is hard-coded; report the measured order for Claude's Step B decision.
