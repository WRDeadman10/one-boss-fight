# 21 — Animation Production: Rig, Root Motion, Montages and Notifies

## Animator handoff standard

Every move must arrive with a `MoveCard`:

- Unique attack ID and move family.
- Source FBX/animation asset name and skeleton compatibility.
- Forward axis, root bone, export scale = Unreal centimeters, source FPS.
- Expected attack origin and capsule displacement in centimeters.
- Wind-up, hold, tracking lock, first/last active and recovery times.
- Weapon socket geometry and impact points.
- Root motion preference, Motion Warping window, target maximum warp distance.
- If paired grab: alignment and escape/release points.
- Distinct earliest release cue visible to player.
- Contact tests at 30 FPS, 60 FPS, 120 FPS.

## Authoring checkpoints

**Blockout:** rough body key poses, broad weapon path, true physical reach. **Combat pass:** lock timing, hit windows and recovery. **Polish pass:** shoulder/hips lead, weapon weight, follow-through and settle, anticipation hold. **Integration pass:** animation import, notify placement, root motion and socket path verification. **Release pass:** camera/readability and QA.

## Root rotation and alignment

An animation that contains root travel should not also have baked world offsets that cause unexpected start teleport. Test animation on an isolated Character in an empty map before hooking AI. Use consistent pelvis-root hierarchy. Fix axis issues in DCC/import pipeline rather than compensate with arbitrary boss rotation every Tick.

## Required montage markers

```text
[0.00] Start / MoveStarted
[0.08..0.48] TrackingAllowed / optional MotionWarping
[0.49] CommitLockFacing
[0.65..0.89] HitWindow / Sweep 01
[0.91] HitWindow close (Notify State End)
[0.96] ComboGate if available
[1.01] RecoveryBegin (if branch rejected)
[1.61] AttackComplete / Montage End
```

These are *example times only*; match actual animation frames. On interrupted montage, close hit state even if `AttackComplete` never fires.

## Weapon socket authoring

At least: `weapon_base`, `weapon_mid`, `weapon_tip` attached to the weapon's mesh/skeleton; sockets can live on a separate weapon mesh as long as owner retrieves correct component. Add `impact_reference` for slam and optional `grab_attach` for paired sequences. At attack start record world-space sample points and never assume static mesh weapon length without comparing contact trajectory.

## Animation quality tests

- Key silhouette distinguishable at telegraph time from 10m camera distance.
- The first actual contact matches authoring timestamps.
- Turning stops/limits as described after commitment.
- Root motion does not drift through arena walls or slide excessively.
- Weapon trail and actual trace geometry match.
- Montage sections blend without foot pop or phantom attack notifies.
- Interruption produces believable reaction and never leaves root-motion movement mode stuck.
- Guard/grab reactions align both characters without shoulder clipping that obscures hit shape.

## Retargeting external animation packs

Third-party animation packs may use different scale, skeleton proportions, root orientation and timing. Do not drop them into the attack data unmodified. Retarget, adjust reach, evaluate root movement, author new attack-hit windows, and re-measure punish timing. Animation visual quality alone does not make combat reliable.
