# QUEUE_BJ_AG Batch 7 Audit (`BJ-A31..BJ-A35`): Target Validation, Leash/Nav, Weapon Trace & Sweep Sampling

**Scope:** Read-only offline C++ and test-source audit (`QUEUE_BJ_AG` Batch 7, `0` Unreal Editor / build / runtime / asset / commit operations). Conditional code observations follow Lead review guidance (`[X-1917]`): labeled as conditional edge cases or follow-up risks rather than confirmed runtime defects.

---

## Summary Table

| Task | Audited Files | Verdict |
|---|---|---|
| `BJ-A31` | [`RPGFrameworkBossCharacter.cpp`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L316-L465), [`RPGBossLeashRules.h`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossLeashRules.h#L9-L18), [`RPGFrameworkBossController.cpp`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Boss/RPGFrameworkBossController.cpp#L13-L80), [`RPGBossNavigationDiagnostics.h`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Boss/RPGBossNavigationDiagnostics.h#L9-L28), [`RPGBossApproachRules.h`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossApproachRules.h#L9-L36), [`RPGBossTrackRules.h`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossTrackRules.h#L18-L100) | Verified with 2 Low conditional notes |
| `BJ-A32` | [`RPGPackTrace.cpp`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Pack/RPGPackTrace.cpp#L15-L395), [`RPGTraceGuard.cpp`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGTraceGuard.cpp#L44-L272) | Verified with 2 Low conditional notes |
| `BJ-A33` | [`RPGFrameworkMoveExecutor.cpp`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L288-L386), [`RPGBossSweepSampling.h`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossSweepSampling.h#L10-L21) | Verified with 1 Low conditional note |
| `BJ-A34` | Nav/Approach/Leash/Trace/Sweep pure-rule vs live-geometry boundary across `RPGBossApproachTests.cpp`, `RPGBossTrackRulesSweepTests.cpp`, `RPGBossArenaLeashBoundaryTests.cpp`, `RPGBossLosLeashDeadlineTests.cpp`, `RPGBossLowSweepAdaptersTests.cpp`, `RPGFrameworkRuntimeTests.cpp` | Clear boundary documented |
| `BJ-A35` | `QUEUE_BJ_AG` Batch 7 findings synthesis & zero-edit closeout | 0 pure-rule defects; 5 conditional notes |

---

## `BJ-A31` — Target Faults, Arena Leash, Band-Walk & Navigation Diagnostics

### Verified Behavior
- **`TargetFault` (`RPGFrameworkBossCharacter.cpp:316-326`)**:
  - Fails closed with `Invalid` if `!TargetController.IsValid()` or `!Target.IsValid()`, with `Destroyed` if `Target->IsActorBeingDestroyed()`, and with `Invalid` if `Target->GetController() != TargetController.Get()`, `TargetController->GetPawn() != Target.Get()`, or `Target->GetWorld() != GetWorld()`.
  - Checks `RPGBossLeashRules::IsOutsideArena(Target->GetActorLocation(), ArenaOrigin, double(P->ArenaRadiusCm))` (`OffArena`). `IsOutsideArena` (`RPGBossLeashRules.h:9-18`) returns `true` on any non-finite coordinate or radius, disables leash for finite coordinates when `RadiusCm <= 0.`, and uses strict `>` on 2D distance so exact-radius positions remain inside.
  - Reads `Attribute.Health` (`Unreadable` if absent, `Dead` if `<= 0.`).
- **`HandleLeash` & Resume (`RPGFrameworkBossCharacter.cpp:413-434, 458-465`)**:
  - Only active when `Fault == OffArena && Dependencies->Profile->bArenaLeash` (`:458`).
  - On leash entry, aborts an active executor move with `ArenaLeash` (`:420-425`), clears `bStartedMove` and `bComboActive`, calls `StopOwnedWalk()` + `StopMovementImmediately()`, and issues `AI->MoveToLocation(ArenaOrigin, P.AcceptanceCm, false, true, true, false)`.
  - On target return (`bLeashed && bTargetOk` at `:459-465`), resets `StartedAt`, logs `arena_leash state=Resume`, and re-engages `WalkToBand`.
- **`WalkToBand` & `OnMoveCompleted` (`RPGFrameworkBossController.cpp:13-80`)**:
  - Rejects invalid owner/target/coincident planar vectors (`:16-20`), applies `RPGBossTrack::CenterBiasedAway` (`RPGBossTrackRules.h:26-44`) when `FromCenter >= CenterBiasStartFraction * ArenaRadiusCm`, projects goal onto navmesh (`ProjectPointToNavigation`), and requires non-partial full path (`!Path.IsValid() || Path->IsPartial()` -> `Framework.Nav.NoFullPath`).
  - Explicitly invalidates `OwnedRequest` before `MoveTo` (`:42`) and `StopMovement` (`:79`) so synchronous abort callbacks from previous requests are ignored, handles `AlreadyAtGoal` explicitly (`:49-54`), and formats `LastDiagnostic` via `RPGBossNavigationDiagnostics::Format` (`RPGBossNavigationDiagnostics.h:9-28`), returned by `GetNavigationResultForTest` (`RPGFrameworkBossCharacter.cpp:251`).
- **LOS Search Gate (`RPGFrameworkBossCharacter.cpp:586-600`, `RPGBossLosLeashDeadlineTests.cpp:20-29`)**:
  - When `P.LosSearchSeconds > 0`, losing LOS moves toward `Los.LastKnown`; regaining LOS calls `WalkToBand`. As documented in `RPGBossLosLeashDeadlineTests.cpp:20-23`, `TickLos` is skipped during leash and `FLosMemory::LostAt` stores absolute world time, so a post-leash hidden observation immediately fires `TimedOut` if elapsed time exceeded `LosSearchSeconds`.

### Conditional Edge Cases / Follow-Up Risks
1. **Low — `HandleLeash` center return bypasses nav projection / `OwnedRequest` tracking (`RPGFrameworkBossCharacter.cpp:427`)**:
   `HandleLeash` calls `AI->MoveToLocation(ArenaOrigin, P.AcceptanceCm, ...)` directly without projecting `ArenaOrigin` via `UNavigationSystemV1` or checking whether `MoveToLocation` succeeded; arrival relies on `WalkArrived` timeout (`WalkTimeoutSeconds` once resumed) or distance check `Dist2D <= AcceptanceCm + 30.` (`:429`). Conditional on arena origins where `ArenaOrigin` itself is off-navmesh.
2. **Low — `TrackRules::ReactionDelaySeconds` vs `StepYawLatched` caller assumptions (`RPGBossTrackRules.h:18-24, 52-65`)**:
   By inspection of `StepYawLatched`, if `MaxTurnDegPerSecond <= 0` or `DeltaSeconds <= 0`, clamped turn step is zero, keeping yaw fixed (`LatchedYaw`). Profile validators keep positive rates; conditional on non-positive overrides.

---

## `BJ-A32` — `RPGPackTrace` Reflection Facade & `RPGTraceGuard`

### Verified Behavior
- **Reflection Contract (`RPGPackTrace.cpp:39-64, 85-120, 370-395`)**:
  - `CollectMissing` verifies the exact union of pack Blueprint properties (`bCollisionEnabled?`, `HitActors`, `CollisionSockets`, `CollisionRadius`, `CollisionRadiusModifier`, `CollisionObjectTypes`, `Current Collision Mesh`, `ActorsToIgnore`, `TargetTypeTag`, `LastSocketLocations`, `TargetAbility`) and functions (`ClearHitActors`, `UpdateTraceLocations`, plus `DeactivateCollisionByTag` on `BP_CollisionComponent_C`) for both live (`CheckLiveNames`) and class (`CheckClassNames`) checks.
- **Visual Weapon Source & Trace Refresh (`RPGTraceGuard.cpp:44-134`, `RPGPackTrace.cpp:238-270`)**:
  - `RefreshVisualWeaponTraceSource` collects `Trace_<N>` sockets on the visual sword mesh, sorts numerically (`:112`), requires `>= 2` valid sockets, and calls `FTarget::SetTraceSource`, which immediately invokes Blueprint `UpdateTraceLocations` (`RPGPackTrace.cpp:269`) so `LastSocketLocations` cannot sweep from the hidden pack fallback mesh on first open.
- **Tick Order, Dedupe & Wall Occlusion (`RPGTraceGuard.cpp:162-271`)**:
  - Runs in `TG_PrePhysics` with explicit tick dependency `AddTickPrerequisiteComponent(AttackTracker, Mesh)` (`RPGBossTrackerTickPrerequisite::Add`).
  - Clears any previous frame's `TempSeed` (`:177-184`) before evaluating active state.
  - On open edge (`!bWasActive`), records `OpenRefreshError` vs stored `LastSocketLocations` and, when `bDedupePerInstance` and `Instance == LastWindowInstance`, re-seeds `LastSet` into `HitActors` so multi-window swings hit once per `AttackInstance`.
  - When `Health <= 0.0`, calls `CloseTraceNow("dead")` immediately; on `"reset"` reason (`:150-154`), clears both `HitActors` and `LastSet`.
  - When `bBlockThroughWalls` is active and line trace on `RPGBossDamage::WorldBlockers()` is blocked between boss and player, temporarily adds `Player` to `HitActors` via `TempSeed` for that pack sample only.

### Conditional Edge Cases / Follow-Up Risks
1. **Low — `RPGPackTrace::FTarget::GetStoredLocation` suffix match (`RPGPackTrace.cpp:308`)**:
   Matches `Key.ToString().EndsWith(Socket.ToString())` instead of exact suffix delimiter or equality. Conditional only if two tracked sockets have one name as a suffix of another (e.g., `Trace_1` vs `Aux_Trace_1`), where iteration order in `FScriptMapHelper` could return the longer key's stored location.
2. **Low — File-static `WarnedNames` across PIE sessions (`RPGPackTrace.cpp:17-27`)**:
   Once a missing reflection member logs once in an editor process, subsequent PIE sessions suppress the `LogRPGTrace` warning because `WarnedNames` is a static `TSet<FName>` never cleared on world teardown (`CheckLiveNames`/`CheckClassNames` still surface missing names explicitly).

---

## `BJ-A33` — Executor `SweepWindows` & Key-Pose Sampling

### Verified Behavior (`RPGFrameworkMoveExecutor.cpp:288-386`, `RPGBossSweepSampling.h:10-21`)
- **`SweepWindows` (`RPGFrameworkMoveExecutor.cpp:288-386`)**:
  - Checks `PrevAnimPosition`..`AnimPosition` overlap against move windows, evaluating direct hit windows (`Windows`) before `SecondaryWindows`, sharing hit-group dedupe within a swing (`Resolver->Resolve` + `HitGroup`).
  - Supports both ring sweeps (`bRing` via `RPGBossTrack::RingTouches`) and blade capsule/segment sweeps between key poses (`RPGBossSweep::BuildKeyPoses` switching between component-space baked samples `bBaked=true` and tick-interpolated world poses `bBaked=false`).
  - Enforces bounded spatial substeps (`HitStepCm`, `HitMaxSubsteps` cap) and initializes `FCollisionQueryParams` ignoring both `OwnerBoss` and `IgnoredPawns`.
- **`BuildKeyPoses` Contract (`RPGBossSweepSampling.h:13-20`)**:
  - Documented as returning `false` when the window and tick do not overlap, and returning at least two ordered poses for any overlapping interval (`start`, internal baked apex samples, `end`), preventing a long frame from skipping a thrust apex.

### Conditional Edge Case / Follow-Up Risk
1. **Low — `HitMaxSubsteps` clamp under extreme angular velocity / teleport (`RPGFrameworkMoveExecutor.cpp:288-386`)**:
   Bounding substeps by `HitMaxSubsteps` prevents runaway per-tick sweep cost, with the intentional engineering tradeoff that extreme frame hitches or large single-frame rotations beyond `HitMaxSubsteps * HitStepCm` coarsen swept spacing.

---

## `BJ-A34` — Test Boundaries: Pure Rules vs Live Geometry / PIE Gaps

- **Covered Offline / Pure-Rule Unit Tests**:
  - `RPGBossApproachTests.cpp` (`1-56`): tests pure approach math (`StepFraction`, `StepCm`, `PeakSpeedCm`).
  - `RPGBossTrackRulesSweepTests.cpp` (`1-55`): tests pure tracking/LOS/ring rules (`StepYawLatched`, `CenterBiasedAway`, `LosStep`, `RingTouches`).
  - `RPGBossArenaLeashBoundaryTests.cpp` (`1-52`): tests strict boundary equality, Z-invariance planar distance, non-finite fail-closed, and disabled `0` radius on `RPGBossLeashRules::IsOutsideArena`.
  - `RPGBossLosLeashDeadlineTests.cpp` (`8-32`): tests absolute `LostAt` world-time behavior across simulated leash skip.
  - `RPGFrameworkRuntimeTests.cpp` (`942-953`): tests `RPGBossNavigationDiagnostics::Format` string/hex flag formatting.
  - `RPGBossLowSweepAdaptersTests.cpp` (`18-22`): explicitly labeled source/config-only without world execution or live collision/damage proof.
- **Live-Only / Unverified Without PIE & Cooked Geometry**:
  - Actual `UNavigationSystemV1::ProjectPointToNavigation` / navmesh connectivity in `L_SevarogArena` (`WalkToBand`, `HandleLeash` return to `ArenaOrigin`).
  - Actual socket naming (`Trace_N`) and `UpdateTraceLocations` Blueprint execution on the pack `BP_CollisionComponent_C` / `BP_EnemyAbilitySweepingTraceTarget_C`.
  - Skeletal mesh bone transforms, baked apex fidelity in real weapon swings, `WorldBlockers()` pillar collision geometry for LOS/trace wall blocking, and `SweepWindows` overlap against live player capsules.

---

## `BJ-A35` — Batch 7 Disposition

- **Pure-rule / C++ source defects requiring offline fix:** `0`.
- **Conditional follow-up notes:** `5` Low/Informational notes (`HandleLeash` raw `MoveToLocation`, `StepYawLatched` non-positive rate assumption, `RPGPackTrace` `EndsWith` key lookup & static `WarnedNames`, `HitMaxSubsteps` coarse hitch bound), plus clear separation of live PIE/geometry dependencies per `BJ-A34`.
