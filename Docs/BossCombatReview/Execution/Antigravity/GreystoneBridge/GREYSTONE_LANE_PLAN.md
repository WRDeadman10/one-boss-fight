# Greystone Visual Bridge Staged Source Plan (A-249)

**Document Version:** 1.0.0  
**Author:** Antigravity  
**Task Reference:** `[C-384]`, Order A-249  
**Status:** DELIVERED (Staged Source Plan, Zero Code/Content Edits)  
**Target Engine:** Unreal Engine 5.5.4  

---

## 1. Executive Summary & Lane Definition

The **Greystone Visual Lane** implements a decoupled, non-invasive cosmetic presentation layer for the player character. It resolves historical failure `KI-040` / `KI-052` (where re-pointing 60 core pack assets to `_Grey` copies caused fatal `GetMainAnimBP Accessed None` errors) by guaranteeing that:
1. The Advanced ARPG Combat pack player pawn (`BP_CombatCharacter`) continues running its native gameplay logic, abilities, linked animation Blueprint layers (`ABP_CombatAnimLayersBase`), and mannequin mesh (`SK_CombatMannequin`) without modification.
2. Paragon Greystone (`SK_Greystone`) is added as a purely visual child skeletal mesh that mirrors the gameplay mannequin's pose via Unreal Engine 5.5's native `Retarget Pose From Mesh` node powered by `RTG_CombatMannequin_To_Greystone`.
3. No pack Blueprints, montages, state machines, or animation layers are modified, duplicated, or re-pointed.

---

## 2. Inventory of Required Files & Assets

The Greystone Visual Lane requires exactly four categories of assets and source components:

### 2.1. Existing Foundations (Already on Disk)
- **IK Retargeter:** `Content/OneBossFight/GreystonePack/RTG_CombatMannequin_To_Greystone.uasset` (84,249 bytes)
- **Source IK Rig:** `Content/OneBossFight/GreystonePack/IK_CombatMannequin.uasset` (134,360 bytes)
- **Target IK Rig:** `Content/OneBossFight/Characters/Greystone/IK_Greystone.uasset` (110,643 bytes)
- **Target Skeletal Mesh:** `Content/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone.uasset` (36,449,850 bytes)
- **Target Skeleton:** `Content/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone_Skeleton.uasset`
- **Masking Material:** `Content/OneBossFight/GreystonePack/M_GreyHiddenSlot.uasset` (7,866 bytes)

### 2.2. New Animation Blueprint Asset (To Be Created)
- **Target Asset Path:** `Content/OneBossFight/GreystonePack/ABP_Greystone_VisualBridge.uasset`
- **Parent Class:** `UAnimInstance`
- **Target Skeleton:** `Content/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone_Skeleton.uasset`
- **AnimGraph Topology:**
  ```text
  [Retarget Pose From Mesh] ---> [Output Pose]
  ```
- **Node Configuration (`FAnimNode_RetargetPoseFromMesh`):**
  - Header: `AnimNode_RetargetPoseFromMesh.h:17`
  - `bUseAttachedParent = true` (`AnimNode_RetargetPoseFromMesh.h:27`): Automatically discovers the parent `USkeletalMeshComponent` (`SK_CombatMannequin`) without manual pin wiring.
  - `IKRetargeterAsset = /Game/OneBossFight/GreystonePack/RTG_CombatMannequin_To_Greystone.RTG_CombatMannequin_To_Greystone` (`AnimNode_RetargetPoseFromMesh.h:31`).
  - `LODThresholdForIK = -1` (full solver evaluation).

### 2.3. C++ Staged Source Files (To Be Created)
- `Source/OneBossFight/Player/OneBossFightGreystoneBridgeSubsystem.h`: Declares `UOneBossFightGreystoneBridgeSubsystem` inheriting `UWorldSubsystem` (`WorldSubsystem.h:15`).
- `Source/OneBossFight/Player/OneBossFightGreystoneBridgeSubsystem.cpp`: Implements pawn lifecycle binding, child visual mesh creation, tick prerequisite ordering, hidden-mannequin settings, and weapon socket re-attachment.

### 2.4. Test & Verification Fixtures (To Be Created)
- `Source/OneBossFight/Tests/GreystoneVisualBridgeTests.cpp`: Automation tests verifying tick prerequisite ordering, component attachment hierarchy, bone orientation correlation, and weapon socket world tracking.

---

## 3. Attachment Architecture: Subsystem vs Project Child BP

To add the Greystone visual mesh to the pack player pawn without editing pack Blueprints, two architectural approaches were evaluated:

| Criterion | Approach A: C++ Runtime Subsystem (`UWorldSubsystem`) | Approach B: Project Child Blueprint (`BP_GreystonePlayer_Visual`) |
|:---|:---|:---|
| **Pawn Class** | Native pack `BP_CombatCharacter` unmodified | Project child class subclassing `BP_CombatCharacter` |
| **Pack Assets Touched** | **0 (Zero)** | **0 (Zero)** |
| **Project Assets Touched** | **0 (Zero)** (Injected purely in C++) | **1** (`BP_GreystonePlayer_Visual`) + **1** (GameMode `DefaultPawnClass`) |
| **Risk of `KI-040` Recurrence** | **Zero** (Pawn retains 100% native pack hierarchy) | **Low to Medium** (Child BP can inadvertently override parent construction scripts or components) |
| **Configuration Toggle** | Simple runtime CVAR (`r.OneBossFight.GreystoneVisualBridge 0/1`) | Requires changing GameMode `DefaultPawnClass` |
| **Viewport Visuals** | Created at `BeginPlay` (invisible in Blueprint editor viewport) | Visible at design-time in Blueprint component tree |
| **Code Isolation** | Self-contained in project C++ module | Mixed C++ and Blueprint dependency |

### Architectural Decision: Approach A (C++ Runtime Subsystem) Recommended
**Approach A** is selected as the primary implementation path because it touches **strictly zero existing assets** (neither pack Blueprints nor GameMode assets). It dynamically attaches the visual mesh when the player pawn spawns and can be instantly disabled with a config flag or CVAR if debugging is needed.

### Lifecycle Injection Mechanism:
```cpp
// Source/OneBossFight/Player/OneBossFightGreystoneBridgeSubsystem.cpp
void UOneBossFightGreystoneBridgeSubsystem::OnWorldBeginPlay(UWorld& InWorld) // WorldSubsystem.h:36
{
    Super::OnWorldBeginPlay(InWorld);
    
    // Bind to player controller / pawn possession
    if (APlayerController* PC = InWorld.GetFirstPlayerController())
    {
        if (APawn* Pawn = PC->GetPawn())
        {
            AttachGreystoneVisualBridge(Pawn);
        }
    }
}
```

---

## 4. Hidden-Mannequin Engine Settings

When Paragon Greystone is attached as the visible character, the underlying mannequin mesh (`SK_CombatMannequin`) must be hidden from the player camera while continuing to execute full animation evaluations.

The following engine settings must be applied to `MannequinMeshComponent`:

1. **Uninterrupted Bone Transform Refresh:**
   ```cpp
   // SkinnedMeshComponent.h:87
   MannequinMeshComponent->VisibilityBasedAnimTickOption = 
       EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
   ```
   *Rationale:* Default engine optimization (`OnlyTickPoseWhenRendered`) freezes bone transforms when a mesh is hidden. Setting this to `AlwaysTickPoseAndRefreshBones` guarantees that bone transforms are refreshed every frame so the retargeter always reads fresh poses.

2. **Camera Invisibility:**
   ```cpp
   // SceneComponent.h:210
   MannequinMeshComponent->SetHiddenInGame(true);
   ```
   *Rationale:* Hides the mannequin geometry during gameplay.

3. **Shadow Culling:**
   ```cpp
   MannequinMeshComponent->SetCastShadow(false);
   ```
   *Rationale:* Prevents the hidden mannequin from casting duplicate or overlapping shadows on the arena floor; shadows are cast exclusively by the Greystone visual mesh.

4. **Physics & Gameplay Capsule Invariance:**
   * `UCapsuleComponent` remains the active root collision component for character movement, gravity, and arena boundaries.
   * `MannequinMeshComponent` retains its native collision presets for pack hitboxes and damage traces.

5. **Visual Mask Material Fallback:**
   - As an added safeguard, assign `Content/OneBossFight/GreystonePack/M_GreyHiddenSlot.uasset` to the mannequin's material slots. Even if engine visibility flags are altered dynamically by cinematic sequences or cutscenes, the geometry remains 100% transparent.

---

## 5. Prerequisite Tick Ordering (Zero-Latency Guarantee)

`AnimNode_RetargetPoseFromMesh.h:21` specifies:
> *"The Skeletal Mesh Component to retarget animation from. Assumed to be animated and tick BEFORE this anim instance."*

If tick prerequisites are not established, the engine's task graph may execute Greystone's animation tick before the mannequin's animation tick, causing Greystone to evaluate against the previous frame's bone cache (introducing a 1-frame visual latency and jitter during high-angular-velocity rotations).

### Staged Implementation:
```cpp
// ActorComponent.h:1139
GreystoneMeshComponent->AddTickPrerequisiteComponent(MannequinMeshComponent);
```
This forces the engine's `FTickTaskLevel` to schedule `GreystoneMeshComponent->TickComponent()` strictly after `MannequinMeshComponent->TickComponent()`.

---

## 6. Weapon Re-Attachment Architecture

In the Advanced ARPG Combat pack, weapons are instances of `BP_Weapon_Master` attached to the character's sockets (`hand_r`, `hand_l`, or holstered positions like `KatanaSocket` / `GreatSwordAttachSocket`). Combat melee traces are executed via `UTraceComponent` referencing sockets on the equipped weapon mesh.

### 6.1. Socket Inventory Alignment
- **Source Mannequin Sockets:** `hand_r`, `hand_l`, `GreatSwordAttachSocket`, `KatanaSocket`, `headSocket`.
- **Target Greystone Sockets:** `hand_r`, `hand_l`, `sword_bottom`, `sword_top`, `FX_Sword_Top`, `FX_Sword_Bottom`, `FX_Sword_HiltBase`, `shield_inner`, `shield_outer`.

Both skeletons share identical `hand_r` and `hand_l` naming conventions.

### 6.2. Staged Re-Attachment Sequence
When a weapon actor is spawned or equipped by the pack's inventory component:
```cpp
// SceneComponent.h:701, EngineTypes.h:76
WeaponActor->AttachToComponent(
    GreystoneMeshComponent,
    FAttachmentTransformRules::SnapToTargetNotIncludingScale,
    FName("hand_r")
);
```

### 6.3. Melee Trace Synchronicity
Because `UTraceComponent` queries socket transforms directly from the attached weapon mesh (`WeaponMesh->GetSocketLocation(...)`), re-attaching the weapon to Greystone's `hand_r` socket guarantees that:
1. All weapon melee traces follow the visible sword blade arc with 100% spatial fidelity.
2. Phantom hits (where an invisible blade registers damage away from Greystone's model) and visual misses (where Greystone's visible blade clips through Sevarog without registering) are structurally impossible.

---

## 7. Quantitative Verification & Measurement Tests

To prove mathematically and visually that the Greystone mesh accurately tracks the mannequin pose without latency or drift, the following four automated tests are staged:

### Test 1: Prerequisite Tick Dependency Test (`TEST_ZERO_TICK_LATENCY`)
- **API Call:** `GreystoneMeshComponent->GetPrerequisiteComponents()`
- **Pass Criteria:** `MannequinMeshComponent` is present in the prerequisite list.
- **Tagged Line:**
  ```text
  [VERIFY_TICK] PASS: GreystoneMesh has MannequinMesh as prerequisite component.
  ```

### Test 2: Frame-by-Frame Bone Orientation Tracking (`TEST_BONE_POSE_CORRELATION`)
- **API Calls:** Sample component-space bone rotations per frame across a full attack montage:
  ```cpp
  FQuat Q_Mannequin = MannequinMeshComponent->GetBoneQuaternion(BoneName, EBoneSpaces::ComponentSpace);
  FQuat Q_Greystone = GreystoneMeshComponent->GetBoneQuaternion(BoneName, EBoneSpaces::ComponentSpace);
  float Dot = FMath::Abs(Q_Mannequin | Q_Greystone);
  ```
- **Monitored Bones:** `head`, `upperarm_r`, `lowerarm_r`, `hand_r`, `thigh_r`, `calf_r`, `foot_r`.
- **Pass Criteria:** Quaternion dot product `Dot >= 0.95` across all active swing frames (accounting for minor rest-pose differences mapped in the IK Retargeter).
- **Tagged Line:**
  ```text
  [VERIFY_POSE] PASS: Frame {N} Bone='{BoneName}' QuatDot={Dot:.4f} (Threshold >= 0.9500)
  ```

### Test 3: Weapon Socket World Position Tracking (`TEST_WEAPON_SOCKET_ALIGNMENT`)
- **API Calls:**
  ```cpp
  FVector MannequinHandWorld = MannequinMeshComponent->GetSocketLocation("hand_r");
  FVector GreystoneHandWorld = GreystoneMeshComponent->GetSocketLocation("hand_r");
  float DistanceDelta = FVector::Dist(MannequinHandWorld, GreystoneHandWorld);
  ```
- **Pass Criteria:** `DistanceDelta <= 6.0 cm` (strictly within the physical proportion bound between Greystone's shoulder span and the mannequin's shoulder span; zero sudden spikes across frame boundaries).
- **Tagged Line:**
  ```text
  [VERIFY_SOCKET] PASS: Frame {N} Socket='hand_r' WorldDistDelta={DistanceDelta:.2f}cm (Bound <= 6.00cm)
  ```

### Test 4: Hidden Mannequin Pose Refresh Guard (`TEST_HIDDEN_TICK_INTEGRITY`)
- **API Call:** Sample `MannequinMeshComponent->GetBoneLocation("hand_r")` across consecutive frames while `bHiddenInGame = true`.
- **Pass Criteria:** Hand location transforms change dynamically each frame (proves `AlwaysTickPoseAndRefreshBones` prevents engine culling).
- **Tagged Line:**
  ```text
  [VERIFY_REFRESH] PASS: Hidden mannequin bone transforms updating dynamically (Delta > 0.0cm).
  ```

---

## 8. Verified Engine Citations Summary

| Header | File Path | Line | Symbol / Declaration |
|:---|:---|:---:|:---|
| `AnimNode_RetargetPoseFromMesh.h` | `Engine/Plugins/Animation/IKRig/Source/IKRig/Public/AnimNodes/` | 17 | `struct IKRIG_API FAnimNode_RetargetPoseFromMesh : public FAnimNode_Base` |
| `AnimNode_RetargetPoseFromMesh.h` | `Engine/Plugins/Animation/IKRig/Source/IKRig/Public/AnimNodes/` | 27 | `bool bUseAttachedParent = true;` |
| `AnimNode_RetargetPoseFromMesh.h` | `Engine/Plugins/Animation/IKRig/Source/IKRig/Public/AnimNodes/` | 31 | `TObjectPtr<UIKRetargeter> IKRetargeterAsset = nullptr;` |
| `AnimGraphNode_RetargetPoseFromMesh.h` | `Engine/Plugins/Animation/IKRig/Source/IKRigDeveloper/Public/` | 16 | `class IKRIGDEVELOPER_API UAnimGraphNode_RetargetPoseFromMesh : public UAnimGraphNode_Base` |
| `ActorComponent.h` | `Engine/Source/Runtime/Engine/Classes/Components/` | 1139 | `ENGINE_API virtual void AddTickPrerequisiteComponent(UActorComponent* PrerequisiteComponent);` |
| `SkinnedMeshComponent.h` | `Engine/Source/Runtime/Engine/Classes/Components/` | 87 | `AlwaysTickPoseAndRefreshBones,` (`EVisibilityBasedAnimTickOption`) |
| `SceneComponent.h` | `Engine/Source/Runtime/Engine/Classes/Components/` | 210 | `uint8 bHiddenInGame:1;` |
| `SceneComponent.h` | `Engine/Source/Runtime/Engine/Classes/Components/` | 701 | `ENGINE_API virtual bool AttachToComponent(USceneComponent* InParent, ...);` |
| `EngineTypes.h` | `Engine/Source/Runtime/Engine/Classes/Engine/` | 71 | `struct FAttachmentTransformRules` |
| `EngineTypes.h` | `Engine/Source/Runtime/Engine/Classes/Engine/` | 76 | `static ENGINE_API FAttachmentTransformRules SnapToTargetNotIncludingScale;` |
| `WorldSubsystem.h` | `Engine/Source/Runtime/Engine/Public/Subsystems/` | 15 | `class UWorldSubsystem : public USubsystem` |
| `WorldSubsystem.h` | `Engine/Source/Runtime/Engine/Public/Subsystems/` | 36 | `virtual void OnWorldBeginPlay(UWorld& InWorld) {}` |

---

## 9. Next Steps for Execution Lane (Phase F5)

1. **Step 1 (Offline Blueprint Automation / Editor Helper):** Author helper to generate `Content/OneBossFight/GreystonePack/ABP_Greystone_VisualBridge.uasset` with configured `FAnimNode_RetargetPoseFromMesh`.
2. **Step 2 (C++ Implementation):** Implement `UOneBossFightGreystoneBridgeSubsystem` in `Source/OneBossFight/Player/`.
3. **Step 3 (Automated Verification):** Execute `GreystoneVisualBridgeTests.cpp` in `-nullrhi` test runner and verify zero-latency tracking lines.
