# 07 — Hit Detection, Weapon Sweeps, Point Damage, AoE and Special Attacks

![Geometry profiles](../diagrams/06_hit_geometry.png)

## One centralized damage policy, many collision mechanisms

An attack **shape** determines where/when contact can occur; the damage resolver determines what contact means. Keep them separate. A hit should carry `{AttackID, InstanceID, WindowID, Victim, HitPoint, HitNormal, HitBone, Instigator, DamageType, StanceDamage, Timestamp}`.

### Six geometry families

1. **Thrust / point-target strike:** weapon-tip sphere or small capsule swept along its path; concentrated reach, minimal lateral coverage.
2. **Sweeping arc:** a blade defined by `WeaponBase/WeaponMid/WeaponTip` socket segments; sweep overlapping capsules/spheres through the frame interval; no instant giant wedge unless intentionally magical.
3. **Slam / localized impact:** direct weapon trace plus impact-centered sphere/capsule at ground contact; separately flag direct and splash zones.
4. **Radial expanding ring:** independently simulated expanding radius band `abs(distanceFromOrigin - CurrentRadius) <= RingWidth/2`; ensure active duration, LOS/height checks, and damage only once per wave.
5. **Beam / line hazard:** sphere/capsule trace or box along a forward lane, potentially repeating ticks at configured intervals if persistent.
6. **Grab:** dedicated capture collider and grab eligibility checks; transition attacker and victim to synchronized paired animation only after valid overlap, guard/iframe adjudication and robust warp alignment.

## Swept weapon sampling

At every animation update while the active window is open:

```text
PrevBase, PrevMid, PrevTip = cached world socket transforms
CurrBase, CurrMid, CurrTip = new world socket transforms
For each segment endpoint or several samples along blade:
    Sweep sphere from previous to current position
    Optionally additional sub-steps if angular change/translation > limits
    Collect hits, sort by collision time, resolve per-attack rules
Cache current transforms
```

**Important:** endpoint sweeps alone can miss an object when a long blade rotates in place! Sample multiple points *along the blade* or represent it using a series of swept capsules; adaptive temporal sub-steps help. Use collision channel `ECC_GameTraceChannel...` configured as e.g. `BossWeapon`. QueryOnly; ignore owner and allies. Debug-draw trajectories and actual contact points.

### Sweep pseudocode

```cpp
for (int32 SampleIndex = 0; SampleIndex < BladeSampleCount; ++SampleIndex)
{
    const FVector From = PreviousSamples[SampleIndex];
    const FVector To   = CurrentSamples[SampleIndex];
    TArray<FHitResult> Hits;
    World->SweepMultiByChannel(
        Hits, From, To, FQuat::Identity,
        BossWeaponTraceChannel,
        FCollisionShape::MakeSphere(TraceRadiusCm), QueryParams);
    for (const FHitResult& Hit : Hits)
        Resolver.TryResolveContact(ActiveAttackInstanceId, WindowId, Hit);
}
```

This is intentional **reference pseudocode**, not a drop-in compiled module. Configure correct collision response, world availability, and query params in real code.

## Multi-hit rules

Define `HitPolicy` on each attack:

- `OncePerAttack`: victim may be damaged once across all windows of a move.
- `OncePerWindow`: each window may damage target once (e.g. spin slash hit A, then hit B).
- `Periodic`: damaging zone ticks at `TickInterval`, with max number hits per victim and strict accumulation rules.
- `ImpactPlusExplosion`: direct-hit and AoE cannot double-dip unless authored; explicit precedence.

Maintain `TSet<TWeakObjectPtr<AActor>> HitActors` per instance/window as appropriate; reset **only** at legal new attack/window start. Distinguish damage for initial blade impact versus lingering ground fire.

## Priority of defense adjudication

Proposed ordering: valid target/target team → valid active attack ID/window → target invulnerable/dodge rules → parry/deflect if eligible → guard/block → armor/poise interaction → health/elemental damage → stagger/knockback → gameplay feedback. Keep the exact order documented and test it. Invulnerability should never merely hide damage numbers while posture still receives unintended hits.

## Damage volumes and falloff

**Direct hit:** 100% authored damage and defined posture damage. **Splash:** attenuation by planar/3D distance and cover tests; sample formula `Damage = Base * max(MinFraction, 1 - Pow(r/R, Exponent))`. **Persistent zone:** fixed time cadence and per-target cooldown. **Ring wave:** collision band at each timestep; use `previousRadius → currentRadius` span so fast expansion doesn't tunnel through player. **Ground wave:** decide jump dodge eligibility using player collision/grounded state; don't use screen-space height.

## Collision details to resolve early

- Boss mesh/capsule should not block its own attack queries.
- Multiple skeletal mesh hit bodies on player count as **one logical victim** for single-hit attacks.
- Query on `Actor` damage component and use first relevant component's hit result; don't apply damage once per skeletal body.
- Weapon impact with scenery can trigger sparks/audio independently of target damage, with throttling.
- Distinguish `hit registered` from `damage applied`; invulnerable roll counts contact but not health loss.
- If using `ApplyPointDamage` / `ApplyRadialDamage`, review the engine's parameter conventions, falloff, occlusion and damage receiver callbacks; custom resolver is often easier for special posture/guard behavior.
- Gravity/vertical attacks must include Z tolerance; a planar wedge must not damage a player on another floor.
- Do not rely on overlap event ordering under low frame rates for an extremely fast blade.

## Hit feedback

One attack can send multiple **cosmetic** messages: weapon trail begins, blade whoosh, local blood/sparks, camera impulse, force reaction, sound, hitstop. Health-changing damage occurs exactly once in the authoritative hit resolver. VFX timing should support readability, not mask the hit shape.

## Essential debug modes

1. Show weapon samples and swept paths (green no hit/red hit).
2. Show AoE center, current ring radius, lifetime and LOS blockers.
3. Overlay victim dodge/guard/iframes over the boss active interval.
4. Show hit actor set count, window ID and `AttackInstanceID`.
5. Run 30/60/120 FPS tests and time dilation + interruptions.
