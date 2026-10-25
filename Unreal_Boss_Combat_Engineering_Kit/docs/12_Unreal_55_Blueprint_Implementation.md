# 12 — UE 5.5/5.5.4 Blueprint Implementation (Practical Editor Build Guide)

This guide builds a **functional vertical slice** with `QuickThrust`, `WideSweep`, `OverheadSlam`, then scales to all twelve moves. Names are prescribed so you can follow the documents exactly. The exact editor UI may differ between UE 5.5 and more recent documentation versions.

## A. Project setup

1. Start a **Games > Third Person** template in UE 5.5.4, Blueprint or C++ project. Set a known 60 FPS testing target.
2. Enable plugins: **AI Perception** is engine functionality; **Motion Warping** plugin; **Environment Query Editor** if you plan EQS; **Gameplay Debugger**, **Animation Insights** as needed. Only enable GAS if using the GAS branch.
3. Create collision presets: `BossBody`, `BossWeaponQuery` (Query Only, ignored by owner; overlaps/hits Pawn hit components), `BossAOEQuery`, and `PlayerHurtbox`. Verify profiles by drawing collisions in PIE.
4. Create `/Game/Bosses/AshenBellwarden/{Blueprints,AI,Data,Montages,Animations,Notifies,FX,Audio,Debug}`.
5. Prepare player combat Blueprint with `IsDodging`, `IsInvulnerable`, `IsHealingCommitted`, `IsAttackCommitted`, `IsBlocking`, health/stamina, and damage receiver function/interface. Avoid purely decorative booleans with no actual state transitions.

## B. Character and controller

6. Create `BP_Bellwarden` derived from `Character`; assign mesh, correct capsule, socket names `weapon_base`, `weapon_mid`, `weapon_tip`, and `AI Controller Class = BP_BellwardenController`. Set `Auto Possess AI` for placed/spawned use.
7. Add component BPs: `BPC_CombatAwareness`, `BPC_AttackDecision`, `BPC_AttackExecutor`, `BPC_WeaponTrace`, `BPC_Posture`, `BPC_Phase` (or equivalent functionality in C++).
8. Add `MotionWarping` component. In Character Movement, configure rotation so it cannot compete with authored montage facing. Test root motion movement before AI attacks.
9. Create `BP_BellwardenController` from `AIController`; add `AI Perception` with Sight. On Perception Updated, set `TargetActor` in `BB_Bellwarden`. Use `Run Behavior Tree` on BeginPlay / OnPossess after ensuring controller, pawn and BB initialize correctly.
10. Create `BB_Bellwarden` keys: `TargetActor` (Object/Actor), `HasLOS` (Bool), `DesiredMoveLocation` (Vector), `CombatMode` (Enum/Name), `ExecutorBusy` (Bool), `LastSeenPosition` (Vector).

## C. High-level Behavior Tree

11. Create `BT_Bellwarden`: Selector -> `Dead/Stagger/Phase` branch; `ExecutorBusy` branch (wait for completion); `Combat` branch. Combat branch: if target invalid -> Reset; else `BTT_SelectCombatAction` -> attack or positioning.
12. Create BT Task `BTT_SelectCombatAction`. Obtain actor `BPC_CombatAwareness.BuildSnapshot` -> `BPC_AttackDecision.ChooseMove`. If resulting `Attack`: call `BPC_AttackExecutor.TryStartAttack`, return succeeded if started. If resulting `Position`: write destination to BB and use `MoveTo` or shorter combat locomotion task. **Do not tick continuous attack choices during montage**.
13. Add service to refresh target/position cache every `0.1–0.2s`; final attack context recomputed at legal decision gate.

## D. Attack data assets

14. Create Blueprint `PDA_BossAttack` derived from `PrimaryDataAsset` (or `DataAsset`). Suggested fields: AttackTag/ID, Montage, RangeMin, RangeMax, IdealRange, AngleMin/Max, BaseWeight, Cooldown, ActiveWindowProfiles, Damage, PoiseDamage, TrackingConfig, AllowedPhases, ComboEdges, RecoveryClass.
15. Make `DA_QuickThrust`, `DA_WideSweep`, `DA_OverheadSlam` with values from the CSV. Add all to `DA_Bellwarden_Phase1` array.
16. Create Blueprint Function Library helpers: `GetSignedYawToTarget`, `IsAttackEligible`, `RangeFit`, `AngleFit`, `ComputeAttackScore`, `WeightedSelection`. Ensure no weight is NaN, no negative sum, and fallback when no candidate.

## E. Montage and Notify States

17. Create attack Montage `AM_QuickThrust`, `AM_WideSweep`, `AM_OverheadSlam` on the boss skeleton. Include root motion where appropriate.
18. On each montage, add notifies: `AN_Commit`, `ANS_AttackWindow` (specifies WindowId), `AN_ComboGate` (if supported), `AN_RecoveryBegin`, `AN_AttackFinished`. Add `ANS_TrackingAllowed` early; `ANS_HyperArmor` for only configured moves.
19. `BPC_AttackExecutor.TryStartAttack`: verify executor state Neutral, valid asset, correct controller state, cooldown; set **new** AttackInstanceID and selected attack; disable AI steering; start Montage; if Montage Play fails, rollback.
20. `AN_Commit` passes timing to executor, which sets rotation cap/target freeze. `ANS_AttackWindow` Begin/End enables/disables BPC_WeaponTrace; NotifyTick (or executor Tick during active) performs traces.
21. Use Montage Blend Out / End delegates to close windows and transition to recovery/neutral; interruption path is separate. Add watchdog fallback if expected notify fails. `AN_AttackFinished` alone must not be your only cleanup mechanism.

## F. Blueprint weapon tracing, exact node flow

22. On BeginWindow, sample socket transforms of `weapon_base`, `weapon_mid`, `weapon_tip`, store `PreviousSamples`; set `IsActive` and clear damaged actors according to HitPolicy.
23. Each Tick **only while active**: for each socket point and intermediate blade points -> `Sphere Trace Multi By Channel` from previous to current world position; `Actors to Ignore` includes Boss; accumulate unique candidate actors.
24. For each hit: validate player `BPI_Damageable`, ignore already hit if single-hit, check dodge i-frame, guard/parry, apply damage through `BPC_DamageResolver` or interface, update hit list. Spawn cosmetic contact FX.
25. Cache current weapon samples for next frame. When window closes or montage aborts, set inactive and clear trace state.
26. For AoE slam, use a **separate impact notify** that spawns a radial burst actor; ring waves update outward radius each frame and test the **swept annulus** from previous radius to current radius.

## G. First combo gate

27. Add a `AN_ComboGate` after Sweep active window. At gate, evaluate target proximity/angle and select only linked follow-ups, otherwise Montage transitions to authored recovery section.
28. Require `MaxComboDepth` and edge cooldown; do not use an unrestricted `Play Montage` call from every branch.
29. Add `AttackGraphDebug` output to screen/log showing chosen edge, distance, angle and rejecting conditions.

## H. Movement + warping

30. Create `EQS_BellwardenSpacing` (ring points, nav reachable, distance/visibility/wall clearance tests). Trigger only when choosing a move action; save chosen goal.
31. Add `ANS_MotionWarping` window on `AM_Lunge` and `AttackTarget` named warp target. Capture target transform only while tracking is allowed, then freeze it before commit; clamp large warp distances.
32. Implement strafe direction selection with low-frequency decisions, explicit cooldown and minimum commitment period (e.g. 0.5s).

## I. Defense and phase

33. Implement `BPC_Posture`: take poise damage, timer to recovery, `OnPostureBroken` -> executor interruption + stance break montage + critical vulnerability.
34. Implement boss damage reception and health. When health goes under threshold, queue phase transition; defer until executor neutral for first release.
35. On phase transition, change allowed attack assets/weights and play transition montage. Ensure active hitbox is closed before new state is entered.

## J. Debugging and first validation

36. Press PIE. Verify attack menu with `QuickThrust`, `WideSweep`, `OverheadSlam`. Force each attack using a debug key or console command to test independent of AI.
37. Draw enemy forward vector, target yaw, range bands, active trace path, warp point, last 5 decision scores, combo gate states.
38. Set 30 FPS cap, then 60, then 120. Confirm no skipped/duplicated damage; perform high-speed sword swing to expose tunneling.
39. Verify `Interrupted` Montage path leaves zero active windows, no movement stuck state, no target freeze leak.
40. Run tests from `tests/qa_scenarios.csv` before adding more animation assets.

## Common editor implementation traps

- Root motion ignored because AnimBP/root motion mode is incompatible with Montage setup.
- `Set Actor Rotation` on Tick fights movement component/controller and Motion Warping.
- `AnimNotifyState` can fire over blended montages; validate instance identity.
- Timelines using fixed seconds drift when Montage Play Rate changes.
- Querying the skeletal mesh overlap yields duplicate hits on different bones.
- Gameplay Tags must be actually exported/set by player action state to be observable.
- `AI MoveTo` and Montage compete for positional authority.

## Milestone: vertical slice definition of done

The boss chooses among three actions based on range/angle, exposes at least one conditional follow-up, stops turning at attack commitment, traces the actual blade for damage, has one fair punish, takes posture damage, can be killed, handles montage interruption, and shows debug decisions on screen.
