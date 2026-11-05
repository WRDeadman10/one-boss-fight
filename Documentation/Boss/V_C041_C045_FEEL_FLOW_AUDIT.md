# Queue V Codex batch: V-C041–V-C045 feel and flow audit

Status: evidence gathering in progress. This sheet records repository evidence only; it does not claim a Lead PIE/build run. Freeze values below are design targets and must not be confused with witnessed runtime measurements.

## V-C041 — input-to-montage latency

Added `Scripts/Editor/pie_input_montage_latency.py`. It injects the real attack/dodge/parry input actions, timestamps just before injection, and records the first active player montage change; it reports the measured `dt` so the Lead can account for per-tick observation resolution. `H019_ENCOUNTER_DEFINITION` selects the data route; unset selects legacy, matching existing PIE-driver convention. The six route/action samples remain Lead-run. The measurement is input-injection-to-first-observed-montage, not hardware-device latency.

## V-C042 — hit-feel vs freeze

| Element | Freeze / implementation evidence | Audit finding |
|---|---|---|
| Hit stop | `RPGLegend.h`: `HitStopSeconds = 0.08f`, `HitStopDilation = 0.05f`; lethal ripostes skip hit stop (`bSkipHitStopOnLethal`). `pie_legend.py` L4 records measured duration against the 0.08 s target. | Driver has a measurement assertion path. No fresh Lead receipt or per-hit-type classification attached in this audit. |
| Camera shake | `RPGLegend.cpp`: A2/A6 trigger slam shake once per active attack instance; phase transition triggers roar shake. `pie_legend.py` L1/L2/L3 checks A2/A6/roar counts and L6 has visual capture steps. | Trigger coverage exists in the driver. No fresh Lead run or visual captures attached here. |
| Sound | Optional parry `USoundMix` is null by default and applies only to the parry slow-motion scope. | No per-hit-type impact sound audit evidence found yet; do not claim a sound cue per attack or hit result. |

## V-C043 — telegraph time vs reaction window

Freeze v1.2 section 4 lists the intended attack windups: A1 0.35 s, A2 1.40 s apex hold, A3 0.40 s, A4 0.60 s, A5 0.40 s before release, and A6 0.90 s ascent. The table describes A1/A2/A3/A4/A5/A6 active durations as 0.15/0.12/0.20+0.25/0.30/flight/shockwave; these are authored/design descriptions, not measurements of a player's reaction window.

Current `RPGAttackTracker.cpp` sets tracked active starts at A1 .35, A2 1.93, A3a .40, A3b .15, A4 .60, and A6 .75 montage seconds; the close-attack comment explicitly records the pack stand-in clips at 0.12–0.17 s versus the freeze's 0.35–0.40 s and says play-rate adjustment is used until authored clips arrive. The tracker has no A5 row in this timing table. Therefore this is a target-to-configuration comparison, not evidence that all attacks deliver the frozen readable tell at runtime. **Remaining:** cite the A5 route separately and attach paired runtime recordings/logs before declaring reaction windows met.

| Move | Freeze target (s) | Current tracker timing (s) | Status |
|---|---:|---:|---|
| A1 | 0.35 windup | commit .33; active .35 | configured; runtime readability not witnessed here |
| A2 | 1.40 apex hold; .25 before hit | commit 1.68; active 1.93 | configured; runtime readability not witnessed here |
| A3a | 0.40 | commit .38; active .40 | configured; runtime readability not witnessed here |
| A3b | no separate second-stage windup value stated in the Freeze table | commit .13; active .15 | do not compare against A3a's .40 value; runtime readability not witnessed |
| A4 | 0.60 | commit .40; active .60 | configured; runtime readability not witnessed here |
| A5 | 0.40 telegraph before release | no row in `RPGAttackTracker` | separate heal-punish path needs driver/source timing citation |
| A6 | 0.90 ascent | commit .16; active .75 | configured from pack stand-in; runtime readability not witnessed here |

## V-C044 — phase-two transition

`Scripts/Editor/pie_phase_reset.py` has explicit checks for no transition at 62%, transition start at 59%, transition completion after the roar, one-time x1.25 Attack buff, idempotence under further health drops, reset restoring phase one/buff/posture, and transition deferral during a stance break followed by one transition. `Scripts/Editor/pie_boss_hud.py` checks phase two reached and the HUD bar follows roughly 55% boss health. These are driver assertions, not a fresh Lead run receipt. **Remaining:** attach current Lead run receipts before marking complete.

## V-C045 — death/restart

`Scripts/Editor/pie_boss_death.py` documents checks D1–D10: death state/count, death montage, body lifetime, final pose/physics, and mesh/weapon presentation. `Scripts/Editor/pie_boss_hud.py` checks `Victory` state once, victory banner, hidden bar, and no remaining prompt. `Scripts/Editor/pie_player_death_reset.py` kills the player during stance break, riposte, A4 sweep, and A5 javelin scenarios; it checks replacement pawn, single encounter generation/reset increment, boss home/dormant/full health and poise, cleared combat objects, and full player health. These are driver checks, not current run evidence. **Remaining:** attach Lead receipts for boss-kill/victory and player-respawn flows.

## Evidence and next step

- Design baseline: `Documentation/Master_Design_Freeze_v1_2_AI_Implementation_Ready.md`, section 4 and phase-two requirements.
- Implementation: `Source/OneBossFight/Player/RPGAttackTracker.cpp`, `RPGAttackTracker.h`, `RPGLegend.cpp`, `RPGLegend.h`.
- Existing/new drivers: `Scripts/Editor/pie_input_montage_latency.py`, `pie_legend.py`, `pie_phase_reset.py`, `pie_boss_hud.py`, `pie_boss_death.py`, `pie_player_death_reset.py`.
- Lead-only work remains: paired route latency measurements and runtime checks/captures. Codex did not launch Unreal, build, package, or run PIE.
- Before closing this five-task batch, run the project offline suite and post one corrected batch receipt to Claude. Lead's route/action latency samples and the phase-two/hit-feel/death-flow live checks remain open run gates.
