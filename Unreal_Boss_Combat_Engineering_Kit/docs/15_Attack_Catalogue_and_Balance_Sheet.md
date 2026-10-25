# 15 — Attack Catalogue, Timing Table, Balancing Procedure

The authoritative machine-readable tuning example is `../data/attack_catalogue.csv`. Distances in **centimeters**, times in **seconds**, angles in **degrees**, damage in illustrative gameplay points. This is an **initial tuning design**, not a claim about any commercial game's frame data.

![Timings](../diagrams/05_attack_timing.png)

## Recommended per-move fields

**Identity:** ID, gameplay tag, family, phase, animation, section. **Eligibility:** range min/max, ideal distance, front/side/rear yaw sectors, LOS, cooldown, player action tags, resources. **Animation:** anticipation, pre-selected hold variant, turn lock time, active windows, recovery, root motion, warp window, armor window, sound cues. **Damage:** geometry type, weapon samples, reach, hit policy, direct damage, splash damage, stance damage, knockback, guard effect, element, dodge/parry policy. **Branching:** legal gates, target sectors, hit-confirm policy, max depth, family repetition. **UX:** telegraph clarity, expected player response, punish type.

## Validating timing

Suppose `A03` has 0.70s wind-up, 0.28s hold, 0.19s active, 0.98s recovery. Duration from start through recovery ≈ **2.15s** (plus any distinct follow-through overlap). The first active contact begins around **0.98s** before victim-specific collision timing. At 60fps the active span is about 11 frames, but actual player contact may be much narrower. Test collision at 30fps anyway.

## Damage principles

- Damage scales with commitment, reach, avoidability and phase expectations, not merely visual size.
- A sweep may do moderate damage with large angular coverage; a narrow thrust may do higher posture damage.
- A radial wave with limited escape space needs longer telegraph or lower damage.
- Grab damage can be high if narrow, telegraphed and very punishable on miss; never make it camera-obscured and unavoidable.
- Posture damage to boss should reward charged and well-timed offense; avoid excessive regen that invalidates slower weapon builds.

## Per-move measurements to capture (from your prototype)

1. `TimeToFirstActive` measured from montage start in Unreal Insights/Rewind.
2. `ActiveDuration` as actually fired by Notify State.
3. `PeakTipSpeedCmPerSec` and maximum swept angle.
4. `PostLockRotationDeg` over rest of move.
5. `WhiffRecoveryTime` and `HitRecoveryTime` if variants exist.
6. `PunishAvailableToLight`, `PunishAvailableToHeavy` at 0/1/2m response positions.
7. `PlayerHitRate` per move and distance, separated by novices/veterans.
8. `MoveUseFrequency` and `SameFamilyRepeatRate`.
9. `ContactOutsideVisibleVolume` counts (should be near zero).
10. `InterruptionCleanupLeaks` (must be zero).

## Balance tuning order

1. Fix **camera visibility and hitbox mismatch** before modifying damage.
2. Fix teleport-like tracking before extending dodge i-frames.
3. Ensure correct safe responses before decreasing reaction time.
4. Tune recovery for slow/light player weapons, not only your test character's fastest attack.
5. Reduce excessive attack frequency by neutral pacing and cooldown rather than globally slowing all animation.
6. Change one attribute group at a time: geometry → telegraph → damage → utility weights → phase pressure.
7. Run QA matrix and compare event logs after every significant change.

## Spreadsheet formulas designers can reuse

```text
AttackStartToFirstHit = WindupS + HoldS
TotalApproxDuration = WindupS + HoldS + ActiveS + RecoveryS
FramesAt60 = round(DurationSeconds * 60)
PotentialPunishMargin = RecoveryS - TravelS - PlayerStartupS - SafetyS
RecommendedUtilityWeight = DesignerBaseWeight * ContextMultipliers - RepeatPenalty
```

Use `data/combat_settings.json` for initial constants. Do not use attack catalogue values as exact Montage timings until the actual assets are measured; the **Montage timeline and notify positions** must match gameplay data.
