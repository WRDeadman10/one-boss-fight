# Sevarog First Five Move Cards: Typed Spec Table (A-246)

**Document Version:** 1.0.0  
**Author:** Antigravity  
**Task Reference:** `[C-380]`, Order A-246  
**Status:** DELIVERED (Typed Authoring Spec, Offline, Zero Content/Source Writes)  
**Target C++ Struct:** `FRPGBossMoveCardSpec` in `Source/OneBossFight/Player/RPGBossMoveCard.h:29-54`  

---

## 1. Specification Overview

This document provides the authoritative typed field values for Sevarog's first five move cards, structured strictly to match the runtime C++ schema defined in `Source/OneBossFight/Player/RPGBossMoveCard.h`.

Per `[C-380]`, all timing fields (`CommitSeconds`, `ActiveStartSeconds`, `ActiveEndSeconds`, `RecoveryEndSeconds`, and window `StartSeconds`/`EndSeconds`) are **intentionally left empty / TBD**, awaiting empirical weapon motion measurements from the Hit-Window Extraction Probe (`probe_weapon_motion.py`, A-243).

### C++ Struct Definitions (Live in `Source/OneBossFight/Player/RPGBossMoveCard.h`)
- **`FRPGBossMoveCardSpec`:**
  - `int32 Schema = 1`
  - `FName MoveId`
  - `FName FamilyId`
  - `FName PhaseId`
  - `TSoftObjectPtr<USkeleton> Skeleton`
  - `TSoftObjectPtr<UAnimSequence> Sequence`
  - `TSoftObjectPtr<UAnimMontage> Montage`
  - `FName SlotName`
  - `FName SectionName`
  - `float PlayRate`
  - `float CommitSeconds` *(TBD from Probe)*
  - `float ActiveStartSeconds` *(TBD from Probe)*
  - `float ActiveEndSeconds` *(TBD from Probe)*
  - `float RecoveryEndSeconds` *(TBD from Probe)*
  - `float TrackDegreesPerSecond`
  - `float MinRangeCm`
  - `float MaxRangeCm`
  - `float FrontConeDegrees`
  - `float HPDamage` *(TBD in F4)*
  - `bool bUsesRootMotion`
  - `TArray<FRPGBossMoveWindow> Windows` *(Timings TBD from Probe)*
- **`FRPGBossMoveWindow`:**
  - `FName WindowId`
  - `FName HitGroup`
  - `float StartSeconds` *(TBD from Probe)*
  - `float EndSeconds` *(TBD from Probe)*
  - `FName SocketA`
  - `FName SocketB`
  - `float RadiusCm`

---

## 2. Master Spec Table (21 Fields per Card)

| Field Name | Type | MC-01: `DA_Card_SwingSlow` | MC-02: `DA_Card_SwingMedium` | MC-03: `DA_Card_AntiGreed` | MC-04: `DA_Card_HeavySlam` | MC-05: `DA_Card_Speedburst` | Notes & Constraints |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Schema` | `int32` | `1` | `1` | `1` | `1` | `1` | Non-zero valid schema token |
| `MoveId` | `FName` | `Move_Sevarog_SwingSlow` | `Move_Sevarog_SwingMedium` | `Move_Sevarog_AntiGreed` | `Move_Sevarog_HeavySlam` | `Move_Sevarog_Speedburst` | Unique monotonic encounter identifier |
| `FamilyId` | `FName` | `Family_01_DelayedOverhead` | `Family_08_ComboSweep` | `Family_02_AntiGreed` | `Family_06_HeavySlam` | `Family_05_GapCloser` | Morgott 15-family mapping |
| `PhaseId` | `FName` | `Phase_1` | `Phase_1` | `Phase_1` | `Phase_1` | `Phase_1` | Active phase mask |
| `Skeleton` | `SoftObject` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog_Skeleton.Sevarog_Skeleton` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog_Skeleton.Sevarog_Skeleton` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog_Skeleton.Sevarog_Skeleton` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog_Skeleton.Sevarog_Skeleton` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog_Skeleton.Sevarog_Skeleton` | Exact skeleton identity check |
| `Sequence` | `SoftObject` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_Slow.Swing1_Slow` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing2_Medium.Swing2_Medium` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_Medium.Swing1_Medium`* | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing3_Slow.Swing3_Slow` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Speedburst.Speedburst` | Exactly one animation source (*MC-03 substituted to probe-backed Swing1_Medium per C-390) |
| `Montage` | `SoftObject` | `None` | `None` | `None` | `None` | `None` | Pure sequence playback via dynamic montage |
| `SlotName` | `FName` | `FullBody` | `FullBody` | `FullBody` | `FullBody` | `FullBody` | Verified Sevarog AnimBP slot node (`C-376`) |
| `SectionName` | `FName` | `None` | `None` | `None` | `None` | `None` | `None` = full animation sequence length |
| `PlayRate` | `float` | `1.0` | `1.0` | `1.0` | `1.0` | `1.0` | Positive playback rate multiplier |
| `CommitSeconds` | `float` | **[PROBE TBD]** | **[PROBE TBD]** | **[PROBE TBD]** | **[PROBE TBD]** | **[PROBE TBD]** | Rotation tracking cutoff; populates from probe |
| `ActiveStartSeconds` | `float` | **[PROBE TBD]** | **[PROBE TBD]** | **[PROBE TBD]** | **[PROBE TBD]** | **[PROBE TBD]** | Hitbox activation start; populates from probe |
| `ActiveEndSeconds` | `float` | **[PROBE TBD]** | **[PROBE TBD]** | **[PROBE TBD]** | **[PROBE TBD]** | **[PROBE TBD]** | Hitbox deactivation; populates from probe |
| `RecoveryEndSeconds` | `float` | **[PROBE TBD]** | **[PROBE TBD]** | **[PROBE TBD]** | **[PROBE TBD]** | **[PROBE TBD]** | Full clip recovery completion; populates from probe |
| `TrackDegreesPerSec` | `float` | `90.0` | `120.0` | `180.0` | `45.0` | `0.0` | Yaw tracking speed during windup phase |
| `MinRangeCm` | `float` | `200.0` | `150.0` | `0.0` | `180.0` | `400.0` | Proposed distance gate minimum |
| `MaxRangeCm` | `float` | `400.0` | `350.0` | `220.0` | `420.0` | `950.0` | Proposed distance gate maximum |
| `FrontConeDegrees` | `float` | `100.0` | `140.0` | `80.0` | `60.0` | `50.0` | Symmetric full cone (|signed yaw| <= cone/2) |
| `HPDamage` | `float` | `[F4 TBD]` | `[F4 TBD]` | `[F4 TBD]` | `[F4 TBD]` | `[F4 TBD]` | Ratified in F4 damage pass |
| `bUsesRootMotion` | `bool` | `false` | `false` | `false` | `false` | `false` | In-place only; backend fails closed on true |
| `Windows` | `TArray` | 1 Window (see §3) | 1 Window (see §3) | 1 Window (see §3) | 1 Window (see §3) | 0 Windows (Dash) | Swept segment definition |

---

## 3. Swept Hit-Window Specifications (`FRPGBossMoveWindow`)

> [!NOTE]
> **Weapon Track Verification (C-396 / F3b run1)**:  
> Live inspection via `get_animation_track_names` in Claude F3b `run1` confirms that both `weapon_r` and `root_weapon_end_r` possess dedicated animation tracks (155 total sequence tracks). Weapon trajectory evaluates direct bone keyframe animation in addition to arm hierarchy kinematics.


Each damaging card defines exactly one primary swept capsule segment:

### MC-01: `DA_Card_SwingSlow`
- `WindowId`: `Window_SwingSlow_Primary`
- `HitGroup`: `HitGroup_ScytheBlade`
- `StartSeconds`: **[PROBE TBD]**
- `EndSeconds`: **[PROBE TBD]**
- `SocketA`: `weapon_r` (scythe grip base)
- `SocketB`: `root_weapon_end_r` (scythe blade tip)
- `RadiusCm`: `15.0`

### MC-02: `DA_Card_SwingMedium`
- `WindowId`: `Window_SwingMedium_Sweep`
- `HitGroup`: `HitGroup_ScytheBlade`
- `StartSeconds`: **[PROBE TBD]**
- `EndSeconds`: **[PROBE TBD]**
- `SocketA`: `weapon_r`
- `SocketB`: `root_weapon_end_r`
- `RadiusCm`: `15.0`

### MC-03: `DA_Card_AntiGreed`
- `WindowId`: `Window_AntiGreed_Jab`
- `HitGroup`: `HitGroup_ScytheShaft`
- `StartSeconds`: **0.1500s** *(design value derived from probe run_C379)*
- `EndSeconds`: **0.2667s** *(design value derived from probe run_C379)*
- `SocketA`: `weapon_r`
- `SocketB`: `root_weapon_end_r`
- `RadiusCm`: `12.0`
- `DerivationNote`: Bridges twin 1-sample spikes (0.15s and 0.25s); labelled "bridged, design value" per C-390. Sequence substituted to probe-backed `Swing1_Medium` pending future probe of `Swing1_FAST_v2`.

### MC-04: `DA_Card_HeavySlam`
- `WindowId`: `Window_HeavySlam_Terminal`
- `HitGroup`: `HitGroup_ScytheHead`
- `StartSeconds`: **[PROBE TBD]**
- `EndSeconds`: **[PROBE TBD]**
- `SocketA`: `weapon_r`
- `SocketB`: `root_weapon_end_r`
- `RadiusCm`: `25.0`

### MC-05: `DA_Card_Speedburst`
- `Windows`: Empty array `[]` (Movement gap-closer card; non-damaging rush).

---

## 4. JSON Template for Automated Authoring (F4/F5 Ingestion)

```json
[
  {
    "Schema": 1,
    "MoveId": "Move_Sevarog_SwingSlow",
    "FamilyId": "Family_01_DelayedOverhead",
    "PhaseId": "Phase_1",
    "Skeleton": "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog_Skeleton.Sevarog_Skeleton",
    "Sequence": "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_Slow.Swing1_Slow",
    "Montage": null,
    "SlotName": "FullBody",
    "SectionName": "None",
    "PlayRate": 1.0,
    "CommitSeconds": null,
    "ActiveStartSeconds": null,
    "ActiveEndSeconds": null,
    "RecoveryEndSeconds": null,
    "TrackDegreesPerSecond": 90.0,
    "MinRangeCm": 200.0,
    "MaxRangeCm": 400.0,
    "FrontConeDegrees": 100.0,
    "HPDamage": null,
    "bUsesRootMotion": false,
    "Windows": [
      {
        "WindowId": "Window_SwingSlow_Primary",
        "HitGroup": "HitGroup_ScytheBlade",
        "StartSeconds": null,
        "EndSeconds": null,
        "SocketA": "weapon_r",
        "SocketB": "root_weapon_end_r",
        "RadiusCm": 15.0
      }
    ]
  },
  {
    "Schema": 1,
    "MoveId": "Move_Sevarog_SwingMedium",
    "FamilyId": "Family_08_ComboSweep",
    "PhaseId": "Phase_1",
    "Skeleton": "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog_Skeleton.Sevarog_Skeleton",
    "Sequence": "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing2_Medium.Swing2_Medium",
    "Montage": null,
    "SlotName": "FullBody",
    "SectionName": "None",
    "PlayRate": 1.0,
    "CommitSeconds": null,
    "ActiveStartSeconds": null,
    "ActiveEndSeconds": null,
    "RecoveryEndSeconds": null,
    "TrackDegreesPerSecond": 120.0,
    "MinRangeCm": 150.0,
    "MaxRangeCm": 350.0,
    "FrontConeDegrees": 140.0,
    "HPDamage": null,
    "bUsesRootMotion": false,
    "Windows": [
      {
        "WindowId": "Window_SwingMedium_Sweep",
        "HitGroup": "HitGroup_ScytheBlade",
        "StartSeconds": null,
        "EndSeconds": null,
        "SocketA": "weapon_r",
        "SocketB": "root_weapon_end_r",
        "RadiusCm": 15.0
      }
    ]
  },
  {
    "Schema": 1,
    "MoveId": "Move_Sevarog_AntiGreed",
    "FamilyId": "Family_02_AntiGreed",
    "PhaseId": "Phase_1",
    "Skeleton": "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog_Skeleton.Sevarog_Skeleton",
    "Sequence": "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_FAST_v2.Swing1_FAST_v2",
    "Montage": null,
    "SlotName": "FullBody",
    "SectionName": "None",
    "PlayRate": 1.0,
    "CommitSeconds": null,
    "ActiveStartSeconds": null,
    "ActiveEndSeconds": null,
    "RecoveryEndSeconds": null,
    "TrackDegreesPerSecond": 180.0,
    "MinRangeCm": 0.0,
    "MaxRangeCm": 220.0,
    "FrontConeDegrees": 80.0,
    "HPDamage": null,
    "bUsesRootMotion": false,
    "Windows": [
      {
        "WindowId": "Window_AntiGreed_Jab",
        "HitGroup": "HitGroup_ScytheShaft",
        "StartSeconds": null,
        "EndSeconds": null,
        "SocketA": "weapon_r",
        "SocketB": "root_weapon_end_r",
        "RadiusCm": 12.0
      }
    ]
  },
  {
    "Schema": 1,
    "MoveId": "Move_Sevarog_HeavySlam",
    "FamilyId": "Family_06_HeavySlam",
    "PhaseId": "Phase_1",
    "Skeleton": "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog_Skeleton.Sevarog_Skeleton",
    "Sequence": "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing3_Slow.Swing3_Slow",
    "Montage": null,
    "SlotName": "FullBody",
    "SectionName": "None",
    "PlayRate": 1.0,
    "CommitSeconds": null,
    "ActiveStartSeconds": null,
    "ActiveEndSeconds": null,
    "RecoveryEndSeconds": null,
    "TrackDegreesPerSecond": 45.0,
    "MinRangeCm": 180.0,
    "MaxRangeCm": 420.0,
    "FrontConeDegrees": 60.0,
    "HPDamage": null,
    "bUsesRootMotion": false,
    "Windows": [
      {
        "WindowId": "Window_HeavySlam_Terminal",
        "HitGroup": "HitGroup_ScytheHead",
        "StartSeconds": null,
        "EndSeconds": null,
        "SocketA": "weapon_r",
        "SocketB": "root_weapon_end_r",
        "RadiusCm": 25.0
      }
    ]
  },
  {
    "Schema": 1,
    "MoveId": "Move_Sevarog_Speedburst",
    "FamilyId": "Family_05_GapCloser",
    "PhaseId": "Phase_1",
    "Skeleton": "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog_Skeleton.Sevarog_Skeleton",
    "Sequence": "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Speedburst.Speedburst",
    "Montage": null,
    "SlotName": "FullBody",
    "SectionName": "None",
    "PlayRate": 1.0,
    "CommitSeconds": null,
    "ActiveStartSeconds": null,
    "ActiveEndSeconds": null,
    "RecoveryEndSeconds": null,
    "TrackDegreesPerSecond": 0.0,
    "MinRangeCm": 400.0,
    "MaxRangeCm": 950.0,
    "FrontConeDegrees": 50.0,
    "HPDamage": 0.0,
    "bUsesRootMotion": false,
    "Windows": []
  }
]
```
