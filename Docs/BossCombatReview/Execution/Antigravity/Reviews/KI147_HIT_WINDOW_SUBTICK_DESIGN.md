# KI-147 Sub-Tick Hit Window Sweep Design: Runtime Pose Extraction vs Baked Blade Path

**Author:** Antigravity  
**Date:** 2026-10-30  
**Context:** Lead Order `[C-424]` design for eliminating thrust apex chord cutting across frame hitches in `RPGFrameworkMoveExecutor`.  
**Target:** UE 5.5.4, OneBossFight Sevarog Combat Framework  

---

## 1. Executive Summary & Problem Recap

In `[A-305]`, we proved that the AntiGreed miss during 72 ms hitches is caused by linear spatial Lerp of blade endpoints across the active hit window:
$$\text{Lerp}(P_{\text{windup}}, P_{\text{retraction}}, \alpha)$$
Because the scythe performs an out-and-back jab, linear interpolation across a hitch cuts off the forward apex trajectory, producing a 43.9 cm spatial gap between the interpolated blade chord and the player target capsule boundary (radius 42.0 cm).

To ensure 100% reliable hit detection regardless of frame rate drops, two architectural solutions exist:
1. **Option 1 (Runtime Pose Extraction):** Dynamically evaluate the animation sequence at intermediate sub-tick timestamps using UE 5.5 animation runtime APIs.
2. **Option 2 (Baked Blade Path in Data):** Bake component-space blade transforms sampled at 120 Hz directly into the MoveCard data asset.

---

## 2. Option 1: Runtime Sub-Tick Animation Pose Extraction (UE 5.5)

### 2.1 Engine Header Citations & Core APIs

In Unreal Engine 5.5.4, runtime pose decompression from a `UAnimSequence` requires constructing an animation pose context, extracting the local pose, and building component-space transforms:

1. **`UAnimSequence::GetBonePose`:**  
   `C:/Program Files/Epic Games/UE_5.5/Engine/Source/Runtime/Engine/Classes/Animation/AnimSequence.h:480`
   ```cpp
   ENGINE_API void GetBonePose(struct FAnimationPoseData& OutAnimationPoseData, const FAnimExtractContext& ExtractionContext, bool bForceUseRawData = false) const;
   ```
2. **`FAnimationPoseData` Wrapper:**  
   `C:/Program Files/Epic Games/UE_5.5/Engine/Source/Runtime/Engine/Classes/Animation/AnimationPoseData.h:15-18`
   ```cpp
   struct FAnimationPoseData {
       ENGINE_API FAnimationPoseData(FCompactPose& InPose, FBlendedCurve& InCurve, UE::Anim::FStackAttributeContainer& InAttributes);
   };
   ```
3. **`FBoneContainer` & `FCompactPose`:**  
   `C:/Program Files/Epic Games/UE_5.5/Engine/Source/Runtime/Engine/Public/BoneContainer.h:50`  
   Holds the compact pose bone mapping initialized from the target `USkeletalMesh` asset and required bone indices.
4. **`FCSPose<FCompactPose>` (Component-Space Conversion):**  
   `C:/Program Files/Epic Games/UE_5.5/Engine/Source/Runtime/Engine/Public/BonePose.h:407, 466`
   ```cpp
   template<class PoseType> struct FCSPose {
       void InitPose(const PoseType& SrcPose);
       const FTransform& GetComponentSpaceTransform(BoneIndexType BoneIndex);
   };
   ```

### 2.2 Component-Space Bone Chain for `weapon_r` and `root_weapon_end_r`

On the Sevarog skeleton (`Sevarog_Skeleton`), the weapon bones have two distinct hierarchies:
- `weapon_r` is attached to `hand_r` -> `lowerarm_r` -> `upperarm_r` -> `clavicle_r` -> `spine_03` -> `spine_02` -> `spine_01` -> `pelvis` -> `root`.
- `root_weapon_end_r` is a virtual/socket bone attached to `root` or `weapon_r` (depending on retarget setup).

`FCSPose<FCompactPose>::GetComponentSpaceTransform` lazily evaluates and accumulates parent transforms up the skeleton chain:
$$T_{\text{CS}}(\text{bone}) = T_{\text{local}}(\text{bone}) \times T_{\text{local}}(\text{parent}) \times \dots \times T_{\text{local}}(\text{root})$$

### 2.3 Runtime C++ Sketch (UE 5.5 Compatible)

```cpp
#include "Animation/AnimSequence.h"
#include "Animation/AnimationPoseData.h"
#include "BoneContainer.h"
#include "BonePose.h"

bool ExtractSubTickBladePose(
    const UAnimSequence* Sequence,
    const USkeletalMeshComponent* MeshComp,
    double TimeSeconds,
    FVector& OutBaseWorld,
    FVector& OutTipWorld)
{
    if (!Sequence || !MeshComp || !MeshComp->GetSkeletalMeshAsset()) return false;

    // 1. Setup Bone Container for required bones
    const USkeleton* Skeleton = Sequence->GetSkeleton();
    const FReferenceSkeleton& RefSkeleton = MeshComp->GetSkeletalMeshAsset()->GetRefSkeleton();
    
    // In practice, BoneContainer should be cached on the executor during Initialize
    FBoneContainer BoneContainer;
    TArray<FBoneIndexType> RequiredBones;
    const int32 BoneBase = RefSkeleton.FindBoneIndex(TEXT("weapon_r"));
    const int32 BoneTip = RefSkeleton.FindBoneIndex(TEXT("root_weapon_end_r"));
    if (BoneBase == INDEX_NONE || BoneTip == INDEX_NONE) return false;
    
    // Add required bone indices up the parent hierarchy
    for (int32 Curr = BoneBase; Curr != INDEX_NONE; Curr = RefSkeleton.GetParentIndex(Curr)) RequiredBones.AddUnique(Curr);
    for (int32 Curr = BoneTip; Curr != INDEX_NONE; Curr = RefSkeleton.GetParentIndex(Curr)) RequiredBones.AddUnique(Curr);
    RequiredBones.Sort();
    
    BoneContainer.InitializeTo(RequiredBones, UE::Anim::FCurveFilterSettings(), *MeshComp->GetSkeletalMeshAsset());

    // 2. Allocate Compact Pose and Extraction Context
    FCompactPose CompactPose;
    CompactPose.SetBoneContainer(&BoneContainer);
    CompactPose.ResetToRefPose();

    FBlendedCurve Curve;
    Curve.InitFrom(BoneContainer);
    UE::Anim::FStackAttributeContainer Attributes;
    FAnimationPoseData PoseData(CompactPose, Curve, Attributes);
    FAnimExtractContext ExtractContext(TimeSeconds, true);

    // 3. Extract Local Pose from Sequence
    Sequence->GetBonePose(PoseData, ExtractContext);

    // 4. Convert to Component Space via FCSPose
    FCSPose<FCompactPose> CSPose;
    CSPose.InitPose(CompactPose);

    const FCompactPoseBoneIndex CompactBase = BoneContainer.GetCompactPoseIndexFromSkeletonPoseIndex(FSkeletonPoseBoneIndex(BoneBase));
    const FCompactPoseBoneIndex CompactTip = BoneContainer.GetCompactPoseIndexFromSkeletonPoseIndex(FSkeletonPoseBoneIndex(BoneTip));
    
    const FTransform BaseCS = CSPose.GetComponentSpaceTransform(CompactBase);
    const FTransform TipCS = CSPose.GetComponentSpaceTransform(CompactTip);

    // 5. Transform to World Space
    const FTransform& CompToWorld = MeshComp->GetComponentTransform();
    OutBaseWorld = CompToWorld.TransformPosition(BaseCS.GetLocation());
    OutTipWorld = CompToWorld.TransformPosition(TipCS.GetLocation());
    return true;
}
```

### 2.4 Drawbacks of Option 1
- **Heavy GameThread Overhead:** Decompressing animation curves and evaluating bone matrices dynamically during hit resolution creates CPU spikes on the GameThread—precisely when the frame rate is already stuttering!
- **Dynamic Allocation:** `FAnimationPoseData`, `FCompactPose`, and curve buffers involve heap churn unless statically pooled per executor.
- **Complex Retargeting/Blend States:** If montages use slot blending or layer filters, evaluating raw `UAnimSequence` bypasses the AnimBP state machine.

---

## 3. Option 2: Baked Blade Path in MoveCard Data (Recommended)

### 3.1 Concept
Instead of evaluating animation curves at runtime, the exact blade trajectory is sampled offline during asset compilation / authoring (e.g. at 120 Hz) and stored directly in the `URPGBossMoveCard` asset. 

When a tick spans across a hitch `[PrevPosition .. Position]`, `RPGFrameworkMoveExecutor::SweepWindows` iterates through all baked samples falling within `[Lo .. Hi]` and sweeps capsules between consecutive baked samples.

### 3.2 UPROPERTY Data Structs

Add to `Source/OneBossFight/Player/RPGBossMoveCard.h`:

```cpp
/** A single baked blade sample in actor/component space. */
USTRUCT(BlueprintType)
struct ONEBOSSFIGHT_API FRPGBakedBladeSample
{
    GENERATED_BODY()

    /** Local time in seconds within the animation clip. */
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "MoveWindow")
    float TimeSeconds = 0.f;

    /** Component-space position of SocketA (weapon_r base). */
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "MoveWindow")
    FVector3f BaseCS = FVector3f::ZeroVector;

    /** Component-space position of SocketB (root_weapon_end_r tip). */
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "MoveWindow")
    FVector3f TipCS = FVector3f::ZeroVector;
};
```

Extend `FRPGBossMoveWindow` (`RPGBossMoveCard.h`):
```cpp
    /** Baked component-space samples at 120 Hz across [StartSeconds .. EndSeconds]. */
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "MoveWindow")
    TArray<FRPGBakedBladeSample> BakedSamples;
```

### 3.3 Payload Size & Memory Footprint

- Each `FRPGBakedBladeSample`:  
  `sizeof(float) + 2 * sizeof(FVector3f) = 4 + 12 + 12 = 28 bytes`.
- For AntiGreed (`Window_AntiGreed_FastJab`):  
  Duration: `0.3083 - 0.2500 = 0.0583 s`.  
  At 120 Hz ($dt = 0.00833\text{ s}$): $\lceil 0.0583 / 0.00833 \rceil + 1 = 8\text{ samples}$.  
  Total size: $8 \times 28\text{ bytes} = \mathbf{224\text{ bytes}}$!
- For a wide 0.5 s swing:  
  $\approx 61\text{ samples} \times 28\text{ bytes} = \mathbf{1.7\text{ KB}}$.
- Across all 5 MoveCards combined: **$< 10\text{ KB}$ total asset payload**.

### 3.4 Authoring-Tool Generator Extension

Our Python script `Docs/BossCombatReview/Execution/Antigravity/MoveCards/probe_reach.py` already uses `unreal.AnimPoseExtensions.get_bone_pose` to measure sockets across sequence timelines.

In `Docs/BossCombatReview/Execution/Antigravity/MoveCards/author_move_cards.py`:
```python
def bake_window_samples(seq, socket_a, socket_b, start_sec, end_sec, hz=120.0):
    dt = 1.0 / hz
    t = start_sec
    samples = []
    while t <= end_sec + 1e-4:
        pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, unreal.AnimPoseEvaluationOptions())
        t_a = unreal.AnimPoseExtensions.get_bone_pose(pose, socket_a, unreal.AnimPoseSpaces.ROOT)
        t_b = unreal.AnimPoseExtensions.get_bone_pose(pose, socket_b, unreal.AnimPoseSpaces.ROOT)
        samples.append({
            'TimeSeconds': round(t, 4),
            'BaseCS': [round(t_a.translation.x, 2), round(t_a.translation.y, 2), round(t_a.translation.z, 2)],
            'TipCS': [round(t_b.translation.x, 2), round(t_b.translation.y, 2), round(t_b.translation.z, 2)]
        })
        t += dt
    return samples
```

### 3.5 MoveCard Validator Rules (`RPGBossMoveCard.cpp`)

Extend `ValidateMoveCard()` with four deterministic rules:
1. `BakedSamples.Num() >= 2` for every window with duration $> 0.01\text{ s}$.
2. Monotonic timestamps: `BakedSamples[i].TimeSeconds < BakedSamples[i+1].TimeSeconds`.
3. Boundary coverage: `BakedSamples[0].TimeSeconds <= StartSeconds + 1e-3` and `BakedSamples.Last().TimeSeconds >= EndSeconds - 1e-3`.
4. Max sample step: `BakedSamples[i+1].TimeSeconds - BakedSamples[i].TimeSeconds <= (1.0f / 60.0f) + 1e-3` (maximum 16.7 ms step, nominal 8.3 ms).
5. Geometry consistency: For every sample, `FVector3f::Dist(BaseCS, TipCS)` must be within $[40.0, 200.0]\text{ cm}$ (rejects uninitialized zero transforms).

---

## 4. Definitive Recommendation: Option 2 (Baked Blade Path)

| Criterion | Option 1 (Runtime Pose Extraction) | Option 2 (Baked Blade Path) | Winner |
|:---|:---:|:---:|:---:|
| **Runtime CPU Cost** | High (pose decompression, skeleton traversal) | Zero (plain array lookup + matrix transform) | **Option 2** |
| **Memory Allocation** | Heap allocation for pose buffers | Zero runtime allocation | **Option 2** |
| **Determinism** | Dependent on engine decompression state | 100% deterministic & invariant across all hardware | **Option 2** |
| **Footprint** | 0 bytes disk, ~100 KB transient RAM | $< 2\text{ KB}$ per card in data asset | **Option 2** |
| **Frame Hitch Resilience** | Tolerant, but slows down struggling frames | Perfect coverage across arbitrary hitch lengths | **Option 2** |
| **Implementation Risk** | High (UE 5.5 API changes, AnimBP bypass) | Low (data-driven schema extension) | **Option 2** |

**Recommendation:** Proceed with **Option 2 (Baked Blade Path)**. It aligns perfectly with the project's data-driven architecture, adds $< 10\text{ KB}$ to data assets, and completely decouples combat hit registration from engine frame rate jitter.

---

## 5. Sweep-Coverage Unit Test Specification

To verify the fix offline before any PIE run, implement the following test in `Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp`:

```cpp
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FRPGBossSweepHitchCoverageTest,
    "OneBossFight.Framework.Runtime.SweepHitchCoverage",
    EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter)

bool FRPGBossSweepHitchCoverageTest::RunTest(const FString& Parameters)
{
    // 1. Create Mock Card with AntiGreed Window [0.25 .. 0.3083]
    FRPGBossMoveCardSpec Spec;
    Spec.MoveId = TEXT("Move_AntiGreed_Test");
    FRPGBossMoveWindow Window;
    Window.WindowId = TEXT("Window_AntiGreed");
    Window.StartSeconds = 0.25f;
    Window.EndSeconds = 0.3083f;
    Window.RadiusCm = 30.f;

    // 2. Populate 120 Hz Baked Samples with apex at 0.267 s (Base X = 13.67 cm, penetrating target at X=0, R=42)
    // Windup at 0.25s: Base X = 115 cm
    // Apex at 0.267s: Base X = 13.67 cm (HIT!)
    // Retract at 0.308s: Base X = 146 cm
    PopulateMockBakedThrustSamples(Window.BakedSamples);
    Spec.Windows.Add(Window);

    // 3. Simulate a massive 72 ms hitch spanning across the entire window:
    // PrevPosition = 0.225 s, Position = 0.298 s
    TArray<FVector> SweptCapsulePositions;
    ExecuteSweepSampling(Spec, /*PrevPosition=*/0.225, /*Position=*/0.298, SweptCapsulePositions);

    // 4. Assertions:
    // With linear interpolation (legacy bug), min X was 85.9 cm -> FAIL (missed target at X <= 42 cm)
    // With baked blade path, the apex sample at 0.267 s is evaluated -> PASS (min X <= 15.0 cm)
    float MinX = MAX_flt;
    for (const FVector& P : SweptCapsulePositions) MinX = FMath::Min(MinX, float(P.X));

    TestTrue(TEXT("Baked blade path evaluated apex during 72ms hitch"), MinX <= 42.0f);
    TestTrue(TEXT("Deep capsule penetration registered"), MinX <= 15.0f);
    return true;
}
```
