# C264 read-only audit — not an Unreal execution or correction

No DD19/DD20/native source is changed by this audit. Conditions on external runtime
inputs are stated explicitly; a finite authored field does not validate the world,
attribute values, hit amount, time or geometry supplied by other systems.

## DD19 Bleed: all five authored float fields

| Field | Source operation and finding |
|---|---|
| InitialThreshold | RPGBossBleed.cpp:34/:123 seeds the finite value directly. It can later participate in overflowing threshold growth: RPGBleedRules.h:60 evaluates Threshold+ThresholdIncrease before Min. Initial=0.75*FLT_MAX, Increase=0.75*FLT_MAX, Max=FLT_MAX is accepted and the sum overflows. The subsequent Min with a finite Max returns that finite cap. Intermediate overflow possible; this is not a claim that the final threshold stays infinite. |
| ThresholdIncrease | Same :60 counterexample. Nonnegative finite values are not enough to prevent the intermediate addition overflowing. A separate lead correction would be required for a pre-add finite check or bounded record contract. |
| ThresholdMax | Used as a finite cap in :60. It creates no overflow by itself; with the accepted positive finite values, Min(+Inf,finite Max) returns finite Max. It does not prevent the intermediate overflow above. |
| HpFraction | RPGBleedRules.h:67-69 computes MaxHealth*HpFraction; accepted fraction[0,1] cannot overflow if the incoming MaxHealth is a finite nonnegative float. RPGBossBleed.cpp:99 narrows double attribute reads to float first: a finite double attribute beyond FLT_MAX can overflow on narrowing, which this profile does not validate. No arbitrary product/runtime-attribute safety claim. |
| EffectHeight | RPGBossBleed.cpp:108 adds FVector(0,0,EffectHeight) to actor location. UE5 FVector is a double vector; a finite float offset is representable in double and is too small to overflow even a finite double location near its representable maximum on rounding. No overflow at this direct addition under finite FVector input. Downstream renderer/effect float conversions and nonfinite actor input are not certified. |

Related external-input risk: RPGBleedRules.h:55 Buildup+=Amount can overflow for
finite positive accumulated hit values (the amount is not a profile field).
The native proc then resets buildup at:58. This is separate from validating the
five configuration scalars and does not authorize a native edit.

## DD20 LowSweep: all six authored float fields

| Field | Source operation and finding |
|---|---|
| Damage | Passed as payload damage (RPGBossLowSweep.cpp:90), not added to radius/angle geometry. A finite nonnegative damage value alone causes no geometry overflow. Resolver runtime health/attribute/multiplier inputs are outside this profile. |
| Reach | Compared in RPGBossMath.h:74 and used in double-vector debug geometry at RPGBossLowSweep.cpp:198. No overflow from the finite field alone with ordinary finite world geometry; no profile arithmetic adds Reach to another float. |
| InnerRadius | Compared to Distance+PlayerRadius in RPGBossMath.h:74; finite InnerRadius does not itself cause the addition. But finite extreme external Distance and PlayerRadius (e.g. both0.75*FLT_MAX) make that sum overflow. The profile's InnerRadius<Reach condition cannot guarantee representability of external geometry. |
| BladeHeight | Compared to FeetHeight at RPGBossLowSweep.cpp:92-93. The finite threshold does not itself overflow; subtracting extreme opposite-sign finite external feet/ground floats can overflow before comparison. No profile-only guarantee for world geometry. |
| SweepFromDegrees | C258 bounds[-360,360]; RPGBossLowSweep.cpp:191 interpolates with Progress clamped[0,1]. Difference<=720, product and addition remain finite. RPGBossMath.h:78-79 adds/subtracts finite capsule tolerance<=90 under valid finite nonnegative geometry. No overflow from this bounded field. |
| SweepToDegrees | Same bounded interpolation/tolerance reasoning; equal/reversed endpoints remain finite and valid. This is not proof of wrap/multi-turn or actual collision coverage. |

External geometry caveat for Reach/InnerRadius: Distance-PlayerRadius stays in
float range for finite nonnegative operands, but Distance+PlayerRadius may overflow.
The distance is itself narrowed from FVector::Size in LowSweep.cpp:75; huge finite
double positions may produce a distance outside float range before SweepTouches.
These are source arithmetic possibilities, not observed arena failures.

Conclusion for the lead: the concrete DD19 profile-enabled intermediate threshold
overflow deserves a separately ordered decision. DD20 angle bounds close the
profile-driven Lerp issue; its remaining arithmetic risks come from external
geometry, which the typed profile never claimed to validate. No silent bounds or
native guards were added to either accepted package.
