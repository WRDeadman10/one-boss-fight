# AG-10: Naming, Folder, and Import Standard

**Document ID:** `AG10_IMPORT_STANDARD`  
**Author:** Antigravity (Visual & Technical Animation Investigator)  
**Target Engine:** Unreal Engine 5.5.4 (`OneBossFight`, packaged 1080p / 60 FPS)  
**Parent Work Order:** `ANTIGRAVITY_WORK_ORDER_02.md` (`AG-10`)  
**Status:** DELIVERED  

---

## 1. Executive Summary & Objective

This standard defines the authoritative asset hierarchy, naming rules, Blender FBX export pipeline, and Unreal Engine Python import configuration for all boss and combat assets under `/Game/OneBossFight` (`Content/OneBossFight/`).

### Core Design Rules
1. **Self-Contained Boss Modularity:** A new boss exists entirely within a single folder `Content/OneBossFight/Boss<XX>/` plus external Data Assets under `Content/OneBossFight/Data/` (or within the boss folder).
2. **Skeleton Ground Truth:** All boss and player humanoid combatants in this project bind strictly to the shared project mannequin skeleton:
   `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin`
   *(Cited from `Scripts/Editor/import_boss01.py:8`, `Scripts/Editor/import_boss01_clips_r14.py:9`, `Scripts/Editor/import_all_builds.py:17`)*.
3. **In-Place Asset Preservation:** Assets referenced by Montages, Blueprints, or Levels must **never be deleted and recreated**. Deleting an asset severs GUID-based dependency graphs across packages. All asset refreshes must be imported or re-imported in place (`replace_existing = True`) (*Cited from `AGENTS.md` and `Scripts/Editor/import_boss01_clips_r14.py:2`*).
4. **Immediate Disk Persistence:** All programmatic imports must explicitly invoke `unreal.EditorAssetLibrary.save_loaded_asset()` to guarantee persistence across editor restarts (*Cited from `Scripts/Editor/import_boss01.py:46`*).

---

## 2. Directory Architecture under `Content/OneBossFight/`

To maintain clean separation between engine game code, third-party vendor packs, and custom boss content, the directory hierarchy is standardized as follows:

```
Content/OneBossFight/
├── Boss01/                             # Boss 01 (Sevarog Duel Prototype)
│   ├── Animations/                     # Animation sequences (AN_), blendspaces (BS_), montages (AM_)
│   ├── Body/                           # Skeletal mesh (SK_Boss01_Body or SKM_)
│   ├── Data/                           # Boss-specific data tables and combat specs
│   ├── Materials/                      # Material instances (MI_) and boss master materials (M_)
│   ├── Remains/                        # Defeated boss meshes / corpse props
│   ├── Textures/                       # PBR texture maps grouped by material slot
│   │   ├── BlackPlate/                 # Albedo, Normal, ORM for torso armour
│   │   ├── Blade/                      # Weapon texture set
│   │   └── CrimsonCloth/               # Robe / cloth texture set
│   └── Weapons/                        # Static meshes (SM_Boss01_Greatsword) with trace sockets
│
├── Boss<XX>/                           # Standard template for future bosses (Boss02, Boss03, etc.)
│   ├── Animations/
│   ├── Body/
│   ├── Data/
│   ├── Materials/
│   ├── Textures/
│   └── Weapons/
│
├── Characters/                         # Playable character builds & hero meshes
│   ├── Builds/                         # 6 Character builds (SKM_Samurai, SKM_Viking, etc.)
│   └── Greystone/                      # Greystone player assets, rolls, and tweaks
│
├── Data/                               # Global combat data assets (DA_WeaponConfig, etc.)
│
├── Effects/                            # Shared visual effects & Niagara systems
│   ├── Flipbook/                       # Animated texture sheets
│   ├── Materials/                      # Master VFX materials (additive, translucent)
│   ├── Niagara/                        # Niagara Systems (NS_) and Emitters (NE_)
│   └── Textures/                       # Noise, gradients, and particle alphas
│
├── Audio/                              # Sound waves (A_) and sound cues (Cue_)
├── Environment/                        # Arena static meshes, pillars, shrines, and materials
└── UI/                                 # UI art, status icons, reticles, HUD widgets
    └── Art/                            # Texture 2D sprites (T_UI_)
```

### New Boss Onboarding Rule
Adding a new boss requires exactly **one** new directory `Content/OneBossFight/Boss<XX>/` with the 6 standard subdirectories (`Animations`, `Body`, `Data`, `Materials`, `Textures`, `Weapons`), plus global tuning data assets registered in `Content/OneBossFight/Data/`.

---

## 3. Asset Naming Conventions

All assets in `Content/OneBossFight` must adhere to Epic Games / project-standard Hungarian notation:

| Asset Type | Prefix / Pattern | Example Asset Name | Purpose / Notes |
| :--- | :--- | :--- | :--- |
| **Skeletal Mesh** | `SKM_` or `SK_` | `SK_Boss01_Body`, `SKM_Samurai` | Bound to `SK_CombatMannequin` |
| **Static Mesh** | `SM_` | `SM_Boss01_Greatsword`, `SM_CanaryAxe` | Weapons, props, arena pillars |
| **Animation Sequence** | `AN_` | `AN_Boss01_A2_Raise`, `AN_Boss01_Wake` | Raw sampled clip (30.0 fps) |
| **Animation Montage** | `AM_` / `GS_` | `AM_Boss01_A2_SlamCombo`, `GS_SprintAttackFollowUp_Montage` | Combat montages with notify states |
| **Blend Space** | `BS_` | `BS_Boss01_Locomotion` | 1D / 2D blend spaces |
| **Niagara System** | `NS_` | `NS_Shockwave_RV01`, `NS_WeaponTrail` | Spawnable particle effects |
| **Niagara Emitter** | `NE_` | `NE_Shockwave_Ring`, `NE_Dust_Puff` | Modular emitter components |
| **Material (Master)** | `M_` | `M_ShockwaveDecal`, `M_BossMaster` | Base shader graph |
| **Material Instance**| `MI_` | `MI_Boss01_Torso`, `MI_WeaponGlow` | Parametric instance |
| **Texture 2D** | `T_` | `T_Boss01_Blade_D`, `T_Shockwave_Ring_N` | Texture assets (see suffix table below) |
| **Sound Wave** | `A_` | `A_Boss01_HeavySlam_01` | Raw imported audio sample |
| **Sound Cue** | `Cue_` | `Cue_Boss01_HeavySlam` | Sound cue with attenuation & pitch modulation |
| **Data Asset** | `DA_` | `DA_VanguardWeapon`, `DA_Boss01_Config` | Custom gameplay data definitions |
| **Float Curve** | `Curve_` | `Curve_TelegraphEase` | Ease-in/out or timing multipliers |
| **Camera Shake** | `CameraShake_` | `CameraShake_HeavyImpact` | Gameplay camera shake definition |

### Texture Map Suffixes
- `_D` / `_BaseColor`: Diffuse / Albedo (sRGB Enabled)
- `_N`: Normal Map (sRGB Disabled, Normalmap compression)
- `_ORM`: Packed Ambient Occlusion (R), Roughness (G), Metallic (B) (sRGB Disabled, Masks/Default compression)
- `_E`: Emissive Map (sRGB Enabled or Linear HDR)
- `_M`: Alpha Mask / Opacity (sRGB Disabled)

---

## 4. Blender FBX Export Settings

All external DCC authoring (Blender 3.x / 4.x) must export using the exact parameters validated across `Scripts/author_a3_clips.py`, `Scripts/test_export_root.py`, and `Scripts/build_dex_swords.py`.

### 4.1 Skeletal Animation Clips (`AN_*.fbx`)
*(Authoring source: `Scripts/author_a3_clips.py:144-155`, `Scripts/test_export_root.py:41-52`)*

```python
bpy.ops.export_scene.fbx(
    filepath=out_fbx_path,
    use_selection=True,
    global_scale=1.0,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_NONE',    # CRITICAL: Prevents 100x double-scaling UE bone hierarchy
    axis_forward='-Z',                      # Unreal Forward
    axis_up='Y',                            # Unreal Up
    object_types={'ARMATURE'},              # Armature only; no mesh in anim clips
    add_leaf_bones=False,                   # CRITICAL: Disables extra leaf bones that corrupt mannequin sockets
    primary_bone_axis='Y',
    secondary_bone_axis='X',
    bake_anim=True,
    bake_anim_use_all_bones=True,
    bake_anim_use_nla_strips=False,
    bake_anim_use_all_actions=False,
    bake_anim_step=1.0,                     # Sample every integer frame (zero decimation)
    bake_anim_simplify_factor=0.0           # Preserve exact curve keys
)
```
- **Frame Rate:** Project standard is strictly **30.0 fps** (`scene.render.fps = 30`, `scene.render.fps_base = 1.0`).
- **Root Motion:** Locomotion displacement and yaw rotation must be animated on the `root` object itself (`Vector((0, Y, 0))`), with child bones (e.g. `pelvis`) animating relative to root (*Cited from `Scripts/test_export_root.py:28-36`*).

### 4.2 Skeletal Meshes (`SKM_*.fbx`)
*(Authoring source: `Scripts/build_seated_crown.py:230-240`, `Scripts/Editor/test_import_skm.py`)*

```python
bpy.ops.export_scene.fbx(
    filepath=out_fbx_path,
    use_selection=True,
    global_scale=1.0,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_NONE',
    axis_forward='-Z',
    axis_up='Y',
    object_types={'ARMATURE', 'MESH'},
    use_mesh_modifiers=True,
    add_leaf_bones=False,
    primary_bone_axis='Y',
    secondary_bone_axis='X',
    bake_anim=False
)
```

### 4.3 Static Meshes / Weapons (`SM_*.fbx`)
*(Authoring source: `Scripts/build_dex_swords.py:325-336`, `Scripts/build_hero_greatsword_v10.py:349-360`)*

```python
bpy.ops.export_scene.fbx(
    filepath=out_fbx_path,
    use_selection=True,
    global_scale=1.0,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_UNITS',  # Converts Blender metric units to UE cm
    bake_space_transform=True,              # Bakes coordinate transforms into vertex data
    axis_forward='-Z',
    axis_up='Y',
    object_types={'MESH', 'EMPTY'},         # Includes Empty objects used for sockets
    bake_anim=False
)
```

---

## 5. Unreal Engine Import Pipeline & Settings

Unreal Engine automation runs via `Scripts/run_in_editor.py` executing Python scripts in the editor environment.

### 5.1 Skeletal Mesh Import Task Spec
*(Reference: `Scripts/Editor/import_boss01.py:23-34`, `Scripts/Editor/import_all_builds.py:28-39`)*

```python
import unreal

skel = unreal.load_asset("/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin")

task = unreal.AssetImportTask()
task.filename = source_fbx_path
task.destination_path = "/Game/OneBossFight/Boss01/Body"
task.destination_name = "SK_Boss01_Body"
task.replace_existing = True
task.replace_existing_settings = True
task.automated = True
task.save = True

options = unreal.FbxImportUI()
options.set_editor_property("import_mesh", True)
options.set_editor_property("import_as_skeletal", True)
options.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
options.set_editor_property("skeleton", skel)
options.set_editor_property("import_materials", False)      # Handled via explicit slot binding
options.set_editor_property("import_textures", False)
options.set_editor_property("import_animations", False)
options.skeletal_mesh_import_data.set_editor_property("use_t0_as_ref_pose", True)
options.skeletal_mesh_import_data.set_editor_property("import_morph_targets", False)

task.options = options
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
```

### 5.2 Animation Sequence Import Task Spec
*(Reference: `Scripts/Editor/import_boss01.py:40-52`, `Scripts/Editor/import_boss01_clips_r14.py:16-32`)*

```python
task = unreal.AssetImportTask()
task.filename = source_fbx_path
task.destination_path = "/Game/OneBossFight/Boss01/Animations"
task.destination_name = clip_name
task.replace_existing = True
task.replace_existing_settings = True
task.automated = True
task.save = True

options = unreal.FbxImportUI()
options.set_editor_property("import_mesh", False)
options.set_editor_property("import_as_skeletal", False)
options.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_ANIMATION)
options.set_editor_property("skeleton", skel)
options.set_editor_property("import_animations", True)
options.set_editor_property("import_materials", False)
options.set_editor_property("import_textures", False)

task.options = options
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

# Post-import save guarantee
anim_asset = unreal.load_asset(f"{task.destination_path}/{task.destination_name}")
if anim_asset:
    unreal.EditorAssetLibrary.save_loaded_asset(anim_asset)
```

### 5.3 Static Mesh Weapon & Socket Renaming Gotcha
*(Reference: `Scripts/Editor/import_boss01.py:64-70`)*

> [!WARNING]
> **FBX Importer Socket Renaming Bug:**
> The Unreal FBX importer replaces spaces in Blender Empty / Socket names with underscores (e.g. `Weapon Start` becomes `Weapon_Start`).
> The Advanced ARPG Combat pack line traces specifically query socket names with spaces (`"Weapon Start"` and `"Weapon End"`). If uncorrected, melee hitboxes fail silently!

**Required Post-Import Correction Hook:**
```python
sword = unreal.load_asset("/Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword")
if sword:
    for sock in sword.get_sockets_by_tag(""):
        n = str(sock.get_editor_property("socket_name"))
        if n in ("Weapon_Start", "Weapon_End"):
            sock.set_editor_property("socket_name", n.replace("_", " "))
    unreal.EditorAssetLibrary.save_loaded_asset(sword)
```

---

## 6. Editor Owner Import Checklist

Before executing any import script, the Editor Owner must verify and execute the following sequential checklist:

1. **Pre-Flight Environment Verification:**
   - [ ] Editor is closed before any C++ recompile or bulk file copy.
   - [ ] Editor launched with `-nosound` (per `AGENTS.md`).
   - [ ] Git status verified clean on active development branch; no uncommitted conflicting asset edits.
   - [ ] Source files staged under `Import/<Category>/<Subdir>/` (e.g. `Import/Boss01/Animations/AN_Boss01_A2_Raise.fbx`).

2. **Execution:**
   - [ ] Execute the target import script via `Scripts/run_in_editor.py <script_path>.py`.
   - [ ] Confirm log output reports `[Import]` success with zero `ERR` exceptions.

3. **Asset Verification Post-Import:**
   - [ ] **Skeleton Binding:** Confirm `anim.get_editor_property("skeleton") == skel` points to `SK_CombatMannequin`.
   - [ ] **Frame Rate & Duration:** Check sequence length and sampled frame count match Blender authoring targets ($30\text{ fps}$).
   - [ ] **Socket Names:** Inspect StaticMesh sockets; confirm `"Weapon Start"` and `"Weapon End"` contain space characters, not underscores.
   - [ ] **Root Motion Check:** For clips with locomotion, open sequence editor and verify "EnableRootMotion" is checked and red root motion trail displays in viewport.
   - [ ] **Material Assignment:** Verify skeletal mesh materials point to valid project material instances (`MI_` or `/Game/ParagonSevarog/` references), with zero default grey checkerboard slots.

4. **Persistence & Closure:**
   - [ ] Confirm `unreal.EditorAssetLibrary.save_loaded_asset()` was executed on every modified package.
   - [ ] Run targeted PIE driver harness (e.g. `Scripts/Editor/pie_boss_look.py` or `pie_telegraph.py`) to confirm zero null-reference crashes.

---

## 7. Evidence and Limits Table

| Requirement / Setting | Source Evidence | Live Verification Status | Offline Boundary / Limit |
| :--- | :--- | :--- | :--- |
| **Project Mannequin Skeleton** | `Scripts/Editor/import_boss01.py:8`, `import_all_builds.py:17` | Verified in Python scripts; path `/Game/AdvancedARPGCombat/.../SK_CombatMannequin` confirmed. | Cannot inspect binary `.uasset` bone hierarchy directly without editor session. |
| **Armature Export FBX_SCALE_NONE** | `Scripts/author_a3_clips.py:149`, `Scripts/test_export_root.py:46` | Confirmed across all authored animation FBX generation scripts. | Verified via Python AST / text search; actual Blender export validated in previous sprints. |
| **Static Mesh Export FBX_SCALE_UNITS** | `Scripts/build_dex_swords.py:330-331`, `build_hero_greatsword_v10.py:354-355` | Confirmed `bake_space_transform=True` and `FBX_SCALE_UNITS` active. | Mesh bounds verified in log outputs ($205\text{ cm}$ greatsword). |
| **No Leaf Bones (`add_leaf_bones=False`)** | `Scripts/author_a3_clips.py:153`, `test_export_root.py:50` | Verified across all FBX exporter calls. | Prevents dummy end-bones in mannequin tree. |
| **Socket Space Restoration** | `Scripts/Editor/import_boss01.py:64-70` | Confirmed space replacement code `replace("_", " ")` in import script. | Required due to Unreal FBX importer name sanitation. |
| **In-Place Re-import Rule** | `AGENTS.md`, `Scripts/Editor/import_boss01_clips_r14.py:2` | Explicit rule in project root doc and script docstrings. | Offline analysis cannot verify whether third-party Blueprints have stale references. |
| **Save Loaded Asset Requirement** | `Scripts/Editor/import_boss01.py:46` | `unreal.EditorAssetLibrary.save_loaded_asset(a)` explicitly called. | Required to prevent asset loss on editor exit. |
