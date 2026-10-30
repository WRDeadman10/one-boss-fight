# Sevarog Animation Pipeline & Blender Feasibility Study (A-256)

> **Document Status**: Certified Offline Delivery  
> **Target Tool**: Blender 5.1.2 (Verified installed: `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe`)  
> **Engine Target**: Unreal Engine 5.5.4 (`Sevarog_Skeleton.uasset`, `URPGBossMoveCard`)  
> **Scope**: Feasibility and round-trip authoring pipeline for missing animation families (Rear Sweep & Grab/Skewer Paired Reaction).  
> **Content Constraint**: Zero Content import (planning & feasibility only).

---

## 1. Asset Audit: Source FBX vs Editor Export Requirement

An audit of the project disk confirmed the following:

1. **`Content/ParagonSevarog/` Disk Contents**:
   - All assets under `Content/ParagonSevarog/Characters/Heroes/Sevarog/` are compiled Unreal Engine binary packages (`.uasset`).
   - **Zero raw `.fbx` files exist within `Content/ParagonSevarog/`.**
2. **Existing Workspace FBX Assets**:
   - `Import/ThirdParty/Reference/REF_Sevarog_Sevarog.fbx` (2,400,976 bytes) contains the base Sevarog skeletal mesh and 154-bone armature hierarchy (`root`, `weapon_r`, `root_weapon_end_r`).
   - Verified via background Blender 5.1.2 headless execution: successfully imported 1 armature (154 bones) and 1 mesh (`Sevarog.001`, 51,034 vertices, 85,163 polygons).
3. **Pipeline Recommendation (Editor Export)**:
   - While `REF_Sevarog_Sevarog.fbx` provides the static reference mesh, **an FBX export from the Unreal Editor** (performed by the implementer via Asset Actions $\to$ Export) of `Sevarog_Skeleton.uasset` and the candidate source animations (`Swing2_Medium.uasset`, `Subjugation.uasset`) is the cleanest, authoritative path.
   - This guarantees that exported animations preserve exact bone rest poses, retargeting options, and curve metadata matching live UE 5.5.4 packages.

---

## 2. Animation Gaps Analysis & Motion Design

The Morgott 82-Point Combat Reference identifies two critical animation families currently missing from Sevarog's asset library:

### 2.1 Gap 1: Rear Tail / Back Sweep Substitute (Morgott Family 7)
- **Combat Purpose**: High-threat directional deterrent to punish players lingering in the boss's rear/flank blind spots (satisfies `BOSS-AWR-004`, `BOSS-SEL-003`).
- **Sevarog Adaptation**: Because Sevarog is a floating wraith with tattered robes rather than a biological tail, the rear sweep is adapted as an explosive **180° Reverse Horizontal Scythe Sweep**:
  - Sevarog twists his torso and spine sharply to the left rear.
  - The scythe head is dragged along the arena floor behind him and whipped across the rear 180° arc (`Yaw: -90° -> +90°` behind the boss).
  - Terminal follow-through smoothly unwinds the spine back to frontal idle facing.

### 2.2 Gap 2: Grab / Skewer & Paired Victim Reaction (Morgott Family 11)
- **Combat Purpose**: High-punish unblockable command grab breaking passive player guard (satisfies `BOSS-DEF-003`, `BOSS-HIT-006`).
- **Paired Motion Architecture**:
  - Requires **TWO synchronized animations** authored simultaneously in a unified Blender workspace:
    1. **`AN_Sevarog_Grab_Attacker`**: Forward thrust, scythe lift, overhead hold, and ground slam.
    2. **`AN_Greystone_Grab_Victim`**: Pierced chest recoil, vertical airborne suspension, and grounded knockdown/stumble.
  - **Shared Origin Constraint**: Both clips share a common $(0, 0, 0)$ world origin at frame 0. At the moment of impale ($t = 0.40\text{ s}$), the victim's chest bone (`spine_03`) is locked to Sevarog's scythe blade socket (`root_weapon_end_r`).

---

## 3. Blender 5.1.2 Export/Import Round-Trip Specification

To maintain 100% compatibility with Unreal Engine 5.5.4 and our C++ runtime executor, all authored clips must adhere to the following strict pipeline rules:

```text
[UE 5.5 Editor Export] 
        │ (.fbx)
        ▼
[Blender 5.1 Authoring: 60 FPS, Unit Scale 0.01, In-Place Root] 
        │ (.fbx)
        ▼
[Implementer Import & Montage Wrapper: FullBody Slot]
```

### 3.1 Workspace Units & Scene Settings
- **System**: Metric
- **Unit Scale**: `0.01` (1 Blender Unit = 1 Unreal Centimeter)
- **Scene Frame Rate**: Exactly **`60.0 fps`** (matches runtime target 16.67 ms frame budget)
- **Playback Length**: Authored in discrete 60 FPS frames (e.g. 90 frames = 1.500s)

### 3.2 Root Motion Choice: Strict In-Place (Root Motion = False)
- **Governance Requirement**: Our C++ combat framework (`URPGFrameworkMoveExecutor`, `RPGBossMoveModel`) uses kinematic character translation driven by AI pathfollowing and navigation bands.
- **Root Bone Rule**: The root bone (`root`) must remain anchored at $(0, 0, 0)$ with zero translation and zero rotation across all frames.
- All body displacement must be internal to the pelvis and spine bones relative to the static root.
- The exported clip and compiled `URPGBossMoveCard` must have `bUsesRootMotion = false`.

### 3.3 Blender FBX Export Settings
When exporting the authored FBX from Blender 5.1:
- **Format**: `FBX 7.4 binary`
- **Main Options**:
  - `Selected Objects`: Checked (Armature + Mesh only)
  - `Scale`: `1.0` (with Scene Units applied)
  - `Forward`: `-Z Forward`
  - `Up`: `Y Up`
- **Armature Options**:
  - `Primary Bone Axis`: `Y Axis`
  - `Secondary Bone Axis`: `X Axis`
  - `Armature FBXNode Type`: `Null`
  - `Add Leaf Bones`: **Unchecked** (prevents extraneous dummy leaf bones from corrupting UE skeleton matching)
- **Animation Options**:
  - `Bake Animation`: Checked
  - `Key All Bones`: Checked
  - `Simplify`: `0.0` (zero tolerance curve loss)

---

## 4. Proof Clip Authoring Plan: `AN_Sevarog_RearSweep`

The initial proof clip to establish the pipeline is the **Rear Scythe Sweep** (`AN_Sevarog_RearSweep`):

### 4.1 Master Parameters
- **Asset Name**: `AN_Sevarog_RearSweep.fbx`
- **Total Duration**: `1.4000 s` (84 frames at 60 FPS)
- **Clip Type**: In-Place AnimSequence (`bUsesRootMotion = false`)
- **Target Skeleton**: `Sevarog_Skeleton.uasset`
- **Target Slot**: `FullBody`

### 4.2 Keyframe Breakdown Table (60 FPS)

| Phase | Frame Range | Simulation Time ($t$) | Armature Motion & Pose Description | Socket / Velocity State |
| :--- | :---: | :---: | :--- | :--- |
| **Telegraph / Anticipation** | Frames 0 – 24 | `0.000s -> 0.400s` | Sevarog curls torso leftward, pulls right shoulder back, drags scythe blade backward behind left hip. Eyes flare. | Tracking active (up to `t = 0.35s`). Scythe tip velocity $< 400\text{ cm/s}$. |
| **Commit Boundary** | Frame 21 | `t = 0.350s` | Rotational lock. Boss orientation freezes; player can side-roll. | Tracking locks. |
| **Active Strike Release** | Frames 25 – 36 | `0.416s -> 0.600s` | Explosive 180° horizontal sweep. Spine snaps rightward; scythe tip traces a wide circular arc slicing across rear 180°. | **Active Hit Window** (`[0.416s, 0.600s]`). Peak tip velocity $> 3,200\text{ cm/s}$ at $t = 0.500\text{ s}$. |
| **Follow-Through** | Frames 37 – 50 | `0.616s -> 0.833s` | Scythe over-rotates past right flank; deceleration into ground drag. | Velocity drops $< 800\text{ cm/s}$. Active window closes. |
| **Recovery / Punish** | Frames 51 – 84 | `0.850s -> 1.400s` | Heavy recovery posture. Scythe remains lowered while torso gradually rotates back to frontal facing. | **Punish Window** ($\Delta t_{\text{punish}} \approx 0.55\text{ s}$). Recovery ends at $t = 1.35\text{ s}$. |

### 4.3 Proposed MoveCard Parameters (MC-RearSweep)
- `MoveId`: `Move_Sevarog_RearSweep`
- `FamilyId`: `Family_07_RearDeterrent`
- `CommitSeconds`: `0.3500`
- `ActiveStartSeconds`: `0.4167`
- `ActiveEndSeconds`: `0.6000`
- `RecoveryEndSeconds`: `1.3500`
- `ClipLengthSeconds`: `1.4000`
- `FrontConeDegrees`: `180.0` (Rear hemisphere facing)
- `MinRangeCm`: `50.0`, `MaxRangeCm`: `320.0`
- `HitWindow`: `[0.4167s -> 0.6000s]`, `SocketA = "weapon_r"`, `SocketB = "root_weapon_end_r"`, `Radius = 18.0 cm`.

---

## 5. Verification & Feasibility Acceptance

1. **Blender Environment**: Blender 5.1.2 is installed and fully functional in headless CLI mode on this machine.
2. **Skeleton Compatibility**: Verified that Sevarog's 154-bone armature imports cleanly with correct bone hierarchy, naming, and orientation.
3. **Execution Protocol**:
   - Step 1: Implementer exports `Sevarog_Skeleton` and `Swing2_Medium` to `.fbx`.
   - Step 2: Antigravity authors the 84-frame in-place `AN_Sevarog_RearSweep.fbx` via Blender CLI scripts.
   - Step 3: Implementer imports the FBX into `/Game/OneBossFight/FrameworkProof/Animations/` and compiles the corresponding MoveCard.
