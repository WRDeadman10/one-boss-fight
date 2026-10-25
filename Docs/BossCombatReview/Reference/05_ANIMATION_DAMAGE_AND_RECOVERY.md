# Animation, Damage and Recovery

## The timing contract

```text
Anticipation -> optional bounded hold -> commit/track lock -> active contact
             -> follow-through -> recovery lock -> neutral
```

The montage timeline is the authoritative clock. Data fields describe expected timing, but independent delays must not duplicate active, commit or recovery events because play-rate changes, blends and hitstop would make them drift.

The illustrative A03 diagram uses anticipation `0.00-0.70 s`, hold `0.70-0.98 s`, active `0.98-1.17 s`, recovery `1.17-2.15 s`; tracking begins to lock before first possible contact. These values explain the contract only and are not a universal target.

## Telegraph and commitment

An attack communicates family through early silhouette, geometry through shoulders/weapon/step, release through acceleration/audio/VFX, danger through the visible active path and safety through follow-through. A delayed attack is fair when its hold is fixed or chosen from bounded variants before commitment and the release cue is stable.

Each move carries a turn profile. Early wind-up may track strongly, late wind-up is restricted, active damage is usually locked and recovery cannot snap. The exact limits are design data. Commitment converts a live target into a captured aim/warp target; the damage resolver can still hit any valid actor physically intersected by the attack.

## Motion and montage ownership

- Character Movement/AI navigation owns neutral travel.
- Root motion owns committed attack displacement when authored.
- Motion Warping is allowed only in a bounded named window with translation/rotation/vertical caps and a valid destination.
- AI `MoveTo`, per-tick rotation, manual teleport and root motion must not operate as peers.
- Full-body heavy attacks should use an appropriate montage slot; layered lower-body locomotion must not visually or physically contradict them.
- IK/stride warping is reduced where it would fight airborne or violent root motion.

Required montage markers include move start, tracking window, commit, active window(s), combo gate, recovery begin, armor window and completion. Notifies report events to the executor. They are rejected when the instance, montage, section or expected state does not match.

## Animation-to-collision synchronization

At hit-window begin, the trace system records current weapon sample positions and clears the correct per-instance/window victim set. Each animation update sweeps several blade points from previous to current transforms, adding adaptive substeps when travel or angular change is too large. At end, interrupt or watchdog abort, it closes the window before any new attack can start.

Different geometry requires different synchronization:

| Geometry | Animation/collision relation |
|---|---|
| Thrust | Tip path and narrow radius follow the physical point; forward reach alone is not a cone. |
| Sweep | Base/mid/tip and interior samples cover a rotating blade; victim contact time varies around the arc. |
| Slam | Direct blade/weapon contact is distinct from the impact-centered splash. |
| Radial ring | Release notify starts an outward annulus; previous-to-current radius is swept to avoid tunneling. |
| Lane/persistent area | Spawn/release follows the pose; lifetime and tick cadence are independent explicit states. |
| Grab | Capture overlap triggers defense eligibility and paired alignment before control/attachment changes. |

At 60 FPS one frame is roughly 16.67 ms; short active spans cannot rely on a single overlap. Tests at 30 FPS, higher play rates and hitstop prove continuity.

## Central damage adjudication

The collision query reports contact; it does not directly subtract health. The resolver processes:

1. Valid victim/team and live attack instance/window.
2. Per-policy duplicate rejection.
3. Dodge/invulnerability.
4. Parry/deflect eligibility.
5. Guard/block and mitigation.
6. Armor/posture consequences.
7. Health/elemental damage.
8. Stagger/knockback.
9. VFX/SFX/camera/telemetry for the resolved result.

Direct impact and splash precedence must prevent accidental double damage. Periodic areas have explicit intervals and caps. A wave damages once when its moving band passes, not continuously because the player remains inside the final radius. A low wave's jump rule uses world-space character/ground state, not screen height.

## Multi-stage and multi-hit behavior

Every stage has a unique attack/window identity and its own hit policy. `OncePerAttack` shares a victim set across the move; `OncePerWindow` clears it only at the next legal stage; `Periodic` records victim cooldown/count. A combo follow-up normally receives a new attack instance while sharing a combo ID for analytics. Multiple physical hit bodies on one actor never become multiple logical victims.

## Interruption, hyperarmor and cleanup

Hyperarmor is a temporary interruption rule carried by an explicit window. It may allow health/posture damage while suppressing a flinch; the posture-break interaction must be stated. On an allowed interruption, `AbortAttack` closes traces, invalidates gates/callbacks, stops warping, clears armor, resolves montage transition, restores movement ownership and records the cause.

Cleanup is triggered on normal completion, montage blend-out/end, stagger, parry, death, authorized phase transition, target/arena reset, teleport, actor/mesh destruction and watchdog timeout. It is idempotent because more than one callback may arrive.

## Recovery and punish design

`RecoveryMinimumLock` is a gameplay commitment separate from the remaining cinematic animation. The usable opening is:

`boss guaranteed lock - player travel time - player attack startup - safety buffer`.

This must be calculated for several player builds and response positions. High-commitment/high-damage moves need meaningful guaranteed openings. Conditional recoveries are acceptable only when a follow-up has an authored gate and readable cue. A whiff can create a spacing opening even when nominal recovery is short; a posture break creates a resource opening.

An advanced design records hit/whiff recovery separately only when animation and policy visibly support the distinction. It does not cancel every whiff into a fast counter or use recovery animation that looks inert while the executor is already free.

## Verification matrix

| Case | Required observation |
|---|---|
| Early versus post-commit sidestep | Early tracking can follow within cap; post-commit rotation remains within attack data. |
| 30/60/120 FPS | Same visible path produces one equivalent logical hit, no tunneling or duplicates. |
| Play rate 0.75/1.25 | Notifies, active path, recovery and cooldown time base remain coherent. |
| Hitstop/time dilation | Trace does not reapply damage during frozen samples; resume remains aligned. |
| Interrupt on first active frame | Trace closes immediately; movement/warp/armor/gates restore. |
| Blend-out without normal end notify | Executor cleanup/watchdog returns to a legal state. |
| Direct plus splash overlap | Precedence produces only the authored damage count. |
| Ring at low FPS | Swept annulus crosses the player once and never damages after passing. |
| Slow and fast player attacks | Punish classification matches measured travel/startup margins. |
| Wall/ledge/stairs | Warp/path stays legal or attack declines/falls back safely. |
| Grab interrupted by death/reset | Both actors detach, input restores and placement is valid. |
| VFX comparison frames | Before-active, first-contact and end-active visuals match collision state. |

## Animation production evidence

Each move needs a MoveCard: IDs/family, skeleton and asset, axes/root/scale/FPS, capsule displacement, wind-up/hold/commit/active/recovery frames, socket trajectory, release cue, root-motion/warp settings, cancel policy, branch markers, paired alignment if any, and 30/60/120 FPS contact checks. Third-party animations must be retargeted and re-measured; visual quality alone does not validate combat timing.
