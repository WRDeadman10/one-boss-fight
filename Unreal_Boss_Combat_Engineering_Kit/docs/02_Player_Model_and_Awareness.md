# 02 — Player Awareness, Context, and Action Reactions

## A boss needs a model of the player, not psychic access

Observation should come from **game-world state**: visible location, velocity, facing, current committed attack montage, healing animation, guard state, dodge state, collision response, last-known position. Do not consult future inputs or choose a perfect counter before the player has made an observable commitment.

## Minimum `FCombatContext`

| Field | How obtained | Use |
|---|---|---|
| `TargetActor` | Perception + current threat target | Evaluate validity |
| `DistanceCm` | XY center-to-center or attack origin-to-target | Range gates |
| `SignedYawDeg` | Actor forward vs planar target direction | Front/side/rear gates |
| `HasLineOfSight` | Perception + trace as needed | React to casts, target |
| `TargetVelocity` | Movement component, smoothed | Leading/projectile choice |
| `TargetActivity` | Publicly observable action tags | Heal/cast/attack punish |
| `TargetRecoveryRemaining` | Current animation state if known | Opportunistic attack |
| `TargetGuardState` | Character state | Guard-break choices |
| `TargetDodge` | Dodge montage / dodge state | Readability, don't auto-counter every roll |
| `BossHealthFraction` | Combat stats | Phase gates |
| `BossPostureFraction` | Posture component | Risk/defensive score |
| `TimeSinceLastAttack` | Executor | Pace/cooldown |
| `AttackHistory` | Circular last N IDs | Repeat penalty |
| `CurrentPhase` | Phase component | Allowed moves |
| `ArenaSafeZones` | Navmesh & arena actor | Avoid hazards/walls |

### Computing angle (planar)

```cpp
FVector ToTarget = TargetLocation - BossLocation;
ToTarget.Z = 0.0;
ToTarget.Normalize();
const FVector Forward = BossForward.GetSafeNormal2D();
const float Dot = FVector::DotProduct(Forward, ToTarget);
const float CrossZ = FVector::CrossProduct(Forward, ToTarget).Z;
const float SignedYawDeg = FMath::RadiansToDegrees(FMath::Atan2(CrossZ, Dot));
```

Angles are world-relative to **boss facing**, not camera position. E.g. front = abs(yaw) ≤ 55°, side = 55–135°, rear = >135°. Include hysteresis to prevent jitter at boundaries.

## Distances and collision size

For huge enemies, center-to-center distance is misleading. Choose one convention per attack: XY capsule surface gap, nearest weapon reach point, or root-to-root center distance, and label it. `DistanceCm=250` uses **Unreal centimeters**. Character scaling affects entire move catalog; rebake or normalize reach if the mesh scale changes.

## How to model player actions safely

Use a `EPlayerCombatActivity` state exposed by the player combat component: `Idle, Moving, AttackingWindup, AttackingActive, AttackingRecovery, HealingCommitted, CastingCommitted, Dodging, Blocking, Staggered`. Mark transitions using the player's montage notifies or ability state. The boss should **only** react after a committed observable start event plus a reaction delay; in-world sight/awareness still required.

**Heal punish gating example:** healing committed; line of sight; player 300–850cm away; boss neutral; reaction ready; attack cooldown ready; probability or score threshold passed; projected travel time shorter than heal recovery; selected attack animation has real travel. If any condition fails, do not force counter.

## Memory and uncertainty

Use last-seen transform, last-seen timestamp, observed repeated patterns, and a short memory horizon to allow believable searching without perfect awareness. If target teleports or becomes invisible, reacquire instead of tracking hidden location. Player pattern counters should be *soft preferences*, not guaranteed hard counters.

Example history features: `BackRollRateLast8s`, `HealAttemptsLast30s`, `TimeNearRearArc`, `GuardHoldDuration`. Smooth with decay and cap their contribution. Avoid permanent punishment for one mistake.

## Target validity and robustness

Before each new decision: check valid actor, not dead, reachable range, arena membership, max vertical delta, not same owner; handle target destroyed mid-swing. Use original attack aim snapshot after commitment rather than `GetPlayerCharacter` every trace frame. The hit resolver can still collide with any valid victim in the active trace.

## Perception setup in UE

1. Add AI Perception to `BP_BossAIController`; configure Sight and optional Damage. Register player stimuli if needed.
2. On Target Perception Updated: update target candidate/last seen and timestamps; no direct montage play.
3. Drive `BB_TargetActor`, `BB_HasLOS`, and `BB_LastSeenLocation`.
4. Context component queries current actor movement and exported combat action state only at decision gates.
5. Use a custom `BPI_CombatObservable` interface to decouple AI from player implementation.
6. Record false-positive perception and occlusion cases in telemetry.

## Testing

- Player stands front/side/back at 1m, 3m, 6m: correct region labels and hysteresis.
- Player starts heal *after* boss commits: no retroactive attack swapping.
- Player breaks line-of-sight: boss does not choose ranged precision punish.
- Player dodges across front/rear threshold: no rapid oscillation between reactions.
- Target dies during wind-up: finish committed motion safely or move to recover/defeat state per design.
