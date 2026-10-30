# Greystone Visual AnimBP Authoring Options Analysis (A-251)

**Document Version:** 1.0.0  
**Author:** Antigravity  
**Task Reference:** `[C-386]`, Order A-251  
**Status:** DELIVERED (Technical Research Report, Offline Engine Codebase Audit)  
**Target Engine:** Unreal Engine 5.5.4  

---

## 1. Executive Summary & Direct Answer

**Core Question:** Can the Greystone visual AnimBP (`ABP_Greystone_VisualBridge` with a `Retarget Pose From Mesh` node using `RTG_CombatMannequin_To_Greystone`) be created and its graph authored entirely via editor Python in UE 5.5, or does it require a hand-made asset or a C++ editor helper?

**Direct Technical Verdict:**
1. **Asset Container Creation:** Editor Python **CAN** create the blank `UAnimBlueprint` asset container using `unreal.AnimBlueprintFactory`.
2. **AnimGraph Node Spawning & Pin Wiring:** Editor Python **CANNOT** author the inner graph. Unreal Engine 5.5 exposes **zero reflection or scripting APIs** (neither in Python nor in Blueprint) for instantiating `UAnimGraphNode` objects, inserting them into `UAnimationGraph`, or connecting `UEdGraphPin`s.
3. **Final Recommendation:** **Path D (Hand-Made Asset Created in Editor GUI)** is the definitive recommended path. It takes under 30 seconds, uses native engine serialization, introduces zero packaging risks, and fully decouples visual presentation from custom code.

---

## 2. Exhaustive Engine Public API Audit (File:Line Citations)

Every engine header cited below was inspected directly on disk from the official UE 5.5.4 engine installation:

### 2.1. `UAnimBlueprintFactory` (Asset Creation API)
- **Header:** `C:/Program Files/Epic Games/UE_5.5/Engine/Source/Editor/UnrealEd/Classes/Factories/AnimBlueprintFactory.h:17-47`
- **Class Declaration:**
  ```cpp
  // AnimBlueprintFactory.h:17
  UCLASS(HideCategories=Object, MinimalAPI)
  class UAnimBlueprintFactory : public UFactory
  {
      GENERATED_UCLASS_BODY()
      UPROPERTY(EditAnywhere, Category=AnimBlueprintFactory)
      TEnumAsByte<EBlueprintType> BlueprintType;

      UPROPERTY(EditAnywhere, Category=AnimBlueprintFactory, meta=(AllowAbstract = ""))
      TSubclassOf<class UAnimInstance> ParentClass; // L27

      UPROPERTY(EditAnywhere, Category=AnimBlueprintFactory)
      TObjectPtr<class USkeleton> TargetSkeleton; // L31

      UPROPERTY(EditAnywhere, Category=AnimBlueprintFactory)
      TObjectPtr<class USkeletalMesh> PreviewSkeletalMesh; // L35
  ...
  ```
- **Capability in Python:** Python can configure `TargetSkeleton` and `ParentClass` and call `AssetTools.create_asset(...)`. This successfully generates a valid, blank `UAnimBlueprint` on disk.
- **Limitation:** The resulting AnimBP contains only a default root `Output Pose` node. Python cannot populate the graph.

### 2.2. `UAnimationGraph` (AnimGraph Container API)
- **Header:** `C:/Program Files/Epic Games/UE_5.5/Engine/Source/Editor/AnimGraph/Public/AnimationGraph.h:18-32`
- **Class Declaration:**
  ```cpp
  // AnimationGraph.h:18
  UCLASS(BlueprintType)
  class ANIMGRAPH_API UAnimationGraph : public UEdGraph
  {
      GENERATED_UCLASS_BODY()
      ...
      UFUNCTION(BlueprintCallable, Category=AnimationGraph)
      void GetGraphNodesOfClass(TSubclassOf<UAnimGraphNode_Base> NodeClass, 
                                TArray<UAnimGraphNode_Base*>& GraphNodes, 
                                bool bIncludeChildClasses = true); // L31
  };
  ```
- **Audit Result:** `UAnimationGraph` exposes exactly **one** `UFUNCTION`: `GetGraphNodesOfClass` (read-only query). It exposes **zero mutation functions** (`AddNode`, `CreateNode`, `RemoveNode`, `ConnectPins` do not exist as `UFUNCTION`s).

### 2.3. `UEdGraph` & `UEdGraphPin` (Base Graph Reflection Audit)
- **Header:** `C:/Program Files/Epic Games/UE_5.5/Engine/Source/Runtime/Engine/Classes/EdGraph/EdGraph.h:1-327`
- **Audit Result:** `UEdGraph` contains **zero `UFUNCTION` declarations** across its entire 327 lines. Methods like `AddNode()`, `RemoveNode()`, and `SelectNodeSet()` are unreflected C++ functions.
- Furthermore, `UEdGraphPin` in UE 5.5 is not a `UObject` and cannot be manipulated or wired via Python scripts.

### 2.4. `UBlueprintEditorLibrary` (Editor Scripting Utilities)
- **Header:** `C:/Program Files/Epic Games/UE_5.5/Engine/Source/Editor/BlueprintEditorLibrary/Public/BlueprintEditorLibrary.h:1-273`
- **Audit Result:** Provides graph management functions (`FindGraph`, `AddFunctionGraph`, `CompileBlueprint` at `L82`), but contains **zero functions for manipulating graph nodes or pins** inside an animation graph.

### 2.5. `UAnimationBlueprintLibrary` (Animation Authoring Library)
- **Header:** `C:/Program Files/Epic Games/UE_5.5/Engine/Source/Editor/AnimationBlueprintLibrary/Public/AnimationBlueprintLibrary.h:1-618`
- **Audit Result:** While offering extensive APIs for sequences, curves, notifies, and poses (618 lines), graph operations are strictly limited to:
  - `GetAnimationGraphs()` (`L603`)
  - `GetNodesOfClass()` (`L607`)
  - `AddNodeAssetOverride()` (`L618`)
- There are **zero APIs to construct or wire nodes**.

### 2.6. `UAnimGraphNode_RetargetPoseFromMesh` (Target Node Reflection)
- **Header:** `C:/Program Files/Epic Games/UE_5.5/Engine/Plugins/Animation/IKRig/Source/IKRigDeveloper/Public/AnimGraphNode_RetargetPoseFromMesh.h:16-21`
- **Class Declaration:**
  ```cpp
  // AnimGraphNode_RetargetPoseFromMesh.h:16-21
  class IKRIGDEVELOPER_API UAnimGraphNode_RetargetPoseFromMesh : public UAnimGraphNode_Base
  {
      GENERATED_BODY()
  public:
      UPROPERTY(EditAnywhere, Category=Settings)
      FAnimNode_RetargetPoseFromMesh Node; // L21
  ...
  ```
- **Audit Result:** This class resides in the `IKRigDeveloper` editor module. It is not reflected to Python and cannot be instantiated or wired without C++ editor linkage.

---

## 3. Evaluation of All Four Implementation Paths

| Path | Description | Scriptable via Python? | Engine Packaging Risk | Maintenance Overhead | Feasibility Verdict |
|:---|:---|:---:|:---:|:---:|:---:|
| **Path A: Pure Editor Python** | Create AnimBP + spawn node + wire pins | **NO** (Node/pin APIs unreflected) | None | None | **IMPOSSIBLE** |
| **Path B: `SetLeaderPoseComponent`** | Raw transform copy from Mannequin to Greystone | **YES** (Runtime API exists) | None | Low | **DISQUALIFIED** (Horrific mesh distortion) |
| **Path C: C++ Custom Proxy** | Native `UAnimInstance` subclass calling solver | **NO** (Requires C++ code) | Medium | Very High | **REJECTED** (Over-engineered) |
| **Path D: Hand-Made Asset** | Create single AnimBP in Editor GUI (30s) | N/A (One-time asset) | **Zero** | **Zero** | **RECOMMENDED** |

---

## 4. Deep-Dive on Alternative Paths

### 4.1. Why Path B (`SetLeaderPoseComponent`) Is Disqualified
- **Engine Citation:** `SkinnedMeshComponent.h:1694`, `SkinnedMeshComponent.cpp:2974-2975`:
  ```cpp
  // SkinnedMeshComponent.cpp:2974
  const FName BoneName = FollowerRefSkeleton.GetBoneName(BoneIndex);
  LeaderBoneMap[BoneIndex] = LeaderRefSkeleton.FindBoneIndex(BoneName);
  ```
- **Technical Barrier:** `SetLeaderPoseComponent` performs an unscaled 1:1 bone index lookup by name. It copies raw component-space transforms directly without reference-pose retargeting, bone length scaling, or chain orientation compensation.
- **Consequence:** Because Paragon Greystone's skeleton (`Greystone_Skeleton`) has different bone lengths, shoulder widths, and rest poses than `SK_CombatMannequin`, raw transform copying causes Greystone's mesh to collapse, crumple, and stretch unnaturally. `SetLeaderPoseComponent` only works for modular meshes built on the identical base skeleton.

### 4.2. Why Path C (Native C++ AnimInstance Subclass) Is Not Recommended
- **Engine Citation:** `AnimInstanceProxy.h:644` (`virtual bool Evaluate(FPoseContext& Output)`) & `AnimNode_RetargetPoseFromMesh.h:17`.
- **Technical Mechanism:** A native `UAnimInstance` subclass could theoretically hold an instance of `FAnimNode_RetargetPoseFromMesh`, initialize it, and evaluate it inside a custom `FAnimInstanceProxy`.
- **Why It Should Be Rejected:**
  1. `FAnimNode_RetargetPoseFromMesh` was built specifically for the graph evaluation pipeline (`FAnimationInitializeContext`, `FAnimationUpdateContext`, `FPoseContext`). Manually mocking these contexts inside a custom proxy requires roughly 300+ lines of fragile runtime C++ code.
  2. Bypasses Persona animation debugging, visual node inspection, and LOD graph controls.
  3. High maintenance burden across future engine minor updates (5.5 -> 5.6).

### 4.3. Why Path D (Hand-Made Asset) Is Superior
- **Asset Scope:** Exactly **one asset**: `Content/OneBossFight/GreystonePack/ABP_Greystone_VisualBridge.uasset`.
- **Authoring Steps in Editor GUI (Elapsed Time: 30 Seconds):**
  1. Right-click in Content Browser -> *Animation* -> *Animation Blueprint*.
  2. Select `Greystone_Skeleton` as Target Skeleton.
  3. Name asset `ABP_Greystone_VisualBridge`.
  4. Open AnimGraph -> Right-click -> Add node `Retarget Pose From Mesh`.
  5. In Node Details:
     - Set `bUseAttachedParent = true`.
     - Set `IKRetargeterAsset = RTG_CombatMannequin_To_Greystone`.
  6. Connect node output pin to `Output Pose` Result pin.
  7. Click **Compile** and **Save**.
- **Architectural Benefits:**
  - **Zero C++ Code Churn:** No new C++ editor modules or conditional `#if WITH_EDITOR` hacks needed in the runtime `OneBossFight` module.
  - **Zero Packaging Risk:** Standard binary asset format, fully recognized by cooker and packaging pipeline.
  - **Visual Debugging:** Opens in Persona with live interactive viewport inspection.

---

## 5. Architectural Decision & Next Steps

### Selected Implementation: Path D (Hand-Made Asset) + C++ Runtime Subsystem (A-249)
The visual lane is partitioned into two clean, isolated halves:
1. **The Cosmetic Asset:** `ABP_Greystone_VisualBridge.uasset` authored once in the editor.
2. **The Runtime Bridge (C++):** `UOneBossFightGreystoneBridgeSubsystem` (from accepted plan `A-249`) which dynamically attaches Greystone at runtime, assigns `ABP_Greystone_VisualBridge`, establishes tick prerequisites, hides the mannequin, and re-attaches weapons.

This achieves 100% decoupling with zero risk of repeating `KI-040` / `KI-052`.
