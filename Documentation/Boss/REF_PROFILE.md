# Framework boss profile fields

`URPGBossFrameworkProfile` is the authored data asset consumed by `ResolveProfile`. This page lists its editable top-level fields and the nested card/combo structs (`RPGBossFrameworkProfile.h:15-187`). `cm` means centimeters, `s` seconds, `cm/s` centimeters/second, `deg` degrees, and fractions are normalized [0,1] unless noted.

## Identity and locomotion

| Field | Unit / purpose |
|---|---|
| `FixtureLabel` | fixture label; exact lane labels are checked when damage is enabled |
| `Mesh`, `AnimClass`, `TargetPawnClass`, `Card` | soft asset/class references; resolved and cross-validated |
| `BandMinCm`, `BandMaxCm` | target range band, cm |
| `WalkSpeedCmPerSecond` | movement speed, cm/s |
| `AcceptanceCm` | arrival tolerance, cm |
| `WalkTimeoutSeconds` | navigation timeout, s |
| `BlendInSeconds`, `BlendOutSeconds` | montage blend durations, s |
| `CapsuleRadiusCm`, `CapsuleHalfHeightCm` | boss capsule dimensions, cm |
| `MeshRelativeTransform` | mesh offset transform; `bAlignmentAuthored` confirms intentional alignment |
| `TargetHealth` | explicit proof-fixture player health, health units |

## Playback and selector

| Fields | Unit / purpose |
|---|---|
| `bDamageEnabled` | enable profile damage lane; requires the correct fixture label and card data |
| `HitStepCm`, `HitMaxSubsteps` | swept hit sampling distance and per-tick cap |
| `Cards` | `FRPGBossProfileCard` array; each has `Card`, `CooldownSeconds` (s), `Weight`, `bHyperArmor`, `KiteWeightMultiplier`, `HugWeightMultiplier`, `BackDodgeWeightMultiplier`, `GreedWeightMultiplier`, `bHeavyFinisher` (`RPGBossFrameworkProfile.h:37-53`) |
| `RepeatPenalty`, `RepeatMemory` | recent-card score scale and history length |
| `SelectorTieBand`, `SelectorTieSeed` | optional seeded near-tie fraction [0,.5] and seed |
| `ConeHysteresisDegrees` | optional extra full-cone slack, degrees |
| `bRangeBandPartition` | allow card bands to differ from walk band |
| `NeutralStrafeSeconds` | no-candidate neutral movement budget, s |
| `NeutralStrafeMinHoldSeconds`, `NeutralStrafeMaxHoldSeconds` | seeded neutral-strafe direction hold window, seconds (defaults 0.8 and 1.6) |
| `GuardChipFraction` | guarded-hit damage fraction |
| `ParryRecoveryScale`, `ParryFairTelegraph`, `ParryFairMinScale` | optional additional recovery scale, fair-tell switch and playback-rate floor |
| `AttackCount` | number of planned attacks |

## Aggro, pattern, and reaction tuning

| Fields | Unit / purpose |
|---|---|
| `bAggroEnabled` | enable preferred range adaptation |
| `AggroEnterCloseCm`, `AggroExitCloseCm`, `AggroEnterFarCm`, `AggroExitFarCm` | close/far hysteresis thresholds, cm |
| `AggroDodgeEnterRate`, `AggroDodgeExitRate` | dodge thresholds, dodges/s |
| `AggroDodgeWindowSeconds` | rolling dodge observation window, s |
| `FatigueGraceWhiffs`, `FatigueFloor` | clean whiff grace count and minimum playback-rate scale; zero disables |
| `DodgeHistoryDepth`, `DodgeBackThreshold` | pattern ring length and back-dodge count threshold |
| `DodgeSpeedCm` | observed target speed threshold, cm/s |
| `LosSearchSeconds` | blocked-visibility search timeout, s |
| `PunishMarginSeconds` | minimum extra punish margin, s |
| `PlayerLightMontage`, `PlayerHeavyMontage` | soft animation references for punish timing |
| `PlayerReachCm` | player punish reach, cm |
| `ReactionDelayMinSeconds`, `ReactionDelayMaxSeconds`, `ReactionSeed` | seeded flask reaction delay range, s, and seed |
| `AntiCheeseKiteRangeCm`, `AntiCheeseHugRangeCm`, `AntiCheeseStreak` | range cutoffs, cm, and consecutive decision count |

`FRPGBossProfileCard` also exposes `Card`, `CooldownSeconds`, `Weight`, `bHyperArmor`, `KiteWeightMultiplier`, `HugWeightMultiplier`, `BackDodgeWeightMultiplier`, `GreedWeightMultiplier`, and `bHeavyFinisher` (`RPGBossFrameworkProfile.h:37-53`). Each `FRPGBossComboNodeData` has `NodeId`, `MoveId`, and `Edges`; each edge has `ToNode`, `MinRangeCm`, `MaxRangeCm`, `MaxAbsYawDegrees`, `bAnyOutcome`, `Outcome`, and `TempoPauseSeconds` (`:15-33`). These use the same units as the corresponding card range, angle, and timing fields.

## Boss health, phases, posture, and bleed

| Fields | Unit / purpose |
|---|---|
| `BossMaxHealth`, `PlayerHitDamage` | health units; both zero disables hittable boss |
| `PhaseTwoFraction`, `PhaseTwoId` | phase threshold of max health and phase name |
| `bPhaseSupersedesStagger` | allow phase transition to interrupt stagger |
| `PostureMax`, `PlayerPostureHitAmount`, `ParryPostureAmount` | posture units |
| `StaggerSeconds`, `PostureRegenDelaySeconds` | seconds |
| `PostureRegenPerSecond` | posture units/s |
| `bParryGradeScale` | scale parry posture reaction by timing grade |
| `StaggerStartAnim`, `StaggerLoopAnim`, `StaggerEndAnim`, `PhaseTransitionAnim` | optional sequence assets |
| `AnimSlotName` | animation slot name |
| `BleedBuildupPerHit`, `BleedInitialThreshold`, `BleedThresholdIncrease`, `BleedThresholdMax` | buildup units per hit and threshold units |
| `BleedHpFraction` | fraction of boss maximum health removed at a proc, clamped to leave at least one HP |

## Arena and combo

| Fields | Unit / purpose |
|---|---|
| `ComboNodes`, `ComboRoot`, `ComboMaxDepth` | combo graph, root node ID and maximum edge depth |
| `RepositionMax`, `RepositionTurnDegPerSecond` | retry count and turn rate, deg/s |
| `ArenaRadiusCm`, `bArenaLeash` | target leash radius, cm, and return/wait behavior toggle |
| `ArenaCenterBias`, `CenterBiasStartFraction` | center-side positioning blend and normalized activation radius |
| `bArenaCenterAuthored`, `ArenaCenter` | whether the authored `FVector` center replaces the target's starting position |

## Complete editable-field inventory (source snapshot)

Every `EditAnywhere` declaration in the header is listed below, including nested combo and card structs. “No in-class initializer” is literal: the declaration provides no explicit initializer; inspect the owning Unreal object/struct construction path for runtime initialization. Units for design scalars are the declared semantic unit; bounds and special behavior remain in the field comments and validation section above. Source lines are one-based in `Source/OneBossFight/Player/RPGBossFrameworkProfile.h`.

| Field | Exact C++ type | Unit / interpretation | In-class default | Owning type | Header line |
|---|---|---|---|---|---|
| `ToNode` | `FName` | name / text | `no in-class initializer` | FRPGBossComboEdgeData | 18 |
| `MinRangeCm` | `float` | cm | `0.f` | FRPGBossComboEdgeData | 19 |
| `MaxRangeCm` | `float` | cm | `1.e6f` | FRPGBossComboEdgeData | 20 |
| `MaxAbsYawDegrees` | `float` | degrees | `180.f` | FRPGBossComboEdgeData | 21 |
| `bAnyOutcome` | `bool` | boolean | `true` | FRPGBossComboEdgeData | 22 |
| `Outcome` | `ERPGBossComboOutcome` | enum: Hit, Whiff, Guarded, Parried | `ERPGBossComboOutcome::Hit` | FRPGBossComboEdgeData | 23 |
| `TempoPauseSeconds` | `float` | seconds | `0.f` | FRPGBossComboEdgeData | 25 |
| `NodeId` | `FName` | name / text | `no in-class initializer` | FRPGBossComboNodeData | 31 |
| `MoveId` | `FName` | name / text | `no in-class initializer` | FRPGBossComboNodeData | 32 |
| `Edges` | `TArray<FRPGBossComboEdgeData>` | combo-edge collection | `no in-class initializer` | FRPGBossComboNodeData | 33 |
| `Card` | `TSoftObjectPtr<URPGBossMoveCard>` | soft asset/class reference | `no in-class initializer` | FRPGBossProfileCard | 40 |
| `CooldownSeconds` | `float` | seconds | `0.f` | FRPGBossProfileCard | 41 |
| `Weight` | `float` | normalized/scalar (see field comment for bounds) | `1.f` | FRPGBossProfileCard | 42 |
| `bHyperArmor` | `bool` | boolean | `false` | FRPGBossProfileCard | 44 |
| `KiteWeightMultiplier` | `float` | normalized/scalar (see field comment for bounds) | `1.f` | FRPGBossProfileCard | 46 |
| `HugWeightMultiplier` | `float` | normalized/scalar (see field comment for bounds) | `1.f` | FRPGBossProfileCard | 47 |
| `BackDodgeWeightMultiplier` | `float` | normalized/scalar (see field comment for bounds) | `1.f` | FRPGBossProfileCard | 49 |
| `GreedWeightMultiplier` | `float` | normalized/scalar (see field comment for bounds) | `1.f` | FRPGBossProfileCard | 51 |
| `bHeavyFinisher` | `bool` | boolean | `false` | FRPGBossProfileCard | 53 |
| `FixtureLabel` | `FString` | name / text | `no in-class initializer` | URPGBossFrameworkProfile | 60 |
| `Mesh` | `TSoftObjectPtr<USkeletalMesh>` | soft asset/class reference | `no in-class initializer` | URPGBossFrameworkProfile | 61 |
| `AnimClass` | `TSoftClassPtr<UAnimInstance>` | soft asset/class reference | `no in-class initializer` | URPGBossFrameworkProfile | 62 |
| `TargetPawnClass` | `TSoftClassPtr<APawn>` | soft asset/class reference | `no in-class initializer` | URPGBossFrameworkProfile | 63 |
| `Card` | `TSoftObjectPtr<URPGBossMoveCard>` | soft asset/class reference | `no in-class initializer` | URPGBossFrameworkProfile | 64 |
| `BandMinCm` | `float` | cm | `0.f` | URPGBossFrameworkProfile | 65 |
| `BandMaxCm` | `float` | cm | `0.f` | URPGBossFrameworkProfile | 66 |
| `WalkSpeedCmPerSecond` | `float` | cm/s | `0.f` | URPGBossFrameworkProfile | 67 |
| `AcceptanceCm` | `float` | cm | `0.f` | URPGBossFrameworkProfile | 68 |
| `WalkTimeoutSeconds` | `float` | seconds | `0.f` | URPGBossFrameworkProfile | 69 |
| `BlendInSeconds` | `float` | seconds | `0.f` | URPGBossFrameworkProfile | 70 |
| `BlendOutSeconds` | `float` | seconds | `0.f` | URPGBossFrameworkProfile | 71 |
| `CapsuleRadiusCm` | `float` | cm | `0.f` | URPGBossFrameworkProfile | 72 |
| `CapsuleHalfHeightCm` | `float` | cm | `0.f` | URPGBossFrameworkProfile | 73 |
| `TargetHealth` | `float` | health units | `0.f` | URPGBossFrameworkProfile | 75 |
| `bDamageEnabled` | `bool` | boolean | `false` | URPGBossFrameworkProfile | 77 |
| `HitStepCm` | `float` | cm | `0.f` | URPGBossFrameworkProfile | 79 |
| `HitMaxSubsteps` | `int32` | integer count / seed / depth | `0` | URPGBossFrameworkProfile | 80 |
| `Cards` | `TArray<FRPGBossProfileCard>` | card collection | `no in-class initializer` | URPGBossFrameworkProfile | 82 |
| `RepeatPenalty` | `float` | buildup units (per hit for buildup; threshold units for threshold fields) | `0.f` | URPGBossFrameworkProfile | 83 |
| `RepeatMemory` | `int32` | integer count / seed / depth | `0` | URPGBossFrameworkProfile | 84 |
| `SelectorTieBand` | `float` | normalized/scalar (see field comment for bounds) | `0.f` | URPGBossFrameworkProfile | 86 |
| `SelectorTieSeed` | `int32` | integer count / seed / depth | `0` | URPGBossFrameworkProfile | 87 |
| `ConeHysteresisDegrees` | `float` | degrees | `0.f` | URPGBossFrameworkProfile | 89 |
| `bRangeBandPartition` | `bool` | boolean | `false` | URPGBossFrameworkProfile | 91 |
| `NeutralStrafeSeconds` | `float` | seconds | `0.f` | URPGBossFrameworkProfile | 93 |
| `NeutralStrafeMinHoldSeconds` | `double` | seconds | `.8` | URPGBossFrameworkProfile | 95 |
| `NeutralStrafeMaxHoldSeconds` | `double` | seconds | `1.6` | URPGBossFrameworkProfile | 96 |
| `GuardChipFraction` | `float` | normalized/scalar (see field comment for bounds) | `0.f` | URPGBossFrameworkProfile | 95 |
| `ParryRecoveryScale` | `float` | normalized/scalar (see field comment for bounds) | `0.f` | URPGBossFrameworkProfile | 97 |
| `ParryFairTelegraph` | `bool` | boolean | `false` | URPGBossFrameworkProfile | 99 |
| `ParryFairMinScale` | `float` | normalized/scalar (see field comment for bounds) | `.4f` | URPGBossFrameworkProfile | 100 |
| `bAggroEnabled` | `bool` | boolean | `false` | URPGBossFrameworkProfile | 102 |
| `AggroEnterCloseCm` | `float` | cm | `250.f` | URPGBossFrameworkProfile | 103 |
| `AggroExitCloseCm` | `float` | cm | `300.f` | URPGBossFrameworkProfile | 104 |
| `AggroEnterFarCm` | `float` | cm | `700.f` | URPGBossFrameworkProfile | 105 |
| `AggroExitFarCm` | `float` | cm | `600.f` | URPGBossFrameworkProfile | 106 |
| `AggroDodgeEnterRate` | `float` | buildup units (per hit for buildup; threshold units for threshold fields) | `0.6f` | URPGBossFrameworkProfile | 107 |
| `AggroDodgeExitRate` | `float` | buildup units (per hit for buildup; threshold units for threshold fields) | `0.3f` | URPGBossFrameworkProfile | 108 |
| `AggroDodgeWindowSeconds` | `float` | seconds | `5.f` | URPGBossFrameworkProfile | 109 |
| `FatigueGraceWhiffs` | `int32` | integer count / seed / depth | `0` | URPGBossFrameworkProfile | 111 |
| `FatigueFloor` | `float` | buildup units (per hit for buildup; threshold units for threshold fields) | `0.f` | URPGBossFrameworkProfile | 113 |
| `ParryPostureAmount` | `float` | posture units (rate suffix if applicable) | `0.f` | URPGBossFrameworkProfile | 115 |
| `bParryGradeScale` | `bool` | normalized/scalar (see field comment for bounds) | `false` | URPGBossFrameworkProfile | 117 |
| `AttackCount` | `int32` | integer count / seed / depth | `0` | URPGBossFrameworkProfile | 118 |
| `BossMaxHealth` | `float` | health units | `0.f` | URPGBossFrameworkProfile | 120 |
| `PlayerHitDamage` | `float` | health units | `0.f` | URPGBossFrameworkProfile | 121 |
| `PhaseTwoFraction` | `float` | normalized/scalar (see field comment for bounds) | `0.f` | URPGBossFrameworkProfile | 123 |
| `PhaseTwoId` | `FName` | name / text | `no in-class initializer` | URPGBossFrameworkProfile | 124 |
| `PostureMax` | `float` | posture units (rate suffix if applicable) | `0.f` | URPGBossFrameworkProfile | 127 |
| `PlayerPostureHitAmount` | `float` | posture units (rate suffix if applicable) | `0.f` | URPGBossFrameworkProfile | 128 |
| `StaggerSeconds` | `float` | seconds | `0.f` | URPGBossFrameworkProfile | 129 |
| `PostureRegenDelaySeconds` | `float` | seconds | `0.f` | URPGBossFrameworkProfile | 130 |
| `PostureRegenPerSecond` | `float` | posture units (rate suffix if applicable) | `0.f` | URPGBossFrameworkProfile | 131 |
| `StaggerStartAnim` | `TSoftObjectPtr<UAnimSequence>` | soft asset/class reference | `no in-class initializer` | URPGBossFrameworkProfile | 135 |
| `StaggerLoopAnim` | `TSoftObjectPtr<UAnimSequence>` | soft asset/class reference | `no in-class initializer` | URPGBossFrameworkProfile | 136 |
| `StaggerEndAnim` | `TSoftObjectPtr<UAnimSequence>` | soft asset/class reference | `no in-class initializer` | URPGBossFrameworkProfile | 137 |
| `PhaseTransitionAnim` | `TSoftObjectPtr<UAnimSequence>` | soft asset/class reference | `no in-class initializer` | URPGBossFrameworkProfile | 138 |
| `AnimSlotName` | `FName` | name / text | `TEXT("FullBody")` | URPGBossFrameworkProfile | 139 |
| `ComboNodes` | `TArray<FRPGBossComboNodeData>` | soft asset/class reference | `no in-class initializer` | URPGBossFrameworkProfile | 141 |
| `ComboRoot` | `FName` | name / text | `no in-class initializer` | URPGBossFrameworkProfile | 142 |
| `ComboMaxDepth` | `int32` | integer count / seed / depth | `3` | URPGBossFrameworkProfile | 143 |
| `RepositionMax` | `int32` | integer count / seed / depth | `0` | URPGBossFrameworkProfile | 145 |
| `RepositionTurnDegPerSecond` | `float` | deg/s | `0.f` | URPGBossFrameworkProfile | 147 |
| `ArenaRadiusCm` | `float` | cm | `0.f` | URPGBossFrameworkProfile | 149 |
| `bArenaLeash` | `bool` | boolean | `false` | URPGBossFrameworkProfile | 151 |
| `DodgeHistoryDepth` | `int32` | integer count / seed / depth | `0` | URPGBossFrameworkProfile | 153 |
| `DodgeBackThreshold` | `int32` | integer count / seed / depth | `2` | URPGBossFrameworkProfile | 154 |
| `DodgeSpeedCm` | `float` | cm | `600.f` | URPGBossFrameworkProfile | 155 |
| `LosSearchSeconds` | `float` | seconds | `0.f` | URPGBossFrameworkProfile | 157 |
| `PunishMarginSeconds` | `float` | seconds | `0.f` | URPGBossFrameworkProfile | 159 |
| `PlayerLightMontage` | `TSoftObjectPtr<UAnimMontage>` | soft asset/class reference | `no in-class initializer` | URPGBossFrameworkProfile | 160 |
| `PlayerHeavyMontage` | `TSoftObjectPtr<UAnimMontage>` | soft asset/class reference | `no in-class initializer` | URPGBossFrameworkProfile | 161 |
| `PlayerReachCm` | `float` | cm | `0.f` | URPGBossFrameworkProfile | 162 |
| `ReactionDelayMinSeconds` | `float` | seconds | `0.f` | URPGBossFrameworkProfile | 164 |
| `ReactionDelayMaxSeconds` | `float` | seconds | `0.f` | URPGBossFrameworkProfile | 165 |
| `ReactionSeed` | `int32` | integer count / seed / depth | `0` | URPGBossFrameworkProfile | 166 |
| `AntiCheeseKiteRangeCm` | `float` | cm | `0.f` | URPGBossFrameworkProfile | 168 |
| `AntiCheeseHugRangeCm` | `float` | cm | `0.f` | URPGBossFrameworkProfile | 169 |
| `AntiCheeseStreak` | `int32` | integer count / seed / depth | `2` | URPGBossFrameworkProfile | 170 |
| `ArenaCenterBias` | `float` | normalized/scalar (see field comment for bounds) | `0.f` | URPGBossFrameworkProfile | 172 |
| `CenterBiasStartFraction` | `float` | normalized/scalar (see field comment for bounds) | `0.5f` | URPGBossFrameworkProfile | 173 |
| `bArenaCenterAuthored` | `bool` | boolean | `false` | URPGBossFrameworkProfile | 175 |
| `ArenaCenter` | `FVector` | UE vector/transform (cm, degrees, scale components) | `FVector::ZeroVector` | URPGBossFrameworkProfile | 176 |
| `bPhaseSupersedesStagger` | `bool` | boolean | `false` | URPGBossFrameworkProfile | 178 |
| `BleedBuildupPerHit` | `float` | buildup units per hit | `0.f` | URPGBossFrameworkProfile | 181 |
| `BleedInitialThreshold` | `float` | buildup threshold units | `0.f` | URPGBossFrameworkProfile | 182 |
| `BleedThresholdIncrease` | `float` | buildup threshold units per proc | `0.f` | URPGBossFrameworkProfile | 183 |
| `BleedThresholdMax` | `float` | buildup threshold units | `0.f` | URPGBossFrameworkProfile | 184 |
| `BleedHpFraction` | `float` | fraction of boss max health | `0.f` | URPGBossFrameworkProfile | 185 |
| `MeshRelativeTransform` | `FTransform` | UE vector/transform (cm, degrees, scale components) | `no in-class initializer` | URPGBossFrameworkProfile | 186 |
| `bAlignmentAuthored` | `bool` | boolean | `false` | URPGBossFrameworkProfile | 187 |
## Validation and telemetry

### Authored-profile validation (`ValidateProfile`)

Source: `Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp:44-165`; combo graph rules: `Source/OneBossFight/Player/RPGBossComboRules.h:34-75`.

| Rule group | Disabled/allowed state | Enabled/required state and refusal |
|---|---|---|
| Fixture identity | No arbitrary label/lane: identity is always required. | Exactly F3/F4/F5 labels; F4/F5 iff damage is enabled. Mesh, AnimClass, TargetPawnClass must be non-null. F5 requires >=1 candidate and empty single `Card`; F3/F4 require one `Card` and empty `Cards`. Failure: `Framework.Profile.Identity`. |
| Hit sampling and health | When damage is off, hit-step bounds are not checked here. Boss health/damage must both be zero to disable boss hittability. | Damage lane requires finite `HitStepCm` in (0,1e6] and `HitMaxSubsteps` 1..64. Boss health/damage must both be positive or both zero; finite, nonnegative, max health <=1e6, damage <= max health. Failure: `Framework.Profile.Domain`. |
| Phase two | Off only when `PhaseTwoFraction==0` and `PhaseTwoId` is None. | Requires F5, hittable boss, finite fraction strictly (0,1), and non-None ID. Failure: `Framework.Profile.Phase`. Resolved candidate pool must contain cards for exactly phase one and phase two, both nonempty, and each must pass cooldown-starvation feasibility (`.PhaseCards`, `.PhaseCooldownStarvation`; lines 211-218). |
| Posture / stagger | All five posture values exactly zero disables posture. | Otherwise requires F5 + hittable boss; each value finite in [0,1e6], max and per-hit drain >0, drain <= max, stagger duration [.5,60]. Failure: `.Posture`. |
| Optional animation | All four clips empty disables this animation path; default slot name is `FullBody`. | Any clip requires nonempty slot; stagger start/loop/end must be all present or all absent. Stagger clips require F5 and positive posture; phase clip requires F5, hittable boss, positive phase threshold and phase ID. Failures: `.StaggerAnim.SlotNameEmpty`, `.CoherentSet`, `.NoPosture`, `.PhaseTransitionAnim.Phaseless`; loaded assets, skeletons, clip lengths and phase clip rules are checked during resolve (lines 267-288). |
| Combo graph | Empty nodes and None root disable combos. | Any graph requires F5. Graph validator rejects empty graph, max depth outside 1..3, absent root, empty/duplicate node IDs, empty move IDs/unknown edge targets, invalid edge ranges/yaw/pause, any cycle (including unreachable nodes), and longest root path exceeding max depth. Tokens `Framework.Profile.Combo.*`; resolved node MoveIds must match a candidate (`.Combo.UnknownMove`, lines 220-226). |
| Reposition / arena | Reposition off at max=0 and turn rate=0; radius=0 disables leash and center bias. | Reposition max 1..8 must pair with finite turn rate (0,720] and F5. Radius finite [0,1e6], positive only in F5; leash needs positive radius. Center bias [0,1], start fraction (0,1], valid center; authored center or positive bias requires radius. Supersede-stagger needs F5, posture, and phase two. Failures: `.Domain`. |
| Anticheese / reactions | Zero kite/hug thresholds disable state activation. Multiplier defaults are 1. | Thresholds finite [0,1e5], F5 when either positive, hug < kite if both active; streak always 1..8 and all candidate multipliers finite (0,100]. Reaction delay both zero disables; otherwise F5 and valid seeded delay range. Failures: `.Domain`. |
| LOS / dodge / punish | LOS time 0 disables search; dodge history depth 0 disables pattern; punish margin 0 disables attack-margin check (but a heavy-finisher flag then refuses). | LOS finite [0,30] and F5 if positive. Dodge depth 0..8; positive depth requires F5, threshold 1..depth and speed finite (0,1e5]. Punish margin [0,5], reach [0,2000]; positive margin needs F5 and both montages. Failures: `.Domain` at this layer; resolved punish checks have dedicated tokens. |
| Selector / defense tuning | Several switches/zero values opt out of behavior; see field inventory and source comments. | Tie band finite [0,.5], F5 when band or seed is nonzero; cone hysteresis [0,40] and F5 if positive; strafe [0,20] and F5 + positive walk speed if positive; guard fraction [0,1], parry recovery [0,3], F5 if positive. Fair minimum scale is always (0,1], fair tell needs F5. Aggro thresholds are always validated; `bAggroEnabled` additionally needs F5 and valid dodge speed. Fatigue disabled with both values zero; otherwise F5 and floor (0,1], grace 0..100. Parry posture is nonnegative and, if positive, F5 + posture and <= posture max. Grade scaling needs F5. F5 always requires repeat penalty (0,1], memory 1..8 and attack count 1..8; each card needs non-null asset, cooldown [0,1e6], weight (0,1e6]. Failures use dedicated tokens where coded, otherwise `.Domain`. |
| Base movement / geometry / alignment | These are required in all fixture lanes, not optional. | Ten base dimensions/health inputs must be finite (0,1e6]. Band min < max, acceptance < half band width, capsule radius <= half-height. Alignment must be authored and transform valid, finite, positive scale <=1e6 and translation magnitude <=1e6. Failures: `.Domain`, `.Geometry`, `.Alignment`. |

### Resolve-time validation (`ResolveProfile`)

Source: `RPGBossFrameworkProfile.cpp:168-289`. This runs after authored-profile checks and is the load boundary: it refuses invalid object/thread (`.ObjectOrThread`), missing/wrong/non-abstract mesh/anim/pawn dependencies (`.Dependency`), montage/sequence/section/slot or clip-tail mismatches (`.SequenceTelemetryOnly`, `.CardBandOrBlendTail`), damage-card mismatch (`.DamageCard` or `.SequenceTelemetryOnly`), skeleton/compiled-card problems (`.AnimSkeleton`, `.ResolvedCard` or compiler errors), and a profile band outside a card's range unless `bRangeBandPartition` is true. F5 additionally checks phase membership/starvation, combo candidate membership, worst-case run damage (`.DamageBudget`), defensive-card cooldown/counterplay, and optional punish data/margins. Optional F11 clips are loaded and checked against the boss skeleton, slot, lengths, posture duration and phase state.

The generic `.Domain` token intentionally covers multiple authored-field checks; it does not identify which field failed. For exact error ordering and per-case expectations, consult `RPGBossFrameworkRuntimeTests.cpp` and the line-referenced source above. These rules describe current source, not every gameplay semantic implied by a field comment.
