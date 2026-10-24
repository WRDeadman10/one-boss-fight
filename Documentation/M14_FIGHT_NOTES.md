# M14 fight notes: the balance-run bot (`Scripts/Editor/pie_build_fight.py`)

Started 2026-10-22 by a writable helper, then integrated and exercised in PIE. Every run is archived as `Saved/BalanceRuns/<run-id>_<build>.json`, with its source hash and setup identity. The bot is a measurement harness, not a substitute for the owner's feel test.

## 1. What it is

A scripted player bot fights the REAL boss (not held: no `hold_for_test`, the pack's behaviour tree runs) with the sole build word in `Saved/build_fight_build.txt` (`Starter`, `Strength` or `Dex`; no default). It ends on boss death, player death, an inactive boss AI diagnosis, or 420 s of world time from the wake. It logs balance metrics for a human (`[BuildFight] METRIC ...` lines, also written to `Saved/build_fight_result_<Build>.txt`). The ten checks (S1 to S10) are SANITY only and are always evaluated, so `RESULT n/m passed` always has m = 10, also when the fight is lost: parts exist, reset establishes dormant/full-health/full-posture state, build equipped before the wake, fight started, boss attacked, bot swung and the intake was bound, weapon never changed, outcome is one of the three, metrics logged, no error.

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

**Priority 1, evade**: `RPGAttackTracker` says a tracked attack is in Windup, Committed or the first 0.12 s of Active. The dodge key (`Gamepad_FaceButton_Right`, down 0.08 s, the pack dodges on release) goes down so that the i-frames (0.16 to 0.46 s after the key goes down, from `pie_iframes.py` QUICK_WINDOW 0.107 to 0.490 montage seconds at rate 1.3 plus the press) cover the start of the active window. One dodge per attack instance, at least 0.45 s between presses (closer is RPGDodgeTiming's full roll). A dodge also cuts a swing in progress (proven by `pie_hyperarmor.py` 266 to 273). Per move (`PLAN`): A1, A1b, A3a, A3b flank (alternating 60-degree forward-sideways sides), key 0.30 s before the active window; A2 forward through the slam (ends at the boss's feet for its 1.03 s recovery), 0.25 s before; A4 backward; and A6 uses the jump key 0.15 s before the active wave window. `LEAP-01` proves a launch-timed jump can clear the wave; this bot timing is still unverified. A5 never fires (the bot never heals). In phase two the montage position is divided by the attack rate (x1.2). A boss montage the tracker does not know and that looks like an attack by name (`ATTACK_WORDS`) is dodged 0.2 s into it (a guess) and its name is logged once (`UNTRACKED boss montage`).

**Priority 2, riposte**: stance break and `is_riposte_available(pawn)`: press Light Attack once (`IA_NormalAttack` 0.12 s), wait for the execution to end. Until it opens (the fall is 0.7 s) the bot walks to the boss's front (within 130 cm, 55 degrees off its front, going round the boss in 35 degree steps). At most three presses per break; after 1.6 s without a riposte it hits the kneeling boss instead.

**Priority 3, punish**: every recovery, stance break and phase-two roar closes to strike range and attempts the first stamina-legal opener; it no longer rejects a recovery by the estimated walk-plus-hit time. Openers: Strength: stagger JumpHeavy, then Strong, then Light; recovery and roar Strong then Light. Dex: Light chain of three taps 0.5 s apart (as `pie_builds.py` B6). Starter: Strong then Light (two taps only when Light is selected). A dodge that becomes due cuts any swing. A Strength or Starter run with fewer than three Strong/Charged/JumpHeavy presses is marked INCONCLUSIVE evidence.

**Priority 4, spacing**: while the boss is neutral (no tracked move, not down, no roar, no attack-like montage): approach beyond 260 cm and do not retreat by default. Once in strike range, neutral pressure starts after one second if stamina keeps its dodge reserve; Strength uses Strong when it can pay, otherwise Light. This is an unverified pressure policy, not a balance result.

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
7. **A6 (phase two leap and wave).** The bot now jumps 0.15 s before the active window instead of backward rolling. `LEAP-01` proves a jump at wave launch can clear the wave, but this tracker-timed input has not run and may still be early or late. The log records `WAVE JUMP` and its end state.
8. **Spacing and walls.** `WALL_RADIUS` is a guess; the bot can corner itself while backing off. `RETREAT = False` is the simple alternative.
9. **Passive bot.** It never pokes except the bait after 14 s: if the boss rarely attacks, the run times out. It never guards, sprints, locks on or heals (A5 therefore never fires; that move is not exercised by this driver at all).
10. **One boss death per PIE.** The pack destroys a dead boss about 4.4 s after its death; the driver stops 1.2 s after the death, inside that.

## 8. Knobs (top of the file)

`LIMIT_FIGHT_S` 420, `START_DIST` 800, `REFILL_BEFORE_FIGHT` True, `STRIKE_RANGE0` 125, `WALK_SPEED` 450 (logged but no longer used as a recovery veto), `SPACING_MIN/MAX` 170/260, `RETREAT` false, `WALL_RADIUS`, `BAIT_AFTER_S` 1, `DODGE_PRESS_S` 0.08, `DODGE_MIN_GAP` 0.45, `DODGE_STAMINA_MIN` 12, `DODGE_RESERVE` 20, `CLOSE_DODGE` flank, `UNTRACKED_DODGE_AT` 0.2, `OPENING_MIN` 0.45, `RIPOSTE_GO`/`RIPOSTE_CONE`/`RIPOSTE_WAIT_S`, `PLAN` (per move: direction, seconds before the active window, reach), `HIT_DELAY`, `OPENERS`, `CHAIN`, `TAP_SPACING`.

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
- Logic review, OPEN (needs the editor, do these before trusting any number): (1) the bot now uses flank close dodges, 260 cm spacing, recovery attempts without a fit veto, and neutral pressure; verify that it reaches openings rather than attacking into the next windup; (2) the mid range, sprint and retaliation moves are untracked and the bot dodges them at 0.20 s of the montage (a guess): probe their notifies (`RPGMontageUtils::DescribeNotifies`) and add rows; (3) the A6 tracker-timed jump is new: verify that its feet clear the wave and its timestamp is right; (4) the existing less-than-40-percent-health INCONCLUSIVE flag is joined by a fewer-than-three-heavy-swings flag for Starter and Strength; (5) verify the existing dodge-end and 0.5-second tracked-attack decision logs explain the first failures.
- Expect on the first run: outcome `timeout` or `player_dead` with 10/10 checks passing (the checks are sanity only): the first runs measure the bot, not the builds.

## 11. Runs so far (2026-10-22, guarded policy `close-recovery-v2`)

The earlier four rows are invalid as balance evidence: all ran Strength because a backspace character prevented their scenario files from being written. The three runs below passed their 10/10 harness checks, started at exactly 500 health / 100 posture, verified the requested build, and are archived in `Saved/BalanceRuns`.

| Build | Run ID | Outcome | Fight time | Boss health at end | Hit damage / bleed | Posture breaks, ripostes | Hits taken | Reading |
|---|---|---|---:|---:|---|---|---:|---|
| Starter | `20261022T120327_59646f4c` | boss dead | 25.7 s | -10 | 10 Lights at 41 each / 0 | 1, 1 | 1 (36) | Mechanics exercised; only one run |
| Dex | `20261022T120444_694cbf3b` | player dead | 10.2 s | 367.5 | 5 Lights at 16 each / 1 proc for 52.5 | 0, 0 | 4 (144) | **Inconclusive:** short close-attack loss; no break or riposte |
| Strength | `20261022T120530_6d706b58` | boss dead | 37.7 s | 0 | 12 Lights at 16, 4 Strongs at 22.4 / 0 | 3, 3 | 0 | Mechanics exercised; three ripostes dominate the finish |

Reading: these are useful first mechanics traces, not a balance verdict. The active policy exposes the expected contrast (Dex procs once; Strength reaches three posture breaks), but the bot still reacts late to close attacks and only one run exists per build. Next: improve close-windup defence and collect repeated runs before changing combat values; the owner still performs the feel test.

## 12. Runs with the revised bot (Codex Brief 04, 2026-10-23), one run per build, build file now written correctly

| Build | Outcome | Fight time | Boss health lost (weapon hits + bleed + riposte impacts) | Hits (Light/Strong) | Posture breaks, ripostes | Hits taken | Phase two at |
|---|---|---|---|---|---|---|---|
| Starter | boss dead | 23.0 s | 518 (418 + 0 + 100) | 9 (6/3) | 1, 1 | 3 for 108 (player 12 of 120) | 16.4 s |
| Strength | boss dead | 39.6 s | 500 (288 + 0 + 212) | 16 (11/5) | 3, 3 | 3 for 108 (player 12 of 120) | 17.0 s |
| Dex | boss dead | 36.6 s | 509 (304 + 105 + 100) | 19 (19/0) | 1, 1 | 0 | 18.4 s |

Reading: all three builds win, each through the intended loop (stance break, riposte, bleed procs on Dex: two procs of 52.5), and each run is marked INCONCLUSIVE by the bot itself (late dodges against the close attacks, untracked moves dodged at a guessed time). One run per build is a sample, not a result. The finding that matters: a plain bot kills the boss in 23 to 40 seconds because 500 health is small against 16 to 22 health per hit and a 100 to 212 health riposte; the Freeze gives no boss health and no fight length. That is an owner decision (KI-096). Repeat each build three times before drawing any comparison between builds.

## 13. Nine runs with per-event data (2026-10-23, `-Repeat 3`, collector `Scripts/CollectBalanceRuns.py`, accounting closes in every run: `bad_accounting=none`)

| Build | Outcomes | Fight time (min / median / max) | Damage per hit (health, n) | Riposte impact | Bleed proc | Stamina minimum | Hits taken |
|---|---|---|---|---|---|---|---|
| Starter | 2 boss dead, 1 player dead | 11.8 / 19.7 / 23.2 s | Light 41.0 (15), Strong 57.4 (7) | 100 (n 2) | none | 5 | 8 for 288 |
| Strength | 3 boss dead | 37.2 / 38.8 / 43.7 s | Light 16.0 (38), Strong 22.4 (12) | mean 79.6, min 18.4, max 100 (n 8) | none | 0 | 7 for 261 |
| Dex | 3 boss dead | 32.4 / 38.2 / 43.6 s | Light 16.0 (57) | 100 (n 3) | 52.5 (n 6) | 10 | 4 |

Findings: (1) the earlier assumption "Starter light 16" was wrong: the pack's starter sword does 41 health per light and 57.4 per strong, 2.6 times the damage of the Strength and Dex weapons (16 and 22.4), because health damage comes from the pack's attack data and weapon, not from the project's weapon table (which carries posture, stamina, bleed and hyperarmor only). The starter is the strongest weapon and kills the boss in 12 to 23 s. (2) A riposte takes 100 health (min 18.4 is a capped last hit). (3) Strength reaches 0 stamina, the Starter 5: stamina limits them; Dex never goes below 10. (4) All three builds win in under 45 s with this bot, so the fight is too short for every build (KI-096); the Starter is out of line with the builds (KI-097). The bot's evidence flag is still INCONCLUSIVE for late dodges against close attacks: use these as relative numbers.

## 14. Boss health 2000, bleed 0.03, starter 0.39 (2026-10-23, raw pacing / `rpg.CloseTelegraph 0`)

These nine archived flat driver records are the first calibration set under the
new health, bleed and Starter multiplier. The times, damage parts and outcomes
below are read from their `metrics` arrays, not inferred from the older
500-health history. `W` is boss dead and `D` is player dead.

| Run ID | Build | Outcome / seconds | Health damage per hit | Riposte total (count) | Bleed total (count) | Hits taken |
|---|---|---|---|---:|---:|---:|
| `20261023T135708_44c87d61` | Starter | W / 137.9 | Light 16.4 (59), Strong 22.4 (2) | 1000.0 (10) | 0 (0) | 3 |
| `20261023T135948_45a72ee1` | Starter | W / 143.5 | Light 16.4 (61), Strong 22.4 (1) | 1000.0 (10) | 0 (0) | 1 |
| `20261023T140235_25c00119` | Starter | W / 136.5 | Light 16.4 (60), Strong 22.4 (1) | 1000.0 (10) | 0 (0) | 0 |
| `20261023T140515_6eaa9fce` | Strength | D / 23.6 | Light 16.0 (2), Strong 22.4 (4) | 100.0 (1) | 0 (0) | 4 |
| `20261023T140601_4155c6cc` | Strength | W / 126.1 | Light 16.0 (44), Strong 22.4 (12) | 1027.2 (11) | 0 (0) | 1 |
| `20261023T140829_cf3f5e30` | Strength | W / 122.6 | Light 16.0 (45), Strong 22.4 (11) | 1033.6 (11) | 0 (0) | 0 |
| `20261023T141052_b07722d9` | Dex | D / 17.5 | Light 16.0 (9) | 0 (0) | 60.0 (1) | 4 |
| `20261023T141131_b92de201` | Dex | W / 127.5 | Light 16.0 (70) | 400.0 (4) | 480.0 (8) | 1 |
| `20261023T141402_c0de7c31` | Dex | W / 131.0 | Light 16.0 (70) | 400.0 (4) | 480.0 (8) | 0 |

Seven runs win in 122.6 to 143.5 s. The two early deaths are the Strength
23.6 s run and Dex 17.5 s run: each took four 36-health hits, exhausting the
player's 120 health. Q4 found that the terminal unscaled 41-health Starter hit
is the killing-blow behavior (health is already zero), not valid normal DPS
evidence. Q10 found 14 hits across these records: A3b supplied 6, then A1 and
A1b supplied 3 each, and every recorded hit followed a dodge outside its
i-frame window; this points to close-stage anticipation/telegraph rather than
a boss-health retune.

Q9's empirical reconstruction was within 3.6 percent on the six completed
runs because it pools their recorded weapon, bleed and riposte damage. It is a
record reconstruction, not a forward prediction of survival, human play or a
different bot policy.

## 15. Telegraph 0.4 (2026-10-24, boss health 2000 / bleed 0.03 / starter 0.39)

The newest six files in `Saved/BalanceRuns/`, written 2026-10-24 03:37 to
03:50 local, are the `rpg.CloseTelegraph 0.4` comparison set. All six won;
four took no damage. This table quotes the JSON top-level fields directly.

| Run ID | Build | Fight seconds | Hits taken | Damage taken | Player end |
|---|---|---:|---:|---:|---:|
| `20261023T220426_38aaccd1` | Starter | 151.8 | 1 | 36 | 84 |
| `20261023T220721_a8949515` | Starter | 136.6 | 0 | 0 | 120 |
| `20261023T221000_dd74c7bf` | Strength | 122.9 | 0 | 0 | 120 |
| `20261023T221227_5093664e` | Strength | 140.2 | 3 | 108 | 12 |
| `20261023T221511_974dcffe` | Dex | 129.0 | 0 | 0 | 120 |
| `20261023T221742_7ca61cd5` | Dex | 144.8 | 0 | 0 | 120 |

That is 6/6 wins in 122.9 to 151.8 s and four hits in six runs, versus 14
hits in the nine raw-pacing records. The samples support the owner decision to
ship `rpg.CloseTelegraph 0.4` as the temporary default while authored clips
remain unavailable. They do not prove survival or human feel; retain the
owner's hand test as the decision check.
