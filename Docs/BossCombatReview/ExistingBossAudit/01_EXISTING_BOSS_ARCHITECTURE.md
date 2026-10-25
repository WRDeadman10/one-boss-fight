# Existing boss architecture

Audit date: 2026-10-25. Scope: read-only Phase 2 against all ten saved reference documents and all 83 requirements. Only the twelve requested files in this directory are authored. No gameplay, assets, configuration, project trackers, mailbox, build, editor session or tests were changed/run.

## Conclusion and evidence boundary

The active design is **the Advanced ARPG pack's great-sword boss plus project-owned C++ extensions**, not the retired custom Sevarog combat implementation. This is not Epic GAS: reflected Blueprint abilities/effects/attributes form the pack's own ability framework.

Source-confirmed means the inspected code contains the behavior, not that a packaged fight or player experience was validated. Saved runtime observations are dated historical evidence. Binary reference strings identify dependencies, never node execution or timing. The editor is Claude-owned under the team protocol; no handoff was given. Therefore current BT graphs, asset defaults and AnimBP motion ownership remain explicitly UNVERIFIED where saved exports cannot establish them.

Current source, recent mailbox C-84 and actual logs supersede older descriptions. In particular, dormant/wake and authored close replacements now exist; older design reports saying they are absent are stale. B10b's old pose-damping diagnosis is superseded by C-84/KI-106: a setup-dependent driver discrepancy remains, not a demonstrated product defect.

## Runtime route

| Layer | Identified route | Evidence and qualification |
|---|---|---|
| Startup | UE association 5.5, runtime module OneBossFight; single-player project | [OneBossFight.uproject](C:/UnrealProject/OneBossFight/OneBossFight.uproject:1). StateTree plugins enabled does not prove active use. |
| Map/game mode | /Game/OneBossFight/Levels/L_SevarogArena; /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_AdvancedGameMode | [DefaultEngine.ini](C:/UnrealProject/OneBossFight/Config/DefaultEngine.ini:4); map package references corroborate both. |
| Player | BP_CombatPlayerCharacter, combat mannequin, ABP_CombatCharacter | [Subsystem:79](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:79); [Tests:1063](C:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGAutomationTests.cpp:1063); current assignment still needs U01 live dump. Greystone is retired. |
| Boss | /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss | [Subsystem:92](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:92); map package references and [Tests:1201](C:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGAutomationTests.cpp:1201). |
| Boss info/style | Same directory: ExampleGreatSwordBoss and ExampleGreatSwordBossCombatStyle | Map contains boss info reference. Boss BP defaults reference ExampleSwordEnemy instead: preserve placed EnemyInfoRef override; test at [Tests:1214](C:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGAutomationTests.cpp:1214). |
| Controller/brain | BP_MasterEnemy dependency chain points to BP_BaseAIController; BP_BehaviorManagerComponent; BT_ExampleBoss + BB_Base + SM_Humanoid_CombatBehavior | Package references, [Encounter:156](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.cpp:156), [Phases:526](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.cpp:526); exact current possessed controller/defaults/BT connections UNVERIFIED U01–U03. |
| Boss animation | Info references /Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/ABP_HumanoidEnemyCharacter; style references ABP_2HandedSwordLayer | Dependency identity, not proof of live slot graph or root-motion mode; U04. |
| Ability playback | GA_GS_Boss_* derives from GA_EnemyMeleeAttack; own A4/A5 dynamic clips bypass pack ability playback | Saved close-ability T3D parent; [Export:270](C:/UnrealProject/OneBossFight/Saved/asset_text/GA_EnemyMeleeAttack.t3d:270); [Tracker:234](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:234). |
| Presentation body | Boss01 follower meshes and separate visible greatsword; hidden pack mesh/weapon remain gameplay drivers | [Look:54](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossLook.cpp:54). No gameplay collision on followers. |
| Native attachment | World subsystem handles existing and newly spawned matching pawns, adds components once | [Subsystem:39](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:39), [Subsystem:138](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:138). |

All /Game paths map to Content/<remaining path>.uasset, except the map (.umap). Exact unresolved dependencies and required inspection are catalogued in document 11.

## Ownership map

| Responsibility | Current owner(s) | Integration constraint |
|---|---|---|
| Perception, ordinary choice, chase/strafe | Pack controller, BT, behavior state machine, ability activation rules | Native tracker is not the selector; do not replace BT based on an uninspected graph. |
| Montage execution | Pack abilities for Close/A2/A6 and other pack actions; tracker PlayClip for A4/A5; stance/phase/wake/death components for special states | Several entry points; not one pre-start executor transaction. |
| Identity/stage/heading | RPGAttackTracker polls active montage, recognizes names, assigns instance, samples montage position | ID is assigned after playback; same timing index is not a montage-instance identity. |
| Pack hit queries | BP_EnemyAbilitySweepingTraceTarget through BP_CollisionComponent and ANS_CollisionTrace | RPGPackTrace is reflection access, not a replacement trace algorithm. RPGTraceAudit is an observer, not production damage. |
| Pack trace safety | RPGTraceGuard closes on explicit interruptions, carries HitActors across windows of an instance, suppresses wall-obstructed player samples | Keep actual notify/mesh/trace tick ordering; inspect U05 before changing. |
| Own special queries/damage | LowSweep, Javelin, Shockwave -> RPGDamageResolver -> pack health attribute | Resolver covers A4/A5/wave, NOT pack blade/central hits. Guard/parry/reactions are not unified. |
| Player offense | Pack damage; RPGHitIntake next-frame records + table posture/bleed/health scaling; RPGSwingTracker for swing/stamina/armor | Dual blades can apply pack HP twice while posture/bleed merge once; this is explicitly documented, not automatically a duplicate defect. |
| Posture/break/critical | RPGBossPosture -> RPGBossStagger; pure RPGBossRules; RPGBossInterrupt | Separate 100-point pool, quiet regen, one bounded break/riposte, phase handoff. |
| Encounter reset | RPGBossEncounter generation, home transform, phase/posture/bleed reset; player respawn detection | Generation invalidates own projectiles; death-active reset refused. Not a proven navigation leash. |
| Phase | RPGBossPhases: 60%, one transition, leap unlock, pack rates/damage and movement buffs | Transition interrupts ordinary attacks by project policy; queues behind stance break. |
| Feedback/debug | BossHud, CameraRig, Legend, music/footsteps/flipbooks; CombatDebug, TraceAudit, DamageResolver audit | Existing diagnostics useful, but not a full candidate/seed decision trace. |

## Active versus retired

Preserve active pack assets and project components. Source/Boss/RPGSevarogDirector and Pack/RPGHideBones are retained legacy code, not the active boss. Content/OneBossFight/SevarogPack, GreystonePack and Characters/Greystone are retired content; Archive/CppCombat_2026-10-19 is retired combat. [State:13](C:/UnrealProject/OneBossFight/Documentation/PROJECT_STATE.md:13) and [Tests:1177](C:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGAutomationTests.cpp:1177) identify this boundary. No deletion is recommended in this audit.

The pack combat style still references MidRangeAttack, SprintAttack, RetaliationAttack and TurnInPlace in addition to the tracked catalogue. Their reach, choice and timing must not be assumed covered by A1–A6 merely because the tracker only lists those IDs. U03/U06 require an actual live ability pool export.

## Configuration and data

Gameplay tag tables are registered in [DefaultGameplayTags.ini](C:/UnrealProject/OneBossFight/Config/DefaultGameplayTags.ini:1); Attribute.Poise is project-added. DefaultEngine collision profiles make Pawn/CharacterMesh ignore visibility/camera; Interactable is a custom channel. These config facts alone do not establish live trace filtering. [DefaultGame.ini](C:/UnrealProject/OneBossFight/Config/DefaultGame.ini:19) cooks own assets and required pack directories.

DA_WeaponAttacks is an existing player table, not a boss utility catalogue. Boss timing lives in FRPGAttackTiming constructor rows; phase tuning in component properties; pack attack data/montages in abilities/style. Reuse these boundaries before considering data consolidation.

## Snapshot fingerprints

SHA-256 at audit read time (not a commit or compiled-build fingerprint):

- RPGAttackTracker.cpp: F2D2615F1B938AA8BF1F4AD9D7574B1876446823D83B87CD69521CA9D1153F0C
- RPGBossShockwave.cpp: 9632381F60E92D3F2D7CC7362883CBC03C3B258191ABBBB4755A4BC9591CF3A4
- RPGBossHealPunish.cpp: 1E63046D9C215FD0D7A5F894EE1B4539D64DDBEFD9C80812CECBBAE89C476906
- RPGDamageResolver.cpp: 82DA0DD3400A049D92BD96409F90DB58A319FD7DB73E44F7B46B766E938A6BCA
- Saved/asset_text/GA_EnemyMeleeAttack.t3d: 0D41BA870691B6F33DCEAA53BA5F72AC67A931D3FDC4C908CC2D97C23892ADD2

T3D last-write time is 2026-10-19 11:50:59 local; corresponding uasset reports 2025-12-12 17:33:54. Timestamps do not prove equivalence. It is reliable evidence of the exported graph, not a newly verified current editor graph. Saved/Logs/OneBossFight.log is mutable; observations cited here are from its 2026-10-24 19:38–19:40 UTC entries. No new gameplay evidence was generated.

