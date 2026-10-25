# Systems to preserve

The evidence supports incremental extensions, not replacement with the Bellwarden example.

| System | Decision | Why and integration risk |
|---|---|---|
| Pack boss/player/controller/BT/ability framework | Preserve backbone; inspect first | Already runs the duel and owns attack data, montage dispatch, movement and effects. Replacing it before U02/U03 would discard unknown working behavior. |
| RPGPlayerMovesSubsystem | Preserve class-filtered attachment | Supports existing/spawned pawns without asset edits; changing class names or attachment order can silently disable extensions. [Subsystem:39](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:39), [Subsystem:79](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:79). |
| RPGPackTrace / RPGBlueprintCall facade | Preserve typed/reflection validation | Centralizes pack names and warnings. Pack reimport is already risky; never bypass name/signature checks. [Trace:34](C:/UnrealProject/OneBossFight/Source/OneBossFight/Pack/RPGPackTrace.cpp:34); [Tests:1101](C:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGAutomationTests.cpp:1101). |
| RPGBossPosture and RPGBossRules | Preserve logic; extend tests | Separate health/posture, delay/rate, holds and explicit priorities. Avoid reintroducing the legacy poise pool as a second authority. [Posture:34](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPosture.cpp:34), [Rules:8](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossRules.h:8). |
| RPGBossStagger/riposte | Preserve reward loop; targeted input fix only if reproduced | One execution, paired clips, cleanup and phase handoff. Changes can break input restoration, collision, death and queued transition. [Stagger:553](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossStagger.cpp:553), [Stagger:730](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossStagger.cpp:730). |
| RPGBossEncounter generation/reset | Preserve; optional leash extension later | Own projectiles/callbacks rely on generation; phase/buff/posture/bleed reset ordering matters. Never revive a death-active boss. [Encounter:297](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.cpp:297). |
| RPGBossPhases | Preserve threshold, monotonicity and priority policy | Buff reversal and leap tag lock must stay idempotent; moving threshold policy changes earned posture rewards. [Phases:245](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.cpp:245), [Phases:349](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.cpp:349). |
| RPGBossCloseClipSwap | Preserve live-instance, all-or-none swap approach | It leaves pack assets intact and restores on lifecycle exits. Extend fallback timing contract, not destructive montage replacement. [Swap:133](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp:133). |
| AttackTracker | Extend/partially refactor at pack boundary | Keep move names, counters and heading semantics; introduce reliable identity/timing/finalization without a rival planner. |
| TraceGuard and interrupt helpers | Preserve immediate close and dedupe/wall safeguards | Changes must keep animation/trace tick order and cannot depend only on NotifyEnd. [Guard:22](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGTraceGuard.cpp:22), [Interrupt:16](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossInterrupt.cpp:16). |
| DamageResolver and special geometry | Preserve generation/iframe/dedupe checks; extend | Bring pack outcome provenance/defense policy through adapters. Do not delete functioning pack damage or silently change blockability. |
| HitIntake/WeaponAttackTable/SwingTracker/BuildLoadout | Preserve player build integration | Stamina, posture, bleed and health scaling encode current balance. Native merged posture is not proof pack dual-blade HP should be merged. [Intake:421](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp:421), [Weapon:35](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGWeaponAttackTable.cpp:35). |
| DodgeTiming/IFrameMonitor | Preserve measured defensive baseline | Keep3.2m roll constraint; no dodge retune to compensate for hidden threat or faulty boss contact. [Dodge:21](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGDodgeTiming.cpp:21), [IFrames:145](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGIFrameMonitor.cpp:145). |
| CameraRig/Legend/HUD/music | Preserve controls and cleanup; validate presentation | Shake reduction and real-time effect restoration exist. Audio/visual feel not certified by logic tests. |
| Existing automation/drivers/packaged benchmark | Preserve harness, strengthen provenance | Record rpg.WakeClip and telegraph switches, actual runtime montage and build. Do not relax assertions to declare a product fix. |

## Reusable assets

- /Game/OneBossFight/Boss01/Animations/AM_Boss01_A1, AM_Boss01_A3a, AM_Boss01_A3b and their authored sequences.
- Pack GS_Attack04_Montage remains A1b; GS_ChargedAttack_Montage and GS_LeapAttack_Montage remain stand-ins until measured replacement approval.
- Authored A4/A5, dormant/wake, roar, stagger and paired riposte clips remain useful. Their existence does not certify visual contact.
- /Game/OneBossFight/Data/DA_WeaponAttacks remains the player tuning source; do not repurpose it into a boss selector.
- ExampleGreatSwordBoss / ExampleGreatSwordBossCombatStyle and pack attack-data objects remain integration sources. Exact effective values require U03/U07.
- Boss01 body/accessories/sword can stay leader-pose driven. Align visible geometry to production trace through measured adjustments if needed.

## Refactor only where demonstrated

The justified architectural work is narrow: pre-start identity and lifecycle boundary, asset-specific timing/fallback, correlated damage outcomes, explicit branch/default recovery. A new AI framework, full combat rewrite, GAS migration, StateTree migration or removal of legacy assets is not justified by this audit.

Before any future change, preserve existing assets in place, record baseline/fallback values, use project-owned adapters, and run the named regressions. Rollback means reverting only that approved change or disabling its project-owned integration—not deleting/recreating referenced assets, resetting the worktree or overwriting another agent.

