# E-004 Bot-driven natural samples (CI-P0-C-01), 2026-10-25

Diagnostic samples, bot-driven (existing `Scripts/Editor/pie_build_fight.py`, unchanged), NOT human play and NOT frequency estimates. One run per configuration, Starter build, same map, editor binary as in E-001. Observer: `probes/p0_natural_montage_log.py` (read-only getters, polls the boss's active montage every tick; a montage that starts and ends between two ticks, or restarts under the same name, is not seen; dynamic montages have generated names `AnimMontage_N`). Runner: `probes/p0_run_natural_sample.sh <label> <build> <wake> <telegraph> <legend>`.

## Harness validity finding (read this first)

The editor window was MINIMIZED (user32 `IsIconic` true at 10:5x IST) when samples A0 and B0 ran: PIE ticked at about 2.8 frames/s (editor log frame counter: 23 frames in 8.15 s of the 12 s ability-dump driver; 177 frames in 60 s during sample B0). At that rate the bot's swings whiffed, the tracker first saw each stage at montage position 0.34 s (one frame) and the boss "stood idle" for about 400 s. Both runs are invalid as behavior evidence and are kept only as `natural_sample_A0_..._INVALID_3fps*`, `natural_sample_B0_..._INVALID_3fps.txt`, `BalanceRun_A_*`, `BalanceRun_B0_*`. Restoring the window without activating it (`ShowWindowAsync(h, SW_SHOWNOACTIVATE)`) gave 106 frames in 3.0 s (about 35 fps) and the valid runs below logged 32.3 to 34.2 frames/s. Setting `bDisableRealtimeViewportsInRemoteSessions` to false (probe `p0_realtime_remote_on.py`, in memory only) had NO effect on the frame rate. Operational lesson (add to PROJECT_STATE gotchas): a minimized editor window makes every timing driver fail; check `IsIconic` before a run. The 2026-10-24 successful bot run ran at about 17 fps by the same frame-counter method (frame counter wraps at 1000).

## Valid samples

| Sample | Config at start (observer line) | Outcome | Files |
|---|---|---|---|
| A2 defaults | `rpg.WakeClip` 1, `rpg.CloseTelegraph` 0.4, `rpg.Legend` 0, build Starter, 32.4 to 34.2 fps | boss_dead at 140.0 s of fight time; boss 2000 -> -13 (1013 weapon hits + 1000 riposte impact); bot took 1 hit (A3b, 36 health) | `exports/natural_sample_A2_defaults_Starter_valid.txt`, `exports/BalanceRun_A2_defaults_20261025T054422_b71de62b_Starter.json` |
| B warm | `rpg.WakeClip` 0, `rpg.CloseTelegraph` 0, `rpg.Legend` 0, build Starter, 33.0 to 34.2 fps | player_dead at 24.4 s; boss 2000 -> 1775; bot took 4 hits for 144 (A1b x3, A3a x1) | `exports/natural_sample_B_warm_Starter_valid.txt`, `exports/BalanceRun_B_warm_20261025T054726_658f064d_Starter.json` |
| A1 defaults (observer partial) | same as A2, observer crashed on a time call | boss_dead at 139.9 s | `exports/natural_sample_A1_defaults_Starter_valid33fps_observer_partial.txt`, `exports/BalanceRun_A1_defaults_*` |

(`rpg.Legend 0` was chosen to match the RunDrivers harness; it is not the shipped value of 1.)

## Observed montage starts (observer, per sample)

- **A2 defaults:** named boss montages: `GS_ChargedAttack_Montage` x2 (A2, at 17.15 s and 20.29 s, player 134 to 139 cm away), `AM_Boss01_A3b` x1 (23.11 s), `GS_EquipWeapon_Montage` x1 (enter combat, 16.22 s); all others are dynamic montages named `AnimMontage_N` (the stagger, riposte, roar and clip players; their identity is not resolvable from the name). Phase two started about 67.8 s (observer flags `phase_two=True`, `transition=True` at 67.76 s). **No `Mid01`, no sprint follow-up, no retaliation montage in this fight.** The `AM_Boss01_A1` and `GS_Attack04` (A1b) montages did not occur either.
- **B warm:** `GS_ChargedAttack_Montage` x3, `GS_Attack04_Montage` x3 (A1b), `AM_Boss01_A3a` x2, `AM_Boss01_A1` x2, `GS_EquipWeapon_Montage` x1, **`Mid01_Anim_Montage` x1 at t=16.51 s with the player 129 cm away** (the bot dodged it; no hit), dynamic montages for the rest. No sprint follow-up, no retaliation.
- The first dynamic montages at t=0.43 and t=9.4 are wake/dormant clips played before the fight starts.

## What this supports and what it does not

- Supports (observed once): the pack MidRange montage (`Mid01`) does occur in a real fight; it started while the player was at 129 cm, a distance the BT assigns to the Close branch (< 250), so the decision was made earlier at a larger distance, or another path started it (not resolved; read the behavior state at the moment of selection next).
- Does NOT support: any frequency, any claim about sprint or retaliation (not seen in two short fights), any claim about human play, A5 (the bot never heals), or that the defaults fight is balanced (one bot win in 140 s and one bot death in 24 s are one sample each). The tracker fields `tracker_phase`/`tracker_move` logged by the observer are sampled on the first tick of a montage and mostly read None (a montage is first seen before the tracker's own tick has classified it): do not use them as stage evidence.
- Historical comparison (mutable files, 10-24, Starter win 138.5 s, Strength win 140.2 s, Dex player death) is in `exports/historical/`.

## Integrity

Hashes at capture: see the table at the end of this file.

```
ba384cce674a8e87618577d97d195b754f8cc8b38ffad64b778d68b3dabc0244 *probes/bt_t3d_tree.py
4fc9f0ea757e62b22ca96d617db96fbe8b58579e9069c9d0bbfb74f999cc018a *probes/p0_cvar_state.py
cc7a25637e8eacda83378644865f6c365724a7bd5c5f7cd20b70ba5f8eb4c041 *probes/p0_editor_perf_settings.py
a48651c178bf938b68090e79c9042d5734db1136873f341920f8cee5cc3b4c19 *probes/p0_export_text.py
11bf9f9debcedd7024514f2663f96aff428f9b9992996c259c46df13c9056e9a *probes/p0_montage_notifies.py
971853c17647e406df18afd98a8996c7c83c17f75eac238a94be474c7de15981 *probes/p0_natural_montage_log.py
4d88b155c00f8b0f918ccb8b2804a18b4ceefed30fc2f9efb7d52731ee0cf685 *probes/p0_realtime_remote_on.py
34b13b1c50dd8de8a7bdf479a6aace84f39eb37284575f70cc19ee1be0f92bc2 *probes/p0_set_cvars.py
365a535c4af7ead42066860d2bbdf4ee336f4b4d348ef3dff0b9ad53eb403dd7 *probes/p0_run_natural_sample.sh
4c3e4cfc912dc9a1275084771b1878f4c98b28a3e82348b065f4e68c2191db02 *Scripts/Editor/pie_build_fight.py
0712da978d5f28843e62d75b0d5027bbaf9a40a4c786fafc4a914ef211fc23b7 *exports/natural_sample_A2_defaults_Starter_valid.txt
6ee6d7b8763c1fe184239f462010365271806d15aae12333e04f7beb9bc27c3c *exports/natural_sample_B_warm_Starter_valid.txt
06b2825876e0b3900fa71412432972eb3c34f7daa40d16f6e27eec14bd48d9d9 *exports/BalanceRun_A2_defaults_20261025T054422_b71de62b_Starter.json
683a297187fa982e83e560e28f5546726e7ac4b68eebd898b9773b9bca97b5d5 *exports/BalanceRun_B_warm_20261025T054726_658f064d_Starter.json
```
