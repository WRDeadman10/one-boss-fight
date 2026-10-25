# 06 — Animation, Rotation Limits, Root Motion, Motion Warping

![Tracking phases](../diagrams/07_tracking_and_commit.png)

## Authoritative motion sources

- **Neutral locomotion:** `CharacterMovementComponent` and turn-in-place/strafe animation BlendSpace.
- **Committed melee attacks:** prefer authored root motion for directional travel and body mass, with carefully bounded movement if required.
- **Special gap closers:** root-motion montage + **Motion Warping** in a specific early window only; clamp displacement and rotation.
- **Reaction and stagger:** montage or animation state with explicit movement/cancel policy.

**Avoid simultaneously** calling `AI MoveTo`, setting actor location, rotating on Tick, and playing a root-motion attack. Movement authority should switch cleanly by state.

## Rotation tracking profile per move

| Stage | Proposed rule |
|---|---|
| Neutral | Aim at target at up to movement-defined max turn speed |
| Early wind-up | Up to 120–220°/s for a tracked attack |
| Late wind-up | Up to 10–35°/s depending on heaviness |
| Active | 0–15°/s, often zero for fully committed slash |
| Recovery | No arbitrary snap; turn-in-place after unlock |

These are **design parameters**, not engine defaults. Use `DeltaYawClamped = Clamp(DeltaYaw, -MaxDegreesPerSecond * DeltaSeconds, +...)` applied through the authoritative movement controller. Do not call `FindLookAtRotation → SetActorRotation` unconditionally each Tick while an attacking montage plays.

## Motion Warping: when and when not

Motion Warping can modify root motion to align to a named target during a Notify State window. UE's Motion Warping plugin provides Skew Warp and Scale strategies. Use it for controlled lunges/steps; stop warping at the commitment boundary. Never refresh warp target every frame across a fully committed active attack if that erases dodging skill.

### Practical recipe

1. Enable **Motion Warping** plugin, restart UE if requested.
2. Add Motion Warping component to boss Character.
3. Confirm animation has meaningful root-bone motion and Root Motion enabled.
4. Create `AM_Lunge` Montage, add Motion Warping Notify State from time `0.10–0.48s`, target name `AttackTarget`.
5. On move start sample desired target transform within the legal warp radius; call **Add or Update Warp Target** once or at specifically authorized early gate.
6. After `TrackingLock` event, freeze target update or let warping window end before active damage.
7. Test target strafing perpendicular, dodging behind, moving onto stairs, and being outside navmesh; cap warp translation and vertical displacement.

## Montage authoring

For each attack create tracks:

- `Timing`: `AN_AttackCommit`, `ANS_TrackingWindow`, `ANS_AttackActive`, `AN_ComboGate`, `AN_RecoveryBegin`, `AN_AttackComplete`.
- `Motion`: optional `ANS_MotionWarping`, root motion configuration, movement/rotation constraints.
- `Feedback`: audio preparation cue, weapon whoosh, impact cue, Niagara ground or weapon FX, camera impulse (local player only).
- `Gameplay`: posture armor start/end, i-frame if specifically intended, grab attachment window.

Use montage sections such as `Start`, `Hold`, `Release`, `ComboB`, `Recover` with explicit Next Section behavior. `Montage_SetNextSection` only makes sense when the current montage/section authoring supports it. Don't assume every blend or interruption will preserve notifies.

## Animation Blueprint design

- `Locomotion State Machine`: Idle, Walk, Run, Strafe, Turn, Stagger, Death.
- `Slot 'DefaultGroup.CombatFullBody'`: full-body attack Montages with carefully configured blend-in/out.
- Layered blend per bone only for actions explicitly designed as upper-body attacks; massive full-body polearm sweeps should not independently play strafing lower body.
- `DistanceMatching`/`StrideWarping` optional polish, not prerequisites.
- Control-rig IK/foot placement allowed during movement but turn off or reduce weight on violent airborne frames to avoid fighting root motion.

## Synchronizing hitboxes

Use `UAnimNotifyState` begin/end to open/close a **named hit window**. Each frame while open perform weapon socket sweeps between previous and current locations. If montage skips frames or ends abnormally, executor must close the window on interruption. Track unique attack ID to prevent stale notifies from old montages enabling damage.

## Animation production requirements

Require the animator to provide: root-bone axis and forward direction convention, contact times, target facing lock time, capsule displacement, release cue, weapon socket paths, grab alignment, recovery lock, cancel authorization, loop/section boundaries, phase variant, and optional camera-readable silhouette poses. See doc 21 for asset workflow.

## Edge case tests

- 30 FPS; montage timescale altered; heavy swing still hits once.
- Player crosses behind during commit; boss does **not** rotate 180° instantly.
- Warp target moves off ledge; attack uses bounded fallback or declines start.
- Montage interrupted during active trace; no phantom collision remains.
- `AnimBP` blend-out doesn't fire expected end event; watchdog repairs state.
