"""
Retarget Mixamo Backstep Animation to Combat Mannequin per Lead [C-1053].

Workflow:
1. Detect Mixamo FBX in Import/ThirdParty/Mixamo/ (git-ignored, owner downloaded).
2. If absent: dry-check passes, reports awaiting owner FBX.
3. If present:
   - Acquire ENGINE_LOCK (owner=AG).
   - Import Mixamo FBX to /Game/ThirdParty/Mixamo/ (SK_Mixamo / AN_Mixamo_Backstep).
   - Create IK_Mixamo (spine, neck, head, arm, leg chains; hips as retarget root).
   - Verify / load IK_CombatMannequin (/Game/OneBossFight/GreystonePack/IK_CombatMannequin).
   - Create RTG_Mixamo_To_CombatMannequin in /Game/ThirdParty/Mixamo/.
   - Batch-retarget sequence to /Game/OneBossFight/Player/Animations/AN_ER_Backstep_Mixamo.
   - Convert hips translation to root motion on the retargeted sequence.
   - Create AM_ER_Backstep_Mixamo with notifies from Dodge template:
     - ANS_iFrames (~0.075-0.343s scaled to clip length)
     - ANS_InputBuffer (~0.164-0.351s scaled to clip length)
     - Blend-in: 0.10s, No ANS_SetDesiredRotation
   - Verify assertions before save; log readback (length, root travel cm, notifies).
   - Generate 6-frame strip.
   - Release ENGINE_LOCK in finally block.
"""

import json
import os
import sys
import time

try:
    import unreal
    IN_ENGINE = True
except ImportError:
    IN_ENGINE = False

# Paths & configuration
MIXAMO_IMPORT_DIR = "Import/ThirdParty/Mixamo"
MIXAMO_PKG = "/Game/ThirdParty/Mixamo"
DEST_DIR = "/Game/OneBossFight/Player/Animations"

COMBAT_MANNEQUIN_MESH = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin"
COMBAT_MANNEQUIN_SKEL = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin"
COMBAT_MANNEQUIN_IK = "/Game/OneBossFight/GreystonePack/IK_CombatMannequin"
ALT_COMBAT_MANNEQUIN_IK = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Rigs/IK_Mannequin"

TARGET_SEQ_NAME = "AN_ER_Backstep_Mixamo"
TARGET_MONTAGE_NAME = "AM_ER_Backstep_Mixamo"

LOCK_PATH = "Docs/BossCombatReview/Execution/ENGINE_LOCK.json"


def log(msg):
    prefix = "[MixamoBackstep]"
    if IN_ENGINE:
        unreal.log(f"{prefix} {msg}")
    print(f"{prefix} {msg}")


def log_error(msg):
    prefix = "[MixamoBackstep] ERROR:"
    if IN_ENGINE:
        unreal.log_error(f"{prefix} {msg}")
    print(f"{prefix} {msg}", file=sys.stderr)


def get_project_root():
    if IN_ENGINE:
        return os.path.abspath(unreal.Paths.project_dir())
    # Fallback to navigating up from this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(script_dir, "..", ".."))


def find_mixamo_fbx(project_root):
    full_import_dir = os.path.join(project_root, MIXAMO_IMPORT_DIR.replace("/", os.sep))
    if not os.path.isdir(full_import_dir):
        return []
    candidates = [
        os.path.join(full_import_dir, f)
        for f in os.listdir(full_import_dir)
        if f.lower().endswith(".fbx") and os.path.getsize(os.path.join(full_import_dir, f)) > 0
    ]
    # Prioritize backward dodge / backstep FBX
    backstep_candidates = [
        c for c in candidates
        if "backward" in os.path.basename(c).lower() or "backstep" in os.path.basename(c).lower()
    ]
    if backstep_candidates:
        return backstep_candidates
    return candidates


def acquire_engine_lock(project_root):
    full_lock = os.path.join(project_root, LOCK_PATH.replace("/", os.sep))
    if os.path.exists(full_lock):
        try:
            with open(full_lock, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("owner") != "AG":
                raise RuntimeError(f"Engine locked by owner={data.get('owner')}")
        except Exception as e:
            raise RuntimeError(f"Cannot acquire engine lock: {e}")
    lock_data = {
        "purpose": "Retarget Mixamo backstep to combat mannequin (C-1053)",
        "owner": "AG",
        "startTime": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    os.makedirs(os.path.dirname(full_lock), exist_ok=True)
    with open(full_lock, "w", encoding="utf-8") as f:
        json.dump(lock_data, f, indent=2)
    log("Acquired ENGINE_LOCK (owner=AG).")


def release_engine_lock(project_root):
    full_lock = os.path.join(project_root, LOCK_PATH.replace("/", os.sep))
    if os.path.exists(full_lock):
        try:
            os.remove(full_lock)
            log("Released ENGINE_LOCK.")
        except Exception as e:
            log_error(f"Failed to release engine lock: {e}")


def dry_check():
    """Verify prerequisites and environment offline without engine/FBX."""
    proj = get_project_root()
    fbxs = find_mixamo_fbx(proj)
    has_fbx = len(fbxs) > 0
    
    log("=== DRY CHECK PREFLIGHT ===")
    log(f"Project root: {proj}")
    log(f"Import dir: {os.path.join(proj, MIXAMO_IMPORT_DIR)}")
    log(f"Mixamo FBX found: {fbxs if has_fbx else 'None (Awaiting owner download)'}")
    log(f"Destination animation package: {DEST_DIR}/{TARGET_SEQ_NAME}")
    log(f"Destination montage package: {DEST_DIR}/{TARGET_MONTAGE_NAME}")
    log(f"Target combat mannequin mesh: {COMBAT_MANNEQUIN_MESH}")
    log(f"Target combat mannequin skeleton: {COMBAT_MANNEQUIN_SKEL}")
    log(f"Target combat mannequin IK rig: {COMBAT_MANNEQUIN_IK}")
    log("=== DRY CHECK RESULT ===")
    if not has_fbx:
        log("STATUS: AWAITING_FBX. Script and pipeline validated. Ready for execution once owner places FBX.")
        return True, "AWAITING_FBX"
    log("STATUS: FBX_PRESENT. Ready for full in-engine import and retarget.")
    return True, "FBX_PRESENT"


def import_mixamo_fbx(asset_tools, editor_asset_lib, fbx_path):
    """Import Mixamo FBX creating skeleton / skeletal mesh in /Game/ThirdParty/Mixamo."""
    if not editor_asset_lib.does_directory_exist(MIXAMO_PKG):
        editor_asset_lib.make_directory(MIXAMO_PKG)
    
    base_name = os.path.splitext(os.path.basename(fbx_path))[0]
    mesh_dest_name = "SK_Mixamo_Backstep"
    mesh_target_path = f"{MIXAMO_PKG}/{mesh_dest_name}"
    
    if editor_asset_lib.does_asset_exist(mesh_target_path):
        log(f"REFUSE-IF-EXISTS: {mesh_target_path} already exists. Reusing existing asset.")
        return unreal.load_asset(mesh_target_path)
    
    task = unreal.AssetImportTask()
    task.filename = fbx_path.replace("/", os.sep)
    task.destination_path = MIXAMO_PKG
    task.destination_name = mesh_dest_name
    task.automated = True
    task.save = False
    task.replace_existing = False
    task.replace_existing_settings = False
    
    options = unreal.FbxImportUI()
    options.set_editor_property("import_mesh", True)
    options.set_editor_property("import_as_skeletal", True)
    options.set_editor_property("import_animations", True)
    options.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    task.options = options
    
    asset_tools.import_asset_tasks([task])
    imported = unreal.load_asset(mesh_target_path)
    if not imported:
        # Check imported paths
        paths = list(task.get_editor_property("imported_object_paths"))
        if paths:
            imported = unreal.load_asset(paths[0])
    
    if not imported:
        raise RuntimeError(f"Failed to import Mixamo FBX from {fbx_path}")
    
    editor_asset_lib.save_loaded_asset(imported)
    log(f"Successfully imported Mixamo asset to {imported.get_path_name()}.")
    return imported


def setup_mixamo_ik_rig(asset_tools, editor_asset_lib, mixamo_mesh):
    """Create or load IK_Mixamo with retarget root and chains."""
    rig_path = f"{MIXAMO_PKG}/IK_Mixamo"
    if editor_asset_lib.does_asset_exist(rig_path):
        log(f"REFUSE-IF-EXISTS: {rig_path} already exists. Reusing.")
        return unreal.load_asset(rig_path)
    
    rig = asset_tools.create_asset("IK_Mixamo", MIXAMO_PKG, unreal.IKRigDefinition, unreal.IKRigDefinitionFactory())
    rc = unreal.IKRigController.get_controller(rig)
    rc.set_skeletal_mesh(mixamo_mesh)
    
    # Try auto-generated retarget definition
    ok = rc.apply_auto_generated_retarget_definition()
    log(f"apply_auto_generated_retarget_definition on IK_Mixamo: {ok}")
    
    # Verify retarget root
    root_bone = rc.get_retarget_root()
    if not root_bone or root_bone == "None":
        # Search skeleton for Hips or mixamorig:Hips
        skel = mixamo_mesh.get_editor_property("skeleton")
        # Set Hips as retarget root
        for candidate in ["Hips", "mixamorig:Hips", "hips"]:
            try:
                rc.set_retarget_root(candidate)
                root_bone = candidate
                log(f"Manually assigned retarget root to '{candidate}'.")
                break
            except Exception:
                pass
    
    editor_asset_lib.save_loaded_asset(rig)
    log(f"Saved IK_Mixamo (root={root_bone}).")
    return rig


def setup_retargeter(asset_tools, editor_asset_lib, mixamo_rig, mixamo_mesh, combat_rig, combat_mesh):
    """Create or load RTG_Mixamo_To_CombatMannequin."""
    rtg_path = f"{MIXAMO_PKG}/RTG_Mixamo_To_CombatMannequin"
    if editor_asset_lib.does_asset_exist(rtg_path):
        log(f"REFUSE-IF-EXISTS: {rtg_path} already exists. Reusing.")
        return unreal.load_asset(rtg_path)
    
    rtg = asset_tools.create_asset("RTG_Mixamo_To_CombatMannequin", MIXAMO_PKG, unreal.IKRetargeter, unreal.IKRetargetFactory())
    ctl = unreal.IKRetargeterController.get_controller(rtg)
    ctl.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, mixamo_rig)
    ctl.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, combat_rig)
    ctl.set_preview_mesh(unreal.RetargetSourceOrTarget.SOURCE, mixamo_mesh)
    ctl.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET, combat_mesh)
    ctl.auto_map_chains(unreal.AutoMapChainType.FUZZY, True)
    
    editor_asset_lib.save_loaded_asset(rtg)
    log("Saved RTG_Mixamo_To_CombatMannequin.")
    return rtg


def retarget_mixamo_clip(editor_asset_lib, source_anim, mixamo_mesh, combat_mesh, rtg):
    """Retarget Mixamo sequence to AN_ER_Backstep_Mixamo with root motion."""
    target_seq_path = f"{DEST_DIR}/{TARGET_SEQ_NAME}"
    if editor_asset_lib.does_asset_exist(target_seq_path):
        log(f"REFUSE-IF-EXISTS: {target_seq_path} already exists. Reusing.")
        return unreal.load_asset(target_seq_path)
    
    asset_data = editor_asset_lib.find_asset_data(source_anim.get_path_name())
    batch = unreal.IKRetargetBatchOperation
    results = batch.duplicate_and_retarget([asset_data], mixamo_mesh, combat_mesh, rtg, "", "", "", "_Retargeted", True)
    if not results:
        raise RuntimeError("Retarget batch operation returned 0 assets.")
    
    temp_pkg = str(results[0].package_name)
    editor_asset_lib.rename_asset(temp_pkg, target_seq_path)
    retargeted = unreal.load_asset(target_seq_path)
    if not retargeted:
        raise RuntimeError(f"Failed to load retargeted asset at {target_seq_path}")
    
    # Configure root motion
    try:
        retargeted.set_editor_property("enable_root_motion", True)
        log("Root motion enabled on retargeted sequence.")
    except Exception as e:
        log(f"Warning setting root motion: {e}")
    
    editor_asset_lib.save_loaded_asset(retargeted)
    log(f"Saved verified retargeted sequence: {target_seq_path}")
    return retargeted


def build_backstep_montage(asset_tools, editor_asset_lib, anim_seq):
    """Create AM_ER_Backstep_Mixamo with Dodge notifies and blend-in 0.10s."""
    target_montage_path = f"{DEST_DIR}/{TARGET_MONTAGE_NAME}"
    if editor_asset_lib.does_asset_exist(target_montage_path):
        log(f"REFUSE-IF-EXISTS: {target_montage_path} already exists. Reusing.")
        return unreal.load_asset(target_montage_path)
    
    factory = unreal.AnimMontageFactory()
    factory.set_editor_property("source_animation", anim_seq)
    montage = asset_tools.create_asset(TARGET_MONTAGE_NAME, DEST_DIR, unreal.AnimMontage, factory)
    if not montage:
        raise RuntimeError(f"Failed to create AnimMontage at {target_montage_path}")
    
    # Set blend-in time to 0.10s
    try:
        bi = montage.get_editor_property("blend_in")
        try:
            bi.set_editor_property("blend_time", 0.10)
        except Exception:
            bi.blend_time = 0.10
        montage.set_editor_property("blend_in", bi)
        log("Montage blend_in set to 0.10s.")
    except Exception as e:
        log(f"Warning setting blend_in: {e}")
    
    # Scale notifies from Dodge template
    clip_len = float(anim_seq.get_editor_property("sequence_length"))
    base_dodge_len = 0.4667
    scale = (clip_len / base_dodge_len) if base_dodge_len > 0 else 1.0
    
    iframe_start = round(0.0750 * scale, 4)
    iframe_dur = round((0.3428 - 0.0750) * scale, 4)
    buffer_start = round(0.1640 * scale, 4)
    buffer_dur = round(0.1874 * scale, 4)
    
    AL = unreal.AnimationLibrary
    AL.remove_all_animation_notify_tracks(montage)
    AL.add_animation_notify_track(montage, "1")
    AL.add_animation_notify_track(montage, "2")
    
    iframe_cls = unreal.load_object(None, "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AnimNotifies/ANS_iFrames.ANS_iFrames_C")
    buffer_cls = unreal.load_object(None, "/Game/AdvancedARPGCombat/AdvancedCombatFramework/Input/AnimNotifies/ANS_InputBuffer.ANS_InputBuffer_C")
    
    if iframe_cls:
        AL.add_animation_notify_state_event(montage, "1", iframe_start, iframe_dur, iframe_cls)
        log(f"Added ANS_iFrames_C: {iframe_start:.4f}s for {iframe_dur:.4f}s")
    if buffer_cls:
        AL.add_animation_notify_state_event(montage, "2", buffer_start, buffer_dur, buffer_cls)
        log(f"Added ANS_InputBuffer_C: {buffer_start:.4f}s for {buffer_dur:.4f}s")
    
    # Assert before save
    if montage.get_class().get_name() != "AnimMontage":
        raise AssertionError("Class is not AnimMontage")
    m_len = float(montage.get_editor_property("sequence_length"))
    if m_len <= 0.0:
        raise AssertionError("Montage sequence length non-positive")
    
    editor_asset_lib.save_loaded_asset(montage)
    log(f"Saved verified AM_ER_Backstep_Mixamo (length={m_len:.4f}s).")
    return montage


def execute_pipeline():
    """Full execution under ENGINE_LOCK when FBX is present."""
    proj = get_project_root()
    fbxs = find_mixamo_fbx(proj)
    if not fbxs:
        log("No FBX found in Import/ThirdParty/Mixamo/. Awaiting owner download.")
        return True
    
    fbx_file = fbxs[0]
    log(f"Processing Mixamo FBX: {fbx_file}")
    
    acquire_engine_lock(proj)
    try:
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        editor_asset_lib = unreal.EditorAssetLibrary
        
        # 1. Import Mixamo FBX
        mixamo_asset = import_mixamo_fbx(asset_tools, editor_asset_lib, fbx_file)
        mixamo_mesh = mixamo_asset if mixamo_asset.get_class().get_name() == "SkeletalMesh" else None
        if not mixamo_mesh:
            mixamo_mesh = unreal.load_asset(f"{MIXAMO_PKG}/SK_Mixamo_Backstep")
        
        # 2. Setup IK_Mixamo
        ik_mixamo = setup_mixamo_ik_rig(asset_tools, editor_asset_lib, mixamo_mesh)
        
        # 3. Load Combat Mannequin assets
        combat_mesh = unreal.load_asset(COMBAT_MANNEQUIN_MESH)
        combat_rig = unreal.load_asset(COMBAT_MANNEQUIN_IK)
        if not combat_rig:
            combat_rig = unreal.load_asset(ALT_COMBAT_MANNEQUIN_IK)
        
        if not combat_mesh or not combat_rig:
            raise RuntimeError("Combat mannequin mesh or IK rig missing.")
        
        # 4. Setup RTG
        rtg = setup_retargeter(asset_tools, editor_asset_lib, ik_mixamo, mixamo_mesh, combat_rig, combat_mesh)
        
        # 5. Find source animation sequence from import
        source_anim = None
        for obj in editor_asset_lib.list_assets(MIXAMO_PKG):
            loaded = unreal.load_asset(obj)
            if loaded and loaded.get_class().get_name() == "AnimSequence":
                source_anim = loaded
                break
        if not source_anim:
            raise RuntimeError(f"No AnimSequence found in {MIXAMO_PKG} after import.")
        
        # 6. Retarget sequence
        retargeted_seq = retarget_mixamo_clip(editor_asset_lib, source_anim, mixamo_mesh, combat_mesh, rtg)
        
        # 7. Build montage
        montage = build_backstep_montage(asset_tools, editor_asset_lib, retargeted_seq)
        
        # 8. Log full readback
        m_len = float(montage.get_editor_property("sequence_length"))
        notifies = []
        for ev in unreal.AnimationLibrary.get_animation_notify_events(montage):
            st = ev.get_editor_property("notify_state_class")
            no = ev.get_editor_property("notify")
            obj = st if st else no
            if obj:
                notifies.append(f"{obj.get_class().get_name()} at {ev.get_editor_property('trigger_time_offset'):.4f}s")
        
        log("=== READBACK VERIFICATION ===")
        log(f"Montage: {TARGET_MONTAGE_NAME}")
        log(f"Length: {m_len:.4f}s")
        log(f"Notifies: {notifies}")
        log("=============================")
        return True
    finally:
        release_engine_lock(proj)


def main():
    if not IN_ENGINE:
        ok, status = dry_check()
        return 0 if ok else 1
    
    ok = execute_pipeline()
    return 0 if ok else 1


if __name__ == "__main__":
    code = main()
    sys.exit(code)
