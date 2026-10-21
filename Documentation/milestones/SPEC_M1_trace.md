# SPEC M1: weapon trace review (TASKS G1-4, Freeze 13, tests H01 to H07 and H11)

Written 2026-10-21 by a read-only design agent. Nothing under Source/, Content/, Config/, Scripts/ or Plugins/ was changed. No editor run, no build, no PIE.

Evidence labels used below:
- Graph-read: a pack Blueprint graph read through `Scripts/bp_graph.py`, `Scripts/bp_pins.py` or `blueprint_query` (get_node_pins, get_functions, get_variables, asset_dependencies, asset_referencers). Read only.
- Code-confirmed: our C++ in `Source/OneBossFight/`, file:line given.
- Engine-confirmed: UE 5.5 source under `C:/Program Files/Epic Games/UE_5.5/Engine/Source`, file:line given.
- Unverified: not read or not run. Each one is also listed in section 8.

Short answer for the owner:
- The pack already sweeps previous to current socket positions every frame, so tunnelling is a measurable property, not a design hole (Graph-read, section 2.1).
- The pack's dedupe unit is the trace window (one `ANS_CollisionTrace` begin), not our attack instance.
- Three Freeze items very likely fail today and need a small runtime fix of ours (no pack edit): through-wall hits (H11), trace not closed on stagger/phase/reset/death (H07, proof pending), phantom reach of the 50 cm sphere (open question).
- Everything in the task list (a to g) can be proven by a PIE driver and an observer component without editing the pack.

---------------------------------------------------------------------------------------------------

## 1. Goal and Freeze requirements

Goal: prove, with numbers and trial counts, that the boss's close-attack weapon trace behaves as the Freeze says. Where the proof fails, add the smallest fix that lives in our C++. Make the debug output show "trace overlap" and "damage accepted" as separate numbers.

Freeze lines (file `Documentation/Master_Design_Freeze_v1_2_AI_Implementation_Ready.md`):

| Req | Freeze line | Text in short |
|---|---|---|
| Trace begin | 537-543 (13.1 items 1,2) | validate attacker, mesh, sockets, channel, instance; clear the hit set; cache initial socket positions |
| Swept sample | 544 (13.1 items 3,4) | sweep previous to current; segments or a swept shape if one centerline misses the arc; smallest design that catches contacts and makes no obvious hit outside the blade |
| Filter | 545-547 (items 5,6,7) | ignore owner, weapon, invalid, dead, already-hit; add to hit set before damage logic; one damage resolution per target per stage |
| Stop | 548 (item 8) | stop at notify end, montage interrupt, stagger, transition, death, cancel |
| Reset | 549 (item 9) | reset previous positions and hit set on the next instance; no long sweep over an idle period |
| Debug | 550 (item 10) | draw previous/current positions, sweep paths, hit location, accepted/rejected and reason |
| Acceptance | 552-561 (13.2) | slow hit, fast hit no tunnel, visible miss no damage, many samples one damage, A3 stage 2 only if configured, disabled at once on interrupt/stop/phase/stagger/death/reset, no hit through walls, radius/channel/sockets reported |
| Instance identity | 526-533 (12.2) | repeated samples of one swing hit once; a new authored stage may hit again; set reset only on a new instance or stage, never per tick |
| Damage order | 508-522 (12.1) | step 2 rejects duplicates and hits after cancel; step 4 rejects on invulnerability; step 11 writes attack ID, outcome, reject reason, hit count, montage time |
| Overlap vs accepted | 488-489 (11.3) | resolver validates at resolution; debug must distinguish `trace overlap` from `damage accepted` |
| Lifecycle | 1245-1261 (32.1) | one authoritative source per window; interruption must still clean up |
| Death | 774-785 (18.2), 1267-1269 (32.3) | death disables traces; lethal hit short circuits |
| Phase | 766 (18.1) | transition start cancels/clears active trace windows |
| Reset list | 787-805 (18.3), item at 795 | reset restores trace active flags, previous socket transforms and hit sets |
| Cleanup rule | 1308-1316 (34.1) | notify state cleanup is idempotent and runs on every exit |
| Debug panel | 908-926 (22), item at 917 | active trace on/off, socket names, current and previous positions, hit set count; logs low volume; stripped in Shipping |
| Tests | 950-962 (23.2) H01..H11; 1329-1335 (35.2) | trial counts; "N/N under setup X" wording |
| A1 / A3 / A4 rules | 616, 621, 647, 662 | active trace only in the window; never hits outside the weapon arc; dedupe per slash stage; low sweep cannot hit through geometry |

Tracker rows (`Documentation/DELTA_AUDIT.md` 72-75): TR-01 swept trace Present; TR-02 per instance dedupe Present; TR-03 stop on interrupt Partial; TR-04 debug draw Missing. TASKS G1-4 (`Documentation/TASKS.md` line 39) is Todo. MILESTONE_GATE2_CODE.md row M1 is Todo.

---------------------------------------------------------------------------------------------------

## 2. Current state

### 2.1 The pack's trace chain, end to end (Graph-read unless noted)

Paths are under `/Game/AdvancedARPGCombat/`. All pack assets are Blueprint only.

1. Boss setup. `MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss` (parent `BP_MasterSoulEnemy_C`, then `BP_MasterEnemy_C`) EventGraph, Event BeginPlay:
   - `Add Collision Target Type` on its `CollisionComponent` (`BP_CollisionComponent_C`) with `TargetTypeTag = TargetType.MainWeapon`.
   - `Set Collision Properties(Current Collision Mesh = Weapon Mesh, Socket Names = Get All Socket Names(Weapon Mesh))`.
   - `Set CollisionRadius`, pin default **50.0** (cm).
   - `asset_dependencies` of the boss BP: `BP_EnemyAbilitySweepingTraceTarget`, `BP_CollisionComponent`, `BP_TargetType`, `.../DemoAssets/Meshes/Weapons/Paragon/SM_KwangSword` (static mesh). It does not depend on the weapon actor `BP_KwangSword`.
   - Correction of two notes: `DELTA_AUDIT.md` line 18 and the task text say the boss weapon is `BP_KwangSword`; the boss has no weapon actor. The traced mesh is the static mesh component `Weapon Mesh` (mesh asset `SM_KwangSword`). `DECISIONS.md` "A2 stand-in facts" says the sword is "part of the mesh": it is a separate static mesh component.
   - `Weapon Mesh` is attached to boss mesh socket `HeavySwordSocket_R` when combat is enabled and to `HeavySwordSheath_Back` otherwise (event `On Combat Toggled`, Select node, Attach Component To Component). Event `DropEquipment` detaches it (KeepWorld), enables collision and physics, profile `ragdoll` (the caller of `DropEquipment` was not read).
   - Sockets traced = every socket of `Weapon Mesh`. `DELTA_AUDIT.md` 19 lists five on SM_KwangSword: `BladeStart`, `BladeEnd`, `MiddleSocket`, `Weapon Start`, `Weapon End`. Socket positions were not read (Unverified).
   - Class of the target object: expected `BP_EnemyAbilitySweepingTraceTarget_C` (referencers query lists the boss BP; the class pin default is not shown by the bridge). Parent chain: `BP_AbilitySweepingTraceTarget` -> `BP_SweepingSocketTraceTarget` -> `BP_TraceTarget` -> `BP_TargetType` -> `BP_BaseObject`.
2. Window open. `CollisionSystem/AnimNotifies/ANS_CollisionTrace` (variables `Collision Target Tag`, `EventTag`, `AttackData`, `Swing Direction`, `TraceRadiusModifier`):
   - Received_NotifyBegin: `Get Owner` of the mesh component -> `Get Component by Class(BP_CollisionComponent)` -> `Get Collision Target Types By Tag(Collision Target Tag)` -> for each: `Set LastSwingDirection`, `Set EventTag`, `Set Collision Radius Modifier(TraceRadiusModifier)`, `Set Attack Data(AttackData)`, `Activate Collision`.
   - Received_NotifyEnd: `Deactivate Collision by Tag(Collision Target Tag)`.
   - The tag of the boss's own montage notifies is not read. It must be `TargetType.MainWeapon`, because the boss registers no other target type (inference).
3. Activate. `CollisionSystem/BP_SweepingSocketTraceTarget` EventGraph, `Event ActivateCollision`: `Clear Hit Actors` -> `Update Trace Locations` -> `Set Collision Enabled(true)` -> `Start Trail`. The `BP_AbilitySweepingTraceTarget` override first runs `Update Target Ability` (`TargetAbility` = animating ability of the owner's ability system component) and then the parent.
   - Result: hit set cleared and previous positions refreshed at every window open. The hit set is NOT cleared per tick.
4. Tick. `CollisionSystem/BP_CollisionComponent` EventGraph: `Event Tick` -> for each `CreatedTargetTypes` -> `Collision Tick`. `BP_TraceTarget`: `CollisionTick` -> if `Is Collision Enabled?` -> `CollisionTrace`.
   - One sample per game frame. No sub-stepping.
   - The component's tick group is the engine default `TG_DuringPhysics` (Engine-confirmed `Private/Components/ActorComponent.cpp:444`); a Blueprint override was not read (Unverified). `USkeletalMeshComponent` ticks in `TG_PrePhysics` (`SkeletalMeshComponent.cpp:384`), so sockets are read after the frame's animation update and notifies.
5. Sample. `BP_SweepingSocketTraceTarget` EventGraph, `Event CollisionTrace`: a Sequence.
   - then_0 (confirmed with get_node_pins): for each name in `CollisionSockets` -> `Is Valid(Current Collision Mesh)` -> `Multi Sphere Trace for Objects` with Start = `Get Socket Location(mesh, socket)` (the current pose), End = `Find(LastSocketLocations, GetProceduralSocketName(mesh, socket))` (the previous pose), Radius = `Get Collision Radius` (= `CollisionRadius + CollisionRadiusModifier`, graph `GetCollisionRadius`), ObjectTypes = variable `CollisionObjectTypes`, `bTraceComplex` unconnected (false), ActorsToIgnore = variable `ActorsToIgnore`, DrawDebugType = variable `DrawDebugType` (default None), `bIgnoreSelf` true.
   - Engine: `UKismetSystemLibrary::SphereTraceMultiForObjects` (`KismetSystemLibrary.cpp:2028`) calls `World->SweepMultiByObjectType(..., FCollisionShape::MakeSphere(Radius), ...)`. An empty `CollisionObjectTypes` logs "Invalid object types" and returns no hit.
   - The sweep runs from the current pose to the previous pose. The swept volume is the same as previous to current. The `Find` "found" output is not connected: a socket key missing from the map reads (0,0,0) and would sweep to the world origin (only if the socket list changes while a window is open).
   - For each hit: `Set Last Hit` -> `Can Hit Actor?` -> Branch -> `Add Hit Actor` -> `On Hit`. The actor is added before `On Hit` runs (Freeze 13.1 item 6 satisfied).
   - then_1 (confirmed): `Update Trace Locations` writes the current socket locations into `LastSocketLocations` (a `TMap<FName, FVector>`; the key is mesh display name + socket name). It runs after all sockets were swept, so every sample is previous to current with no gap between samples.
6. Filter. `BP_TargetType` function `Can Hit Actor?`: true only if all hold:
   - hit actor is not `Performing Actor` ("Don't Hit Performing Actor");
   - hit actor is not in `HitActors` ("Hit one enemy only once");
   - the actor has none of `GameplayTagsToIgnore` (BP gameplay tag interface);
   - `CanHitComponent?`: component not in `HitComponents`, collision profile name not in `CollisionProfileNamesToIgnore`;
   - actor class not in `ActorClass To Ignore`.
   - There is no life-state check and no line-of-sight check. `OnCollisionTargetAdded` adds performing actor, instigator and owner to `ActorsToIgnore`.
7. Hit. `BP_AbilitySweepingTraceTarget.OnHit`: parent OnHit (broadcasts the `OnHit` dispatcher of the collision component) -> `Make Hit Event Data` -> `Run State Machine by Tag(StateMachine.ImpactDecision)` on the hit actor -> `Hit Handle` (damage interface message to the hit actor) -> `Send Hit Event to Ability` (`TargetAbility`.`GameplayEventRecieved`, event tag `GameplayEvent.AttackHit`) -> `GA_Attack.GameplayEventRecieved` -> `ApplyGameplayEffectWithEventData` (damage gameplay effect to the target).
   - Without an animating attack ability (a bare montage played by `PlayMoveMontageForTest`) the trace runs but there is no `TargetAbility`, so no damage. This matches TASKS and `pie_close_attacks.py`.
   - Where the pack rejects an invulnerable target was not located (M2, D-05).
8. Other: `BP_CollisionComponent` `End Play(Destroyed)` -> `ClearTargetTypes` -> `OnRemoved` -> `DeactivateCollision`. Component functions `Activate Collision by Tag` and `DeactivateCollisionByTag` take one input `CollisionTargetTag`.

### 2.2 What ends a trace window

Engine-confirmed (`Engine/Source/Runtime/Engine/Private/Animation/`):
- `AnimInstance.cpp:1548-1640` `TriggerAnimNotifies`: a notify state that is no longer in the frame's notify queue gets `NotifyEnd`.
- `AnimInstance.cpp:2095-2130`: when a montage instance ends, `NotifyEnd` is sent to the notify states of that instance.
- `AnimInstance.cpp:355-380` and `:1752` (`EndNotifyStates`): uninitialize ends all active notify states (skipped while re-instancing).
- `AnimMontage.cpp:2673`: `HandleEvents` returns early when `bInterrupted`, so an interrupted montage queues no more notifies. `FAnimMontageInstance::Stop(..., bInterrupt = true)` is the default (`AnimMontage.h:496,498`); `Montage_Stop` goes through `Montage_StopInternal` (`AnimInstance.cpp:2407`) to `Stop`. `Montage_Play(..., bStopAllMontages = true)` stops montages of the same group with interrupt (`AnimInstance.cpp:3112,3130`).
- So a stopped or replaced montage ends the pack trace at the next anim notify trigger (same frame if the stop came before the anim update, else the next frame). Group of the boss attack montages versus the stagger/roar montage was not read (Unverified; the A2 interruption driver passed 24/24 for stagger and reset, `TASKS.md` G1-2).

Not ending a trace (Graph-read): ability end (`GA_Attack.OnAbilityEnd` does not touch collision), phase logic, encounter reset (only our `Montage_Stop`), boss death by itself. `GA_EnemyDeath` adds `Status.Dead`, stops behaviour and plays a death montage with `bStopAllMontages` if one is found; without one the boss ragdolls and the attack montage clock keeps running (`TASKS.md` G2-9 note). Whether the boss has a death montage was not read.

### 2.3 Our code that touches it

- Nothing reads or writes the pack trace today. `grep` for `CollisionTrace` in `Source/` finds only a comment (`Pack/RPGPackNotifies.h:15`).
- `Player/RPGAttackTracker.cpp:22-95` timing data; the tracker only observes the montage: instance counter `++AttackInstance` at `:298`, `GetAttackInstance()` at `RPGAttackTracker.h:133`, `GetTiming` at `:95`, `GetCurrentMove` at `:136`, `IsActiveWindow` at `:143`. Window numbers there are observed pack windows (A1 0.12-0.42, A1b 0.16-0.46, A3a 0.17-0.47, A3b 0.14-0.44, A2 1.93-2.11 only, A6 0.75-1.17).
- A2 stand-in has two pack trace windows, 1.57-1.76 s and 1.93-2.11 s (`DELTA_AUDIT.md` 36); only the second hurt anyone in tests (`DECISIONS.md` "A2 stand-in facts"). The tracker marks only the second as Active.
- Overlay: `Player/RPGCombatDebug.cpp:64-133` `BuildLines()`; tracker line `:104-108`; keys `0x52504700 + Index` at `:418`; log once per second in `rpg.Debug 2` at `:421-428`.
- Component attach: `Player/RPGPlayerMovesSubsystem.cpp:120-204` `Attach`; tracker attach `:173-177`; `Deinitialize` `:49-56`.
- Interrupt owners: `RPGBossStagger.cpp:127` `StartStagger`, `Montage_Play(Fall)` at `:185`, `ForceBreakForTest` `:292`; `RPGBossPhases.cpp:157` `StartTransition`, `Montage_Play(Roar)` at `:194`; `RPGBossEncounter.cpp:222` `ResetEncounter` (`++Generation` `:227`, `SetCombatEnabled(false)` `:255` which moves the weapon mesh to the sheath, `Montage_Stop(0.1)` `:273`, teleport `SetActorTransform` `:280`).
- Helpers: `Player/RPGBossDamage.h:18` `IsInvulnerable` (tag `Status.Invulnerable`), `:33` `IsAlive`, `:53` `WorldBlockers()` (WorldStatic and WorldDynamic), used by the A4 line-of-sight test at `RPGBossLowSweep.cpp:100-112`. `Pack/RPGBlueprintCall.h:15` `CallBlueprintFunction`, `:62` `FindComponentByClassName`, `:120` `ReadAttribute`.
- Test hooks that exist: `URPGBossEncounter::HoldForTest/Wake/ResetForTest` (`RPGBossEncounter.h:59-67`), `URPGBossStagger::ForceBreakForTest` (`:116`), `URPGCombatDebug::DebugKillBoss/DebugSetBossHealthFraction/DebugSpawnWall/DebugClearWalls/DebugRefillPlayer`, `URPGAttackTracker::StartMove/PlayMoveMontageForTest/EnterCombat` and the property `BranchRange`.

### 2.4 Numbers already known

- Player capsule radius 42 cm, half height 96 cm (`DELTA_AUDIT.md` 16). Boss mesh scale 1.5, boss capsule radius 63 (`:15`). SM_KwangSword 23 x 16 x 184 cm, about 276 cm on the boss (`:18`).
- Reach of one socket path = sphere 50 + capsule 42 = 92 cm to the capsule axis. A player centred between two socket paths is missed only if the paths are more than 2 x 92 = 184 cm apart.
- Visual blade half width, if the 23 cm side is the width: 11.5 x 1.5 = 17 cm (Unverified: axis not read). Phantom reach = 50 - 17 = 33 cm outside the visible blade.
- Tip speed (estimate, Unverified): tip about 350 cm from the shoulder, peak angular speed 11 to 16 rad/s, so 4000 to 5600 cm/s. Step per frame: 30 fps 130-190 cm, 60 fps 65-95 cm, 120 fps 33-47 cm. Every one of those but the last is above the capsule radius 42, so a point test would tunnel and only the sweep prevents it. Chord to arc deviation (sagitta) of one step: `r (1 - cos(theta/2))`; at 30 fps about 10 cm, at 60 fps 2.4 cm, at 15 fps about 40 cm, at 8 fps about 125 cm (above 92). The driver measures these; do not quote the estimates as results.

---------------------------------------------------------------------------------------------------

## 3. Gaps

| ID | Gap | Freeze | Provable without a pack edit? |
|---|---|---|---|
| G-1 | No runtime view of the pack trace: active flag, hit set, sockets, radius, object types, previous positions | 550, 917, 561 | Yes: read the live target object by reflection |
| G-2 | Swept coverage at several frame rates never measured (TR-01 is graph-read only) | 544, 556 | Yes: continuity, step, sagitta, placement scan at fixed 30/60/120 fps |
| G-3 | Dedupe unit is the trace window; our unit is the attack instance. A2 stand-in has two windows in one instance | 526-533, 647 | Yes: count windows and damage events per instance |
| G-4 | Trace end on stagger, phase transition, death, reset rests on the engine ending notify states. Unproven. Reset teleports the boss (`RPGBossEncounter.cpp:280`) and re-sheathes the weapon (`:255`) in the same frame the montage is stopped: a stale sweep across the arena is possible if a sample runs after the teleport | 548-549, 559, 766, 779, 795 | Proof yes. Fix is ours (guard) |
| G-5 | No occlusion in the pack trace: sweeps and filter never test world geometry. Players behind a wall inside the sphere path are hit | 560, 662 | Proof yes (expected FAIL). Fix is ours (guard) |
| G-6 | Radius 50 cm is a constant in the boss BeginPlay. About 33 cm of phantom reach beyond the blade | 544, 556, 621 | Measure yes. Change needs an owner decision |
| G-7 | "Trace overlap" and "damage accepted" are not separated anywhere | 489, 522 | Yes: observer |
| G-8 | A hit-set entry is consumed by an overlap that the damage resolver rejects (i-frames), so a later sample of the same window cannot hurt once i-frames end. Not a trace bug but a dedupe-unit question | 35.3 scenario 1 and 3 (1339-1341), 12.1 step 2-4 | Measure yes. Hand-off to M2 |
| G-9 | The pack trace can be open while the tracker says "not Active" (A2 window 1) and the Freeze wants the trace only in the authored active window | 616 | Yes: compare windows with `FRPGAttackTiming` |
| G-10 | Hitches: at 8 fps (largest sensible frame) one chord can miss a fast arc | 556 | Measure at 15 fps; below that documented limit |

Nothing in this list needs a pack asset edit. Two optional pack edits are named in 4.8 as fallbacks only.

---------------------------------------------------------------------------------------------------

## 4. Design

### 4.1 Overview

Three new pieces. The pack stays as it is.

1. `Pack/RPGPackTrace.h/.cpp`: one facade over the live pack objects (reflection only).
2. `Player/RPGTraceGuard.h/.cpp`: small enforcement component, compiled in every build (Freeze 13.1 items 8 and 9, 13.2 walls, 12.2 instance rule).
3. `Player/RPGTraceAudit.h/.cpp`: observer and test hooks, compiled out of Shipping (Freeze 22: debug removable). It counts overlaps versus accepted damage per attack instance and per trace window and writes the overlay lines.

Not changed:
- No pack `.uasset`, graph, variable default, tag, input or config. No pack re-apply script is needed for the main design.
- `FRPGAttackTiming` data, `URPGAttackTracker` logic, damage numbers, notify times, A4/A5/A6 components, HUD.
- The pack's own ability, damage and impact-decision path.

New runtime writes into pack objects (all through reflection, all reverted or idempotent): the target's `HitActors` array (temporary seed, 4.3), `CollisionRadius` (only if the owner sets an override), `DrawDebugType` (only with `rpg.TraceDebug 2`), plus calls to the pack's own `DeactivateCollisionByTag`, `ClearHitActors`, `UpdateTraceLocations`.

### 4.2 Pack facade: `Source/OneBossFight/Pack/RPGPackTrace.h/.cpp`

```cpp
namespace RPGPackTrace
{
    // Blueprint names exactly as `Scripts/bp_graph.py` prints them (BP variable names keep spaces and '?').
    // Variables of BP_TargetType_C: "bCollisionEnabled?", "HitActors", "CollisionSockets", "CollisionRadius",
    //   "CollisionRadiusModifier", "CollisionObjectTypes", "Current Collision Mesh", "ActorsToIgnore", "TargetTypeTag".
    // Of BP_SweepingSocketTraceTarget_C: "LastSocketLocations". Of BP_TraceTarget_C: "DrawDebugType".
    // Of BP_AbilitySweepingTraceTarget_C: "TargetAbility". Of BP_CollisionComponent_C: "CreatedTargetTypes".
    // Functions: component "DeactivateCollisionByTag"(CollisionTargetTag); target "ClearHitActors" (custom event), "UpdateTraceLocations".
    struct FTarget
    {
        TWeakObjectPtr<UObject> Collision;   // BP_CollisionComponent_C on the boss
        TWeakObjectPtr<UObject> Object;      // the BP_TargetType_C with TargetTypeTag == Tag
        bool Resolve(const AActor* Boss, FName Tag);     // lazy; cheap when valid; logs once if a name is missing
        bool IsActive() const;                            // "bCollisionEnabled?"
        void GetHitActors(TArray<AActor*>& Out) const;    // "HitActors"
        bool HitSetContains(const AActor*) const;
        bool HitSetAdd(AActor*);                          // appends once; returns false if already there
        bool HitSetRemove(AActor*);                       // removes one entry
        UPrimitiveComponent* GetMesh() const;             // "Current Collision Mesh"
        void GetSockets(TArray<FName>& Out) const;        // "CollisionSockets"
        double GetBaseRadius() const;  double GetRadiusModifier() const;  void SetBaseRadius(double Cm);
        void GetObjectChannels(TArray<ECollisionChannel>& Out) const;     // via UEngineTypes::ConvertToCollisionChannel(EObjectTypeQuery)
        void GetActorsToIgnore(TArray<AActor*>& Out) const;
        bool GetStoredLocation(FName Socket, FVector& Out) const;         // FScriptMapHelper over "LastSocketLocations"; key ends with the socket name
        bool HasAbility() const;                           // "TargetAbility" valid
        uint8 GetPackDrawMode() const;  void SetPackDrawMode(uint8 Mode); // "DrawDebugType": 0 None, 1 ForOneFrame, 2 ForDuration, 3 Persistent
        bool Deactivate();                                 // component.DeactivateCollisionByTag(tag); idempotent
        void ClearHitSet();                                // target.ClearHitActors
        void RefreshPrevious();                            // target.UpdateTraceLocations
    };
    bool CheckPackProperties(FString& OutMissing);         // used by Content.PackWiring (4.9)
}
```
Rules: resolve `BP_CollisionComponent_C` with `RPGPack::FindComponentByClassName` (`RPGBlueprintCall.h:62`); read `CreatedTargetTypes` (object array); pick the object whose `TargetTypeTag` equals `TargetType.MainWeapon`. Cache `FProperty*` per class. A missing name: log once in `LogRPGTrace` (Warning), return false, and the callers switch themselves off. No gameplay depends on a successful resolve.

### 4.3 `URPGTraceGuard` (`Player/RPGTraceGuard.h/.cpp`, all builds)

Attached to the boss. Tick group `TG_PrePhysics` with `AddTickPrerequisiteComponent(boss skeletal mesh)` so it runs after the animation update and notifies of the frame and before the pack's `TG_DuringPhysics` sample. Also a prerequisite on nothing else.

```cpp
UCLASS(ClassGroup=(Boss)) class ONEBOSSFIGHT_API URPGTraceGuard : public UActorComponent
{
    UPROPERTY(EditAnywhere, Category="Trace") FName TargetTypeTag = "TargetType.MainWeapon";
    UPROPERTY(EditAnywhere, Category="Trace") bool bCloseOnInterrupt = true;     // CloseTraceNow acts (stagger, transition, reset, death)
    UPROPERTY(EditAnywhere, Category="Trace") bool bBlockThroughWalls = true;    // Freeze 13.2 walls; baseline runs set false
    UPROPERTY(EditAnywhere, Category="Trace") bool bDedupePerInstance = true;    // Freeze 12.2: hit set carried across windows of one tracked instance
    UPROPERTY(EditAnywhere, Category="Trace", meta=(ClampMin="0")) float TraceRadiusOverrideCm = 0.f; // 0 = keep the pack's 50 cm; >0 writes CollisionRadius at every window open (owner decision, G-6)
    UFUNCTION(BlueprintCallable) void CloseTraceNow(FName Reason);               // calls FTarget::Deactivate(); for "reset" also ClearHitSet() and RefreshPrevious(); idempotent
    UFUNCTION(BlueprintPure) bool IsPackTraceActive() const;
    UFUNCTION(BlueprintPure) int32 GetCloseCount() const;  int32 GetOccludedSampleCount() const;  int32 GetCarrySeedCount() const;
    UFUNCTION(BlueprintPure) float GetOpenRefreshErrorCm() const;                // max |stored - current| over sockets at the last window open
    static void CloseFor(AActor* Boss, FName Reason);                            // finds the component; no-op if absent (used by the interrupt owners)
};
```
Per tick, in this order (skip all if the pack target cannot be resolved):
1. Read `A` = pack flag. Detect edges against the last tick.
2. Remove the temporary seed of the previous frame: if `TempSeed` is valid, still in `HitActors`, and the window id is unchanged, remove one entry. Clear `TempSeed`.
3. If `!A`: remember `HitActors` as `LastSet` (first inactive tick keeps the final contents; the pack clears only at the next activation); return.
4. Open edge (`A` now, not before): `++WindowId`; measure `OpenRefreshErrorCm` = max over sockets of `|FTarget::GetStoredLocation - Mesh->GetSocketLocation|` (this is the proof that `Activate` refreshed the previous positions, Freeze 13.1 item 2 and 9); if `TraceRadiusOverrideCm > 0` write it with `SetBaseRadius`; if `bDedupePerInstance` and the tracker shows the same instance as the previous window (`URPGAttackTracker::GetAttackInstance`, `GetCurrentMove` not None) then re-add every actor of `LastSet` to `HitActors` (persistent, not a temp seed) and `++CarrySeedCount`.
5. Death: if `bCloseOnInterrupt` and boss health <= 0 (`RPGPack::ReadAttribute`, only while `A`) -> `CloseTraceNow("dead")`; return.
6. Wall gate: if `bBlockThroughWalls`, player pawn valid, player not in `HitActors`: one `LineTraceSingleByObjectType` from the boss actor location to the player actor location, objects `RPGBossDamage::WorldBlockers()` (`RPGBossDamage.h:53`), ignore boss and player, `bTraceComplex` false (same pattern as `RPGBossLowSweep.cpp:100-112`). If blocked: `HitSetAdd(player)`, remember it as `TempSeed`, `++OccludedSampleCount`.
Why one tick function is enough: the seed lives for exactly one pack sample (step 6 of frame N, pack sample in frame N, removed at step 2 of frame N+1 before the check is repeated). A real hit earlier in the window is never removed (we only remove what we added). `ClearHitActors` of a new window in the same frame removes the seed for us (step 2 then finds nothing).

`CloseTraceNow(Reason)` is the only place that ends a trace early. It never opens one. The notify end stays the authority for normal ends (Freeze 32.1 line 1261: the owners only clean up when the notify cannot).

Call sites (one line each, before the existing code of the function):
- `RPGBossStagger.cpp:127` `StartStagger`: `URPGTraceGuard::CloseFor(GetOwner(), "stance break");` (before `Montage_Play(Fall)` at `:185`).
- `RPGBossPhases.cpp:157` `StartTransition`: `CloseFor(GetOwner(), "phase transition");` (before `Montage_Play(Roar)` at `:194`).
- `RPGBossEncounter.cpp:222` `ResetEncounter`, first statements, before `HoldBehaviour()`, `SetCombatEnabled(false)` (`:255`), `Montage_Stop` (`:273`) and the teleport (`:280`): `CloseFor(Owner, "reset");`.
- Death: the guard's own step 5 (at most one frame after the health write).

### 4.4 `URPGTraceAudit` (`Player/RPGTraceAudit.h/.cpp`, non-Shipping)

Attached to the boss by the subsystem. Tick group `TG_PostUpdateWork` (after the pack's `TG_DuringPhysics` sample and our tracker). Also `AddTickPrerequisiteComponent` on the pack collision component and the tracker once resolved. Everything inside `#if !UE_BUILD_SHIPPING`.

Properties (EditAnywhere, defaults):
| Name | Default | Unit | Meaning |
|---|---|---|---|
| `bEnabled` | true | - | master switch |
| `TargetTypeTag` | `TargetType.MainWeapon` | - | which pack target type to watch |
| `ResolveWindowSeconds` | 0.25 | s | after a hit-set insertion, a health drop of the player inside this time counts as its damage |
| `MinResolveTicks` | 3 | ticks | minimum ticks to wait before an insertion is classified as rejected (hitch safety) |
| `ContinuityToleranceCm` | 0.5 | cm | max allowed `|LastSocketLocations - current pose|` after a sample |
| `TunnelMarginCm` | 20 | cm | required margin `(R + capsule radius) - sagitta` |
| `SuspectStepCm` | 800 | cm | a single socket step longer than this counts as a suspect sweep (teleport or stale data) |
| `MaxWindowRecords` | 64 | records | ring size |
| `bShadowSweep` | true | - | repeat the pack's sphere sweep against the player for the overlap count |

Per tick:
1. Resolve the pack target (4.2) and the player pawn (`UGameplayStatics::GetPlayerPawn(this, 0)`; re-fetch if the pointer changed; a new pawn ends the current window as "player replaced").
2. `A` = pack flag. Open edge: new window record: ordinal in instance, instance (`URPGAttackTracker::GetAttackInstance`, or -1 when `GetCurrentMove()` is None, meaning an untracked pack attack), move, generation (`URPGBossEncounter::GetGeneration`), montage name and position, tracker phase name, base radius, modifier, socket list, object channels, `HasAbility`, weapon attach socket name (`Weapon Mesh` parent socket; a window while sheathed counts in `WindowsWhileSheathed`), size of the hit set at open (`SetCountAtOpen`), `TrackerActive` (is the tracker phase Active). Log one line (4.7).
3. While `A` (one sample): `Samples++`; `dt` = world delta seconds (track `MinDt`, `MaxDt`). For each socket `s`:
   - `cur = Mesh->GetSocketLocation(s)`; `prev` = own cache from the previous active tick (at the open tick `prev = cur`: the first pack sample is a zero-length sweep from the refreshed positions).
   - `step = |cur - prev|` -> `PeakStepCm` (per window and global), `PeakSpeedCmPerSec = step / dt`; `SuspectSweeps++` if `step > SuspectStepCm`.
   - Sagitta: with three consecutive samples p0,p1,p2, `d = FMath::PointDistToSegment(p1, p0, p2)` (`UnrealMathUtility.h:2083`); one-step sagitta ~ `d / 4` -> `PeakSagittaCm`.
   - Continuity: `FTarget::GetStoredLocation(s)` after the pack sample must equal `cur`; error -> `MaxContinuityErrorCm`.
   - Shadow overlap (if `bShadowSweep` and the player is valid): `World->SweepMultiByObjectType(Hits, cur, prev, FQuat::Identity, channels, FCollisionShape::MakeSphere(R), Params)` where `R = base + modifier` (float), channels from the pack, `Params.AddIgnoredActors(pack ActorsToIgnore)`, `bTraceComplex` false: the same query as the pack (`KismetSystemLibrary.cpp:2028`). Count the sample as an overlap sample if any hit actor is the player. A second query without the ignore list counts `SelfOverlapSamples` (boss capsule inside its own sweep; proves the self filter is needed).
   - Analytic clearance: `ClearanceCm = FMath::SegmentDistToSegmentSafe(...)` between the swept segment `prev-cur` and the player capsule axis (vertical segment, centre +/- half height), minus `(R + capsule radius)`. Keep the minimum per window (`MinClearanceCm`). Negative = inside reach.
   - Inter-socket gap: at the open tick sort sockets by projection on `BladeStart -> BladeEnd` (fall back to the longest pair) and keep the largest distance between neighbours -> `MaxSocketGapCm`.
4. Hit set tracking: read `HitActors` each active tick. A new element:
   - the player: `SetInsertions++`, record the sample index, whether `RPGBossDamage::IsInvulnerable(player)` at that tick, the player health, and start an outcome timer;
   - the boss itself or its weapon: `SelfInSet++` (must stay 0);
   - anything else: `OtherInSet++` (informational).
5. Outcome resolution (per insertion): when player health drops by more than 0.001 inside `ResolveWindowSeconds` -> `DamageAccepted++`, `DamageTaken += amount`; if the tag was on at the insertion also `AcceptedWhileInvulnerable++` (input for M2). When the timer ends (and `MinResolveTicks` passed) with no drop: `RejectedInvulnerable++` if the tag was on, else `RejectedOther++`. Health drops with no open insertion: `UnattributedDamage++`. Invariant: `SetInsertions == DamageAccepted + RejectedInvulnerable + RejectedOther + Pending`.
6. Interrupt detection (independent of who causes it): the interrupt condition is true when any of: the boss's active montage is not the window's montage, boss health <= 0, generation changed, `URPGBossStagger::IsStaggered()`, `URPGBossPhases::IsInTransition()`. First tick it is true = `InterruptFrame` (`GFrameCounter`). Each later tick with `A` true = `SamplesAfterInterrupt++` (a sample inside the interrupt frame itself is tolerated: the pack may sample before the owner code runs in the same group). `FramesToClose = CloseFrame - InterruptFrame`. A hook-armed interrupt (4.6) uses its own frame as `InterruptFrame`. After the interrupt tick, any health drop of the player counts `DamageAfterInterrupt`.
7. Close edge: classify `CloseReason` = "notify end" (same montage, position at or after the last known window end), "montage stopped" (no montage), "montage replaced", "stance break", "phase transition", "reset", "boss dead", "guard (reason)" (the guard's `CloseCount` rose), "player replaced". Finalize the record (samples, overlap samples, insertions, outcomes, peaks, `SetCountAtClose`), update the per-instance aggregate, write the close log line.
8. Overlay and draw (4.5, 4.7).

Records:
```cpp
USTRUCT() struct FRPGTraceWindowRecord {
  int32 Instance, Ordinal, Generation; FName Move; FString Montage, CloseReason;
  float OpenPos, ClosePos, OpenTime, CloseTime;       // montage seconds, world seconds
  int32 Samples, OverlapSamples, SetInsertions, DamageAccepted, RejectedInvulnerable, RejectedOther, AcceptedWhileInvulnerable;
  int32 SamplesAfterInterrupt, FramesToClose, DamageAfterInterrupt, SetCountAtOpen, SelfInSet, SuspectSweeps, SelfOverlapSamples;
  float DamageTaken, PeakStepCm, PeakSpeedCmPerSec, PeakSagittaCm, MaxContinuityErrorCm, MinClearanceCm, MinDt, MaxDt, BaseRadius, Modifier;
  bool bHasAbility, bTrackerActiveAtOpen, bSheathed;
};
```
Per instance aggregate (`TMap<int32, FRPGTraceInstanceRecord>`, ring of 32): windows, overlap samples, insertions, damage events, damage taken.

Counter access for drivers (Python cannot read arrays of structs easily): string keyed getters.
```cpp
UFUNCTION(BlueprintPure) double GetCounter(FName Name) const;                          // totals since ResetCounters
UFUNCTION(BlueprintPure) double GetWindowCounter(int32 Ordinal, FName Name) const;     // Ordinal 1 = first window since ResetCounters; -1 = last
UFUNCTION(BlueprintPure) double GetInstanceCounter(int32 Instance, FName Name) const;
UFUNCTION(BlueprintPure) int32 GetWindowCount() const;   FString GetWindowSummary(int32 Ordinal) const;
UFUNCTION(BlueprintPure) bool IsTraceActive() const;     int32 GetHitSetCount() const;
UFUNCTION(BlueprintCallable) void ResetCounters();
```
Counter names: `Windows, Samples, OverlapSamples, SetInsertions, DamageAccepted, DamageTaken, RejectedInvulnerable, RejectedOther, AcceptedWhileInvulnerable, UnattributedDamage, SelfInSet, OtherInSet, SelfOverlapSamples, SuspectSweeps, PeakStepCm, PeakSpeedCmPerSec, PeakSagittaCm, MaxContinuityErrorCm, OpenRefreshErrorCm, MaxSocketGapCm, MinClearanceCm, MinDt, MaxDt, SamplesAfterInterrupt, FramesToClose, DamageAfterInterrupt, SetCountAtOpen, WindowsOutsideTracker, WindowsWhileSheathed, WindowsNoAbility, Occluded, Closed, Carried, Sockets, BaseRadius, Modifier, Channels`.

### 4.5 Overlay lines (Freeze 489, 917)

`URPGCombatDebug::BuildLines()` (`RPGCombatDebug.cpp:104-108`, insert after the tracker block): `if (const URPGTraceAudit* Audit = Boss->FindComponentByClass<URPGTraceAudit>()) Lines.Append(Audit->BuildLines());` plus the include. Three lines, text exactly:
```
  trace ACTIVE A3a #12 window 1 of 1  sockets 5  radius 50+0  types Pawn  hit set 1  sheathed no  ability yes
  overlap samples 14 | new in hit set 1 | damage accepted 1 (36.0) | rejected: invulnerable 0, other 0 | blocked by wall 0 | before-hit frames
  sweep peak step 82 cm (42 = capsule radius)  sagitta 2.4 cm  continuity 0.0 cm  suspect 0  closed: notify end at 0.47 s (+0 frames)
```
(`ACTIVE`/`idle`; the middle line is the Freeze 489 split: overlap samples versus damage accepted are separate numbers.) `GetCounter`-based drivers parse nothing from the strings; the strings are only checked for the words `overlap`, `damage accepted`, `rejected`.

### 4.6 Test hooks (non-Shipping, on `URPGTraceAudit`)

```cpp
UFUNCTION(BlueprintCallable) void ArmInterrupt(FName Kind, float AtMontagePosition);   // "stop" | "stagger" | "phase" | "reset" | "death"; fires once on the first tick with the boss montage position >= AtMontagePosition
UFUNCTION(BlueprintCallable) void CancelInterrupt();
UFUNCTION(BlueprintCallable) bool PrimeCloseAttack(int32 AttackIndex);                 // GA_GS_Boss_CloseAttack_C: "Random Attack Index?" = false, SetAttackIndex(AttackIndex) (found with RPGPack::FindAbilityByClassName)
UFUNCTION(BlueprintCallable, Category="RPG|Test") static void SetTestFrameRate(float Fps);   // FApp::SetUseFixedTimeStep(true), FApp::SetFixedDeltaTime(1/Fps); 0 restores; remembers the old values
UFUNCTION(BlueprintCallable, Category="RPG|Test") static void ClearTestFrameRate();
UFUNCTION(BlueprintPure, Category="RPG|Test") static bool IsTestFrameRateActive();
```
- `ArmInterrupt` kinds call existing code: `stop` -> `Montage_Stop(0.1, current montage)` (pure pack behaviour, no guard call); `stagger` -> `URPGBossStagger::ForceBreakForTest`; `phase` -> `URPGCombatDebug::DebugSetBossHealthFraction(0.59)`; `reset` -> `URPGBossEncounter::ResetForTest`; `death` -> `URPGCombatDebug::DebugKillBoss`.
- Fixed step: Engine-confirmed `Core/Public/Misc/App.h:512-546` (`SetFixedDeltaTime`, `SetUseFixedTimeStep`) and `UnrealEngine.cpp:2645-2665` (fixed step overrides the real delta; whole engine frame). It is guarded by `WITH_FIXED_TIME_STEP_SUPPORT` (value in this build Unverified). `URPGPlayerMovesSubsystem::Deinitialize` (`RPGPlayerMovesSubsystem.cpp:49`) calls `ClearTestFrameRate()` so the end of a PIE always restores real time. `Scripts/Editor/pie_stop.py` should call it too.
- The world delta is clamped by `WorldSettings` Min/MaxUndilatedFrameTime (`WorldSettings.h:715,719`; defaults not read, Unverified).

### 4.7 Console variable and log

- `rpg.TraceDebug` (int, default 0, not Shipping): 0 off; 1 our drawing (`DrawDebug*` from `DrawDebugHelpers.h`): socket spheres at `cur` with radius R, a line `prev -> cur` per socket (white sample, yellow overlapping the player, green set insertion, red insertion with rejected outcome, orange occluded by the guard), 0.1 s life; 2 additionally writes `DrawDebugType = ForOneFrame` into the pack target so the pack draws its own sweeps (`FTarget::SetPackDrawMode`), restored when the variable drops to 0 and in `EndPlay`.
- Log category `LogRPGTrace`. One line at window open and one at close (never per frame), for example: `trace window open: A3a instance 12 window 1 generation 3 at 0.17 s, tracker Committed, radius 50+0, sockets 5, channels Pawn, ability yes, set 0` and `trace window close (notify end) at 0.47 s: samples 18 overlap 14 insertions 1 accepted 1 (36.0) rejected 0/0 peak step 82 cm sagitta 2.4 cm continuity 0.0 cm after-interrupt 0`. Warnings: `suspect sweep`, `trace stayed on N sample(s) after <reason>`, `accepted while invulnerable`.

### 4.8 Pack edit fallbacks (only if the runtime design proves unreliable; re-apply scripts follow `Scripts/poise_by_power.py` style with `Scripts/bp_edit.py`, run after `Scripts/ImportAssetClosure.py`, guard against running twice)

| Fallback | Script | Edit |
|---|---|---|
| Wall block | `Scripts/pack_trace_wall_block.py` | In `CollisionSystem/BP_TargetType` function `Can Hit Actor?`, AND the result with `NOT(Line Trace For Objects(Start = Performing Actor location, End = Hit Actor location, WorldStatic + WorldDynamic, ignore performer and hit actor))` |
| Radius | `Scripts/pack_trace_radius.py` | Change the 50.0 pin default of `Set CollisionRadius` in `BP_ExampleGreatSwordBoss` BeginPlay (only if the owner picks a new radius and does not want the runtime override) |

No fallback is needed for notify end, interrupt, stagger, phase, death or reset: they are our C++ (4.3).

### 4.9 Other edits to existing files

| File | Change |
|---|---|
| `Player/RPGPlayerMovesSubsystem.cpp` | includes; after `:177` add `URPGTraceGuard` (all builds) and, inside `#if !UE_BUILD_SHIPPING`, `URPGTraceAudit`, same `IsPackBoss(Pawn) && !FindComponentByClass` pattern; `Deinitialize` (`:49`) calls `URPGTraceAudit::ClearTestFrameRate()` |
| `Player/RPGCombatDebug.cpp` | include + 1 line after `:108` |
| `Player/RPGBossStagger.cpp`, `RPGBossPhases.cpp`, `RPGBossEncounter.cpp` | one `URPGTraceGuard::CloseFor` line each (4.3) |
| `Tests/RPGAutomationTests.cpp` | extend `Content.PackWiring` (`:429`): call `RPGPackTrace::CheckPackProperties` and test it is empty; new tests `OneBossFight.Trace.WindowModel` and `OneBossFight.Trace.SweepMath` (4.10) |
| `Scripts/Editor/pie_stop.py` | add `unreal.RPGTraceAudit.clear_test_frame_rate()` before `editor_request_end_play()` |
| `OneBossFight.Build.cs` | none (Engine, CoreUObject and Core are already dependencies) |

### 4.10 Pure model for automation tests

`Player/RPGTraceModel.h` (header only, no UObject): `struct FRPGTraceWindowModel` with `Tick(const FInput&)` where `FInput` = flag, dt, per-socket current positions, set contents, player health, invulnerable flag, interrupt flag. The audit feeds it from the live objects. Automation tests feed synthetic streams:
- `OneBossFight.Trace.WindowModel`: open/close edges, ordinal, insertion counted once with 30 overlapping samples, outcome classification (accepted, rejected invulnerable, rejected other, pending), samples-after-interrupt and frames-to-close arithmetic.
- `OneBossFight.Trace.SweepMath`: sagitta from three points on a circle equals `r(1-cos(theta/2))` within 2 %, segment-to-capsule clearance sign at the boundary 92 cm, socket gap sort.

---------------------------------------------------------------------------------------------------

## 5. Edge cases and failure modes

| Case | What happens in the pack / engine | Design response | Test |
|---|---|---|---|
| Natural window end | `NotifyEnd` -> `DeactivateCollisionByTag` | none; audit logs "notify end" | T0 |
| `Montage_Stop` (interrupt flag set) | notifies stop queuing (`AnimMontage.cpp:2673`); end at next trigger; expect 1 frame | measured; guard not used on this path (pure pack) | T8 stop |
| Stagger | `Montage_Play(Fall)` stops same-group montages (group not read) | `CloseFor("stance break")` at the top of `StartStagger`; flag false in the same frame | T8 stagger |
| Phase transition | same with the roar montage | `CloseFor("phase transition")` | T8 phase |
| Death | `GA_EnemyDeath`: `Status.Dead`, death montage if one exists, else ragdoll with the attack clock running; `DropEquipment` re-parents the sword to physics | guard step 5 closes within one frame of health <= 0; no damage after | T8 death |
| Reset | `Montage_Stop`, weapon re-sheathed (`:255`), boss teleported (`:280`) in one call chain: a sample after the teleport would sweep from the old pose to the home pose across the arena | `CloseFor("reset")` first; `ClearHitSet` and `RefreshPrevious` (Freeze 795) | T8 reset, T8 reset-teleport |
| Generation token | `Generation` rises on reset (`:228`) | a window whose generation differs from the current one closes as "reset"; its counts are not mixed into the new fight; guard drops seeds on generation change | T8 reset |
| Two interrupts in one frame | - | `CloseTraceNow` is idempotent (Freeze 34.1) | T8 |
| Frame rate 30 / 60 / 120 | one chord per frame, sagitta grows with 1/fps^2 | measured; margin must be at least 20 cm | T1, T2 |
| Hitch up to 15 fps | sagitta near 40 cm | measured at 15 fps; informational | T1 |
| Hitch at 8 fps or worse | sagitta above R + 42 for the fastest arcs | known limit (R-5); counter `PeakSagittaCm` makes it visible; no fix without a pack edit | - |
| Slow play rate 0.25 or phase two 1.2 | notify times scale with the rate | all audit times are montage seconds; samples scale | T3, T11 |
| Two windows in one attack (A2 stand-in) | each `Activate` clears the set | `bDedupePerInstance` carries the set inside one tracked instance; A3b is a new instance by the tracker, so it still hits again | T6, T6b |
| Untracked pack attacks (sprint follow-up, mid range) | traces run, tracker has no instance | recorded with instance -1; dedupe stays per window | T11 |
| Player dies and respawns during a window | pawn replaced | audit ends the window "player replaced"; guard drops `TempSeed` (weak pointer) | `pie_player_death_reset.py` regression |
| Player behind a wall | pack sweeps through (no occlusion) | guard wall gate (boss centre to player centre line trace) | T9 |
| Player inside the sphere path but invulnerable | overlap is consumed by the set, damage rejected | audit counts `RejectedInvulnerable` and `AcceptedWhileInvulnerable`; refund of the set entry is M2's decision | T10 |
| Weapon sheathed while a window opens | traces run on the back | `WindowsWhileSheathed` must stay 0 in tests | T0 |
| Weapon mesh or sockets change (G2-15 swaps in `SM_Boss01_Greatsword`, 7 sockets) | pack reads sockets at BeginPlay only | audit reads mesh and sockets at every window open and logs them; any `Find` key missing shows as a suspect step | T0 after G2-15 |
| Pack re-import renames a variable | reflection lookup fails | `Resolve` fails safe (both components off, one warning); `Content.PackWiring` fails the build gate | automation |
| PIE ends with fixed step on | engine would keep the fixed step | `Deinitialize` and `ClearTestFrameRate` restore it; driver preflight checks `IsTestFrameRateActive()` is false | P0 |
| Seed removal race | `ClearHitActors` of a new window already removed the seed | removal only if the entry is still there and the window id is the same | T9 |
| Shipping build | audit and hooks absent | guard stays (gameplay), no debug code | G4-3 |

---------------------------------------------------------------------------------------------------

## 6. PIE test plan

Driver: `Scripts/Editor/pie_trace_audit.py`, log prefix `[Trace]`, house style of `pie_leap_wave.py` and `pie_a5_heal_punish.py`: module `S` state, `check(name, ok, detail)`, `comp(actor, class_name)`, `health(actor)`, `place(pawn, boss, dist, ang)`, a `STEPS` list of `(delay, fn)` built by small scenario builders, `_tick` state machine on `register_slate_post_tick_callback`, final line `RESULT n/m passed`. Run: `MSYS_NO_PATHCONV=1 python -I Scripts/run_in_editor.py Scripts/Editor/pie_trace_audit.py`, after `no_throttle.py` and one warm-up `pie_debug_overlay.py` (first PIE has broken attributes, `HANDOVER.md` section 4).

Rules for the driver:
- Time: with the fixed step on, step delays are counted in world time (`unreal.GameplayStatics.get_time_seconds(world)`), not in slate `dt` (whether the slate `dt` follows the fixed step is Unverified).
- Frame rate: every scenario sets `unreal.RPGTraceAudit.set_test_frame_rate(F)` before `editor_request_begin_play()`; default F = 60.
- Common setup per run: `enc.wake(); enc.hold_for_test(True); tr.enter_combat(); dbg.debug_refill_player()`; boss reset to the home pose and heading 0 and `inst.montage_stop(0)` between trials; `au.reset_counters()` before each trial; `tr.set_editor_property("branch_range", 0.0)` when only the first stage is wanted (the second stage is then denied by the tracker before its window opens), default 400.0 for chain tests.
- Hitting trials use the pack ability path (`tr.start_move("Close")` after `au.prime_close_attack(i)`, or `start_move("A2")`), because a bare montage deals no damage and its hits would run the pack's hit path with no ability (side effects, Blueprint error lines). Bare montages (`tr.play_move_montage_for_test`) are used only with the player out of reach.
- Close attack index to move: the first run (T0) logs which tracker move each primed index produces (expected from `RPGAttackTracker.cpp:35-38` and `pie_close_combo_watch.py`: 0 = A3a then pack chain A3b, 2 = A1 then pack chain A1b; Unverified). Later scenarios use the logged map, not the expectation.
- Progress and resume: after each scenario the driver writes `Saved/trace_audit_progress.json` (scenario id, checks passed, total). `Saved/trace_sections.txt` (comma list, default all) selects scenarios; a section already complete in the progress file is skipped when `Saved/trace_resume.txt` exists. The final line sums all sections of the progress file. Death runs need their own PIE (the boss does not come back): section `death:0.14`, `death:0.27`, `death:0.40`, `death:open` one per run.
- Pass wording: "passed N/N under setup F fps, boss held, player at D cm" (Freeze 1329-1335). No scenario is reported as passed unless the driver printed it.
- Blueprint error lines: at the start and end the driver counts `Blueprint Runtime Error` lines in `Saved/Logs/OneBossFight.log`; the delta is printed (informational, KI-052 metric).

Scenarios (expected = analysis, estimates are marked; pass = what the check requires):

### P0 Pre-flight (1 run, 8 checks)
1. Audit and guard components exist on the boss. 2. Pack target resolved: class name contains `AbilitySweeping`, tag `TargetType.MainWeapon`. 3. `Sockets == 5` and names equal {BladeStart, BladeEnd, MiddleSocket, Weapon Start, Weapon End} (print the real list; if the list differs, record it in DECISIONS and relax only this check). 4. `BaseRadius == 50.0` (+/- 0.01). 5. Channels non-empty and contain `ECC_Pawn`. 6. `IsTraceActive()` false at rest. 7. `IsTestFrameRateActive()` false before the scenario sets it. 8. After `enter_combat` the `Weapon Mesh` parent socket is `HeavySwordSocket_R`.

### T0 Windows and data (A1, A1b, A3a, A3b, A2; one run each, 120 fps, player at 700 cm, bare montages; 5 checks + 2)
Per montage, all of: window count exact (1,1,1,1, and 2 for A2); open and close montage position within 0.04 s of the tracker `ActiveStartTime/ActiveEndTime` (A2: window 2 only; window 1 is recorded and must raise `WindowsOutsideTracker == 1`, the known stand-in deviation); `Samples` within [length x 120 - 2, length x 120 + 2]; `MaxContinuityErrorCm <= 0.5`, `OpenRefreshErrorCm <= 0.5`, `SuspectSweeps == 0`; `SetCountAtOpen == 0`, `SelfInSet == 0`, `WindowsWhileSheathed == 0`, `CloseReason == "notify end"`.
Global checks: `MaxSocketGapCm <= 150` (limit 184 = 2 x (50 + 42)); the prime-index to move map is logged.
Information printed: peak step cm, peak speed cm/s, peak sagitta cm, base radius and modifier per window, `WindowsNoAbility` (bare montages: expected 1 per window).

### T1 Step versus frame rate, fastest swing (a) (fastest montage M* from T0 by `PeakSpeedCmPerSec`; fps 120, 60, 30, 15; 3 runs each = 12 runs; player at 700 cm)
Checks: `MinDt` and `MaxDt` equal 1/fps within 0.0001 (fixed step is really on) for every fps (4); sagitta at 30, 60, 120 fps is at most `(50 + 42) - 20 = 72` cm (3); `PeakStepCm(30) / PeakStepCm(120)` between 3.0 and 5.0 (1). 15 fps sagitta: printed only (estimate 40 cm). Printed table: step cm per frame at 30/60/120 against 42 cm and the words "point test would tunnel: yes/no" (expected yes at 30 and 60).

### T2 Placement scan, no tunnel (a, H02) (A1 only, `branch_range` 0; 24 placements = distances {100,150,200,250,300,350} cm x angles {-40,-15,+15,+40} deg; fps 30, 60, 120 = 72 trials)
Checks (4):
- T2.a oracle agreement: for every trial `SetInsertions == (OverlapSamples > 0)`: 72/72 required. (The shadow sweep and the pack agree; if not, the shadow is wrong, fix it before trusting anything else.)
- T2.b consistency across frame rates: placements whose `ClearanceCm` at 120 fps is within +/-12 cm of 0 are "boundary" and are listed (expected at most 4); for all other placements hit(30) == hit(60) == hit(120): N/N required.
- T2.c inside placements (clearance <= -12 at 120 fps) are hit at every fps: required all.
- T2.d outside placements (clearance >= +12) are never hit at any fps: required all.

### T3 Slow strike, one accepted hit (H01) (A1, play rate 0.25 set right after `start_move` with `inst.montage_set_play_rate(montage, 0.25)`; player at {70, 90} cm in front; 10 trials each = 20; 60 fps)
Per trial: `SetInsertions == 1`, `DamageAccepted == 1`, `DamageTaken` equal across trials within 0.5, first overlap sample index equal to the insertion sample index +/- 1 (contact at the visible touch), `OverlapSamples >= 10` (estimate 40 to 70 at this rate). Check: 20/20. If the rate change did not take (`get_current_active_montage()` None) the trial is repeated and the repeat count printed.

### T4 Clear miss (H03) (A1, `branch_range` 0, 60 fps)
- Far: distances {450, 600, 800} cm x 4 trials = 12: `OverlapSamples == 0`, `SetInsertions == 0`, health unchanged, no `DamageAccepted`.
- Near-miss band: from T2 pick up to 5 placements with minimum clearance in [+10, +40] cm at 60 fps; run each 4 times = 20 trials: same requirements (visible air gap must not hurt).
- Info: `PhantomReachCm` = largest `(min clearance + R)` ... reported as `R - blade half width` (expected 50 - 17 = 33 cm) over all hits seen in T2, T3, T5: the number for open question O-1.
Check: 32/32 no damage.

### T5 Many samples, one damage (H04) (A1, `branch_range` 0, player stationary at 70 cm)
20 trials at 60 fps + 5 at 30 + 5 at 120. Per trial window: `OverlapSamples >= 3` (estimate 15 to 40), `SetInsertions == 1`, `DamageAccepted == 1`, `Samples >= OverlapSamples`, and the invariant `SetInsertions == DamageAccepted + RejectedInvulnerable + RejectedOther`. Three checks (60, 30, 120 fps groups).

### T6 Second stage hits again (H05) (prime index 0 = A3a then A3b, `branch_range` 400, player at 80 cm)
- Chain: 20 trials at 60 fps, 5 at 30, 5 at 120. Per trial: tracker instance count +2, `Windows == 2`, window ordinals within instance 1 and 1 (two instances), `SetCountAtOpen == 0` for both, `SetInsertions == 1` and `DamageAccepted == 1` in each, total `DamageAccepted == 2`, total health loss within 1.0 of twice the single-hit loss.
- Denied branch: player at 450 cm (outside `BranchRange` 400): 10 trials: `Windows <= 1`, the tracker's branch denied counter +1, no window opens for the denied stage (a stage the tracker stops before its window opens must open no trace), damage 0.
Checks: chain 30/30, denied 10/10.

### T6b One damage per attack instance, A2 stand-in (G-3) (A2 via `start_move("A2")`, player at {60, 100, 140, 180, 220, 260} cm x 5 trials = 30; 60 fps)
Record windows per instance (expect 2) and `DamageAccepted` per instance. Required with `bDedupePerInstance` true: at most 1 per instance in 30/30. Baseline run with the flag false is printed (how many instances show 2 hits; expected 0 to few: the first window did not hurt in earlier tests). This run decides whether step 7 of section 7 is needed.

### T7 Self and owner ignored (H06) (A1, player at 700 cm, 5 trials)
Per trial: `SelfInSet == 0`, `GetHitSetCount() == 0` at close. `SelfOverlapSamples > 0` in at least 4 of 5 (proves the boss capsule is inside its own sweep and the filter is what saves it). Invalid actors: not provoked (Unverified, listed in section 8).

### T8 Trace ends on every interruption (H07) (A1, boss held, player at 70 cm, 60 fps, interrupt offsets in montage seconds {0.14, 0.20, 0.27, 0.34, 0.40} x 4 trials = 20 per kind)
Kinds and results required per trial (guard on):
| Kind | How | Required |
|---|---|---|
| stop | `au.arm_interrupt("stop", pos)` (pack behaviour only) | `FramesToClose <= 1`, `SamplesAfterInterrupt == 0`, `DamageAfterInterrupt == 0`, `CloseReason == "montage stopped"` |
| stagger | `arm_interrupt("stagger", pos)` -> `ForceBreakForTest` | `FramesToClose == 0`, samples after 0, damage after 0, reason "stance break" |
| phase | `arm_interrupt("phase", pos)` (health 0.59; after each trial `enc.reset_for_test()`, `wake()`, `hold_for_test(True)`, `enter_combat()` as in `pie_phase_reset.py`) | `FramesToClose <= 1`, samples after 0, damage after 0, reason "phase transition" |
| reset | `arm_interrupt("reset", pos)` -> `ResetForTest`, then wake and hold again | `FramesToClose == 0`, samples after 0, damage after 0, reason "reset", hit set empty after the reset |
Reset teleport: the boss starts 800 cm from its home; the player stands on the line between boss and home at 400 cm from the boss; reset at offset 0.27: 20 trials: `DamageAfterInterrupt == 0` and `SuspectSweeps == 0`. Baseline (guard `bCloseOnInterrupt` false) is run once per kind (5 trials) and printed, to document what the pack does alone.
Death: 4 separate PIE runs (offsets 0.14, 0.27, 0.40 and "the frame the window opens"), one trial per run, player at 70 cm: `FramesToClose <= 1`, samples after 0, damage after 0, tracker phase None. The death edge has 4 trials, not 20 (the boss does not come back); this is the wording in the report.
Checks: one per kind (4) + reset teleport (1) + death (1 per run, 4).

### T9 Walls (H11) (A2 via `start_move("A2")`; wall from `dbg.debug_spawn_wall(boss + fwd x 110, boss rotation, Vector(0.2, 8, 6))` = 20 x 800 x 600 cm, 110 cm in front of the boss; 60 fps)
| Case | Setup | Trials | Required |
|---|---|---|---|
| W0 control | no wall, guard on, player 200 cm in front | 10 | `DamageAccepted == 1` in 10/10 (A2 hit 140 to 220 cm 3/3 earlier) |
| W1 baseline | wall, `bBlockThroughWalls` false | 20 | printed only: expected hits through the wall (a FAIL of Freeze 560, the reason for the guard) |
| W2 guarded | wall, guard on, player 200 cm behind it | 20 | `DamageAccepted == 0`, `SetInsertions == 0`, `Occluded >= 1`: 20/20 |
| W3 side | wall moved 400 cm to the side, guard on | 10 | `DamageAccepted == 1` (no false block): 10/10 |
`dbg.debug_clear_walls()` after each case.

### T10 Overlap versus accepted in the debug output (g)
- After one hit trial: `dbg.build_lines()` contains a line with `overlap` and one with `accepted`, and the numbers equal `GetCounter("OverlapSamples")` and `GetCounter("DamageAccepted")` (3 checks).
- Invulnerable overlap: force the player's `Status.Invulnerable` tag for the whole window (`pawn.call_method("AddOwnedGameplayTag", args=(tag,))` as in the A4 driver, removed afterwards), A1 at 70 cm, 5 trials: per window `OverlapSamples >= 1` and `SetInsertions == DamageAccepted + RejectedInvulnerable + RejectedOther`. Printed for M2: `AcceptedWhileInvulnerable` (whether the pack hurts a tagged player), and whether `RejectedInvulnerable` windows later saw the blade still touching (the consumed-entry case, G-8). 1 check.

### T11 Natural fight, informational with invariants (60 s, boss not held, player stands at 100 cm, refilled every 3 s, 60 fps)
Over all windows: `DamageAccepted <= 1` per window, `SamplesAfterInterrupt == 0`, `SuspectSweeps == 0`, `WindowsWhileSheathed == 0`. Printed: windows by move (including untracked pack attacks), peak speed per move, phase two (rate 1.2) peak step. 4 checks.

### T12 Cleanup
After `editor_request_end_play()` the next run's P0 check 7 proves the fixed step was restored. 1 check.

Counts: about 75 checks; about 410 trials; time estimate 20 to 30 minutes of PIE in sections (progress file makes it resumable). Trials per edge: 20 for the dedupe, stage, interrupt, wall and slow-strike edges; death 4; scan 72; others as listed.

Regression after implementation (must stay green): `pie_close_attacks.py` 43, `pie_attack_rules.py` 13, `pie_a4_low_sweep.py` 14, `pie_a5_heal_punish.py` 31, `pie_leap_wave.py` 17, `pie_phase_reset.py` 14, `pie_player_death_reset.py` 25, `pie_riposte.py`, `pie_boss_hud.py` 29, `pie_victory_lock.py` 9, `pie_a2_interrupts.py` (stagger, reset), 6 automation tests plus the new ones (`Scripts/Rebuild.ps1 -Tests`).

---------------------------------------------------------------------------------------------------

## 7. Ordered implementation steps (each leaves the project building; one step at a time, main thread only)

0. Docs only: set row M1 to Doing in `MILESTONE_GATE2_CODE.md` and G1-4 to Doing in `TASKS.md`. Resume point: the first step below whose files do not exist yet.
1. `Pack/RPGPackTrace.h/.cpp` (facade, `CheckPackProperties`) and the `Content.PackWiring` addition. Build (`Scripts/Rebuild.ps1 -Tests`): 6 tests pass, PackWiring now lists the trace names. No gameplay change.
2. `Player/RPGTraceAudit.h/.cpp` v1: resolve, active flag, window open/close records, log lines, `GetCounter` (windows, samples), `BuildLines`, attach in the subsystem, one line in `RPGCombatDebug.cpp`. Build. Run `pie_debug_overlay.py`, then `rpg.Debug 1`, play one attack: the first real numbers (socket names, radius, channels, windows). Run `pie_trace_audit.py` sections P0 and T0 (v1 of the driver). Write the facts into DECISIONS (closes the unverified sockets, channels and notify tag items).
3. Audit v2: shadow sweep, hit-set tracking, outcome resolution, continuity, step, sagitta, clearance, interrupt detection, per-instance aggregate, `rpg.TraceDebug`. Build. Driver sections T1, T3, T5, T10.
4. Test hooks: `ArmInterrupt`, `PrimeCloseAttack`, `SetTestFrameRate/Clear/IsActive` (+ subsystem `Deinitialize`, `pie_stop.py`). Build. Driver sections T2, T4, T6, T7. If `PrimeCloseAttack` cannot set the ability variables, group trials by the move the tracker reports and say so in the report.
5. Baseline run of T8 with `bCloseOnInterrupt` false (the guard exists but only observes: add `URPGTraceGuard` with `CloseTraceNow` and the three call sites already in place, flag default true). Run T8 with the flag false, record the pack-alone numbers, then true. Build after adding the guard (all builds). Death step 5 of the guard included.
6. Guard wall gate (4.3 step 6). Driver T9: W1 baseline first (flag false), then W0, W2, W3.
7. Only if T6b baseline shows a double hit or the owner wants the Freeze 12.2 unit enforced: `bDedupePerInstance` carry code. Only if the owner decides on a radius: `TraceRadiusOverrideCm` (4.3). Both are small; each gets its own driver pass.
8. Automation tests `Trace.WindowModel` and `Trace.SweepMath` (4.10). `Scripts/Rebuild.ps1 -Tests`.
9. Full driver run (all sections, progress file), regression drivers, docs (section 9). Only now mark G1-4 Verified, with the numbers printed by the driver.

---------------------------------------------------------------------------------------------------

## 8. Risks and open questions

Risks:
- R-1 Reflection names. BP variable names with spaces and `?` (`Current Collision Mesh`, `bCollisionEnabled?`) are expected to be the `FProperty` names; not run. `Resolve` fails safe and `PackWiring` guards it.
- R-2 The wall gate and the dedupe carry write into the pack's `HitActors` array and rely on `Can Hit Actor?` reading it (Graph-read: nodes `Get HitActors`, `Contains Item`, NOT, comment "Hit one enemy only once"). If a future pack version changes that, the fallback in 4.8 applies.
- R-3 Tick order: the guard runs after the skeletal mesh tick (prerequisite) and before the pack's `TG_DuringPhysics` tick; the character movement of the player also ticks in `TG_PrePhysics`, so the player position the gate sees can be one frame old (about 9 cm at 550 cm/s and 60 fps; margin 92 cm).
- R-4 The audit assumes the pack's sample ran before its own tick (`TG_PostUpdateWork` plus prerequisites). If the Blueprint component overrides its tick group the prerequisite keeps the order.
- R-5 Hitches: below about 15 fps one chord can miss the fastest arc; documented, measured by `PeakSagittaCm`.
- R-6 Fixed step: `WITH_FIXED_TIME_STEP_SUPPORT` and the slate `dt` semantics in PIE are not verified. Fallback: `t.MaxFPS` caps and the measured `MinDt/MaxDt` printed (the T1 dt checks then become "within 10 %").
- R-7 Shadow sweep cost: 5 sphere sweeps per active frame, only while a window is open (well under 0.2 ms); compiled out of Shipping.
- R-8 Python call conventions (`FName` arguments from `str`, static functions as `unreal.RPGTraceAudit.set_test_frame_rate`) follow `RPGInputTestUtils`; not run for this class.
- R-9 Interplay with M2: the pack consumes the hit-set entry at the first overlap even when the damage resolver rejects it (G-8). M1 only measures; M2 decides whether the guard refunds the entry (remove the player from `HitActors` one frame after a rejected-invulnerable insertion).
- R-10 `PrimeCloseAttack` depends on ability variable names read from the BP variable list (`Attack Index`, `Random Attack Index?`, function `SetAttackIndex`); the mapping of index to montage is not read.

Open questions for the owner (decisions, not facts):
- O-1 Trace radius: keep the pack's 50 cm (phantom reach about 33 cm beyond the visible blade, Freeze 544 and 621 ask for the smallest design) or set `TraceRadiusOverrideCm` to about 28 (blade half width 17 cm plus 11 cm)? The A2 stand-in slam widens it with a per-notify modifier, so its reach would shrink by the same 22 cm.
- O-2 Wall rule: boss centre to player centre is the proposed test. A slam that the Freeze may want to pass low walls (waist high) is not covered; say if some attacks should ignore walls (Freeze 560 "unless the attack explicitly allows it").
- O-3 Per instance dedupe default on (A2 stand-in two windows count as one swing)?
- O-4 Guard in Shipping: yes (it is gameplay). Audit and hooks: no.
- O-5 Attach the same audit and guard to the player weapon later (same pack classes; victim = boss)? Out of scope for M1.

Unverified (could not be read or run):
- Socket positions and the hand-axis orientation of SM_KwangSword; the live boss weapon world scale.
- `CollisionObjectTypes` and `GameplayTagsToIgnore` defaults of the boss target; the object type of the player's mesh component.
- The `Collision Target Tag`, `TraceRadiusModifier` and `AttackData` on the boss's own montage notifies (windows are known only from `DELTA_AUDIT.md` 30-44).
- Tick group override of `BP_CollisionComponent`; montage group of boss attack, stagger and roar montages.
- Whether a death montage exists for the boss; the caller of `DropEquipment`.
- Same-frame latency from hit-set insertion to the player's health change.
- Class default of the `TargetTypeClass` pin (`BP_EnemyAbilitySweepingTraceTarget` expected from the referencer query).
- `Attack Index` to montage mapping of `GA_GS_Boss_CloseAttack`.
- `WITH_FIXED_TIME_STEP_SUPPORT` in this build; `WorldSettings` frame time clamps; slate `dt` under fixed step.
- All speed, step and sagitta numbers in section 2.4 are estimates.
- Invalid-actor filtering (Freeze H06 second half) cannot be provoked cheaply and is not tested.
- Dead-target filtering: no life-state test was found in `Can Hit Actor?`; whether `GameplayTagsToIgnore` holds `Status.Dead` is not read.

---------------------------------------------------------------------------------------------------

## 9. Docs to update (after the driver has run, with its numbers)

- `Documentation/TASKS.md`: G1-4 status and a Done entry (what was built, N/N results, deviations); G2-16 note (two new automation tests); gap list rows if a new KI appears.
- `Documentation/DECISIONS.md`: new entry "Weapon trace review (G1-4)": boss traces the `Weapon Mesh` component (SM_KwangSword), radius 50 constant in BeginPlay, sample order, dedupe unit is the trace window, the guard (close on interrupt, wall gate, optional instance carry, radius override), why no pack edit, the numbers (steps, sagitta, phantom reach), the correction of the `BP_KwangSword` and "sword is part of the mesh" notes, the open decisions O-1 to O-3.
- `Documentation/KNOWN_ISSUES.md` (next free id KI-071): through-wall hits in the pack trace (closed by the guard once T9 W2 passes), A2 stand-in with two trace windows, phantom reach, hitch limit below 15 fps, consumed hit-set entry on i-frame overlaps (owner M2), any failed baseline of T8.
- `Documentation/TEST_PLAN.md`: rows TRACE-01 (T0 to T1), TRACE-02 (T2 scan), TRACE-03 (T3 to T7), TRACE-04 (T8 interruptions), TRACE-05 (T9 walls), TRACE-06 (T10 debug split), automation rows for `Trace.WindowModel`, `Trace.SweepMath`, and the PackWiring trace names.
- `Documentation/DELTA_AUDIT.md`: rows TR-01 to TR-04 (status, evidence), section 1 weapon row correction (the boss uses `Weapon Mesh` with SM_KwangSword, not the `BP_KwangSword` actor).
- `Documentation/PROJECT_STATE.md`: tools line for `RPGPackTrace`, `RPGTraceGuard`, `RPGTraceAudit`, `rpg.TraceDebug`, `pie_trace_audit.py`, `set_test_frame_rate` and the `pie_stop.py` restore.
- `Documentation/MILESTONE_GATE2_CODE.md`: row M1 status and Done-when text; regression list gains `pie_trace_audit.py`.
- `Documentation/PROGRESS_LOG.md` one line.

STATUS: COMPLETE
