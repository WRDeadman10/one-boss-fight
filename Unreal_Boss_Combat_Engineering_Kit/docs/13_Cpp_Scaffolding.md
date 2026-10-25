# 13 — C++ Scaffolding: Types, Components, Interfaces, Ownership

`../code/` contains reference starting points. **These are implementation sketches / schemas; they have not been compiled against a local UE 5.5.4 editor**. Replace the placeholder `YOURGAME_API`, integrate modules/UPROPERTY settings, verify includes and gameplay code.

## Suggested source tree

```text
Source/YourGame/
  Boss/
    BossCharacter.h/.cpp
    BossAIController.h/.cpp
    BossCombatTypes.h
    BossAttackData.h/.cpp
    BossAttackDecisionComponent.h/.cpp
    BossAttackExecutorComponent.h/.cpp
    BossHitTraceComponent.h/.cpp
    BossPostureComponent.h/.cpp
    BossPhaseComponent.h/.cpp
    BossCombatDebugComponent.h/.cpp
    BossDamageReceiverInterface.h
    Notifies/
      AN_BossAttackCommit.h/.cpp
      ANS_BossHitWindow.h/.cpp
      AN_BossComboGate.h/.cpp
```

## Build.cs proposed modules

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core", "CoreUObject", "Engine", "InputCore", "AIModule",
    "GameplayTasks", "NavigationSystem", "GameplayTags",
    "AnimGraphRuntime", "MotionWarping"
});
// Only if GAS is used: GameplayAbilities, GameplayTags, GameplayTasks.
```

Ensure UE 5.5 project's plugin configuration includes MotionWarping if referenced in C++.

## Types and responsibilities

**`FBossCombatContext`** snapshot generated once per decision gate. Timestamp, target weak ref, distance, signed yaw, line of sight, player observable activity tag, boss phase, repeated action memory, posture. Never cache raw target pointers indefinitely without validation.

**`UBossAttackData`** designer-owned asset. Field lists in `code/BossAttackData.h`, `data/attack_catalogue.csv`; references to montage, windows, hit spec, steering, cooldown, prerequisites and branches.

**`UBossAttackDecisionComponent`** provides `SelectAttack(Context, AttackSet, Seed, OutDebugTrace)` using an eligibility pass then utility scoring; never triggers animation directly.

**`UBossAttackExecutorComponent`** is state machine and event endpoint. `TryStart`, `Commit`, `BeginHitWindow`, `OnComboGate`, `EndHitWindow`, `Interrupt`, `Finalize`. Owns `InstanceId`, `CurrentAttack`, authoritative state, cooldown commits and timeout.

**`UBossHitTraceComponent`** only traces while window active; keeps `PreviousBladeSamples`, `HitActors`, `WindowId` and hit policy. Never directly chooses attack.

## Attack decision pseudocode

```cpp
FBossDecision UBossAttackDecisionComponent::Choose(const FBossCombatContext& Ctx)
{
    TArray<FAttackCandidate> Candidates;
    for (const UBossAttackData* A : CurrentPhase->Attacks)
    {
        FText RejectReason;
        if (!PassesHardGates(A, Ctx, RejectReason)) { LogReject(A, RejectReason); continue; }
        float Score = EvaluateUtility(A, Ctx) - GetRepeatPenalty(A);
        Candidates.Add({A, Score});
    }
    if (Candidates.IsEmpty()) return FBossDecision::Reposition();
    SortByScore(Candidates);
    return SampleNearBest(Candidates, Seed, /*temperature*/ 0.18f);
}
```

## Executor event and watchdog pseudocode

```text
TryStartAttack(A):
    if State != Neutral or A null: false
    InstanceID++; CurrentAttack=A; State=Windup
    Freeze/commit movement ownership
    If !PlayMontage(A->Montage): Abort(PlayFailed); false
    ArmWatchdog(A->MaxDuration + margin); true
OnAttackCommit(instance):
    if wrong ID or wrong state: return
    State=Committed; cache target aim transform; set turn cap
OnHitWindowBegin(instance,window):
    validate instance && window is legal; hitTrace.Begin(instance,window)
OnHitWindowEnd(instance,window):
    hitTrace.End(instance,window)
OnComboGate(instance,gate):
    validate, choose linked edge ONCE using fresh context
    transition only if montage/section supports it
OnInterrupted(reason):
    close all windows; cancel warping/latent tasks
    reset movement authority; transition to proper reaction
OnMontageEnded(interrupted):
    ensure cleanup; apply recovery policy or neutral
```

## Collision pseudocode and safe pointers

`UWorld::SweepMultiByChannel` does socket-path queries. Handle `TWeakObjectPtr<AActor>`, mesh invalidation, actors destroyed midtrace, skip `PendingKill`/dead targets, account for server authority if net enabled, and use strong temporary references only during resolution. `TSet` membership is per attack instance or window as configured.

## Gameplay Tags taxonomy example

```text
Boss.State.Neutral
Boss.State.Windup
Boss.State.Committed
Boss.State.Recovering
Boss.State.Staggered
Boss.State.PhaseTransition
Boss.Attack.Thrust / Sweep / Slam / AOE / Grab
Boss.Window.HitActive / CanTrack / HasHyperarmor / CanCombo
Player.Action.HealingCommitted / CastingCommitted / Rolling / Guarding
Damage.Type.Physical / Fire / Shockwave / Grab
```

**Do not introduce GAS solely to gain GameplayTags**; GameplayTags can be used outside GAS. If using ASC/attributes already, integrate attack abilities and GameplayEffects consistently and maintain executor ownership of timing.

## Threading and determinism

Gameplay state, movement and animation operations should remain on Unreal's game thread. Heavy offline analysis may be background work, but never access `UObject`s from raw worker threads without appropriate engine coordination. For debugging use deterministic RNG per encounter/decision (do not reseed every Tick); store seed and attack trace. Consistency across FPS still requires animation/event testing.

## Interfaces

`IBossDamageable` or `BPI_Damageable` should receive a single `FResolvedAttackHit`, never a dozen bespoke parameters from every attack Blueprint. `IBossCombatObservable` exposes committed player action state, guard, iframe and recovery information. `IBossAttackEventSink` routes montage notify events into the executor.

## Do not create these architectural mistakes

- No per-attack Blueprint deals health damage directly via raw overlap while another component also traces.
- No parallel BT + StateTree both authorizing `PlayMontage`.
- No hidden direct player-health check inside hit trace to choose combo.
- No unbounded timer loops or stale callbacks referencing destroyed boss.
- No action-state replication assumptions in a single-player prototype.
