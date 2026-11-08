# Queue AL C11–C15 — full-fight PIE driver port

Ported the retained `Docs/BossCombatReview/Execution/Claude/P_FIGHTVIDEO/pie_full_fight.py` into `Scripts/Editor/pie_full_fight.py` under Claude's engine lock. This is offline authoring only; no PIE, frame capture, build or ffmpeg render was run.

| Task | Result |
|---|---|
| C11 | Mapped retained actor/component lookup, health, montage, game time, enter-combat, placement, refill and end-play to `pie_lead_common.py`. The retained full-fight driver uses [FullFight] markers and `f_%05d.png` frames at 15 fps. |
| C12 | Shared-helper substitutions are explicit: `plc.component`, `boss_actor`, `player_montage`, `game_time`, `enter_combat`, `place_player`, `boss_debug`/`refill_player` and `end_play`. Max-health read remains local because the helper supplies only current health. Missing-health exceptions still return `None`. FRAME/ACTION/COUNTER/BOSS_DEAD/SUMMARY/finished log grammar remains. |
| C13 | Preserved player refill below 35 HP, boss health/AI untouched, `slomo 0.5`, game-time `g` deltas, 15-fps capture and pending-PNG wait. `ER_FIGHT_TIER2=1` sets `rpg.Art.Tier2 1` before PIE request; absence sets 0. This is a Development-only opt-in, and PIE must verify console command reachability. |
| C14 | `python -I -m unittest discover -s Scripts/Editor -p test_pie_full_fight_offline.py` passes 4/4. Fake-Unreal tests verify 15-fps game-time capture waits for the prior PNG, Tier 2 default/off versus opt-in command before PIE, retained action cycle, refill threshold and marker presence. No editor module is needed in the offline process. |
| C15 | Lead smoke: run both encounter routes with a bounded fight, inspect actual [FullFight] log and frame-folder count/sequence, verify Tier 2 cvar readback and player refill; then feed the log/frames to `make_fight_video.py`. Runtime behavior and visual quality are not claimed by the offline tests. |

One intentional behavior change: `plc.place_player` sets both pawn and controller yaw to 180° during setup, while the retained driver set pawn yaw only and later faced the boss each fight tick. Lead smoke should check that this does not alter early draw/capture. `plc.enter_combat` now raises a clear error when the player ASC is absent, whereas the retained driver would fail on a missing component without that diagnostic.
