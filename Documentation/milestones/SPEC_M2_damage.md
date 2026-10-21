# SPEC M2: Damage path and i-frames (TASKS G1-5)

Written 2026-10-21 by Claude (read-only research agent). Row M2 of `MILESTONE_GATE2_CODE.md`. Driver to build: `Scripts/Editor/pie_damage_path.py`.
No file under Source/, Content/, Config/, Scripts/ was changed for this spec. Evidence labels:
- [code] project source, file:line.
- [bridge] pack Blueprint node lists read through `Scripts/bp_graph.py` / `bp_pins.py` (node titles, pin defaults, link counts; not link topology).
- [asset] values parsed offline from the pack `.uasset` bytes (read-only helper in the agent scratchpad). Cross-checked later by the C++ monitor (section 4.2).
- [engine] UE 5.5 source under `C:/Program Files/Epic Games/UE_5.5/Engine/Source`, path:line.
- UNVERIFIED = not proven; section 8 lists them.

## 1. Goal and Freeze requirements

Goal: one damage path whose invulnerability decision is made where damage resolves, a measured and separately defined i-frame window for the quick dash and the full roll, an audit that separates "trace overlap" from "accepted" from "rejected", and cleanup of `Status.Invulnerable` on every exit.

Note on the task text: "Freeze section 14" is the tracking section (Freeze 563). The damage and i-frame text is in the sections below.

| Id | Requirement | Freeze line |
|---|---|---|
| FR-1 | One damage-resolution path using a hit payload. Damage must not be applied twice (trace and GE or hit reaction) | 419 (10.1 row), 12.1 at 508-524 |
| FR-2 | Invulnerability is applied by the damage-resolution path plus a montage notify state or tag. The trace must not decide invulnerability separately from the receiver | 416 (10.1 row) |
| FR-3 | Window times in montage-local seconds, with the play rate recorded. Quick dash and full roll windows separately configurable. 26-28 frames at 60 FPS is only a test baseline, not valid for the quick dash | 483-486, 1200, 214 |
| FR-4 | Default policy on a valid i-frame hit: no direct HP damage, no hit reaction, no guard or poise impact. Status buildup bypasses only if the damage type says so | 487 |
| FR-5 | The receiver validates invulnerability at the moment damage is resolved, not from the montage or the trace | 488 |
| FR-6 | A trace may overlap during i-frames. Debug output must distinguish "trace overlap" from "damage accepted" | 489, 12.1 step 11 at 522 |
| FR-7 | Every dodge exit clears invulnerability: natural end, interruption, attack or stagger interruption, death, respawn or reset, missing montage, ability cancel, pawn destroy | 491-493, 18.3 at 800, 34.1 at 1308-1317 (idempotent cleanup) |
| FR-8 | Processing order: validate, reject duplicate, read target state, reject if invulnerable, guard, HP once, poise, posture, status, feedback once, diagnostics | 508-522 |
| FR-9 | Lethal hit short circuit: after HP damage re-check death, skip posture, hit stun, branch, phase actions | 1267-1269 |
| FR-10 | Attack instance identity: repeated samples of one swing hit once; a new authored stage may hit again | 526-533 |
| FR-11 | Debug shows "player invulnerability active/inactive and the source window/effect" | 918 |
| FR-12 | Tests D12 to D15, H08 (also H09, H10 for guard and field independence); 20 trials per deterministic input-edge condition; report "N/N under setup X" | 945-948, 959-961, 1331, 1241 |
| FR-13 | Boss attacks do not populate BossPostureDamage | 504 |

Project values in the Freeze table (HP, guard stamina, poise tier): A4 50, 70, Knockdown (line 138); A5 30, 25, Light Flinch; A6 120, 180 (Guard Break), Flatten Knockdown. Project HP values are scaled by 0.4 for a 120 HP player: A4 20, A5 12, A6 48 (`RPGBossLowSweep.h:35-37`, `RPGBossHealPunish.h:47-48`, `RPGBossShockwave.h:36-39`).

## 2. Current state

### 2.1 How the pack damages a character (weapon trace path) [bridge]
All names are Blueprints under `/Game/AdvancedARPGCombat/`. The order is read from node titles and positions; link topology was not read.
1. `CollisionSystem/BP_TraceTarget` EventGraph: custom event `CollisionTrace` runs a multi sphere trace for objects, then for each hit calls `Can Hit Actor?` (function of `BP_TargetType`), then `Add Hit Actor`, then `On Hit`.
2. `Can Hit Actor?` (`CollisionSystem/BP_TargetType`): checks the performing actor, `HitActors` (hit one enemy only once), `CollisionProfileNamesToIgnore`, `ActorClass To Ignore`, `Can Hit Component?`, and `GameplayTagsToIgnore` through the interface message `Has Any Matching Gameplay Tags` sent to the hit actor.
3. `GameplayTagsToIgnore` default: the strings `GameplayTagsToIgnore`, `Status.Dead`, `Status.Invulnerable` sit together in `BP_TraceTarget.uasset` (offsets 4505, 6611, 6631) and in `CoreCombatSystem/Collision/BP_EnemyAbilitySweepingTraceTarget.uasset` (934, 1267, 1287). Conclusion (UNVERIFIED value, strong evidence): the default ignore set is {Status.Dead, Status.Invulnerable}.
4. `CoreCombatSystem/Collision/BP_AbilitySweepingTraceTarget.OnHit`: `Make Hit Event Data`, `Run State Machine by Tag (StateMachine.ImpactDecision)` on the victim, `Hit Handle` interface message (`CoreCombatSystem/Interfaces/BP_DamageInterface`, inputs: Impact Decision, DamagedActor, Instigator, Event Location, HitResult, EventData), `Send Hit Event to Ability` (`Gameplay Event Recieved` on the attacker's ability), then hit impulse.
5. `MeleeCombatSystem/Blueprints/States/SM_ImpactDecision` decides block, parry, deflect: tags `Status.Blocking` (hit angle in -65 to 65 degrees, `CanAttackBeBlocked?` = not `IsUnblockable Attack?` of the hit data), `Status.ParryActive` (distance <= `Minimum Parry Distance`, `Can be Parried`), deflect by `InputTag.Block` held time <= `Deflection Timing`. It writes `ImpactDecisionTag` (`ImpactDecision.BlockedHit`, `ParriedHit`, `DeflectedHit`).
6. The attacker's ability applies a damage gameplay effect; its execution is `CoreCombatSystem/Abilities/Executions/BP_DamageExecution` (child `MeleeCombatSystem/Blueprints/Abilities/Executions/BP_MeleeDamageExecution`). `Event Execute` calls `Can Damage be Applied?`, then Pre Calculation Bonus, Critical Damage, Post Calculation Bonus, Damage Resist, Deal Damage.
7. `Can Damage be Applied?` reads `DamageImmuneTags` (variable). The only tag string near it in the asset is `Status.DamageImmune` (offset 8654; `ImpactDecision.ParriedHit` at 5930). No pack Blueprint sets `Status.DamageImmune` (searched `AdvancedCombatFramework` and `MeleeCombatSystem/Blueprints`: only `BP_DamageExecution` and `DT_CoreCombatGameplayTags`). So this layer is dormant for `Status.Invulnerable` (UNVERIFIED default value).
8. `BP_MeleeDamageExecution.Deal Damage` switches on `ImpactDecisionTag`. Plain hit: `Modify Attribute(Attribute.Health, -Damage)`. Blocked: a stamina decrease computed from damage and `Attribute.Stability` (clamped to 100, divided by 100) and a health decrease reduced by `Attribute.BlockPhysicalDamageReduction` (clamped to 100, divided by 100). Both finish with `On Damage Applied` (interface). The exact blocked formula was not traced (UNVERIFIED).
9. Hit reaction: `CoreCombatSystem/GameplayCues/BP_Character_DamageTaken.OnDamageTaken` casts the cue data to `BP_HitData`. If the owner `Has Any Matching Gameplay Tags {Status.Dead, Status.Invulnerable}` is false, `Activate Damage Taken Ability` runs (`Get Abilities By All Tags(Ability.HitReaction)`, cast `GA_BaseHitReaction`, `Set Hit Data`, `Try Activate Ability`) and the camera shake runs. `GE_DamageBase` carries an `ExecuteGameplayCues` entry (string at offset 3316; the cue tag was not read). The default tag set of that check sits in the cue asset at offset 165994: `(GameplayTags=((TagName="Status.Dead"),(TagName="Status.Invulnerable")))`.
10. `CoreCombatSystem/Abilities/GA_HitStun` (child of `GA_BaseHitReaction`): `Commit Ability`, `Enter State by Tag (Character.State.Hit.Stun)`, `Get Ability Montage` (map by `E_HitReactionDirection`), plays the montage with stop-all, 5 s hit count timer, optional rotation and knockback from `BP_HitData`. `GA_BaseHitReaction.Can Activate Ability?` is poise gated (`Attribute.Poise` minus 20, minus 50 more for attack power >= 3; `bUsesPoise`). `GA_HitStun_NoHitData` activates only when no hit data is set.
11. `BP_HitData` variables: SourceTags, ImpactDecisionTag, Damage, HitResult, Instigator, DamageCauser, HitAngle, HitFromDirection, AttackData (`BP_AttackData`), Swing Direction. Its getters (`GetAttackPower`, `IsUnblockable Attack?`, `CauseKnockback?`, `GetAttackImpactEffects`) read `AttackData`. Pack assets exist under `MeleeCombatSystem/Blueprints/DataAssets/AttackData/`: `DefaultMeleeAttackData`, `MeleeKnockdownAttackData`, `StrongMeleeAttackData`, `ChargedMeleeAttackData`, `DefaultGrabAttackData`, `PoisonDamageAttackData`.

Consequence for the question "what happens when a hit lands during i-frames": for a pack weapon trace the player is dropped at step 2, before `Add Hit Actor`, before `On Hit`. Nothing after that runs: no impact decision, no gameplay event, no damage effect, no `Deal Damage`, no cue, no hit reaction, no camera shake, no guard or poise change. The policy of FR-4 is met, but (a) the trace decides (conflicts with FR-2 and FR-5), (b) the overlap is not recorded anywhere (FR-6), (c) the player is not added to `HitActors`, so a contact that lasts past the end of the i-frames inside the same trace window is accepted late (this matches Freeze 35.3 scenario 3, "result follows measured i-frame overlap").
Layers 3 and 9 and the dormant layer 7 are three separate invulnerability checks in the pack; only layer 3 is live for a boss swing.

### 2.2 `Status.Invulnerable` source [bridge, engine]
- `CoreCombatSystem/AnimNotifies/ANS_iFrames`: `Received_NotifyBegin` sends `Add Owned Gameplay Tag(Status.Invulnerable)` through `BP_GameplayTagBlueprintInterface` to the owner of the mesh; `Received_NotifyEnd` sends `Remove Owned Gameplay Tag(Status.Invulnerable)`. No tick, no counter.
- Storage: `BP_BaseCombatCharacter` variable `GameplayTags` is a `GameplayTagContainer` (not a counted container). The interface functions are implemented in a collapsed graph ("Combat System Events") that the bridge cannot read, so add and remove semantics are UNVERIFIED. If it is a plain container, two overlapping i-frame states cancel each other on the first End.
- Other writers of the string: `BP_EnemyDeathTask` (enemies only). No dodge ability effect applies the tag (`Status.Invulnerable` is not in `GA_Player_Dodge`'s referencing assets; searched with the string grep).
- Engine cleanup guarantees [engine]: when a montage instance ends or is interrupted, `UAnimInstance::TriggerMontageEndedEvent` calls `NotifyEnd` on the active notify states that belong to that montage instance (`AnimInstance.cpp:2088-2140`). `TriggerAnimNotifies` ends states that are no longer in the queue (`AnimInstance.cpp:1548-1642`). The anim instance teardown also ends active states (`AnimInstance.cpp:340-385`). Order in one update: `TriggerAnimNotifies` at `AnimInstance.cpp:778`, then `TriggerQueuedMontageEvents` at `AnimInstance.cpp:781`; ended events of a stopped montage are queued (`AnimInstance.cpp:2074-2085`) and dispatched after the notify begin of a newly started montage (hypothesis DC-1 below).
- Montage time [engine]: `FAnimMontageInstance::Advance` moves the position by `DeltaTime x PlayRate` through a sub-stepper and fires notifies for the crossed range (`AnimMontage.cpp:2427-2490`). Notify begin and end are therefore exact in montage seconds, but the Blueprint begin and end events run once per frame, so the observable tag edge lands up to one frame (one `dt x rate` of montage time) after the notify time.

### 2.3 The two dodge montages and their windows [asset]
`URPGDodgeTiming` writes the clip and play rate into the dodge ability's montage map (`RPGDodgeTiming.cpp:25-29`, `:158-207`; rates `RPGDodgeTiming.h:57,60`: quick 1.3, full 1.0). The old note in `DELTA_AUDIT.md` D-04 ("one window serves both", quick plays `Dodge_To_Idle` at 1.3) is wrong: the quick dash uses its own montage with its own `ANS_iFrames`.

| Clip | Montage | Length (montage s) | `ANS_iFrames` start (montage s) | Duration | End (montage s) | Play rate | Start, end in real s after the montage starts |
|---|---|---|---|---|---|---|---|
| Quick dash | `Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage` | 0.66667 | 0.10718 | 0.38257 | 0.48975 | 1.3 | 0.0824 to 0.3767 |
| Full roll | `MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Montage` | 2.33333 | 0.0001 | 0.69977 | 0.69987 | 1.0 | 0.0001 to 0.6999 |

Other notify states in the same montages (for context): full roll `InputBufferNS_C` 0.48461 for 1.19216 s, `ANS_MovementCancel_C` 1.70662 for 0.62671 s, `RotateCharacterNS_C` 0.0001 for 0.25 s; quick `RotateCharacterNS_C` 0.0001 for 0.28501 s, `InputBufferNS_C` 0.23380 for 0.26772 s. The notify state class in both montages is `ANS_iFrames_C` (import table of each `.uasset`).
So the "separate windows" already exist as pack data. Quick window length 0.38257 montage s = 0.294 s real. Full window 0.700 s real = 42 frames at 60 FPS (the Freeze test baseline is 26 to 28 frames = 0.43 to 0.47 s). The pack data is wider than the baseline; narrowing is a tuning decision for the owner (section 8, Q1).
DELTA_AUDIT line 41 and `TEST_PLAN.md` A4-01 note: a dodge starts about 0.2 s after the key press (measured). The existing A4 S6 result (backward roll pressed at 0.50 s passes the blade on i-frames, 5 trials) and S9 (rolls pressed at 0.60 s or later are caught) are consistent with these windows but are not a window measurement.

### 2.4 Our code: boss moves bypass the pack
- `RPGBossDamage.h:13-14`: the pack has no entry point for damage without a weapon trace, so health is written directly. `IsInvulnerable` `:18-31` (interface call `HasMatchingGameplayTag` with `Status.Invulnerable`), `IsAlive` `:33-37`, `HurtPlayer` `:39-50` (read attribute, write `max(0, before - damage)`), `WorldBlockers` `:53-59`, `FeetZ` `:62-65`.
- Three call sites, two code copies of the invulnerability check:
  - A4 `RPGBossLowSweep.cpp:117-126` (shared helper), damage `:127-134`.
  - A5 `RPGBossJavelin.cpp:137-157` (shared helper), `ReportJavelin(Dodged)` once `:139-144`.
  - A6 `RPGBossShockwave.cpp:96-105` (private copy of the same interface call), damage `:119`.
- Differences between the three (all untested as a policy):
  - A4 and A5 do not spend the hit on an i-frame contact (`bDamaged` is set only after the write; the javelin flies on). A6 sets `bResolved = true` at `:93` before the check at `:106`, so the wave spends its only chance on an invulnerable contact.
  - A4 and A6 do not check that the player is alive; a dead player counts as a hit (`HitCount` goes up, health stays 0). A5 checks `IsAlive` (`RPGBossJavelin.cpp:146`).
  - A6 priority rule "the central hit already hurt" is a health comparison (`HealthAtLaunch`, `RPGBossShockwave.cpp:44-48,111-115`).
  - Generation checks are per component (`LowSweep :155-158`, `Javelin :106-114`, `Shockwave :143-146`), not at the point of damage.
  - None of the three reads `Status.Blocking`, writes stamina, or plays a hit reaction. KI-065, KI-067, KI-068 record the missing reactions.
- No audit exists. `RPGCombatDebug.cpp:75-125` (`BuildLines`) has boss, A4, A5 counters and the player dodge stage, but no invulnerability line (FR-11) and no damage line.
- Test hooks that exist: `pawn.call_method("AddOwnedGameplayTag", ...)` to inject `Status.Invulnerable` (used in `pie_a5_heal_punish.py:335,344`), `debug_refill_player`, `debug_set_player_health`, `reset_for_test`, `hold_for_test`, `start_move`, `RPGInputTestUtils.set_key_down`. Per-move counters: sweep `inv/jumped/blocked/hits` (`RPGBossLowSweep.h:68-82`), javelin `hit/dodged/world`, wave `invulnerable/central`.
- Player components attach in `RPGPlayerMovesSubsystem.cpp:148-151` (dodge timing) and `:153-203` (boss set). `Deinitialize` at `:49`.
- Encounter reset: `RPGBossEncounter.cpp:225-226` (`++ResetCount; ++Generation;`) and the player respawn trigger `:93-102`. The reset does nothing to the player's tags (a respawn gives a new pawn with a new container).

### 2.5 Frame rate facts [engine, code]
- `t.MaxFPS` only caps (`UnrealEngine.cpp:11627-11670`; the editor calls it through `UEditorEngine::GetMaxTickRate`). The editor PIE runs at about 80 FPS here (DECISIONS: "about 80 fps"; PERFORMANCE_LOG baseline 79 FPS), so 120 FPS cannot be reached with a cap.
- `UEngine::bUseFixedFrameRate` and `FixedFrameRate` (`Engine.h:1527-1536`, ClampMin 15): `UpdateTimeAndHandleMaxTickRate` uses `MaxTickRate = FixedFrameRate` and, when real time is slower, sets the logical delta to exactly `1 / FixedFrameRate` ("we start falling behind real time", `UnrealEngine.cpp:2699, 2769-2790`). This gives exact `dt` at 30, 60 and 120 on this machine.
- The project already toggles these members in `RPGBenchmarkRunner.cpp:374-424` (`bUseFixedFrameRate`, `bSmoothFrameRate`, `t.MaxFPS`, `r.VSync`) with save and restore.
- The Python slate tick `dt` used by the drivers is the Slate delta (UNVERIFIED that it equals the logical delta). Drivers must keep their own clock from the world (`world.get_time_seconds()`), not from the slate `dt`.
- Montage time is frame-rate independent in value, only quantized by frame (section 2.2).

## 3. Gaps
- G-1 No single place decides invulnerability for boss moves; two code copies (`RPGBossDamage.h:18`, `RPGBossShockwave.cpp:96`), three policies for what a rejected contact does.
- G-2 No audit: "trace overlap" is not separated from "accepted" or "rejected, reason" (FR-6, FR-11).
- G-3 Moves ignore death of the target (A4, A6), generation at the point of damage, guard, hit reaction.
- G-4 The i-frame windows were never measured in montage seconds at several frame rates (D12). DELTA_AUDIT D-04 holds a wrong fact.
- G-5 Cleanup (D13) is delegated to engine notify cleanup and never tested; reset has no player-side hook; a forced roll starts a new montage while the quick montage's end event is still queued (DC-1).
- G-6 No debug line for player invulnerability and its source window.
- G-7 For pack weapon moves (A1, A2 stand-in, A3) the pack rejects at the trace and leaves no record. Cannot be changed without editing the pack (excluded).
- G-8 No fixed frame rate helper for drivers; no automatic restore at PIE end.

Defect candidate DC-1 (UNVERIFIED hypothesis, to measure first): in `URPGDodgeTiming::ForceFullRoll` (`RPGDodgeTiming.cpp:209-266`) the quick montage is stopped and the full montage starts in the same moment. The quick montage's iFrames state ends when its instance terminates (after its blend-out) or when its own window ends, and that `Remove Owned Gameplay Tag` may arrive while the full roll's own window (0.0001 to 0.6999) is open. Result if true: the full roll loses i-frames for the rest of its window.

## 4. Design

### 4.1 `URPGDamageResolver` (new, `Player/RPGDamageResolver.h/.cpp`)
Component on the boss, attached next to the other boss components in `RPGPlayerMovesSubsystem::Attach` (after `URPGBossEncounter`), idempotent (`FindComponentByClass` first; also a static `FindOrAdd(AActor* Boss)` used by the moves, so a missing component never skips damage). It is the only code that lowers the player's health for boss moves.

Types (all in the same header):
- `UENUM(BlueprintType) enum class ERPGDamageOutcome : uint8 { Overlap, Accepted, Blocked, RejectedInvulnerable, RejectedDead, RejectedStale, RejectedDuplicate, RejectedMiss, RejectedSuperseded, Failed }`.
- `UENUM(BlueprintType) enum class ERPGHitReaction : uint8 { None, LightFlinch, HitStun, Knockdown }` (the explicit poise tier of Freeze 12 line 503).
- `USTRUCT(BlueprintType) struct FRPGDamagePayload`:
  - `FName MoveId` ("A4", "A5", "A6"), `int32 AttackInstance` (`URPGAttackTracker::GetAttackInstance()` when the move started), `int32 Generation` (`URPGBossEncounter::GetGeneration()` when the move started), `FName HitKey` (dedupe key inside the instance, default `NAME_None`; a second authored stage uses another key, FR-10).
  - `float HPDamage` (health points, default 0). A4 20, A5 12, A6 48: the existing properties are read by the move and copied into the payload, not moved.
  - `float BossPostureDamage` (default 0; boss moves never set it, FR-13; if non-zero the resolver logs a warning and ignores it).
  - `float GuardStaminaDamage` (stamina points, default 0 until step S10; planned 28, 10, 72 = Freeze 70, 25, 180 x 0.4; UNVERIFIED against the player's stamina pool).
  - `bool bCanBeBlocked` (default true), `bool bBypassInvulnerability` (default false; no move uses it), `ERPGHitReaction Reaction` (default None), `FVector HitLocation`, `FVector HitFromDirection`.
- `USTRUCT(BlueprintType) struct FRPGDamageResult { ERPGDamageOutcome Outcome; float HPApplied; float HealthBefore; float HealthAfter; bool bLethal; bool bGuardApplied; FName Reason; }`.
- `USTRUCT(BlueprintType) struct FRPGDamageAuditEntry { int32 Index; double Time; uint64 Frame; FName MoveId; int32 Instance; int32 Generation; FName HitKey; ERPGDamageOutcome Outcome; FName Reason; float HPRequested; float HealthBefore; float HealthAfter; bool bTagInvulnerable; bool bMontageInWindow; FName PlayerMontage; float PlayerMontagePosition; float PlayerMontageRate; float BossMontagePosition; float DeltaSeconds; }`. `bMontageInWindow` comes from the player's `URPGIFrameMonitor` and is diagnostic only; the decision uses the tag (the pack's authority).

Properties of `URPGDamageResolver` (EditAnywhere): `bEnabled = true`; `bResolveGuard = false` (step S10); `bRequestHitReaction = false` (step S10); `int32 MaxAuditEntries = 64` (ring, newest kept); `float OverlapEpisodeGapSeconds = 0.25` (one Overlap entry per contact episode, not per tick).

Functions:
- `FRPGDamageResult Resolve(AActor* Target, const FRPGDamagePayload& Payload)`. Steps follow Freeze 12.1:
  1. Validate: target is the player pawn and alive (`RPGBossDamage::IsAlive` and no `Status.Dead`) else `RejectedDead`; boss (owner) alive else `RejectedStale` with reason "attacker dead"; `Payload.Generation == Encounter->GetGeneration()` else `RejectedStale`.
  2. Duplicate: key `(MoveId, AttackInstance, HitKey)` already accepted in this generation else `RejectedDuplicate`. The set is cleared when the generation changes. The key is inserted only on `Accepted` or `Blocked` (a rejected contact never spends the hit; this is the A4 and A5 policy and becomes the A6 policy only if the owner asks, Q2).
  3. Read target state at this moment: invulnerable (the single `RPGBossDamage::IsInvulnerable`), blocking (`Status.Blocking`, only if `bResolveGuard`).
  4. Invulnerable and not `bBypassInvulnerability`: `RejectedInvulnerable`. No health, stamina, reaction or duplicate-key change (FR-4).
  5. Guard (only `bResolveGuard && bCanBeBlocked`): `Blocked`, HP reduced by `Attribute.BlockPhysicalDamageReduction` percent, stamina reduced by `GuardStaminaDamage` once (H09). The pack's own stability scaling is not reproduced (UNVERIFIED formula, section 4.5).
  6. HP: `RPGBossDamage::HurtPlayer` once. `Failed` if the attribute is missing.
  7. Lethal check (FR-9): `HealthAfter <= 0` sets `bLethal` and skips steps 8 and 9.
  8. Reaction: only if `bRequestHitReaction` and `Payload.Reaction != None` (section 4.5).
  9. Posture and status: not applied for boss moves (fields exist for H10 independence; asserted zero).
  10. Audit entry written (all outcomes), log line `LogRPGDamage`, counters updated, `URPGCombatDebug` can read them.
- `void NoteOverlap(AActor* Target, const FRPGDamagePayload&, FName Reason)`: writes an `Overlap` entry when the move's own test touched the player's capsule (blade angle test, javelin sphere sweep, wave band). Coalesced per `(MoveId, AttackInstance, HitKey)` while contacts are less than `OverlapEpisodeGapSeconds` apart.
- `void NoteMiss(AActor* Target, const FRPGDamagePayload&, ERPGDamageOutcome Outcome, FName Reason)`: for the move-local geometry verdicts that are not damage rules: "jumped" (feet above the blade or wave), "world blocked", "central hit priority" (`RejectedSuperseded`). Audit and counters only. The moves keep their own existing counters (`JumpedCount`, `BlockedCount`, `CentralPriorityCount`) so existing drivers stay valid.
- Readers for tests (BlueprintPure, snake_case in Python): `GetAuditCount()`, `GetAuditLine(Index)` (text, newest index last), `GetLastOutcomeName()`, `GetOutcomeCount(OutcomeName)`, `GetMoveOutcomeCount(MoveId, OutcomeName)`, `GetReactionRequestCount()`, `ClearAudit()`.
- Test hook (not compiled in Shipping): `FRPGDamageResult ResolveForTest(FName MoveId, int32 Instance, float HP, FName HitKey, int32 Generation, float GuardStamina = 0.f)` builds a payload and calls `Resolve` on the first player pawn; `NoteOverlapForTest(...)` likewise.
- Pure core for the C++ automation test: `static FRPGDamageDecision Decide(const FRPGTargetState& State, const FRPGDamagePayload& Payload, int32 CurrentGeneration, bool bDuplicate, bool bResolveGuard)` where `FRPGTargetState { bool bAlive; float Health; bool bInvulnerable; bool bBlocking; float BlockReductionPercent; float Stamina; }`. `Resolve` reads the state from the pack, calls `Decide`, applies the side effects, writes the audit. The automation test drives `Decide` and the audit ring without any pack Blueprint.

`RPGBossDamage.h` keeps `IsAlive`, `FeetZ`, `WorldBlockers`; `IsInvulnerable` stays as the only implementation (the shockwave copy is deleted); `HurtPlayer` gets a comment "resolver only".

### 4.2 `URPGIFrameMonitor` (new, `Player/RPGIFrameMonitor.h/.cpp`)
Component on the player pawn, attached in `RPGPlayerMovesSubsystem::Attach` next to `URPGDodgeTiming` (`:148-151`). It is a separate class so that `URPGDodgeTiming` stays the single owner of input interpretation (Freeze 413). Tick group `TG_PostUpdateWork` (after the mesh's animation update and notify dispatch; UNVERIFIED tick order, covered by the one-frame tolerance).

Observation (default behavior changes nothing in the game):
- Each tick: `bTag = RPGBossDamage::IsInvulnerable(Owner)`; active montage = `AnimInstance->GetCurrentActiveMontage()` (`AnimInstance.cpp:3076`, uses `IsActive`, `AnimMontage.h:513`); `Position = Montage_GetPosition`, `Rate = Montage_GetEffectivePlayRate` (effective rate is what the Freeze asks to record, line 485).
- Expected window of a montage: the first `FAnimNotifyEvent` in `Montage->Notifies` whose `NotifyStateClass->GetClass()->GetName() == "ANS_iFrames_C"`; start = `GetTriggerTime()`, end = `GetEndTriggerTime()` (`Public/Animation/AnimTypes.h:422-427`; `AnimTypes.cpp:82-100`). Cached per montage asset. This is the independent check of the numbers in section 2.3.
- Records: `USTRUCT(BlueprintType) struct FRPGIFrameRecord { FName Montage; float PlayRate; float ExpectedStart; float ExpectedEnd; float StartPosition; float EndPosition; double StartTime; double EndTime; float StartDelta; float EndDelta; int32 Generation; FName EndReason; bool bClosed; bool bMontageOwned; }`. A record opens when the tag rises and closes when it falls. `EndReason` in {Natural (position within one frame step of the end), Interrupted (montage stopped or replaced), Death, EncounterReset, StaleCleared, Unknown}. Ring of `MaxRecords = 32`.
- `bMontageOwned` is true when the tag rose while the active montage had an iFrames window containing the position (within one frame step). A tag that rises with no such window (a test injecting `AddOwnedGameplayTag`, or an unknown writer) is "foreign" and is never touched by the cleanup below.
- Counters: `GetRecordCount()`, `GetRecord(Index)`, `GetUnexpectedDropCount()` (tag false while `Position` is inside `[start + step, end - step]` of the active montage's window: the DC-1 detector), `GetStaleClearedCount()`, `GetReassertCount()`, `GetResetClearCount()`, `IsInsideWindowByMontage()`, `GetSourceText()` (e.g. "Status.Invulnerable via Dodge_Small_Forward_Roll_Montage at 0.213 of window 0.107 to 0.490, rate 1.30").
- Frame step `step = DeltaSeconds x |Rate|` and boundary tolerance `step + 0.004` montage seconds.

Cleanup (D13), only for tags the monitor saw as montage-owned:
- Stale watchdog: a montage-owned tag that is still true more than `StaleGraceSeconds = 0.10` after the active montage is gone, or after `Position > ExpectedEnd + step`, is removed through `Remove Owned Gameplay Tag` (the pack's interface function, found by `FindFunction` on the pawn as `IsInvulnerable` does) and counted. The pack's own later `NotifyEnd` removal is a harmless repeat (idempotent, FR-7, Freeze 1310).
- Death: when `IsAlive(Owner)` turns false while a montage-owned tag is set, remove it at once (reason Death).
- Reset: `OnEncounterReset(int32 NewGeneration)` is called from `URPGBossEncounter::ResetEncounter` right after `++Generation` for the first player pawn. It removes a montage-owned tag (reason EncounterReset) and closes the record. The running dodge montage is not stopped (a live-pawn reset only happens in tests; a respawn gives a new pawn).
- Pawn destroy and PIE end: no statics, no delegates held outside the component; `EndPlay` closes the open record. Nothing to restore.
- Foreign tags are never cleared (`bClearForeignTags = false`), so the injected-tag tests of A4, A5, A6 stay valid.
- DC-1 repair (only if the driver confirms it): `bReassertOnDrop = false` by default; if `GetUnexpectedDropCount()` shows drops inside a window of the active montage, set it true. Then, when the tag is false while `Position` is inside `[start + 2 x step, end - step]` of a montage-owned window and the previous record ended in the last 0.25 s by interruption, the monitor sends `Add Owned Gameplay Tag` once and counts a reassert. This makes the monitor a second writer of the tag, so it must be documented in DECISIONS and limited to this case. Alternative with no second writer: delay the full roll's start by the quick montage's remaining blend-out in `ForceFullRoll` (changes feel; not preferred).

Optional tuning (step S11, off by default): `TArray<FRPGIFrameClamp> Clamps` with `FRPGIFrameClamp { FName MontageName; float StartSeconds = -1.f; float EndSeconds = -1.f; }`. Values are montage seconds; -1 means "use the pack's window". The monitor only narrows: if the tag is true and `Position` is outside `[StartSeconds, EndSeconds]` of the matching entry, it removes the tag (reason Clamp); it never adds. This is how "separately configurable quick and full windows" (FR-3) are met without editing the pack montages. Default empty, so the measured pack windows are the shipped behavior.

Debug (FR-11): `URPGCombatDebug::BuildLines` (`RPGCombatDebug.cpp:75-125`) gets, under PLAYER, `IFRAME  invulnerable ON|off  source <GetSourceText>  records N  unexpected drops N  stale cleared N  reasserts N`, and, under the boss lines, `DAMAGE  accepted N  rejected invulnerable N  duplicate N  stale N  dead N  overlaps N  last: <GetAuditLine(last)>`. Same text goes to the once per second log of `rpg.Debug 2`.

### 4.3 Frame rate helper for drivers (`Combat/RPGInputTestUtils.h/.cpp`)
- `UFUNCTION(BlueprintCallable, Category = "RPG|Test") static bool SetFixedFrameRate(float Fps)`: `Fps > 0` saves the current `GEngine->bUseFixedFrameRate`, `FixedFrameRate`, `bSmoothFrameRate`, then sets fixed rate on, `FixedFrameRate = Fps`, smoothing off, `r.VSync 0`; `Fps <= 0` restores. Pattern: `RPGBenchmarkRunner.cpp:374-424`. Clamp `Fps` to 15 or more (engine ClampMin).
- `static float GetFixedFrameRate()` returns 0 when off.
- Automatic restore: `URPGPlayerMovesSubsystem::Deinitialize` (`RPGPlayerMovesSubsystem.cpp:49`) calls the restore, so a crashed or aborted driver cannot leave the editor at 30 FPS after the PIE world is torn down. No `UnrealEd` dependency.
- `t.MaxFPS 30` / `t.MaxFPS 60` stays valid as a cap for a manual check; it cannot produce 120.
- Driver proof of setup: the driver samples `world.get_time_seconds()` differences for 60 frames after each change and requires mean within 2 percent of `1/fps` and max-min under 10 percent of `1/fps`, otherwise it marks the fps cell "setup failed" (a FAIL, not a skip).

### 4.4 Hook points and migration (behavior preserved)
- A4 `URPGBossLowSweep::Test` (`RPGBossLowSweep.cpp:60-135`): the angle, reach, jump (`:87-97`) and world line (`:98-116`) tests stay. After the capsule overlap is established call `NoteOverlap`. Jump and world blocked call `NoteMiss`. Replace `:117-134` by `Resolve` with `MoveId = MoveId`, `AttackInstance = LastInstance`, `Generation = SweepGeneration`, `HPDamage = Damage`, `bCanBeBlocked = true`. Map the result: `Accepted` or `Blocked` sets `bDamaged`, `++HitCount`; `RejectedInvulnerable` keeps the once-per-sweep `InvulnerableCount` and the existing "the blade can still catch the player if the i-frames end" behavior (no early return flag); other rejects log and return. Getters unchanged.
- A5 `ARPGBossJavelin::Tick` (`RPGBossJavelin.cpp:135-157`): `Launch` gets one more argument `int32 InAttackInstance` (set from `Tracker->GetAttackInstance()` in `URPGBossHealPunish::Release`, `RPGBossHealPunish.cpp:157`). The pawn sweep that finds the player calls `NoteOverlap`; then `Resolve`. `RejectedInvulnerable` keeps `Punish->ReportJavelin(Dodged)` once and the javelin flies on. `Accepted`, `Blocked` or `Failed` finish with `Hit` as now. `RejectedDead` and `RejectedStale` let it fly on (stale ends it through its own generation check).
- A6 `URPGBossShockwave::Resolve` (`RPGBossShockwave.cpp:61-122`): delete the private tag check (`:96-105`) and use the resolver. Keep `bResolved = true` before the decision (A6 policy unchanged in this migration, Q2). Keep the central hit priority in the component (call `NoteMiss(..., RejectedSuperseded, "central hit")` for the audit). `HitCount`, `InvulnerableCount`, `CentralPriorityCount`, `JumpedCount` keep their meaning.
- Behavior changes that the migration makes on purpose, and must be checked by the old drivers: A4 and A6 no longer count a hit on a dead player (`pie_player_death_reset.py` must stay 25/25); A6 and A4 get the generation check at the point of damage.
- Pack weapon moves (A1, A2 stand-in, A3): unchanged. They reject at the pack's trace (section 2.1). Their outcome is verified from health and the absence of a player hit reaction (scenario M4). No shadow audit is planned (it needs the signature of `BP_CollisionComponent.OnHit`, UNVERIFIED; listed in section 8, Q5).
- `URPGBossEncounter::ResetEncounter` (`RPGBossEncounter.cpp:225`): after `++Generation`, call `URPGIFrameMonitor::OnEncounterReset` on the first player pawn, and `URPGDamageResolver::OnGenerationChanged` on the owner (clears the duplicate set).

### 4.5 Hit reaction and guard through the pack: feasibility
Verdict: feasible in principle by reflection, not proven; two routes; a probe step decides. If the probe fails, keep the direct write and record "no hit reaction for boss moves" (KI-065, KI-067, KI-068 stay open).
- Route A (call the ability): find the player's `GA_HitStun_C` instance with `RPGPack::FindAbilityByClassName(Player, "GA_HitStun_C")` (name to be confirmed with `DumpPlayerAbilities`), build a `BP_HitData_C` object with `NewObject` from the class loaded by path `/Game/AdvancedARPGCombat/AdvancedCombatFramework/CollisionSystem/Objects/BP_HitData.BP_HitData_C`, fill Instigator, DamageCauser, HitResult (location), HitAngle, HitFromDirection, Damage, ImpactDecisionTag, AttackData (load `MeleeKnockdownAttackData` for Knockdown, `DefaultMeleeAttackData` otherwise; a null `AttackData` makes the getters access None), call `Set Hit Data` on the ability, then `Try Activate Ability` on the ASC (`RPGBlueprintCall.h` already has `CallBlueprintFunction`). The base ability's poise gate (section 2.1 item 10) decides whether it plays; this mirrors the pack for the player.
- Route B (play the pack's cue): execute the damage taken gameplay cue on the player's ASC with the hit data as source object. The pack's own filter then suppresses it for `Status.Dead` or `Status.Invulnerable` (a second layer), and the camera shake is included. Needs the cue tag (not read) and the cue parameter layout.
- Both routes are called only after a `Resolve` accepted the hit, so D14 holds by construction for the reaction.
- Guard: reading `Status.Blocking` and the hit angle (pack uses -65 to 65 degrees) is cheap. Reproducing the pack's blocked formula (stability, reduction) is not planned; step S10 uses the documented approximation: HP x (1 - reduction/100), stamina minus `GuardStaminaDamage`, once. Off by default (Q3).
- Probe (step S9, no gameplay change): `Scripts/Editor/pie_probe_hit_react.py` calls a non-shipping `URPGDamageResolver::ProbeHitReaction()` that tries route A on the player at full poise and at zero poise. Accept only if: a `HitReact_*` or knockdown montage plays within 3 frames, `Character.State.Hit.Stun` clears when it ends, 0 "Blueprint Runtime Error" lines in `Saved/Logs/OneBossFight.log`, and the pack's own `Status.Invulnerable` player is never reacted (resolver rejects first).

### 4.6 What is NOT changed
- No pack asset (`ANS_iFrames`, montages, `BP_TraceTarget`, `BP_DamageExecution`, `GA_Player_Dodge`, hit stun abilities) is edited or recreated.
- The pack's trace-level rejection for A1, A2 stand-in and A3 stays (deviation from Freeze 416, 488; DECISIONS entry in step S12).
- `URPGDodgeTiming` input logic, window, clips and rates stay. Only if DC-1 is confirmed, one call is added after the forced activation in `ForceFullRoll`, or the monitor repair is switched on.
- A4, A5, A6 damage numbers (20, 12, 48), geometry, timings and counters stay.
- The boss posture, stagger, riposte, phase systems stay.

## 5. Edge cases and failure modes
- Interruption of the boss move (stagger, phase change, death, reset): the move component stops calling `Resolve` (existing `End(...)` paths: `RPGBossLowSweep.cpp:145-158`, `RPGBossJavelin.cpp:106-114`, `RPGBossShockwave.cpp:132-146`). A late call is rejected by the generation or attacker-dead check in `Resolve`. Open overlap episodes close at the next generation.
- Interruption of the dodge (stagger, attack, hit): the engine ends the notify state of the stopped montage instance (`AnimInstance.cpp:2088-2140`); the monitor records `Interrupted` and clears a montage-owned tag that outlives it by more than 0.10 s.
- Player death: `Resolve` rejects `RejectedDead` after the first lethal hit (FR-9); the monitor clears a montage-owned tag on death; a respawn creates a new pawn with a new tag container and a new monitor.
- Same-frame double contact (blade and wave, javelin and wave): the first accepted hit lowers health; the second `Resolve` sees health and either hits again (different `MoveId`, legal) or is a duplicate (same key). A6 keeps its central priority check.
- Reset and generation: payload generation is compared at resolution; stale means no damage, an audit entry, no counters of the move. The duplicate set clears on generation change. Resetting twice is safe: both calls are idempotent (Freeze 18.3, line 804).
- Phase transition: boss moves do not start during it (tracker veto, `RPGAttackTracker`); a javelin already in flight is a player-damaging projectile and is unaffected (existing behavior).
- Frame rate: the blade test covers the swept angle range, the wave band is 180 cm thick at 1000 cm/s (0.18 s), the javelin uses a swept sphere. The i-frame verdict at a boundary frame can differ by one frame between 30 and 120 FPS (a contact decided in the frame where the tag edge falls). This is intended ("result follows measured overlap", Freeze 1341); the audit keeps `PlayerMontagePosition` and `bMontageInWindow` to explain it. The D12 tolerance is one frame step.
- Time dilation (M3 hit stop and slow motion): windows are montage seconds and the monitor uses world time and montage position, so a dilation scales both consistently. Not tested here; M3 must re-run `pie_damage_path.py` group F once.
- Tick order: the boss component can tick before the player's mesh notify dispatch in the same frame, so the tag is as of the last dispatched notify (up to one frame stale in either direction). The resolver reads the tag at resolution, never a cached monitor value.
- PIE end: no statics in the new classes; fixed frame rate restored in `Deinitialize`; audit and records die with their components.
- Missing montage or ability: monitor finds no active montage, records `bMontageOwned = false`, never clears. Missing `Remove Owned Gameplay Tag` function logs once and counts a failed clear.
- Injected tags in tests are foreign by definition and are never removed by the monitor.

## 6. PIE test plan

Driver: `Scripts/Editor/pie_damage_path.py`, log prefix `[Dmg]`, house style of `pie_a4_low_sweep.py`: `check(name, ok, detail)`, state machine in one slate post-tick callback with try and except, `finish()` unregisters the callback, calls `RPGInputTestUtils.set_fixed_frame_rate(0)` and ends PIE, last line `RESULT n/m passed`. Run `pie_debug_overlay.py` once after an editor start (warm-up PIE). Driver clock = `world.get_time_seconds()` differences (not the slate dt). Boss: `enc.wake()`, `enc.hold_for_test(True)` (frozen awake, as A4 and A5 drivers). Player placed with the existing `place(...)` helper; `dbg.debug_refill_player()` before each trial (stamina for the dodge cost).
Resumable: every group is a separate list entry; `GROUPS = [...]` can be restricted with a module constant `ONLY = {"F", "C"}` so a cut run is repeated per group. The driver logs `GROUP x done` lines and per trial raw numbers.

Pack-data cross-check numbers (from section 2.3): quick window 0.10718 to 0.48975, full 0.0001 to 0.69987 montage seconds. The driver also reads the expected window from the monitor record (`ExpectedStart`, `ExpectedEnd`, computed from the montage asset in C++) and checks it equals these constants within 0.001 (pack update guard).

| Id | Freeze | Setup | Trials | Expected (numeric) |
|---|---|---|---|---|
| T0 | - | Components present: `RPGDamageResolver` on the boss, `RPGIFrameMonitor` on the player, `RPGAttackTracker`; fixed frame rate reads 0 at start (previous run restored it) | 1 | 4 checks true |
| F0 | - | For each fps in 30, 60, 120: `set_fixed_frame_rate(fps)`, sample 60 frames | 3 | mean dt within 2 percent of 1/fps, spread under 10 percent |
| FQ30, FQ60, FQ120 | D12 | One tap of the dodge key (press 0.08 s) at fixed fps; read the newest record after the montage ended; player teleported back each trial | 20 each (60) | Exactly 1 record per trial; montage `Dodge_Small_Forward_Roll_Montage`; rate 1.30 +- 0.01; `StartPosition - 0.10718` in [-0.002, step+0.004]; `EndPosition - 0.48975` in [-0.002, step+0.004]; `(EndTime-StartTime) x rate` equals `EndPosition-StartPosition` within step+0.004. `step` = (1/fps) x 1.3 = 0.0433, 0.0217, 0.0108 |
| FF30, FF60, FF120 | D12 | Double tap gap 0.25 s press to press (full roll chosen, no quick running, DECISIONS "Gap 0.25 s: full at 0.27 s") | 20 each (60) | Exactly 1 record; montage `Dodge_To_Idle_Montage`; rate 1.00 +- 0.01; start in [0.0001-0.002, 0.0001+step+0.004]; end `0.69987` within [-0.002, step+0.004]; step = 0.0333, 0.0167, 0.0083. A trial whose chain is not [full] is repeated, count logged (as `pie_dodge_trials.py` does for dropped presses) |
| FX | D12 | Informational: press to dodge start latency (seconds) per fps | all F trials | Logged only (expected about 0.2 s) |
| E1, E2 | D12, D13 | 60 fps, double tap gap 0.14 s (E1) and 0.18 s (E2); classify the chain by records | 10 each | Trials with chain [quick, full]: `GetUnexpectedDropCount` delta 0 during the full window; full record end within [-0.002, step+0.004] of 0.69987. If any trial drops: DC-1 confirmed, FAIL until the repair of 4.2 is on; then expected 0 drops and reassert count 1 per forced trial. Chain [full] only: counted as "no forced roll", at least 5 of 20 overall must be forced, else vary the gap and log |
| C1q, C1f | D13 | 60 fps; quick (C1q) and full (C1f) dodge; when the record is open and position >= 0.25 (C1q) or 0.30 (C1f) call `montage_stop(0.0)` on the player's anim instance | 10 each | Tag false within 3 frames; record closed with reason Interrupted; `GetStaleClearedCount` delta 0 (the engine delivered the end); next dodge in the same trial still produces a normal record |
| C2 | D13 | 60 fps; full roll; at position >= 0.30 `debug_set_player_health(0)`; wait for the real respawn (pattern of `pie_player_death_reset.py`) | 3 | Tag false within 30 frames of the death; after respawn new pawn, tag false, monitor record count 0, boss generation +1; no Blueprint runtime error lines |
| C3 | D13 | 60 fps; full roll; at position >= 0.30 `enc.reset_for_test()` | 5 | Tag false within 2 frames; record reason EncounterReset; `GetResetClearCount` +1; generation +1; resolver duplicate set cleared (a repeated key accepted again) |
| C4a | D13 | Monitor test hook `debug_force_owned_tag(True)` marks the tag montage-owned with no montage | 5 | Tag removed 0.10 s +- 2 frames after; stale cleared +1; one warning log line |
| C4b | D13 | Foreign tag: `AddOwnedGameplayTag(Status.Invulnerable)` for 1.0 s (as `pie_a5_heal_punish.py:335`) | 5 | Tag still true after 1.0 s; stale cleared +0; then removed by the driver |
| R1 | D14, H08 | Tag injected; `NoteOverlapForTest` then `ResolveForTest("T1", k, 10, "k", gen)` with a fresh instance k each trial | 20 | Outcome RejectedInvulnerable 20 of 20; health unchanged (equal to before, +-0.01); audit shows Overlap then RejectedInvulnerable per trial; Accepted +0; reaction requests +0; stamina unchanged |
| R2 | D15 | No tag | 20 | Accepted 20 of 20; health drops by 10.0 +- 0.01 each; HitReactionRequest count +0 (flag off) |
| R3 | H04, FR-10 | Same `(move, instance, key)` twice | 20 | First Accepted, second RejectedDuplicate; total drop 10.0 per trial |
| R3b | H05 | Same instance, different `HitKey` | 10 | Both Accepted; total drop 20.0 |
| R4 | FR-8 step 1 | After `enc.reset_for_test()`, resolve with the old generation, then the new one | 5 | Old: RejectedStale, health unchanged; new: Accepted |
| R5 | FR-8 step 1 | Health set to 0 | 5 | RejectedDead; health stays 0 (never negative) |
| R6 | FR-9 | Health 5, damage 10 | 5 | Accepted, `bLethal` true, health exactly 0, reaction requests +0; a second resolve RejectedDead |
| R8 | H10 | Payload HP 10, guard stamina 8, posture 5; not guarding | 5 | Only health changes (-10); stamina unchanged; posture unchanged; warning logged once |
| R7 | H09 | Added with step S10: flag `bResolveGuard` on, `Status.Blocking` injected, payload HP 10, guard stamina 8 | 10 | Outcome Blocked; stamina drops 8.0 exactly once; health drops 10 x (1 - reduction/100) +-0.01; flag off: full 10 and stamina unchanged |
| M1a | D14, H08 | A4: boss `start_move("A4")`, player 250 cm in front; tag on from 0.55 s to 1.00 s after the start (covers the contact, which the existing S6 puts near 0.74 s) | 10 | Health unchanged; blade `invulnerable` count +1; audit has Overlap >= 1 and RejectedInvulnerable >= 1 for move A4, Accepted 0 |
| M1b | D15 | A4 without tag (the existing S2) | 10 | Exactly one Accepted per sweep, health -20.0, `hits` +1 |
| M2a, M2b | D14, D15 | A5: P06 style (boss frozen, heal hook, tag on during the flight) and without tag | 10 each | With tag: javelin result Dodged +1, health unchanged, RejectedInvulnerable >= 1, Accepted 0. Without: hit +1, health -12.0, one Accepted |
| M3a, M3b | D14, D15 | A6: `wave.launch_for_test()`, player 700 cm; tag on while the band passes (from launch+0.3 s to +1.2 s); without tag | 10 each | With tag: `invulnerable` +1, health unchanged, no Accepted. Without: health -48.0, one Accepted |
| M4a, M4b | D14, D15, H08 | A2 stand-in through the pack trace (start as `pie_a2_scenarios.py`): tag on from 1.70 s to 2.40 s after the start; without tag | 10 each | With tag: health unchanged (+-0.01), player montage never named `HitReact*` during 1.0 s after the contact, `GA_HitStun_C` instance on the player not active (skipped with a logged note if the name is not found). Without: health -36.0 +-0.5 (A2-STAND data) |
| S1 | FR-6, FR-11 | After the groups | 1 | `GetAuditCount() > 0`; sum of per outcome counters equals the number of entries not Overlap; `build_lines()` contains one line starting `DAMAGE` and one starting `IFRAME` |

About 95 checks in all (printed as `RESULT n/m passed`). Trial counts follow Freeze 1331 (at least 20 per deterministic edge condition for D12; the other groups are 3 to 10 because their outcome has no random edge). Report wording: "N/N under fixed frame rate X, editor PIE, build Y" (Freeze 1241).

Regression drivers that must stay green after every step: `pie_a4_low_sweep.py` 14, `pie_a5_heal_punish.py` 31, `pie_leap_wave.py` 17, `pie_player_death_reset.py` 25, `pie_dodge_trials.py` (all pass), `pie_dodge.py`, `pie_close_attacks.py` 43, `pie_attack_rules.py` 13, `pie_phase_reset.py` 14, `pie_boss_hud.py` 29, `pie_victory_lock.py` 9, `pie_riposte.py`, plus the 6 existing automation tests and the 2 new ones.

New C++ automation tests in `Source/OneBossFight/Tests/RPGAutomationTests.cpp` (existing tests at `:76,104,137,201,306,429`):
- `OneBossFight.Combat.DamageResolver.Decide`: decision table over `FRPGTargetState` x payload (invulnerable, dead, stale, duplicate, lethal clamp, guard on and off, bypass flag), 40 cases, plus the audit ring (capacity 64, newest kept, overlap coalescing within 0.25 s).
- `OneBossFight.Combat.IFrameMonitor.Window`: pure helpers (boundary tolerance, window containment, clamp narrowing never widens).

## 7. Ordered implementation steps
Each step builds and leaves the old drivers green. After each step update row M2 of `MILESTONE_GATE2_CODE.md` ("Doing: step N").
1. S1 Single invulnerability implementation: `RPGBossShockwave.cpp` uses `RPGBossDamage::IsInvulnerable`, private copy deleted. Build, `pie_leap_wave.py` 17.
2. S2 `URPGInputTestUtils::SetFixedFrameRate` and `GetFixedFrameRate`, restore in `URPGPlayerMovesSubsystem::Deinitialize`. Build. Smoke: `set_fixed_frame_rate(30)`, sample, `0`, end PIE, start PIE again and read 0.
3. S3 `URPGIFrameMonitor` observation only (records, expected window from the montage, counters, source text, test hook `debug_force_owned_tag`), attached for the pack player. Build. Write `pie_damage_path.py` groups T0, F0, FQ, FF, FX. Run; write the measured numbers into `TEST_PLAN.md`; regression `pie_dodge_trials.py`.
4. S4 Monitor cleanup: watchdog for montage-owned tags, death clear, `OnEncounterReset` hook in `RPGBossEncounter.cpp`. Driver groups C1 to C4, E1, E2. If E1 or E2 show drops: turn on the DC-1 repair (`bReassertOnDrop`) and rerun until 0 unexpected drops. Regression `pie_player_death_reset.py` 25.
5. S5 `URPGDamageResolver` (types, `Decide`, `Resolve`, audit ring, counters, readers, test hooks), attached for the pack boss; no move uses it yet. Add the two automation tests. Build with tests (`Scripts/Rebuild.ps1 -Tests`). Driver groups R1 to R6, R8.
6. S6 Migrate A4 (`RPGBossLowSweep.cpp`). Run `pie_a4_low_sweep.py` 14 and group M1.
7. S7 Migrate A5 (`RPGBossJavelin.cpp/.h`, `RPGBossHealPunish.cpp`). Run `pie_a5_heal_punish.py` 31 and group M2.
8. S8 Migrate A6 (`RPGBossShockwave.cpp`), keep `bResolved` policy. Run `pie_leap_wave.py` 17 and group M3. Then group M4 (pack trace, no code change) and S1.
9. S9 Debug lines (`RPGCombatDebug.cpp`) for IFRAME and DAMAGE; `rpg.Debug 2` log. Look at one overlay screenshot (`Shot ShowUI`).
10. S10 Hit reaction probe (`ProbeHitReaction`, `pie_probe_hit_react.py`). Decide route A, B or none with the owner.
11. S11 If the probe passes: `bRequestHitReaction` and `bResolveGuard` wiring, payload `Reaction` and `GuardStaminaDamage` values per move (A4 Knockdown 28, A5 LightFlinch 10, A6 Knockdown 72; all UNVERIFIED), group R7, KI-065/067/068 updated. Default flags stay off until the owner agrees.
12. S12 Optional: `FRPGIFrameClamp` narrowing (only if the owner wants a shorter window than the pack's), with a driver group that repeats FQ and FF at 60 FPS with the clamp on.
13. S13 Docs (section 9). Full regression pass.

## 8. Risks and open questions
Risks:
- R-1 Montage-owned detection depends on reading `Montage->Notifies` and the class name `ANS_iFrames_C`. If the pack montages are replaced (the AAA animation pass) the cached window changes; the pack-data guard in the driver catches it.
- R-2 A second writer (DC-1 repair, clamp) fights the pack's notify state if both act on the same tag in one frame. Mitigation: repair and clamp only act on montage-owned tags and are off by default.
- R-3 `HasMatchingGameplayTag` through `ProcessEvent` each frame in the monitor and in each resolve: small cost; measure with the benchmark before shipping (PERF-01 target is 120 FPS).
- R-4 Fixed frame rate in editor PIE might not give exact `dt` (section 8 unverified item 8). The F0 check fails loudly instead of passing silently.
- R-5 Migration changes dead-player and stale behavior of A4 and A6 on purpose. Covered by `pie_player_death_reset.py` and `pie_leap_wave.py`.
- R-6 The pack's block formula is not reproduced; a Blocked outcome is an approximation and may feel different from the pack's guard.
- R-7 The pack rejects at the trace for pack moves; a swing whose contact outlasts the i-frames by one frame hits at that frame. That is the pack's behavior and the Freeze's rule 35.3, but it differs from a resolver that could "spend" the contact.

Open questions for the owner:
- Q1 Keep the pack's windows (quick 0.294 s real, full 0.700 s real) or narrow the full roll toward the Freeze test baseline of 26 to 28 frames at 60 FPS (0.43 to 0.47 s) with the clamp? Recommendation: keep, measure (step S3), then decide with real fights.
- Q2 A6 spends its only hit on an invulnerable contact (A4 and A5 do not). Unify to "a rejected contact never spends the hit" for A6 too? The result: a player whose i-frames end while the 180 cm band is still on them takes the hit.
- Q3 Should boss moves be blockable (guard) at all, and with which stamina numbers? Default off in this milestone.
- Q4 Hit reaction scope after the probe: which moves react (A4 Knockdown, A5 LightFlinch, A6 Knockdown per Freeze) and are they allowed to interrupt a roll recovery?
- Q5 Accept the deviation that pack weapon moves reject at the trace (no audit of the overlap)? An alternative is a shadow audit through `BP_CollisionComponent.OnHit` (delegate signature unread).
- Q6 DC-1 repair: monitor re-assert (second writer) or delay the forced roll?

UNVERIFIED claims (not proven by an engine run):
1. Default value of `GameplayTagsToIgnore` (strings only), of `DamageImmuneTags`, and which cue tag `GE_DamageBase` executes.
2. The wiring (links) of the nodes listed in section 2.1; only node titles, pin defaults and positions were read. `BP_BaseCombatCharacter` implementations of `HitHandle`, `OnDamageApplied`, `AddOwnedGameplayTag`, `RemoveOwnedGameplayTag` are in a collapsed graph and unreadable through the bridge.
3. Whether the tag container is counted (two overlapping iFrames states).
4. The offline parse of the two montages (section 2.3). The monitor's `ExpectedStart` and `ExpectedEnd` and the driver's pack-data check verify it at runtime.
5. Tick order between the player's mesh notify dispatch and the components; update-rate optimization on the player mesh (a lower anim update rate would quantize notify time).
6. DC-1 (forced roll loses i-frames).
7. The pack block formula (stability scaling) and the exact conditions of the hit stun ability for the player; the player's list of `Ability.HitReaction` abilities and the name `GA_HitStun_C` on the player.
8. That `bUseFixedFrameRate` gives an exact logical delta in editor PIE and that the Python slate delta equals it.
9. Guard stamina values 28, 10, 72 (scaled from the Freeze) against the player's stamina pool.
10. The A2 stand-in numbers used in M4 (36 health at about 2.0 s) come from `TEST_PLAN.md` A2-STAND and were not re-run today.

## 9. Docs to update
- `TASKS.md`: G1-5 row (Done list entry when finished, with the measured windows); G2-4 and G2-3 rows mention the resolver.
- `MILESTONE_GATE2_CODE.md`: row M2 status per step.
- `DELTA_AUDIT.md`: correct D-04 (quick dash has its own montage and window, measured numbers), D-05 (pack rejects at `Can Hit Actor?` through `GameplayTagsToIgnore {Status.Dead, Status.Invulnerable}`; our moves reject in the resolver), D-06 (cleanup tested); add ATK rows note that damage goes through the resolver; section 1 line 41 and 69 corrected.
- `DECISIONS.md`: single damage resolver for boss moves; rejected contact does not spend the hit (A6 exception until Q2); pack-trace deviation from Freeze 416 and 488; windows are pack-owned with an optional narrowing clamp; DC-1 decision; fixed frame rate test helper; hit reaction decision after the probe.
- `KNOWN_ISSUES.md`: KI-065, KI-067, KI-068 updated after the probe; new items for any unproven part (pack block formula, tick order); close nothing without a run.
- `TEST_PLAN.md`: rows D12 (per fps numbers), D13, D14, D15, H08 (and H09, H10 when built), the measured medians and maxima of the offsets, the fixed frame rate setup text; a line for the new automation tests.
- `PROJECT_STATE.md`: new classes, driver and the fixed frame rate command.
- `HANDOVER.md` section 4: the regression list gets `pie_damage_path.py`.

STATUS: COMPLETE
