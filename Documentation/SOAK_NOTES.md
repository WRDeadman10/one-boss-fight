# Gate 4 soak runner notes

\`Scripts/Editor/pie_soak.py\` is a deterministic 30-encounter soak draft for
G4-4. Codex did not run it; Claude owns the editor execution and debugging.

## Scenario plan

The driver uses six PIE sessions. Each contains this order, repeated six times:

| Order | Scenario | Deterministic action | Expected outcome |
|---|---|---|---|
| 1 | \`natural\` | Wake the boss, keep the player at 220 cm and refill every 0.5 s for 20 s, then reset. | One reset; dormant boss at home. |
| 2 | \`break\` | Wake and hold; call \`ForceBreakForTest\`; reset in the break. | One reset; no stagger or montage. |
| 3 | \`roar\` | Wake and hold; set health to 55 percent; reset during the roar. | One reset; phase one start state. |
| 4 | \`player_death\` | Wake and hold; set player health to zero; wait for the real new pawn. | Automatic reset and full-health replacement pawn. |
| 5 | \`boss_death\` | Wake and hold; call \`DebugKillBoss\`; wait for destruction. | Intentional terminal no-boss state; end PIE. |

Five encounters share a PIE because their reset paths are the subject under
test. Boss death is last because the pack destroys the boss about 4.4 seconds
later and reset correctly does not revive it. The following PIE begins cleanly.

## Fixed accounting and limits

The expected total is **213**: 30 encounters x 7 checks (210), then all 30 ran,
no tick exception, and no watchdog hang (3). Per encounter the checks are
scenario goal; start or terminal outcome; no illegal starts; no double launches;
generation/reset count; no stale boss/projectile/wave; and no player health drop
during the 1.5 seconds following the interrupt/reset.

Boss death expects no generation change because no reset is legal after death.
Its terminal outcome is the missing destroyed boss; the next PIE supplies the
following clean start. Setup failures and watchdogs fill all outstanding checks
as failures, preserving \`RESULT n/213 passed\`.

Limits are 60 seconds per encounter, 40 seconds without a player pawn, 65
minutes total, and a 15-second heartbeat. Claude should add this row to
\`Scripts/RunDrivers.ps1\` only after runtime validation:

\`\`\`powershell
@{ N = 'pie_soak'; K = 'R'; Min = 213; T = 4200 }
\`\`\`

## API provenance

Every project component call is the snake-case form of a UFUNCTION.

| Python API | Header evidence |
|---|---|
| \`reset_for_test\`, \`wake\`, \`hold_for_test\`, \`get_generation\`, \`get_reset_count\`, \`is_dormant\`, \`get_home_transform\` | \`Source/OneBossFight/Player/RPGBossEncounter.h:38-71\` |
| \`get_illegal_start_count\`, \`get_double_launch_count\`, \`get_attack_instance\`, \`get_commit_count\`, \`get_interrupted_count\`, \`get_current_move\` | \`Source/OneBossFight/Player/RPGAttackTracker.h:103-107\`, \`:131-160\` |
| \`set_cooldown_for_test\`, \`force_break_for_test\`, \`is_staggered\`, \`get_stagger_count\`, \`get_riposte_count\` | \`Source/OneBossFight/Player/RPGBossStagger.h:138-148\`, \`:186-203\`, \`:227-231\` |
| \`is_phase_two\`, \`is_in_transition\` | \`Source/OneBossFight/Player/RPGBossPhases.h:95-105\` |
| \`get_posture\` | \`Source/OneBossFight/Player/RPGBossPosture.h:45-49\` |
| \`debug_refill_player\`, \`debug_set_player_health\`, \`debug_set_boss_health_fraction\`, \`debug_kill_boss\`, \`debug_boss_montage_anim_name\` | \`Source/OneBossFight/Player/RPGCombatDebug.h:58-79\`, \`:66-71\` |
| \`is_wave_active\` | \`Source/OneBossFight/Player/RPGBossShockwave.h:66-67\` |

The attribute read is the pack Blueprint function \`Get Current Attribute Value\`,
using existing-driver reflection. It is not a project component UFUNCTION. No
component receives \`set_editor_property\` in PIE.

\`RPGBossJavelin\` is an actor class evidenced by
\`Scripts/Editor/pie_a5_heal_punish.py:75-77\`. The current wave is a component
(\`RPGBossShockwave.h:22\`), not a spawned actor; the runner checks both
\`is_wave_active()\` and actor class names containing \`Shockwave\` or \`Wave\`.

## Not verified

- Codex did not run PIE, a build, package, or full driver.
- Actual respawn, destruction and total duration still need Claude's evidence.
- The actor-name cleanup scan cannot prove there are no unrelated pack effects.
- Natural-fight coverage checks lifecycle and legality, not balance or feel.

## Likely first failures

1. KI-081 cold shader/data work delays the warm-up or timing.
2. Respawn exceeds 25 seconds or uses an unexpected pawn-name convention.
3. A stale pack actor uses a class name outside the javelin/wave scan.

