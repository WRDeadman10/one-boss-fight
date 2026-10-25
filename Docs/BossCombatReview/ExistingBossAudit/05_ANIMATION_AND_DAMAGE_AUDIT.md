# Animation and damage audit

## Tracked attack contracts

Seconds below are **montage-local source timing declarations**, not newly measured contacts or duration-derived guesses. Actual pack notifies and live montage rates require U06. Recovery end is a declared timestamp, not automatically a guaranteed lock.

| Move/stage | Playback | Commit | Active | Recovery end | Turn rate before commit | Damage route |
|---|---|---:|---|---:|---:|---|
| A1 | AM_Boss01_A1; fallback GS_Attack03_Montage | .33 | .35–.50 |1.20|360deg/s| Pack ability/weapon trace |
| A1b | GS_Attack04_Montage |.12|.16–.46|1.25|360| Pack, native branch gate |
| A3a | AM_Boss01_A3a; fallback GS_Attack01_Montage |.38|.40–.60|.80|360| Pack ability/weapon trace |
| A3b | AM_Boss01_A3b; fallback GS_Attack02_Montage |.13|.15–.40|1.3333|360| Pack, native branch gate |
| A2 | GS_ChargedAttack_Montage |1.68|1.93–2.11|3.14|120| Pack; source records earlier1.57–1.76 trace window too |
| A4 | AN_Boss01_A4_LowSweep dynamic montage |.40|.60–.90|1.75|180| Own swept-angle floor geometry;20HP |
| A5 | AN_Boss01_A5_JavelinThrow dynamic montage |.45|.45–.50 release window|.95|240| Own projectile;12HP |
| A6 | GS_LeapAttack_Montage |.16|.75–1.17|1.80|120| Pack central hit plus own48HP ring |

Source: [Tracker:24](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:24). Project montages/sequences live under /Game/OneBossFight/Boss01/Animations; pack montages under /Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss.

The source records A2 historical measured behavior as a ground-centered slam, not a narrow directional overhead. Its earlier pack trace window lies outside the tracker's declared active interval. Do not assert exact A2 geometry/contact time from the tracker alone. The three authored A2 sequences are not selected by this tracker.

## Timing and identity defects/risks

1. **Fallback mismatch (confirmed configuration structure):** FindTimingIndex maps authored and fallback names to one row. Pack failure fallback therefore keeps authored commit/active/recovery values. The code comment records much earlier pack close windows. Swap intentionally retains pack assets on failure, but tracker timing does not revert with them. This can produce precommit pack contact and incorrect telegraph scaling. [Tracker:105](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:105), [Tracker:285](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:285), [Swap:69](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp:69). Runtime failure scenario still needs reproduction.
2. **Skipped active windows (confirmed control flow):** tracker can go Committed directly to Recovery on a large montage-position step. A4/A5/A6 start/release only when IsActiveWindow is true. A5 has only50ms. At nominal30FPS it can be sampled; a >50ms interval spanning the whole window can miss it. Legend already uses HasReachedActive for slam feedback; damaging mechanics do not. [Tracker:465](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:465), [Heal:255](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHealPunish.cpp:255), [Sweep:175](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossLowSweep.cpp:175), [Wave:153](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.cpp:153), [Legend:456](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGLegend.cpp:456).
3. **Post-start identity:** instance assignment and branch veto follow playback. Same timing-index restart without an observed empty frame is not explicitly recognized as a new montage instance. This is an architectural risk, not a demonstrated double-hit reproduction. [Tracker:362](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:362), [Tracker:389](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:389).
4. **Recovery:** RecoveryEndTime is used for interruption accounting, not minimum lock or watchdog. Actual end/replacement dictates tracker freedom. [Tracker:251](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:251). Phase-rate changes and A1b telegraph restoration to1.0 also require rate-parity inspection ([Tracker:269](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:269), [Phases:410](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.cpp:410)).

## Geometry and query fidelity

A4 uses player capsule radius and an angular interval from previous to current blade angle: it is not a static broad cone. Range60–380cm, blade height40cm,90 to-90degrees. It checks a low world-blocker line. It does not check a lower Z tolerance; player below the recorded floor is not excluded by the “jumped” condition. Its analytic arc still needs comparison with the actual visible blade.

A5 sweeps a25cm sphere between projectile positions, chooses player contact only before a nearer world hit, flies straight after release, and expires at3000cm or old generation/dead boss. A starting-penetration grace within150cm lets it leave the hand near walls; test that this cannot shoot through thin cover. Iframe rejection does not consume it. [Javelin:103](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossJavelin.cpp:103).

A6 expands200→1100cm at1000cm/s, thickness180cm, jump clearance50cm. It tests the current band only. Example: previous radius500, new800, stationary player650; old outer590 and new inner710, so the player crosses the band but is marked passed without damage. This is a mathematical consequence of [Wave:73](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.cpp:73) and [Wave:162](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.cpp:162), not a run performed here. At steady30FPS radius moves about33cm, so the example specifically requires a hitch/large step or other crossing; do not call every30FPS wave broken. Current code has no wave wall/ground connectivity query and no lower-floor tolerance.

The visible boss sword has NoCollision; hidden pack weapon sockets still drive blade traces. Five sockets/radius50 were observed historically, but socket names/count alone do not establish coverage of the new sword. Preserve leader pose and measure the mismatch before any radius/socket alteration.

## Damage authority and defense

Pack blade/central contacts resolve through the Blueprint framework. Own specials call RPGDamageResolver, which checks target alive, attacker alive, encounter generation, duplicate key and live invulnerability, then directly writes HP. It does not apply guard/parry, guard stamina, flinch or knockdown. This is confirmed by [DamageH:25](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGDamageResolver.h:25), [DamageH:104](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGDamageResolver.h:104), [Damage:110](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGDamageResolver.cpp:110).

A6 precedence uses player health decrease since launch as evidence of the central hit. Unrelated loss can suppress a valid ring; healing can mask the central loss; direct damage before HealthAtLaunch is captured may escape attribution. Current W4 test deliberately lowers health, so it verifies that heuristic—not correlated central-hit identity ([LeapTest:103](C:/UnrealProject/OneBossFight/Scripts/Editor/pie_leap_wave.py:103)). Replace only after proving the real pack event boundary.

No adaptive pack substep implementation is claimed: RPGPackTrace exposes reflected data, and RPGTraceAudit's SweepMulti is diagnostic. Inspect the production Blueprint graph U05.

## Required validation

Per move and fallback: frame-synchronized visible weapon, sockets/volume, montage position, actual notify open/close, attack/window/generation, defense outcome and health delta. Repeat30/60/120FPS, .75/1/1.25 rates,120–300ms synthetic hitches, hitstop, interruption at both active edges, wall/vertical placements and zero-time starts. Current saved tests cover useful subsets, not this full matrix.

