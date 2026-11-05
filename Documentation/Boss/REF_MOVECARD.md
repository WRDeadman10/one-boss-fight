# MoveCard fields (schema 1)

The editable data is `URPGBossMoveCard::Spec`, a `FRPGBossMoveCardSpec`. A zero-valued draft is invalid; pure validation does not load soft assets (`RPGBossMoveCard.h:73-129`; `RPGBossMoveCard.cpp:31-164`). The only accepted `Schema` is 1 (`RPGBossMoveCard.cpp:35`). Runtime profile resolution additionally loads and checks animation, skeleton, card range/blend tail, and profile damage constraints (`RPGBossFrameworkProfile.cpp:168-198`).

## Card fields

| Field | Meaning / unit | Validation or token family |
|---|---|---|
| `Schema` | `int32` data schema; current accepted value is 1 (zero is the invalid C++ draft default) | `MoveCard.Identity` |
| `MoveId`, `FamilyId`, `PhaseId` | Unique move identity, repeat family, phase name | nonempty/unique/phase membership; `MoveCard.*` |
| `Skeleton` | soft skeleton asset reference | required and consistent with animation; `MoveCard.Skeleton`, profile `Framework.Profile.AnimSkeleton` |
| `Sequence`, `Montage` | exactly one animation source | `MoveCard.AnimationSource` |
| `SlotName`, `SectionName` | montage slot and optional section (`None` means full source) | nonempty slot; section checked during resolution |
| `PlayRate` | animation time scale | finite positive bounded rate |
| `CommitSeconds`, `ActiveStartSeconds`, `ActiveEndSeconds`, `RecoveryEndSeconds` | card-local seconds | ordered within resolved clip; active interval nonempty |
| `TrackDegreesPerSecond` | turn cap, degrees/second | finite nonnegative bounded |
| `WarpStartSeconds`, `WarpEndSeconds` | card-local seconds for bounded in-place warp | disabled when max distance is zero; ordered within active span |
| `WarpMaxDistanceCm`, `WarpStandoffCm` | distance limits, centimeters | finite nonnegative |
| `WarpMaxAngleDegrees` | total yaw change, degrees | finite nonnegative bounded |
| `WarpEaseInOut` | smooth distance distribution toggle | requires a valid warp interval |
| `bDefensive`, `bWarpAway` | defensive classification and retreat direction | boolean; retreat requires warp configuration |
| `HoldAtSeconds`, `HoldMinSeconds`, `HoldMaxSeconds`, `HoldSeed` | deterministic windup hold boundary/duration in seconds and integer seed | valid ordered bounds; hold cues must match a hold |
| `Cues` | cue ID, card time, hold-release toggle, visual, optional sound, socket | `MoveCard.Cue.*` |
| `MinRangeCm`, `MaxRangeCm` | horizontal range band in centimeters | finite ordered nonnegative interval |
| `FrontConeDegrees` | eligibility half-cone in degrees | finite bounded angle |
| `MaxVerticalDeltaCm` | feet-to-feet height allowance in centimeters; zero disables limit | finite nonnegative |
| `HPDamage` | per-contact damage request | finite nonnegative; damage-enabled profile constrains it |
| `bUsesRootMotion` | explicit root-motion capability declaration | true is rejected by current in-place executor |
| `Windows` | one or more contact windows (below) | IDs/times/geometry/group coherence validated |

## Exact editable-field inventory

All `EditAnywhere` declarations, including baked samples, cues, windows, spec, and the asset wrapper, are listed here. “No in-class initializer” describes the declaration only; it does not claim a concrete serialized asset default. Source lines are one-based in `Source/OneBossFight/Player/RPGBossMoveCard.h`.

| Field | Exact C++ type | Unit / meaning | In-class default | Owning type | Header line |
|---|---|---|---|---|---|
| `TimeSeconds` | `float` | seconds in card or window time | `0.f` | URPGBossMoveCard | 19 |
| `BaseCS` | `FVector` | component-space vector in cm | `FVector::ZeroVector` | URPGBossMoveCard | 20 |
| `TipCS` | `FVector` | component-space vector in cm | `FVector::ZeroVector` | URPGBossMoveCard | 21 |
| `CueId` | `FName` | identifier / socket / section name | `no in-class initializer` | FRPGBossCue | 35 |
| `TimeSeconds` | `float` | seconds in card or window time | `0.f` | FRPGBossCue | 36 |
| `bAtHoldRelease` | `bool` | boolean | `false` | FRPGBossCue | 38 |
| `Visual` | `ERPGBossCueVisual` | enum: None, HitSpark, DodgeDust, BloodBurst | `ERPGBossCueVisual::None` | FRPGBossCue | 39 |
| `Sound` | `TSoftObjectPtr<USoundBase>` | soft asset reference | `no in-class initializer` | FRPGBossCue | 40 |
| `Socket` | `FName` | identifier / socket / section name | `no in-class initializer` | FRPGBossCue | 41 |
| `WindowId` | `FName` | identifier / socket / section name | `no in-class initializer` | FRPGBossMoveWindow | 48 |
| `HitGroup` | `FName` | identifier / socket / section name | `no in-class initializer` | FRPGBossMoveWindow | 49 |
| `StartSeconds` | `float` | seconds in card or window time | `0.f` | FRPGBossMoveWindow | 50 |
| `EndSeconds` | `float` | seconds in card or window time | `0.f` | FRPGBossMoveWindow | 51 |
| `SocketA` | `FName` | identifier / socket / section name | `no in-class initializer` | FRPGBossMoveWindow | 53 |
| `SocketB` | `FName` | identifier / socket / section name | `no in-class initializer` | FRPGBossMoveWindow | 54 |
| `RadiusCm` | `float` | cm | `0.f` | FRPGBossMoveWindow | 55 |
| `bSecondary` | `bool` | boolean | `false` | FRPGBossMoveWindow | 57 |
| `bRing` | `bool` | boolean | `false` | FRPGBossMoveWindow | 59 |
| `RingStartRadiusCm` | `float` | cm | `0.f` | FRPGBossMoveWindow | 60 |
| `RingSpeedCmPerSecond` | `float` | cm/s | `0.f` | FRPGBossMoveWindow | 61 |
| `RingThicknessCm` | `float` | cm | `0.f` | FRPGBossMoveWindow | 62 |
| `RingHeightCm` | `float` | cm | `0.f` | FRPGBossMoveWindow | 63 |
| `bGrab` | `bool` | boolean | `false` | FRPGBossMoveWindow | 65 |
| `GrabAttachSocket` | `FName` | identifier / socket / section name | `no in-class initializer` | FRPGBossMoveWindow | 66 |
| `GrabReleaseSeconds` | `float` | seconds in card or window time | `0.f` | FRPGBossMoveWindow | 67 |
| `BakedSamples` | `TArray<FRPGBakedBladeSample>` | nested data collection | `no in-class initializer` | FRPGBossMoveWindow | 69 |
| `Schema` | `int32` | schema version integer | `0` | FRPGBossMoveCardSpec | 77 |
| `MoveId` | `FName` | identifier / socket / section name | `no in-class initializer` | FRPGBossMoveCardSpec | 78 |
| `FamilyId` | `FName` | identifier / socket / section name | `no in-class initializer` | FRPGBossMoveCardSpec | 79 |
| `PhaseId` | `FName` | identifier / socket / section name | `no in-class initializer` | FRPGBossMoveCardSpec | 80 |
| `Skeleton` | `TSoftObjectPtr<USkeleton>` | soft asset reference | `no in-class initializer` | FRPGBossMoveCardSpec | 81 |
| `Sequence` | `TSoftObjectPtr<UAnimSequence>` | soft asset reference | `no in-class initializer` | FRPGBossMoveCardSpec | 83 |
| `Montage` | `TSoftObjectPtr<UAnimMontage>` | soft asset reference | `no in-class initializer` | FRPGBossMoveCardSpec | 84 |
| `SlotName` | `FName` | identifier / socket / section name | `no in-class initializer` | FRPGBossMoveCardSpec | 85 |
| `SectionName` | `FName` | identifier / socket / section name | `no in-class initializer` | FRPGBossMoveCardSpec | 87 |
| `PlayRate` | `float` | playback rate multiplier | `0.f` | FRPGBossMoveCardSpec | 88 |
| `CommitSeconds` | `float` | seconds in card or window time | `0.f` | FRPGBossMoveCardSpec | 89 |
| `ActiveStartSeconds` | `float` | seconds in card or window time | `0.f` | FRPGBossMoveCardSpec | 90 |
| `ActiveEndSeconds` | `float` | seconds in card or window time | `0.f` | FRPGBossMoveCardSpec | 91 |
| `RecoveryEndSeconds` | `float` | seconds in card or window time | `0.f` | FRPGBossMoveCardSpec | 92 |
| `TrackDegreesPerSecond` | `float` | degrees/s | `0.f` | FRPGBossMoveCardSpec | 93 |
| `WarpStartSeconds` | `float` | seconds in card or window time | `0.f` | FRPGBossMoveCardSpec | 95 |
| `WarpEndSeconds` | `float` | seconds in card or window time | `0.f` | FRPGBossMoveCardSpec | 96 |
| `WarpMaxDistanceCm` | `float` | cm | `0.f` | FRPGBossMoveCardSpec | 97 |
| `WarpMaxAngleDegrees` | `float` | degrees | `0.f` | FRPGBossMoveCardSpec | 98 |
| `WarpStandoffCm` | `float` | cm | `0.f` | FRPGBossMoveCardSpec | 99 |
| `WarpEaseInOut` | `bool` | boolean | `false` | FRPGBossMoveCardSpec | 101 |
| `bDefensive` | `bool` | boolean | `false` | FRPGBossMoveCardSpec | 103 |
| `bWarpAway` | `bool` | boolean | `false` | FRPGBossMoveCardSpec | 104 |
| `HoldAtSeconds` | `float` | seconds in card or window time | `0.f` | FRPGBossMoveCardSpec | 106 |
| `HoldMinSeconds` | `float` | seconds in card or window time | `0.f` | FRPGBossMoveCardSpec | 107 |
| `HoldMaxSeconds` | `float` | seconds in card or window time | `0.f` | FRPGBossMoveCardSpec | 108 |
| `HoldSeed` | `int32` | integer seed | `0` | FRPGBossMoveCardSpec | 109 |
| `Cues` | `TArray<FRPGBossCue>` | nested data collection | `no in-class initializer` | FRPGBossMoveCardSpec | 111 |
| `MinRangeCm` | `float` | cm | `0.f` | FRPGBossMoveCardSpec | 112 |
| `MaxRangeCm` | `float` | cm | `0.f` | FRPGBossMoveCardSpec | 113 |
| `FrontConeDegrees` | `float` | degrees | `0.f` | FRPGBossMoveCardSpec | 114 |
| `MaxVerticalDeltaCm` | `float` | cm | `0.f` | FRPGBossMoveCardSpec | 116 |
| `HPDamage` | `float` | health units per contact | `0.f` | FRPGBossMoveCardSpec | 117 |
| `bUsesRootMotion` | `bool` | boolean | `false` | FRPGBossMoveCardSpec | 119 |
| `Windows` | `TArray<FRPGBossMoveWindow>` | nested data collection | `no in-class initializer` | FRPGBossMoveCardSpec | 120 |
| `Spec` | `FRPGBossMoveCardSpec` | nested editable spec | `no in-class initializer` | URPGBossMoveCard | 128 |
## Nested window data

`FRPGBossMoveWindow` includes `WindowId`, `HitGroup`, `StartSeconds`, `EndSeconds`, `SocketA`, `SocketB`, and `RadiusCm` for a swept blade capsule. Optional `bSecondary` marks a splash window; it must share a hit group with a direct window and is processed after direct windows. `bRing` switches to ring-wave geometry (`RingStartRadiusCm`, `RingSpeedCmPerSecond`, `RingThicknessCm`, `RingHeightCm`, all cm or cm/s). `bGrab` switches to catch/release behavior (`GrabAttachSocket`, `GrabReleaseSeconds` in card seconds). `BakedSamples` stores `TimeSeconds` and `BaseCS`/`TipCS` component-space vectors copied from the animation pose. Pure validation requires at least two strictly ordered, finite samples that span the complete window, stay inside the clip, and have finite bounded vector coordinates (`RPGBossMoveCard.cpp:140-153`). Re-bake after changing the animation: the schema has no source-animation hash/revision link, so validation cannot detect stale baked pose data. Empty samples use live sockets; ring windows forbid sockets and baked samples (`RPGBossMoveCard.cpp:118-121`).

Nested cues use `MoveCard.Cue.*` tokens. Validation returns a named `MoveCard.*` issue; see `RPGBossMoveCard.cpp:31-164` and tests in `RPGBossMoveCardTests.cpp`. For the complete bake → validate → resolve → start/abort path, see [MOVECARD_LIFECYCLE_S144.md](MOVECARD_LIFECYCLE_S144.md).
