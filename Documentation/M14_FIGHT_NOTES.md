# M14 fight notes: the balance-run bot (`Scripts/Editor/pie_build_fight.py`)

Written 2026-10-22 by a writable helper that could not run the editor, a build, PIE or any script that needs them: the driver was only read-checked, `ast.parse`d and checked for unbound names. **It has never run.** Expect the first run to be a debugging run; every log line says what the bot decided and why so that the failure can be read off the log. Nothing existing was edited (no `RunDrivers.ps1` row, no TASKS or MILESTONE_GATE3_CODE change: M14 stays Todo until a run exists).

## 1. What it is

A scripted player bot fights the REAL boss (not held: no `hold_for_test`, the pack's behaviour tree runs) with the build in `Saved/build_fight_build.txt` (`Starter`, `Strength` or `Dex`, default `Strength`, read at import, BOM tolerated). It ends on boss death, player death or 240 s of world time from the wake. It logs balance metrics for a human (`[BuildFight] METRIC ...` lines, also written to `Saved/build_fight_result_<Build>.txt`). The ten checks (S1 to S10) are SANITY only and are always evaluated, so `RESULT n/m passed` always has m = 10, also when the fight is lost: parts exist, boss slept, build equipped before the wake, fight started, boss attacked, bot swung and the intake was bound, weapon never changed, outcome is one of the three, metrics logged, no error.

Per the M14 row it is a driver plus the owner's feel test: the driver proves nothing about balance by itself.

## 2. How to run

1. Editor open on `L_SevarogArena`, bridge up, warm-up done (`no_throttle.py`, `legend_off.py`, `build_off.py`, `pie_debug_overlay.py` once after an editor start: PROJECT_STATE says the first PIE after an editor start has player health 0; `RunDrivers.ps1` does this warm-up itself). `legend_off.py` matters: hit stop and slow motion would stretch the world clock the bot reads.
2. Pick the build: `Set-Content Saved\build_fight_build.txt Strength -Encoding ascii` (or `Dex`, `Starter`).
3. `MSYS_NO_PATHCONV=1 python -I Scripts/run_in_editor.py Scripts/Editor/pie_build_fight.py`. The driver sets `rpg.Build` before the PIE begins, waits for the loadout while the boss sleeps, and clears `rpg.Build` in `finish()`.
4. Read `Saved/Logs/OneBossFight.log` for `[BuildFight]`. A real fight is about 40 s of setup plus up to 240 s of fight: the driver stops itself 420 real seconds after the first frame with a pawn and a boss (or 300 s after the PIE began if they never appear), whatever happens.
5. RunDrivers row (the owner adds it): `@{ N = 'pie_build_fight'; K = 'R'; Min = 10; T = 600 }`. `RunDrivers.ps1` has no hook that writes the scenario file per row: three rows need either a `-Build` parameter that writes `Saved\build_fight_build.txt` before the row, or three two-line wrapper scripts that write the file and `exec` this one. A driver that times out leaves its tick callback registered (restart the editor).
6. The boss AI is random: one run per build is an anecdote. Run each build several times before reading anything into the numbers.

## 3. What the bot does

One decision per frame, in this order (`decide()` in the file). The generator style is that of `pie_builds.py`: a `script()` generator, `until()`, a tick that applies held input every frame, a heartbeat (every 10 s in the fight, 15 s before), `finish()` clearing `rpg.Build`, RESULT line.

**Setup**: reset the encounter (boss dormant), check loadout style and state `Idle` (up to 20 s) plus the build's weapon ability (the weapon actor class is only reported), one `debug_refill_player()` (flag `REFILL_BEFORE_FIGHT`; the bot is never healed afterwards and the boss never), enter combat mode, teleport to 800 cm in front of the boss and let it wake by itself (gate 1200 cm; `wake()` only after 6 s). A build that does not apply ends the run as `setup_failed` (the checks still count).

**Priority 1, dodge**: `RPGAttackTracker` says a tracked attack is in Windup, Committed or the first 0.12 s of Active. The dodge key (`Gamepad_FaceButton_Right`, down 0.08 s, the pack dodges on release) goes down so that the i-frames (0.16 to 0.46 s after the key goes down, from `pie_iframes.py` QUICK_WINDOW 0.107 to 0.490 montage seconds at rate 1.3 plus the press) cover the start of the active window. One dodge per attack instance, at least 0.45 s between presses (closer is RPGDodgeTiming's full roll). A dodge also cuts a swing in progress (proven by `pie_hyperarmor.py` 266 to 273). Per move (`PLAN`): A1, A1b, A3a, A3b sideways (alternating sides, `CLOSE_DODGE = "flank"` for 60 degrees forward-sideways), key 0.30 s before the active window; A2 forward through the slam (ends at the boss's feet for its 1.03 s recovery), 0.25 s before; A6 and A4 backward (no stick: RPGDodgeTiming turns away from the camera), A6 0.15 s before; A5 never fires (the bot never heals). In phase two the montage position is divided by the attack rate (x1.2). A boss montage the tracker does not know and that looks like an attack by name (`ATTACK_WORDS`) is dodged 0.2 s into it (a guess) and its name is logged once (`UNTRACKED boss montage`).

**Priority 2, riposte**: stance break and `is_riposte_available(pawn)`: press Light Attack once (`IA_NormalAttack` 0.12 s), wait for the execution to end. Until it opens (the fall is 0.7 s) the bot walks to the boss's front (within 130 cm, 55 degrees off its front, going round the boss in 35 degree steps). At most three presses per break; after 1.6 s without a riposte it hits the kneeling boss instead.

**Priority 3, punish**: an opening (Recovery of a tracked attack, the stance break, the phase two roar) whose estimated remaining real seconds cover the walk to the strike range (165 cm, shrinks 12 cm after a whiff) plus `HIT_DELAY[kind]` x 0.85, and whose stamina cost plus a 20 reserve fits. Openers: Strength: stagger JumpHeavy, Strong, Light; recovery and roar Strong, Light. Dex: Light chain of three taps 0.5 s apart (as `pie_builds.py` B6). Starter: Light chain of two (Strong in a stagger). A dodge that becomes due cuts any swing.

**Priority 4, spacing**: while the boss is neutral (no tracked move, not down, no roar, no attack-like montage): approach beyond 380 cm, back off inside 230 cm (not beyond 1000 cm from the boss's home: the arena radius is not read). After 14 s without any boss attack or opening the bot walks up and throws one bait Light.

**Input** is real: `RPGInputTestUtils.inject_action` for attacks and `IA_Move`, `set_key_down` for dodge and jump. Every frame the control rotation looks at the boss (so the stick axes are boss relative, as in `pie_a2_scenarios.py`) and, when the pawn plays no montage, `set_actor_rotation` turns it to the boss (the stand-in for lock-on, as `pie_pack_fight.py` 124).

## 4. Metrics (one `[BuildFight] METRIC name = ...` line each)

build; outcome and reason; fight seconds; boss health (start, end, lost = weapon hits + bleed procs + riposte impacts + other); hits landed by kind (from the intake's record lines) and records without a health drop; boss health per hit (average and per kind, hit records paired with the boss's health drops by time); swings (bot presses by kind, swing-tracker count by kind, whiffs, ignored, cut by a dodge); swing to hit delay (median per kind against the guess); posture breaks; ripostes (impacts, presses, accepted, rejected); bleed procs; dodges (presses, dodge montages quick/full, ignored by the pack, late, stamina cost samples); hits taken (count, health, by move, health start/end/lowest); attacks seen by move (hit me / avoided by a dodge / missed on their own); openings (usable seen, used, tried, by kind: an opening is a boss Recovery of at least 0.45 s, a stance break or a roar; used = at least one hit or a riposte impact); stamina (start, lowest and when, seconds below 15, dips below 20); phase two (time and boss health); untracked boss montages; measured walk speed; strike range at the end. Event lines: `BOSS ATTACK`, `DODGE`, `HIT TAKEN` (with i-frame state: damage during i-frames is flagged), `SWING`, `RIPOSTE`, `OPENING`, `BOSS HEALTH`, `MODE`, `STAMINA`, `PHASE TWO`, `API PROBLEM` (the first failure of every API call, see below).

## 5. APIs used and where they were found

Names are the UE snake_case of the UFUNCTIONs (headers read, line numbers as read on 2026-10-22; the owner's session is editing headers, so trust the names, not the numbers). "Proven" = already called the same way by a driver that ran.

| Python name | Source | Proven in |
|---|---|---|
| `tr.get_current_move()`, `get_phase_name()` (None, Windup, Committed, Active, Recovery), `get_position()`, `get_attack_instance()` | `RPGAttackTracker.h` 136, 140, 92, 133 | `pie_attack_rules.py` 152, `pie_real_kill.py` 106 |
| `tr.get_editor_property("attacks")` rows: `move_id` | `RPGAttackTracker.h` 22, 75 | `pie_a5_heal_punish.py` 395 to 397 |
| the same rows: `commit_time`, `active_start_time`, `active_end_time`, `recovery_end_time`, `montage_name` | `RPGAttackTracker.h` 26 to 41 | NOT proven (only `move_id`, `clip_path` were read before); a failure logs `SETUP could not read the tracker's Attacks table` and the built-in copy of the C++ defaults is used |
| `stg.is_staggered()`, `is_critical_window_open()`(not used), `get_clip_stage_name()` (none, fall, down, getup, riposte), `is_riposte_available(pawn)`, `is_riposte_executing()`, `get_stagger_count()`, `get_riposte_count()`, `get_riposte_impact_count()`, `get_riposte_reject_count()`, `get_last_riposte_result()` | `RPGBossStagger.h` 187, 191, 180, 109, 98, 228, 118, 102, 121, 125 | `pie_riposte_exec.py` 133, 143, 155; `pie_riposte.py` 131; `pie_boss_hud.py` 101 |
| `stg.get_editor_property("stagger_seconds")`, `ph.get_editor_property("transition_seconds" / "attack_rate_scale" / "phase_two_health_fraction")` (reads, fall back to 2.5 / 1.8 / 1.2) | `RPGBossStagger.h` 36; `RPGBossPhases.h` 35, 58, 31 | NOT proven (`riposte_base_damage` and `critical_multiplier` reads are: `pie_riposte.py` 166) |
| `post.get_posture()` | `RPGBossPosture.h` 46 | `pie_boss_encounter.py` 142, `pie_builds.py` 226 |
| `ph.is_phase_two()`, `is_in_transition()` | `RPGBossPhases.h` 96, 99 | `is_in_transition`: `pie_attack_rules.py` 78, `pie_bleed.py` 157; `is_phase_two`: `pie_phase_reset.py` 89, 97 |
| `enc.is_dormant()`, `reset_for_test()`, `wake()`, `get_generation()`, `get_home_transform().translation` | `RPGBossEncounter.h` 39, 67, 71, 53, 59 | `pie_builds.py`, `pie_boss_encounter.py` 98 |
| `death.get_death_state_name()` (alive, dying, dead) | `RPGBossDeath.h` 94 | `pie_boss_death.py` 118 |
| `hud.get_state_name()` (Dormant, Fighting, Victory) | `RPGBossHud.h` (around 170 to 183) | NOT proven from Python |
| `bleed.get_proc_count()`, `get_last_proc_damage()` | `RPGBossBleed.h` 79, 86 | `pie_builds.py` 387 to 389 |
| `intake.get_boss_hit_count()`, `get_record_lines()` (newest last), `is_hit_intake_bound()` | `RPGHitIntake.h` 84, 109, 98 | `pie_hit_intake.py` 144, `pie_builds.py` |
| `swing.get_attack_swing_count()`, `get_last_swing_text()` | `RPGSwingTracker.h` 68, 75 | `pie_builds.py` 215, 219 |
| `ld.get_actual_style_name()`, `get_state_name()`, `has_choice()`, `get_chosen_build_name()`, `get_equipped_actor_class_name()`, `has_weapon_ability_for_test()`, `get_build_line()`, `get_apply_attempt_count()`, `get_last_result()`, `is_combat_enabled()` | `RPGBuildLoadout.h` 67, 71, 59, 55, 118, 122, 63, 79, 75, 114 | `pie_builds.py` |
| `dodge.get_press_count()` | `RPGDodgeTiming.h` 97 | `pie_dodge_trials.py` 74 |
| `mon.is_invulnerable_now()` | `RPGIFrameMonitor.h` 59 | `pie_iframes.py` 145 |
| `dbg.debug_refill_player()` | `RPGCombatDebug.h` 75 | everywhere |
| `unreal.RPGInputTestUtils.inject_action(pc, action, Vector)`, `set_key_down(pc, key, bool)` | `RPGInputTestUtils.h` 25, 30 | `pie_builds.py` 208 and 586; `pie_iframes.py` 67 |
| `IA_Move` stick (x right, y forward, relative to the control rotation) | `pie_dodge.py` 12 and 117 | `pie_a2_scenarios.py` 66 to 67, 129 to 135 (a dodge key press 0.08 s with the stick held from 0.15 s before it) |
| dodge key `Gamepad_FaceButton_Right`, jump key `Gamepad_FaceButton_Bottom` | `pie_iframes.py` 13; `pie_builds.py` 18 | same |
| `pawn.set_actor_rotation(Rotator(0, 0, yaw), False)`, `pc.set_control_rotation`, `set_actor_location_and_rotation` | `pie_pack_fight.py` 124; `pie_builds.py` 114 to 115 | same |
| `inst.get_current_active_montage()`, `inst.montage_get_position(m)`, `m.get_name()` | `pie_pack_fight.py` 51 | same |
| `move.is_falling()` on the `CharacterMovementComponent` | `pie_dodge.py` 133 | same |
| `GameplayStatics.get_time_seconds(world)` (the world clock) | `pie_iframes.py` 37 | same |
| `comp.call_method("Get Current Attribute Value", args=(tag,))` with `Attribute.Health`, `Attribute.Stamina` | `pie_builds.py` 61 to 70 | same |
| the console variable `rpg.Build "<Name>"` set in the editor world before the PIE begins | `pie_builds.py` 97 to 105 and 563 (it clears it there) | setting before the PIE is NOT proven, setting in the PIE is (`b9_selectors`) |

Every call whose absence would not stop the run goes through `safe()`: the first failure of each is logged as `API PROBLEM <key>: <error>` and the run goes on with a default. Check for those lines first.

## 6. What could NOT be verified

- Everything at run time. No line of the driver has run.
- The boss's reach per move, the player's walk speed (measured and logged: `walk_speed`), the stamina maximum and regeneration, the stamina cost of a dodge (sampled and logged), the real press-to-hit delay of each kind (`HIT_DELAY` is a guess; the log prints the measured median), the strike range (starts at 165, learns from whiffs).
- The names and timing of the pack's mid range and sprint attack montages. The tracker has no entry for them (DECISIONS "A2 stand-in facts": Far = `Mid01`, Leap and Sprint attack are Far Rare). `ATTACK_WORDS` and the 0.2 s dodge point are guesses.
- Whether the pack's character turns with the movement and fights `set_actor_rotation` (and whether walking backward then looks or behaves badly), and whether `IA_Move` plus a control rotation that changes every frame moves the pawn as expected (proven only with a fixed control rotation).
- Whether the diagonal stick of `CLOSE_DODGE = "flank"` gives a diagonal roll (only forward, sideways and no stick are proven).
- That the loadout applies a build chosen with `rpg.Build` set BEFORE the PIE begins (the loadout reads the variable every poll; the driver sets it again in the PIE if the loadout has no choice after the reset).
- The boss's natural attack rate: `pie_attack_rules.py` R5 saw 5 tracked attacks in a 40 s close fight (about one per 8 s), so 240 s may hold only 25 to 30 openings.
- The brief says phase two at 55 percent health; `RPGBossPhases.h` 31 says 0.6 (Freeze 30.1 and 36). The bot never uses a threshold: it reads `is_phase_two()` and logs the property value at the start.
- `unreal.Name` to `str` for `get_current_move()` (the drivers compare `str(...) == "None"`), the hit record text format (`kind (\w+)` is read from `FRPGHitRecord::ToString`, `RPGHitIntake.cpp` 96), the swing text format (`RPGSwingTracker.cpp` 47).

## 7. Known weak points of the bot (most likely to misbehave first)

1. **Quick close attacks.** A1, A1b, A3a and A3b have 0.12 to 0.17 s of windup in the pack's clips (`RPGAttackTracker.cpp` 35 to 38, DELTA_AUDIT), the dodge's i-frames start 0.16 s after the key. A bot that reacts to the tracker's Windup is late by construction (`DODGE ... [LATE ...]`, `dodges ... late` count). Expect `HIT TAKEN` on these moves; a hit during i-frames would be flagged `ON (damage during i-frames: look at this)` and would be a game bug, not a bot bug. The only defence in the bot is the roll itself leaving the locked heading; fixing the rest needs the authored 0.35 to 0.40 s clips or a pre-emptive dodge.
2. **Untracked attacks** (mid range and sprint): the bot sees them only as boss montages, dodges at a guessed time, and the tracker's phase, commit and recovery do not exist for them, so they also give no opening. If the bot is hit with `no tracked move (boss montage X)` in the log, add `X` to the tracker table or to `ATTACK_WORDS` and set the time.
3. **Facing and movement.** The pawn is turned by `set_actor_rotation` and the camera by `set_control_rotation` every frame. If the pack's locomotion disagrees the bot may drift, stand sideways, or the roll may go the wrong way. First thing to look at in a replay.
4. **Punish feasibility.** After a sideways roll the bot is about 350 cm from the boss; closing 175 cm takes about 0.4 s plus the swing delay, so openings of 0.6 to 0.8 s (A1, A1b, A3b, A6) are mostly skipped (`OPENING ... (the bot did not try: ...)` gives the reason). Only A2 (1.03 s, forward roll ends at the boss's feet) and the stance break are realistic. Try `CLOSE_DODGE = "flank"` if the numbers show it.
5. **Riposte positioning.** After a roll the bot may be at the boss's side or back; walking round to its front inside the 0.7 s fall plus about 0.9 s can fail. The riposte also depends on the boss turning its front to the bot: unknown.
6. **Stamina.** Strength spends 35 on a strong, a dodge costs an unknown amount, the pool and regeneration are unknown. `DODGE_RESERVE`, `DODGE_STAMINA_MIN` and the `stamina` metric are the knobs and the evidence.
7. **A6 (phase two leap and wave).** Backward roll 0.15 s before the active window is a calculation from the wave's speed (`RPGBossShockwave.h`: 200 to 1100 cm at 1000 cm/s, 180 cm thick), not a measurement. A jump over the wave is not implemented.
8. **Spacing and walls.** `WALL_RADIUS` is a guess; the bot can corner itself while backing off. `RETREAT = False` is the simple alternative.
9. **Passive bot.** It never pokes except the bait after 14 s: if the boss rarely attacks, the run times out. It never guards, sprints, locks on or heals (A5 therefore never fires; that move is not exercised by this driver at all).
10. **One boss death per PIE.** The pack destroys a dead boss about 4.4 s after its death; the driver stops 1.2 s after the death, inside that.

## 8. Knobs (top of the file)

`LIMIT_FIGHT_S` 240, `START_DIST` 800, `REFILL_BEFORE_FIGHT` True, `STRIKE_RANGE0` 165, `WALK_SPEED` 450 (guess, only used to judge whether a walk fits an opening), `SPACING_MIN/MAX` 230/380, `RETREAT`, `WALL_RADIUS`, `BAIT_AFTER_S` 14, `DODGE_PRESS_S` 0.08, `DODGE_MIN_GAP` 0.45, `DODGE_STAMINA_MIN` 12, `DODGE_RESERVE` 20, `CLOSE_DODGE` side or flank, `UNTRACKED_DODGE_AT` 0.2, `OPENING_MIN` 0.45, `RIPOSTE_GO`/`RIPOSTE_CONE`/`RIPOSTE_WAIT_S`, `PLAN` (per move: direction, seconds before the active window, reach), `HIT_DELAY`, `OPENERS`, `CHAIN`, `TAP_SPACING`.

## 9. First run: what to look at, in order

1. `API PROBLEM` lines (a name that does not exist raises AttributeError there: on 2026-10-22 `get_world_scale3d` and `get_relative_location` did not exist).
2. `SETUP` lines: components found, tracker table read (and any `differs from the built-in copy`), loadout `EQUIPPED`, player health and stamina, the wake.
3. `FIGHT START`, then the pairs `BOSS ATTACK ... begins` / `DODGE ...` / `HIT TAKEN` or `... ended: avoided`: is the dodge early enough, in the right direction, and does the pack accept it (`DODGE ignored by the pack`)?
4. `OPENING ... ended`: which openings were seen, used, skipped and why; `SWING ... landed ... first x s after the press` for the real hit delays.
5. The heartbeat for the shape of the fight, `MODE` lines for what the bot did between events, and the final `METRIC` lines.
6. Only then compare builds (several runs each): `fight_seconds`, `boss_health_per_hit` by kind, `hits_taken`, `openings` used/seen, `stamina`, `posture_breaks`, `bleed_procs`.

## 10. Reviews and status (2026-10-22, owner's session)

Status: written by a helper, reviewed twice (read-only), NEVER RUN: the Windows session was disconnected, so the editor could not start (KI-093). `Scripts/RunDrivers.ps1` has three balance rows (not part of the gate): `-Only pie_build_fight_starter,pie_build_fight_strength,pie_build_fight_dex` (each writes `Saved/build_fight_build.txt`, then runs `pie_build_fight.py`; `Min = 10`, `T = 700`).

- API review (every Python name against the C++ headers): no wrong name. Fixed: the boss's mesh is picked without the look's `RPGLook...` follower meshes.
- Logic review, fixed in the file: a swing cut by a due dodge returns at once (the 0.12 s pause delayed the dodge and its i-frames); the bot does not press a swing while its own dodge runs (the press is eaten); the attack that killed the bot is finalized before the report; the tick callback unregister cannot hide the RESULT line.
- Logic review, OPEN (needs the editor, do these before trusting any number): (1) after a sideways roll of 230 to 380 cm the bot stands 400 to 500 cm away and every tracked recovery (0.6 to 0.8 s) is skipped: use a flank or forward roll for A1/A3, lower `SPACING_MAX` to about 260, on a Recovery always close in and throw one Light, poke while the boss is neutral; (2) the mid range, sprint and retaliation moves are untracked and the bot dodges them at 0.20 s of the montage (a guess): probe their notifies (`RPGMontageUtils::DescribeNotifies`) and add rows; (3) the A6 backward roll ends after the i-frames, the wave arrives at 0.75 + (D+120)/1000 s: jump over the wave (LEAP-01 proves it clears) or time the roll; (4) add an INCONCLUSIVE flag when the outcome is not boss_dead and the boss lost less than 40 percent of its health; (5) more logging at the end of a dodge (bot distance, off-front angle, position change, mode, boss yaw) and one decide line about every 0.5 s while a tracked attack runs.
- Expect on the first run: outcome `timeout` or `player_dead` with 10/10 checks passing (the checks are sanity only): the first runs measure the bot, not the builds.

## 11. Runs so far (2026-10-22, bot as delivered plus the review fixes; all four runs were the STRENGTH build)

A path bug (a backspace character in the file name of the three balance rows in `RunDrivers.ps1`, fixed) kept `Saved/build_fight_build.txt` from being written, so the rows `pie_build_fight_starter` and `_dex` ran STRENGTH (the log line `METRIC build = Strength (no file: default Strength)` says so). NO Starter or Dex run has been measured yet: rerun `-Only pie_build_fight_starter,pie_build_fight_dex`.

| Run | Limit | Outcome | Boss health at the end | Hits (Light/Strong) | Posture breaks, ripostes | Hits taken | Phase two at |
|---|---|---|---|---|---|---|---|
| 1 | 240 s | timeout | 51 of 500 | 21 (19/2) | 1, 1 (100 health) | 3 for 108 (player 12 of 120) | 23 s |
| 2 | 420 s | timeout | 62 | 27 (26/1) | 0, 0 | 0 | 191 s |
| 3 | 420 s | timeout | 94 | 25 (24/1) | 0, 0 | 0 | 201 s |
| 4 | 420 s | timeout | 158 | 21 (20/1) | 0, 0 | 0 | 268 s |

Reading (a bot fact, not a balance fact): the bot lands about 16 health per Light hit (Strong 22.4) and throws almost no heavy swings, so it needs 31 or more Light hits to empty 500 health and does not get there in 420 s; runs 2 to 4 took no damage and never broke posture or riposted (it only pokes in openings and stays out of reach); run 1 got a stance break and a 100 health riposte and came closest. Next steps are the OPEN list of section 10: use the build's heavy opener (Strength: jump heavy and strong for posture, the hyperarmor window is authored), close in on recoveries, then three runs per build and a table.
