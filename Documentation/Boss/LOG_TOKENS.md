# FrameworkProof log token reference

The source of truth is `Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py`, variable `SCHEMAS`. Each token below is accepted only with its declared payload pattern there; this index names the semantic fields in source schema order. The 2026-11-03 audit found 138 schema entries, 138 emitted tokens, and 133 retained valid samples. Cross-line semantic rules also apply, so matching one line is not proof of a successful run.

| Token | Payload fields / purpose |
|---|---|
| `dependencies` | mesh, skeleton, animClass, sequence, slot, resolved, label — resolved fixture prerequisites |
| `slot_graph` | name, nodeClass, verified, label — slot graph check |
| `boss_health` | max, playerHitDamage, label; `boss_health_read`: reader, ok, value, max |
| `target_health_init` | value, readback, label; `target_health_mismatch`: valid, actual, expected, generation, optional reason |
| `target_fault_injected` | kind; `pack_style_known`: waitedSeconds; `bystander_spawned`: ok, name, x, y, z |
| `encounter_reset` | accepted form generation, oldState, executorRearmed, bossHealth, targetHealth; refusal form generation, reason |
| `boss_dead` | generation, executorAborted; `RESULT` | outcome and optional acceptedHits, attacks, parriedHits; `ERROR` token and optional detail |
| `nav_ready` | waitedSeconds; `nav_not_ready`: navSystem, buildInProgress, targetLocation |
| `nav` | request, projected, fullPath, result; `walk` | start, end, distanceCm, rangeCm, bandMin, bandMax, capsule, mesh |
| `walk_resumed` | generation; `reposition`: attempt, max, range, reason |
| `reposition_turn` | start, yawToTarget, range, ratePerSecond; `reposition_turn_end`: flips, latchDir, seconds |
| `hyperarmor_absorbed` | card, postureKept, amountSkipped; `combo_pause` | seconds, next; `combo_pause_end` empty |
| `walk_center_bias` | targetFromCenterCm, thresholdCm, bias, near, awayX/Y, biasedX/Y; `anticheese`: state, streak, rangeCm, thresholdCm, seq |
| `arena_leash` | state-specific start/at-center/resume fields; see schema |
| `player_drinks_scheduled` | count; `player_drink_started`: n, offset, ok, length |
| `flask_perceived` | count, latencySeconds, windowMin/Max; `flask_reaction`: count, measuredSeconds, windowMin/Max; `flask_end`: count |
| `los_lost` | lastKnownX/Y, blocker; `los_search_start`: x,y; `los_regained`: lostForSeconds; `los_resume` empty; `los_search_timeout`: seconds |
| `player_dodges_scheduled` | count; `player_dodge_started`: n, offset, direction, ok |
| `dodge_observed` | n, direction, speedCm, back, depth; `dodge_pattern`: state, back, depth, threshold, seq |
| `iframe_sweep_armed` | dodgeAtSeconds; `iframe_sweep_press`: t, sinceFirstAttack; `iframe_probe`: n, sinceDodgePress, outcome, hpApplied; `iframe_sweep_end`: probes |
| `player_activity` | from, to, attackKind; `player_swing`: from, to, heavy; `greed_pattern`: state, source, seq |
| `punish_check` | card, recovery/startup/travel/lightMargin/heavyMargin/required seconds, heavyFinisher, ok |
| `defense_check` | cooldown check or counterplay check fields; `neutral_state`: seq, executorIdle, openWindows |
| `candidate` | attack, card, score, optional seq; `refusal`: attack, card, reason, optional seq |
| `decision` | attack, chosen, score, range, optional phase and seq |
| `heading_commit` | instance, yaw, turnedDegrees, maxRateDegPerSec, capDegPerSec, optional decision/live range and yaw |
| `heading_locked` | instance, yawAtCommit, maxDriftAfterCommitDegrees |
| `warp_step` | instance, from/to, dist/needed/step/actual/moved/budget cm, needed/step/turned/budget degrees; `warp_summary`: instance, movedCm, maxDistanceCm, turnedDeg, maxAngleDeg |
| `warp_blocked` | instance, stepCm, actualCm, blocker, bossX/Y |
| `hold_start` | instance, position, holdAtSeconds, chosenSeconds, min/maxSeconds; `hold_release`: instance, position, heldSeconds, chosenSeconds, min/maxSeconds |
| `cue_fired` | instance, cue, why, mode, visual, audio, visualKind, visualScale, sound |
| `motion_lock` | acquired/released state, instance, mode, optional reason; `motion_intruder` request/result fields |
| `telegraph_cue` | instance, cue, positionSeconds, commitSeconds, visual, audio |
| `playback_start` | encounter, generation, instance, montage, slot, rate, label; `playback`: instance, position, nodeWeight, montageWeight, base, tip |
| `montage_natural_end` | instance, lastPosition, naturalEnd; `montage_end_suppressed`: instance, position |
| `watchdog_timeout` | instance, elapsedSeconds, timeoutSeconds, recoveryEndSeconds, playRate; `watchdog_recovered`: attacksDone |
| `cleanup` | reason, modelIdle, ownedMontageStopped; `stale_callback`: old/new instance, refused, error, newAttackAlive |
| `abort_repeat` | reason, repeats, duplicateCleanups, duplicateReleases, modelIdle |
| `event` | encounter, generation, instance, kind, window, group, localSeconds, label |
| `sweep` | instance, window, from/to, tipDistanceCm, substeps, clamped, optional baked |
| `ring_sweep` | instance, window, from/to, frontLo/HiCm, thicknessCm, targetDist/radiusCm, dzCm, heightCm, contact |
| `grab_catch` | instance, window, socket, releaseAt, modeBefore/modeHeld, attached; `grab_damage`: instance, key, outcome, hpApplied |
| `grab_release` | instance, reason, interrupted, attached, mode, floorFound, floorZ, feetZ, gapCm |
| `sweep_filter` | instance, window, ignoredPawns, first, targetContact, selfHits |
| `hit` | instance, window, key, outcome, hpApplied, healthBefore/After |
| `invariant` | targetHPBefore/After, expectedHP, acceptedHits, appliedDamage; alternate form targetHPBefore/After, damageAPIInvocationsByThisExecutor |
| `pending_hit_queued` | weapon, kind, blades; `attack_row`: weapon, kind, found, posture, bleed, healthMult, optional via |
| `boss_hit` | damage, healthBefore, healthAfter; `player_hits_scheduled`: count |
| `player_hit_injected` | n, offset, ok; `target_shifts_scheduled`: count; `target_shift_injected`: n, dx, dy, dz |
| `posture_drain` | amount, postureBefore/After, max; `posture_regen_start`: posture, sinceLastDrainSeconds, delaySeconds, perSecond |
| `posture_regen_full` | posture, max; `stance_break`: state, duration, generation, phase |
| `stagger_anim` | state-specific start/loop/end/finished fields; `stagger_recovery`: postureRefilled, generation |
| `posture_held` | reason, posture; `stagger_superseded`: reason, health, max, fraction |
| `bleed_buildup` | amount, buildup, threshold, result; `bleed_proc`: procs, damage, healthBefore/After, nextThreshold |
| `phase_transition` | attack, from, to, health, max, fraction; `phase_anim`: triggered/finished state fields |
| `combo_start` | root, move, maxDepth; `combo_step`: node, move, depth |
| `combo_gate` | gate, node, move, outcome, range, yaw, result, next, reason; `combo_gate_duplicate`: gate, result, reason, stateUnchanged |
| `combo_end` | reason |
| `camera_frame` | t, distCm, screen min/max, view size, cornersOnScreen, insideMargin, heightPct, occluded |
| `camera_stage` | index, distanceCm, optional cameraTurnedAway |
| `overlay` | Card, State, Phase, Range, Cone, Window, Posture, Health, Stagger, PhaseHold, optional Parry and Grade |
| `screenshot_requested` | empty or t, viewX/Y, optional showUI, path; `screenshot_quit` empty |
| `guard_state` | instance, window, guard, resolver outcome; `guard_chip`: incoming, applied; `parry_press`: n, t, opened, windowSeconds |
| `parry_reaction` | posture; `attack_row_refused` / `pending_hit_refused`: reason |
| `parry_grade` | grade, scale; `parry_recovery`: grade, extra; `parry_tag`: state, call, reason; `parry_stamina`: before, after, parried |
| `aggro_switch` | from, to — preferred range-band transition |
| `fatigue` | whiffs, scale — consecutive completed whiff count and next rate scale |
| `telegraph_scale` / `telegraph_restore` | card, rate; selected fair-telegraph playback rate and restored active-montage rate |
| `warp_ease` | on; `strafe_stuck`: flipped, movedRatio; `yaw_probe`: sample, yaw |
| `cone_hysteresis` | degrees, seq; `strafe_start`: range, budgetSeconds, speedCmPerSecond, seq |
| `strafe_step` | elapsed, dir, range, movedCm; `strafe_end`: seconds, reason, card |
| `strafe_budget_exhausted` | seconds; `strafe_budget_restarted`: gapSeconds, reason |
| `guard_hook_armed` | mode, seconds; `guard_hook_end` empty |
| `guard_tags` | since, statusBlocking, stateBlocking, abilityParry, abilityBlock, optional statusParryActive and ability presence flags |

Token format compliance alone does not establish gameplay correctness. The emission-location table below is generated from literal token mentions in `Source/OneBossFight`; a missing entry may indicate a dynamically composed log token and requires source review.

Run `python -I Scripts/Tools/check_validator_tokens.py` from the project root to compare literal `UE_LOG` tokens against validator schemas and both indexes below.

## Schema and emission links

Audit snapshot: 138 schemas and 138 emitted tokens; both the semantic index and emission-source index cover all schemas with no duplicate token rows. 133 schemas have a retained valid sample; `attack_row_refused`, `pending_hit_refused`, `strafe_budget_exhausted`, `strafe_budget_restarted`, and `strafe_stuck` do not. The schema regex audit validated 161 literal format variants with zero mismatches (dynamic `ERROR` and `overlay` excluded).

| Token (schema link) | Emission source link(s) |
|---|---|
| [ERROR](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L51) | [RPGFrameworkBossCharacter.cpp:891](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L891), [RPGFrameworkProofFixture.cpp:96](../../Source/OneBossFight/Boss/RPGFrameworkProofFixture.cpp#L96) |
| [RESULT](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L50) | [RPGFrameworkBossCharacter.cpp:618](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L618), [RPGFrameworkBossCharacter.cpp:623](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L623), [RPGFrameworkBossCharacter.cpp:884](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L884) |
| [abort_repeat](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L138) | [RPGFrameworkMoveExecutor.cpp:596](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L596) |
| [aggro_switch](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L205) | [RPGFrameworkBossCharacter.cpp:449](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L449) |
| [anticheese](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L66) | [RPGFrameworkBossCharacter.cpp:459](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L459) |
| [arena_leash](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L67) | [RPGFrameworkBossCharacter.cpp:211](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L211), [RPGFrameworkBossCharacter.cpp:224](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L224), [RPGFrameworkBossCharacter.cpp:255](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L255) |
| [attack_row](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L153) | [RPGHitIntake.cpp:427](../../Source/OneBossFight/Player/RPGHitIntake.cpp#L427), [RPGHitIntake.cpp:597](../../Source/OneBossFight/Player/RPGHitIntake.cpp#L597) |
| [attack_row_refused](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L197) | [RPGHitIntake.cpp:421](../../Source/OneBossFight/Player/RPGHitIntake.cpp#L421) |
| [bleed_buildup](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L169) | [RPGFrameworkBossCharacter.cpp:685](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L685) |
| [bleed_proc](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L170) | [RPGFrameworkBossCharacter.cpp:690](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L690) |
| [boss_dead](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L49) | [RPGFrameworkBossCharacter.cpp:883](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L883) |
| [boss_health](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L41) | [RPGFrameworkBossCharacter.cpp:82](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L82) |
| [boss_health_read](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L42) | [RPGHitIntake.cpp:408](../../Source/OneBossFight/Player/RPGHitIntake.cpp#L408) |
| [boss_hit](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L154) | [RPGFrameworkBossCharacter.cpp:643](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L643) |
| [bystander_spawned](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L47) | [RPGFrameworkBossCharacter.cpp:562](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L562) |
| [camera_frame](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L184) | [RPGCameraProbe.cpp:82](../../Source/OneBossFight/Player/RPGCameraProbe.cpp#L82) |
| [camera_stage](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L185) | [RPGCameraProbe.cpp:78](../../Source/OneBossFight/Player/RPGCameraProbe.cpp#L78) |
| [candidate](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L108) | [RPGFrameworkBossCharacter.cpp:462](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L462) |
| [cleanup](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L135) | [RPGFrameworkMoveExecutor.cpp:207](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L207), [RPGFrameworkMoveExecutor.cpp:588](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L588) |
| [combo_end](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L181) | [RPGFrameworkBossCharacter.cpp:216](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L216), [RPGFrameworkBossCharacter.cpp:345](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L345), [RPGFrameworkBossCharacter.cpp:702](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L702), [RPGFrameworkBossCharacter.cpp:782](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L782), [RPGFrameworkBossCharacter.cpp:797](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L797), [RPGFrameworkBossCharacter.cpp:813](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L813) |
| [combo_gate](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L179) | [RPGFrameworkBossCharacter.cpp:771](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L771) |
| [combo_gate_duplicate](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L180) | [RPGFrameworkBossCharacter.cpp:777](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L777) |
| [combo_pause](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L63) | [RPGFrameworkBossCharacter.cpp:789](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L789) |
| [combo_pause_end](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L64) | [RPGFrameworkBossCharacter.cpp:808](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L808) |
| [combo_start](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L177) | [RPGFrameworkBossCharacter.cpp:571](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L571) |
| [combo_step](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L178) | [RPGFrameworkBossCharacter.cpp:800](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L800), [RPGFrameworkBossCharacter.cpp:816](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L816) |
| [cone_hysteresis](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L211) | [RPGFrameworkBossCharacter.cpp:456](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L456) |
| [cue_fired](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L121) | [RPGFrameworkMoveExecutor.cpp:529](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L529) |
| [decision](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L110) | [RPGFrameworkBossCharacter.cpp:517](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L517) |
| [defense_check](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L103) | [RPGBossFrameworkProfile.cpp:232](../../Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp#L232), [RPGBossFrameworkProfile.cpp:259](../../Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp#L259) |
| [dependencies](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L39) | [RPGFrameworkBossCharacter.cpp:99](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L99) |
| [dodge_observed](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L86) | [RPGFrameworkBossCharacter.cpp:131](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L131) |
| [dodge_pattern](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L87) | [RPGFrameworkBossCharacter.cpp:458](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L458) |
| [encounter_reset](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L48) | [RPGFrameworkBossCharacter.cpp:871](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L871), [RPGFrameworkProofFixture.cpp:109](../../Source/OneBossFight/Boss/RPGFrameworkProofFixture.cpp#L109) |
| [event](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L141) | [RPGFrameworkMoveExecutor.cpp:563](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L563) |
| [fatigue](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L206) | [RPGFrameworkBossCharacter.cpp:588](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L588) |
| [flask_end](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L74) | [RPGFrameworkBossCharacter.cpp:202](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L202) |
| [flask_perceived](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L72) | [RPGFrameworkBossCharacter.cpp:195](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L195) |
| [flask_reaction](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L73) | [RPGFrameworkBossCharacter.cpp:200](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L200) |
| [grab_catch](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L144) | [RPGFrameworkMoveExecutor.cpp:374](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L374) |
| [grab_damage](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L145) | [RPGFrameworkMoveExecutor.cpp:415](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L415) |
| [grab_release](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L146) | [RPGFrameworkMoveExecutor.cpp:394](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L394) |
| [greed_pattern](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L98) | [RPGFrameworkBossCharacter.cpp:457](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L457) |
| [guard_chip](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L201) | [RPGFrameworkMoveExecutor.cpp:291](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L291), [RPGFrameworkMoveExecutor.cpp:413](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L413) |
| [guard_hook_armed](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L218) | [RPGFrameworkBossCharacter.cpp:536](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L536) |
| [guard_hook_end](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L219) | [RPGFrameworkBossCharacter.cpp:279](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L279) |
| [guard_state](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L194) | [RPGFrameworkMoveExecutor.cpp:293](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L293) |
| [guard_tags](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L220) | [RPGFrameworkBossCharacter.cpp:277](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L277) |
| [heading_commit](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L113) | [RPGFrameworkMoveExecutor.cpp:259](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L259) |
| [heading_locked](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L114) | [RPGFrameworkMoveExecutor.cpp:203](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L203) |
| [hit](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L148) | [RPGFrameworkMoveExecutor.cpp:295](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L295) |
| [hold_release](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L120) | [RPGFrameworkMoveExecutor.cpp:492](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L492) |
| [hold_start](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L119) | [RPGFrameworkMoveExecutor.cpp:500](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L500) |
| [hyperarmor_absorbed](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L62) | [RPGFrameworkBossCharacter.cpp:652](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L652) |
| [iframe_probe](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L91) | [RPGFrameworkBossCharacter.cpp:305](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L305) |
| [iframe_sweep_armed](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L89) | [RPGFrameworkBossCharacter.cpp:537](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L537) |
| [iframe_sweep_end](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L92) | [RPGFrameworkBossCharacter.cpp:309](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L309) |
| [iframe_sweep_press](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L90) | [RPGFrameworkBossCharacter.cpp:288](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L288) |
| [invariant](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L149) | [RPGFrameworkBossCharacter.cpp:615](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L615), [RPGFrameworkBossCharacter.cpp:622](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L622) |
| [los_lost](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L77) | [RPGFrameworkBossCharacter.cpp:146](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L146) |
| [los_regained](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L79) | [RPGFrameworkBossCharacter.cpp:147](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L147) |
| [los_resume](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L80) | [RPGFrameworkBossCharacter.cpp:387](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L387) |
| [los_search_start](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L78) | [RPGFrameworkBossCharacter.cpp:381](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L381) |
| [los_search_timeout](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L81) | [RPGFrameworkBossCharacter.cpp:148](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L148) |
| [montage_end_suppressed](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L132) | [RPGFrameworkMoveExecutor.cpp:195](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L195) |
| [montage_natural_end](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L131) | [RPGFrameworkMoveExecutor.cpp:242](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L242) |
| [motion_intruder](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L124) | [RPGFrameworkMoveExecutor.cpp:231](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L231), [RPGFrameworkMoveExecutor.cpp:236](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L236) |
| [motion_lock](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L123) | [RPGFrameworkMoveExecutor.cpp:538](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L538), [RPGFrameworkMoveExecutor.cpp:548](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L548) |
| [nav](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L56) | [RPGFrameworkBossController.cpp:47](../../Source/OneBossFight/Boss/RPGFrameworkBossController.cpp#L47) |
| [nav_not_ready](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L55) | [RPGFrameworkProofFixture.cpp:80](../../Source/OneBossFight/Boss/RPGFrameworkProofFixture.cpp#L80) |
| [nav_ready](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L54) | [RPGFrameworkProofFixture.cpp:85](../../Source/OneBossFight/Boss/RPGFrameworkProofFixture.cpp#L85) |
| [neutral_state](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L105) | [RPGFrameworkBossCharacter.cpp:515](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L515) |
| [overlay](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L188) | [RPGFrameworkBossCharacter.cpp:752](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L752) |
| [pack_style_known](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L46) | [RPGFrameworkProofFixture.cpp:60](../../Source/OneBossFight/Boss/RPGFrameworkProofFixture.cpp#L60) |
| [parry_grade](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L199) | [RPGFrameworkMoveExecutor.cpp:44](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L44) |
| [parry_press](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L195) | [RPGPlayerParry.cpp:107](../../Source/OneBossFight/Player/RPGPlayerParry.cpp#L107) |
| [parry_reaction](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L196) | [RPGFrameworkBossCharacter.cpp:240](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L240) |
| [parry_recovery](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L202) | [RPGFrameworkBossCharacter.cpp:594](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L594) |
| [parry_stamina](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L200) | [RPGPlayerParry.cpp:86](../../Source/OneBossFight/Player/RPGPlayerParry.cpp#L86), [RPGPlayerParry.cpp:91](../../Source/OneBossFight/Player/RPGPlayerParry.cpp#L91), [RPGPlayerParry.cpp:175](../../Source/OneBossFight/Player/RPGPlayerParry.cpp#L175) |
| [parry_tag](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L210) | [RPGPlayerParry.cpp:200](../../Source/OneBossFight/Player/RPGPlayerParry.cpp#L200) |
| [pending_hit_queued](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L152) | [RPGHitIntake.cpp:461](../../Source/OneBossFight/Player/RPGHitIntake.cpp#L461) |
| [pending_hit_refused](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L198) | [RPGHitIntake.cpp:446](../../Source/OneBossFight/Player/RPGHitIntake.cpp#L446) |
| [phase_anim](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L174) | [RPGFrameworkBossCharacter.cpp:398](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L398), [RPGFrameworkBossCharacter.cpp:416](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L416), [RPGFrameworkBossCharacter.cpp:707](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L707) |
| [phase_transition](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L173) | [RPGFrameworkBossCharacter.cpp:407](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L407) |
| [playback](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L130) | [RPGFrameworkMoveExecutor.cpp:264](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L264) |
| [playback_start](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L129) | [RPGFrameworkMoveExecutor.cpp:172](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L172) |
| [player_activity](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L96) | [RPGFrameworkBossCharacter.cpp:178](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L178) |
| [player_dodge_started](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L85) | [RPGFrameworkBossCharacter.cpp:334](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L334) |
| [player_dodges_scheduled](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L84) | [RPGFrameworkBossCharacter.cpp:542](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L542) |
| [player_drink_started](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L71) | [RPGFrameworkBossCharacter.cpp:326](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L326) |
| [player_drinks_scheduled](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L70) | [RPGFrameworkBossCharacter.cpp:534](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L534) |
| [player_hit_injected](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L156) | [RPGFrameworkBossCharacter.cpp:316](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L316) |
| [player_hits_scheduled](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L155) | [RPGFrameworkBossCharacter.cpp:548](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L548) |
| [player_swing](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L97) | [RPGFrameworkBossCharacter.cpp:174](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L174) |
| [posture_drain](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L161) | [RPGFrameworkBossCharacter.cpp:658](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L658) |
| [posture_held](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L167) | [RPGFrameworkBossCharacter.cpp:648](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L648) |
| [posture_regen_full](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L163) | [RPGFrameworkBossCharacter.cpp:371](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L371) |
| [posture_regen_start](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L162) | [RPGFrameworkBossCharacter.cpp:370](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L370) |
| [punish_check](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L101) | [RPGBossFrameworkProfile.cpp:251](../../Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp#L251) |
| [refusal](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L109) | [RPGFrameworkBossCharacter.cpp:463](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L463) |
| [reposition](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L59) | [RPGFrameworkBossCharacter.cpp:484](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L484) |
| [reposition_turn](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L60) | [RPGFrameworkBossCharacter.cpp:468](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L468) |
| [reposition_turn_end](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L61) | [RPGFrameworkBossCharacter.cpp:478](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L478) |
| [ring_sweep](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L143) | [RPGFrameworkMoveExecutor.cpp:311](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L311) |
| [screenshot_quit](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L191) | [RPGCameraProbe.cpp:29](../../Source/OneBossFight/Player/RPGCameraProbe.cpp#L29) |
| [screenshot_requested](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L190) | [RPGCameraProbe.cpp:35](../../Source/OneBossFight/Player/RPGCameraProbe.cpp#L35) |
| [slot_graph](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L40) | [RPGFrameworkMoveExecutor.cpp:89](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L89) |
| [stagger_anim](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L165) | [RPGFrameworkBossCharacter.cpp:714](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L714), [RPGFrameworkBossCharacter.cpp:724](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L724), [RPGFrameworkBossCharacter.cpp:846](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L846), [RPGFrameworkBossCharacter.cpp:852](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L852) |
| [stagger_recovery](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L166) | [RPGFrameworkBossCharacter.cpp:725](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L725) |
| [stagger_superseded](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L168) | [RPGFrameworkBossCharacter.cpp:359](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L359) |
| [stale_callback](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L136) | [RPGFrameworkMoveExecutor.cpp:166](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L166) |
| [stance_break](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L164) | [RPGFrameworkBossCharacter.cpp:716](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L716) |
| [strafe_budget_exhausted](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L215) | [RPGFrameworkBossCharacter.cpp:510](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L510) |
| [strafe_budget_restarted](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L216) | [RPGFrameworkBossCharacter.cpp:493](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L493) |
| [strafe_end](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L214) | [RPGFrameworkBossCharacter.cpp:513](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L513) |
| [strafe_start](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L212) | [RPGFrameworkBossCharacter.cpp:492](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L492) |
| [strafe_step](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L213) | [RPGFrameworkBossCharacter.cpp:507](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L507) |
| [strafe_stuck](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L208) | [RPGFrameworkBossCharacter.cpp:505](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L505) |
| [sweep](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L142) | [RPGFrameworkMoveExecutor.cpp:335](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L335) |
| [sweep_filter](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L147) | [RPGFrameworkMoveExecutor.cpp:356](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L356) |
| [target_fault_injected](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L45) | [RPGFrameworkBossCharacter.cpp:553](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L553) |
| [target_health_init](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L43) | [RPGFrameworkProofFixture.cpp:66](../../Source/OneBossFight/Boss/RPGFrameworkProofFixture.cpp#L66) |
| [target_health_mismatch](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L44) | [RPGFrameworkBossCharacter.cpp:260](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L260) |
| [target_shift_injected](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L158) | [RPGFrameworkBossCharacter.cpp:245](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L245) |
| [target_shifts_scheduled](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L157) | [RPGFrameworkBossCharacter.cpp:528](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L528) |
| [telegraph_cue](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L126) | [RPGFrameworkMoveExecutor.cpp:528](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L528) |
| [telegraph_restore](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L204) | [RPGFrameworkMoveExecutor.cpp:575](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L575) |
| [telegraph_scale](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L203) | [RPGFrameworkMoveExecutor.cpp:141](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L141) |
| [walk](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L57) | [RPGFrameworkBossCharacter.cpp:235](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L235) |
| [walk_center_bias](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L65) | [RPGFrameworkBossController.cpp:30](../../Source/OneBossFight/Boss/RPGFrameworkBossController.cpp#L30) |
| [walk_resumed](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L58) | [RPGFrameworkBossCharacter.cpp:731](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L731) |
| [warp_blocked](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L117) | [RPGFrameworkMoveExecutor.cpp:473](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L473) |
| [warp_ease](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L207) | [RPGFrameworkMoveExecutor.cpp:454](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L454) |
| [warp_step](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L115) | [RPGFrameworkMoveExecutor.cpp:476](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L476) |
| [warp_summary](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L116) | [RPGFrameworkMoveExecutor.cpp:431](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L431) |
| [watchdog_recovered](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L134) | [RPGFrameworkBossCharacter.cpp:346](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L346) |
| [watchdog_timeout](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L133) | [RPGFrameworkMoveExecutor.cpp:189](../../Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L189) |
| [yaw_probe](../../Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py#L209) | [RPGFrameworkBossCharacter.cpp:436](../../Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L436) |

## Emission source locations

Literal `[FrameworkProof]` token emissions are in these files (the validator contains all 138 accepted schema names). Search within the listed source when a schema or payload changes.

| Token | Source file(s) containing its emission |
|---|---|
| `dependencies` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `slot_graph` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `telegraph_scale` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `telegraph_restore` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `boss_health` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp`, `Source/OneBossFight/Player/RPGHitIntake.cpp` |
| `boss_health_read` | `Source/OneBossFight/Player/RPGHitIntake.cpp` |
| `target_health_init` | `Source/OneBossFight/Boss/RPGFrameworkProofFixture.cpp` |
| `target_health_mismatch` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `target_fault_injected` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `pack_style_known` | `Source/OneBossFight/Boss/RPGFrameworkProofFixture.cpp` |
| `bystander_spawned` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `encounter_reset` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp`, `Source/OneBossFight/Boss/RPGFrameworkProofFixture.cpp` |
| `boss_dead` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `RESULT` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp`; `acceptedHits`, `parriedHits`, and `guardedHits` are executor-lifetime totals across generations. |
| `ERROR` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp`, `Source/OneBossFight/Boss/RPGFrameworkProofFixture.cpp` |
| `nav_ready` | `Source/OneBossFight/Boss/RPGFrameworkProofFixture.cpp` |
| `nav_not_ready` | `Source/OneBossFight/Boss/RPGFrameworkProofFixture.cpp` |
| `nav` | `Source/OneBossFight/Boss/RPGFrameworkBossController.cpp`, `Source/OneBossFight/Boss/RPGFrameworkProofFixture.cpp` |
| `walk` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp`, `Source/OneBossFight/Boss/RPGFrameworkBossController.cpp` |
| `walk_resumed` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `reposition` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `reposition_turn` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `reposition_turn_end` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `hyperarmor_absorbed` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `combo_pause` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `combo_pause_end` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `walk_center_bias` | `Source/OneBossFight/Boss/RPGFrameworkBossController.cpp` |
| `anticheese` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `arena_leash` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `player_drinks_scheduled` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `player_drink_started` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `flask_perceived` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `flask_reaction` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `flask_end` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `los_lost` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `los_search_start` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `los_regained` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `los_resume` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `los_search_timeout` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `player_dodges_scheduled` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `player_dodge_started` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `dodge_observed` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `dodge_pattern` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `iframe_sweep_armed` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `iframe_sweep_press` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `iframe_probe` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `iframe_sweep_end` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `player_activity` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `player_swing` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `greed_pattern` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `punish_check` | `Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp` |
| `defense_check` | `Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp` |
| `neutral_state` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `candidate` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `refusal` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `decision` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp`, `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `heading_commit` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `heading_locked` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `warp_step` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `warp_summary` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `warp_blocked` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `hold_start` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `hold_release` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `cue_fired` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `motion_lock` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `motion_intruder` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `telegraph_cue` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `playback_start` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `playback` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `montage_natural_end` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `montage_end_suppressed` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `watchdog_timeout` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `watchdog_recovered` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `cleanup` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `stale_callback` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `abort_repeat` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `event` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `sweep` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp`, `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `ring_sweep` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `grab_catch` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `grab_damage` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `grab_release` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `sweep_filter` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `hit` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp`, `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp`, `Source/OneBossFight/Player/RPGHitIntake.cpp` |
| `invariant` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `pending_hit_queued` | `Source/OneBossFight/Player/RPGHitIntake.cpp` |
| `attack_row` | `Source/OneBossFight/Player/RPGHitIntake.cpp` |
| `boss_hit` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `player_hits_scheduled` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `player_hit_injected` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `target_shifts_scheduled` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `target_shift_injected` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `posture_drain` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `posture_regen_start` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `posture_regen_full` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `stance_break` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `stagger_anim` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `stagger_recovery` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `posture_held` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `stagger_superseded` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `bleed_buildup` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `bleed_proc` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `phase_transition` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `phase_anim` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `combo_start` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `combo_step` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `combo_gate` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `combo_gate_duplicate` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `combo_end` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `camera_frame` | `Source/OneBossFight/Player/RPGCameraProbe.cpp` |
| `camera_stage` | `Source/OneBossFight/Player/RPGCameraProbe.cpp` |
| `overlay` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `screenshot_requested` | `Source/OneBossFight/Player/RPGCameraProbe.cpp` |
| `screenshot_quit` | `Source/OneBossFight/Player/RPGCameraProbe.cpp` |
| `guard_state` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `guard_chip` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `parry_press` | `Source/OneBossFight/Player/RPGPlayerParry.cpp` |
| `parry_reaction` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `attack_row_refused` | `Source/OneBossFight/Player/RPGHitIntake.cpp` |
| `pending_hit_refused` | `Source/OneBossFight/Player/RPGHitIntake.cpp` |
| `parry_grade` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `parry_recovery` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `aggro_switch` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `fatigue` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `warp_ease` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` |
| `strafe_stuck` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `yaw_probe` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `parry_tag` | `Source/OneBossFight/Player/RPGPlayerParry.cpp` |
| `cone_hysteresis` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `strafe_start` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `strafe_step` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `strafe_end` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `strafe_budget_exhausted` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `strafe_budget_restarted` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `guard_hook_armed` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `guard_hook_end` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `guard_tags` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp` |
| `parry_stamina` | `Source/OneBossFight/Player/RPGPlayerParry.cpp` |
