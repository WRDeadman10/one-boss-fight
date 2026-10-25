# Unverified assets and required validation

This is an inspection/test backlog, not permission to run or implement it. No editor, PIE, build, package, asset save or new gameplay test was performed for this audit. Claude retains editor/build/test/performance ownership; obtain the handoff before live inspection. Do not use an export command that compiles or saves assets.

## Evidence boundary

C++ statements describe the inspected source snapshot. Historical tests describe the recorded build/run only. Package reference strings establish asset dependencies, not Blueprint edges, montage timing, current defaults or gameplay quality.

The saved [GA_EnemyMeleeAttack export](C:/UnrealProject/OneBossFight/Saved/asset_text/GA_EnemyMeleeAttack.t3d:247) contains inspectable graphs and pin connections, detailed in document 06. It is dated October 19 and was not regenerated; current package equivalence is unverified. The close-ability export establishes its parent, not its complete live inherited configuration.

Each U item below remains **UNVERIFIED** for the missing information stated. A native subset can nevertheless be IMPLEMENTED or PARTIAL in the matrix. These twelve packages are not twelve missing features.

All paths starting /Game are exact Unreal package paths; physical files are under C:/UnrealProject/OneBossFight/Content with .uasset, except the arena's .umap. Related runtime-created objects must be inspected separately from asset defaults.

## U01 — Current runtime composition

**Assets:**

- /Game/OneBossFight/Levels/L_SevarogArena
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_AdvancedGameMode
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/ExampleGreatSwordBoss
- /Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BP_MasterEnemy
- /Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BP_BaseAIController

**Known:** project configuration, dependency route, native attachment filters and historical placed EnemyInfoRef override. [Subsystem:79](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:79)

**Missing:** fresh placed-actor overrides, actual spawned controller/pawn classes, attached components and runtime-created ability pool. The boss Blueprint default info and placed arena override differ; inspecting only defaults is insufficient.

**Read-only inspection:** record world settings, placed actor class/info, controller, mesh, anim instance and component/ability names in the current map. Confirm this route before examining retired content.

**Acceptance:** one recorded map-to-pawn-to-controller/info/ability chain with asset and source fingerprints; no default-only inference.

## U02 — High-level selection, perception and movement

**Assets:**

- /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/BT_ExampleBoss
- /Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BB_Base
- /Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/Components/BP_BehaviorManagerComponent
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/States/SM_Humanoid_CombatBehavior
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/States/BP_EnemyImpactDecision
- /Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BehaviorTreeNodes/S_CalculateTargetValues
- /Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BehaviorTreeNodes/S_RotateCharacter
- /Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BehaviorTreeNodes/S_UpdateBehavior
- /Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BehaviorTreeNodes/S_UpdateTrackTarget
- /Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BehaviorTreeNodes/T_Strafing
- /Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BehaviorTreeNodes/T_TryActivateAbilitiesByTags
- /Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BehaviorTreeNodes/T_WaitAnimatingAbilityEnd
- /Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BehaviorTreeNodes/D_ChanceCondition

**Missing:** connected BT topology, service intervals, abort modes, BB reads/writes, target loss/memory, range bands, chase/strafe/retreat priority, wait durations, history/weights, failed-choice fallback and movement cancellation.

**Inspection/test:** export graph edges and instance/default values without saving. Trace one neutral decision through eligibility, choice and activation; then target behind/occluded/outside reach/dead, repeated action, stationary target and phase change.

**Acceptance:** explain why an attack or movement was selected from recorded context. Do not call unknown utility/adaptation/retreat logic absent.

## U03 — Ability transaction, attack pool and combo graph

**Assets:**

- /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/ExampleGreatSwordBossCombatStyle
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/AI/GA_EnemyMeleeAttack
- /Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/Abilities/GA_MeleeBase
- /Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/Abilities/GA_Attack
- /Game/AdvancedARPGCombat/AdvancedCombatFramework/AbilitySystem/Abilities/BP_AdvancedGameplayAbility
- /Game/AdvancedARPGCombat/AdvancedCombatFramework/AbilitySystem/BP_AdvancedAbilitySystemComponent
- /Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/AnimNotifies/AN_PerformFollowUp
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/GA_GS_Boss_CloseAttack
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/GA_GS_Boss_CloseRare
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/GA_GS_Boss_LeapAttack
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/GA_GS_Boss_MidRangeAttack
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/GA_GS_Boss_SprintAttack
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/GA_GS_Boss_RetaliationAttack
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/GA_GS_Boss_TurnInPlace

**Missing:** current inherited CanActivate/Activate/Commit/OnAbilityEnd connections; cooldown consumption and rollback; actual runtime montage arrays after native swap; notify-to-successor edges, failed follow-up recovery, cancellation and watchdog coverage. Midrange/sprint/retaliation moves must not be silently omitted from the damaging catalogue.

**Inspection/test:** compare current graph with saved EventGraph, CanActivateAbility and GetAbilityMontage exports; record all live ability tags, cooldowns, montage choices and predecessor/successor edges. Exercise denied branch, missing animation, repeat same montage, interruption and normal completion.

**Acceptance:** every natural damaging action accounted for, transaction/finalize owner identified, and finite combo/default recovery behavior measured. Native ID deficiency is separately established; a pack internal ID must not be assumed to propagate into native consumers.

## U04 — Animation graph and motion ownership

**Assets:**

- /Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/ABP_HumanoidEnemyCharacter
- /Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/ABP_CombatCharacter
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Animation/AnimLayers/ABP_2HandedSwordLayer
- /Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword

**Missing:** slot/layer blends, root-motion mode, root translation/yaw, motion-warping usage if any, locomotion cancellation during attacks and hidden leader/visible follower alignment.

**Inspection/test:** read AnimGraph, linked layers, slot and per-sequence root settings; capture actor/root/mesh/visible blade transforms while attacking, following up and interrupted. Overlay production trace positions, not only diagnostic approximations.

**Acceptance:** identify the owner of translation/yaw in each attack phase; measure visible contact error before changing sockets, trace radii or animation.

## U05 — Production trace and damage graph

**Assets:**

- /Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/Collision/BP_EnemyAbilitySweepingTraceTarget
- /Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/Collision/BP_AbilitySweepingTraceTarget
- /Game/AdvancedARPGCombat/AdvancedCombatFramework/CollisionSystem/BP_CollisionComponent
- /Game/AdvancedARPGCombat/AdvancedCombatFramework/CollisionSystem/AnimNotifies/ANS_CollisionTrace
- /Game/AdvancedARPGCombat/AdvancedCombatFramework/CollisionSystem/Objects/BP_HitData
- /Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/DataAssets/BP_AttackData

**Known:** native reflection facade, trace guard, historical five-socket/radius-50 samples, own special resolver. [Trace:221](C:/UnrealProject/OneBossFight/Source/OneBossFight/Pack/RPGPackTrace.cpp:221) [Guard:126](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGTraceGuard.cpp:126)

**Missing:** actual sweep nodes and ordering, interpolation/substeps, filtering, hitset lifecycle, central A2/A6 damage volume, attack-data values, block/parry/armor evaluation and accepted/rejected outcome propagation.

**Inspection/test:** trace notify begin/tick/end through collision query, HitActors, effect calculation and final health write. Record tick group/prerequisites and all damage paths. Test close crossings, fast arcs, multiple windows, iframe boundaries, walls, reset/death and direct-plus-wave.

**Acceptance:** production path is distinguished from RPGTraceAudit's observer sweep; every accepted health change has a known source and defense outcome.

## U06 — Effective montage/notifies and per-move timing

**Assets:**

- /Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_Attack01_Montage
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_Attack02_Montage
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_Attack03_Montage
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_Attack04_Montage
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_ChargedAttack_Montage
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_LeapAttack_Montage
- /Game/OneBossFight/Boss01/Animations/AM_Boss01_A1
- /Game/OneBossFight/Boss01/Animations/AM_Boss01_A3a
- /Game/OneBossFight/Boss01/Animations/AM_Boss01_A3b
- /Game/OneBossFight/Boss01/Animations/AN_Boss01_A4_LowSweep
- /Game/OneBossFight/Boss01/Animations/AN_Boss01_A5_JavelinThrow
- /Game/OneBossFight/Boss01/Animations/AN_Boss01_DormantIdle
- /Game/OneBossFight/Boss01/Animations/AN_Boss01_Wake
- /Game/OneBossFight/Boss01/Animations/AN_Boss01_PhaseRoar
- /Game/OneBossFight/Boss01/Animations/AN_Riposte_Player_Front
- /Game/OneBossFight/Boss01/Animations/AN_Riposte_Boss_Reaction

**Missing:** current montage sections, notify start/end and offsets, blend-out, effective play-rate interactions, full recovery/next-action gate, contact-to-cue alignment and fallbacks. Native timing rows are not a fresh reading of notify tracks.

**Inspection/test:** export exact tracks/sections/sequence rates; capture neutral -> tell -> commit -> contact -> branch/recovery -> earliest next damaging action. Include phase two and missing-replacement fallback.

**Acceptance:** a measured card for each live move (including additional moves found in U03); animation position and wall-clock time labeled separately. Never derive punish time from total duration alone.

## U07 — Player builds and usable punish margin

**Assets:**

- /Game/OneBossFight/Data/DA_WeaponAttacks
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter
- Player weapon abilities/montages actually selected by that pawn and table: exact resolved list still requires U01/U03-style runtime export; do not guess names.

**Known:** source default posture/stamina/bleed/health scaling and player armor windows. [Weapon:1](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGWeaponAttackTable.cpp:1)

**Missing:** current data-asset overrides, startup/contact/recovery by build, closing time, stamina availability and demonstrated light/heavy punish after each boss opening.

**Test:** quick/strength builds at declared spacing, with realistic reaction and stamina, both phases. Measure boss earliest retaliation minus player reaction/approach/startup/contact budget.

**Acceptance:** approved positive usable margin for intended punishes; owner validates visual recognition. Scripted attack success alone is insufficient.

## U08 — Defense, healing and input state

**Assets:**

- /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/Player/GA_PlayerGuardBlock
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/Player/GA_PlayerParry
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/Player/GA_Player_Dodge
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Animation/AnimNotifies/ParryFramesNS
- /Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AnimNotifies/ANS_iFrames
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/DrinkingPotion_Montage
- /Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage
- /Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Montage

**Missing:** current guard/parry graph policy for every attack, effective dodge timing under current rates, drink semantic mapping, boss defensive reaction policy, and held-key riposte behavior.

**Test:** early/late iframe edges against each damage path; parry/guard/front/rear; actual drink vs cancelled drink/other consumable; riposte with held attack/movement through unlock and reset. KI-085 remains unconfirmed, not a newly reproduced input bug.

**Acceptance:** explicit per-move defense table, live-tag cleanup and no stuck input; no reaction to future/raw player input.

## U09 — Arena, navigation and landing

**Asset:** /Game/OneBossFight/Levels/L_SevarogArena, including its placed collision and navigation data.

**Missing:** current nav coverage, arena bounds/leash, legal leap landing, collision at pillars/gate/corners, elevation/ground connectivity and reachable-target fallback. Native reset home transform is not proof of a navigation leash.

**Test:** chase and leap near every obstruction; target above/below/outside/unreachable; wave across walls/elevation; knockback at boundaries.

**Acceptance:** bounded legal fallback and readable escape; no through-floor/wall damage where design forbids it. Inspect topology before claiming the arena triggers the source-level Z/occlusion risks.

## U10 — Current presentation, fairness and accessibility

**Assets:** U01 arena and U04/U06 visible/animation assets; project feedback components RPGLegend, RPGCameraRig and RPGBossLook. Any independently wired wave VFX asset is **not identified**, not presumed absent globally.

**Missing:** debug-off Shipping ring visibility, visible weapon alignment, audio/camera/occlusion, low-shake/effects readability, lock-on/gamepad/slopes and human perception of tells/recovery.

**Test:** owner captures complete fights with normal and reduced effects, no debug drawing, both builds/phases and constrained camera positions. Identify actual renderer if the wave is already visible.

**Acceptance:** owner can explain each failure from visible/audible evidence and identify intentional punish windows. A passing source or automation check cannot certify feel.

## U11 — Current regression and reproducibility

**Exact existing files:** [RunDrivers.ps1](C:/UnrealProject/OneBossFight/Scripts/RunDrivers.ps1:98), [wake_clip_off.py](C:/UnrealProject/OneBossFight/Scripts/Editor/wake_clip_off.py:1), [pie_dormant_wake.py](C:/UnrealProject/OneBossFight/Scripts/Editor/pie_dormant_wake.py:1), [pie_close_attacks.py](C:/UnrealProject/OneBossFight/Scripts/Editor/pie_close_attacks.py:1), [pie_close_reach.py](C:/UnrealProject/OneBossFight/Scripts/Editor/pie_close_reach.py:1), [Tests:1](C:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGAutomationTests.cpp:1), [TestPlan:97](C:/UnrealProject/OneBossFight/Documentation/TEST_PLAN.md:97).

**Missing:** complete fresh regression on current source/assets; reproducible decision context/seed; outcome after hitches/rate changes; shipping-equivalent wake and hand-test evidence.

**Historical evidence, not rerun here:**

| Record | What it supports | Limitation |
|---|---|---|
| C-84: 37/37 automation; flask 7/7; build selection 18/18; dormant wake 11/11 | Reported owner-run subsets after recent changes | Not a full current release/feel gate; old 12-check wake claim is superseded |
| TRACE-01: 30/30; IFR-01: 19/19, October 21 | Historical trace/iframe coverage | Does not cover every later authored move/rate or all hitch cases |
| Soak: 213/213, October 23 | Historical scripted stability | Predates latest close/wake work; not human balance validation |
| C-84: seven real behind attacks, four branch denials, then seven frontal hits | Refutes stale-montage/pose-damping explanation for KI-106 | Separate close driver still 2/5; setup/heading discrepancy unresolved |
| Saved trace log, October 24 19:38–19:40 UTC | Actual swap/trace observations for authored close moves | Mutable saved file; not a fresh build fingerprint |

RunDrivers always disables background throttling and runs wake_clip_off; the dedicated wake driver enables it temporarily. Shipping always plays the wake. Preserve that distinction in any result. Do not repeat the superseded B10b pose-fault diagnosis.

**Acceptance:** recorded commit/source/asset fingerprints, build/config/machine, test switches, seed/context and capture; failures classified as harness vs product only with evidence. Owner runs the existing suite plus targeted P1–P7 tests after approved changes.

## U12 — Packaged performance

**Files:** [Perf:23](C:/UnrealProject/OneBossFight/Documentation/PERFORMANCE_LOG.md:23), [RunBenchmark.ps1](C:/UnrealProject/OneBossFight/Scripts/RunBenchmark.ps1:1), [RunPerfExperiments.ps1](C:/UnrealProject/OneBossFight/Scripts/RunPerfExperiments.ps1:1), [RPGPerfSwitches.cpp](C:/UnrealProject/OneBossFight/Source/OneBossFight/Arena/RPGPerfSwitches.cpp:1).

**Missing:** final repeated Shipping 1080p full-fight result meeting 60 FPS and p99 <=16.67 ms on target hardware or explicitly accepted proxy. 120 FPS is stretch, not the release target.

**Historical:** Shipping baseline roughly 28–29 FPS/p99 ~40 ms; later Development fire-light/shadow experiments improved markedly but baseline blocks varied. An accepted RTX 3060 proxy is not an RTX 2060 Super measurement.

**Test/acceptance:** Claude-owned controlled interleaved packaged baselines with settings/thermal/background state logged, full-phase camera path and comparable sample windows. Confirm visual readability after any approved lighting changes. Development experiment numbers do not establish a final Shipping pass.

## Inspection sequence and stop condition

Resolve U01–U06 first, then U07–U10 with current capture; U11/U12 supply regression/release gates. Update conclusions when evidence arrives rather than retrofitting unknowns into the “missing” category.

This audit ends with the register. Live inspection, test execution and all gameplay changes require the owner's next-phase direction and the applicable editor/team handoff.

