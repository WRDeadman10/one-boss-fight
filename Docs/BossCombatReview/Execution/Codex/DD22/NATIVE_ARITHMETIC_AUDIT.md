# C265 HealPunish read-only arithmetic audit

This is source reasoning, not a runtime/Unreal test. Native HealPunish/Javelin,
world inputs, hardcoded dependencies and runtime guards are unchanged.

| Operation | Actual source/type and conclusion |
|---|---|
| Distance / FlightTime | RPGBossHealPunish.cpp:176: FVector::Dist returns double; FlightTime float is promoted for division. The authored floor0.05 avoids division by zero and bounds the reciprocal at about20; the allowed speed endpoints are finite and coherent (Min<=Max). For normal finite representable world distance the quotient is finite, then clamped into[MinSpeed,MaxSpeed]<=1e6 before float storage. An extreme finite double distance near DBL_MAX can overflow the quotient at the floor, but the resulting positive infinity is clamped to the finite MaxSpeed. No arbitrary unbounded world-coordinate/NaN guarantee is claimed. FMath::Clamp with reversed endpoints is not called undefined; our ordering is an authored coherent-window choice. |
| World time + Cooldown | cpp:170 stores in double CooldownEnd; UWorld::GetTimeSeconds returns double (World.h:2502/:4254). Cooldown is float in[0,1e6]. It cannot itself cause overflow for finite double world time: at values near double maximum,1e6 is far below half an ULP and rounds away. Nonfinite time inputs are outside the record contract and are not repaired. GetCooldownRemaining at cpp:33 subtracts the same runtime time and narrows the result; normal cooldown arithmetic is bounded, arbitrary invalid/reset world-time behavior is not proven by a typed profile. |
| FeetZ + AimHeight | cpp:173: RPGBossDamage::FeetZ returns float from a double actor-location/capsule expression. AimHeight is float in[-1e6,1e6]. Its addition to a finite representable feet float cannot overflow (near FLT_MAX,1e6 is far below half an ULP; elsewhere the magnitude is safe). A huge finite double position can overflow on FeetZ's earlier narrowing, independent of the profile. Nonfinite/invalid external geometry and direction normalization are not certified. |

There is no profile-driven numeric contradiction requiring an additional field,
clamp or native edit under C265. The external world/time/geometry qualifications
above remain explicit. The admission range is checked earlier (cpp:119-120), but
Release does not recheck that range before the distance at:176, so this audit does
not assume that release distance is always <=MaxRange.

Hardcoded and UNRESOLVED by this record: native ThrowMove=A5 (cpp:22, used at:138
and:254) and player DrinkingPotion montage (cpp:236). SpawnSockets is ordered
syntactic identity only: native lookup at:42-47 may fail and use its fallback.
No socket/bone/montage/ability, javelin path, collision or damage execution proof.
