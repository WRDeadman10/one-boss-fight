"""Non-destructive Greystone pack quick/full roll root-motion retarget.

Default mode is a read-only inventory/preflight. Pass --write to create isolated
_RM sequences and montage copies in the player Greystone allowlist. The script
never edits or deletes existing assets. Run only in the full Unreal Editor,
after the Lead releases the editor and required project locks.
"""
import json
import os
import time
import traceback

import unreal

PREFIX = "[GreystonePackRM] "
SOURCE_MESH = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin"
TARGET_MESH = "/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone"
SOURCE_RIG = "/Game/OneBossFight/GreystonePack/IK_CombatMannequin"
TARGET_RIG = "/Game/OneBossFight/Characters/Greystone/IK_Greystone"
OUT_ROOT = "/Game/OneBossFight/Player/Greystone/RootMotion"
RM_TARGET_RIG = OUT_ROOT + "/IK_Greystone_RM"
RETARGETER = OUT_ROOT + "/RTG_CombatMannequin_To_Greystone_RM"
SUFFIX = "_RM"

# This is intentionally a closed, source-derived selection. URPGDodgeTiming's
# QuickMontage/FullMontage defaults, its child readback, and C1259 identify the
# two pack roll assets. No weapon attack array or unrelated pack sequence is
# inferred into the retarget set.
ROLLS = (
    {
        "kind": "quick",
        "source_sequence": "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll",
        "source_grey_sequence": "/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Grey",
        "source_grey_montage": "/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage_Grey",
    },
    {
        "kind": "full",
        "source_sequence": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle",
        "source_grey_sequence": "/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Grey",
        "source_grey_montage": "/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Montage_Grey",
    },
)


def log(message):
    unreal.log(PREFIX + str(message))


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def load(path):
    asset = unreal.load_asset(path)
    require(asset is not None, "required asset missing: " + path)
    return asset


def xy_displacement(sequence, bone):
    length = sequence.get_play_length()
    start = unreal.AnimationLibrary.get_bone_pose_for_time(sequence, bone, 0.0, False).translation
    end = unreal.AnimationLibrary.get_bone_pose_for_time(sequence, bone, length, False).translation
    return ((end.x - start.x) ** 2 + (end.y - start.y) ** 2) ** 0.5


def has_root_chain(rig):
    controller = unreal.IKRigController.get_controller(rig)
    for chain in controller.get_retarget_chains():
        start = str(chain.get_editor_property("start_bone").get_editor_property("bone_name"))
        end = str(chain.get_editor_property("end_bone").get_editor_property("bone_name"))
        if start == "root" and end == "root":
            return controller, str(chain.get_editor_property("chain_name"))
    return controller, None


def write_mode():
    return "--write" in unreal.SystemLibrary.get_command_line().split()


def preflight(write):
    eal = unreal.EditorAssetLibrary
    source_mesh, target_mesh = load(SOURCE_MESH), load(TARGET_MESH)
    source_rig, target_rig = load(SOURCE_RIG), load(TARGET_RIG)
    source_skeleton = source_mesh.get_editor_property("skeleton")
    target_skeleton = target_mesh.get_editor_property("skeleton")
    require(source_skeleton is not None and target_skeleton is not None, "mesh skeleton missing")
    source_controller, source_root = has_root_chain(source_rig)
    require(source_root is not None, "source IK rig lacks root->root chain; refusing source-rig mutation")
    destinations = [RM_TARGET_RIG, RETARGETER]
    for item in ROLLS:
        destinations.extend((OUT_ROOT + "/Sequences/" + item["kind"] + "/" + item["source_sequence"].rsplit("/", 1)[-1] + SUFFIX,
                             OUT_ROOT + "/Montages/" + item["kind"] + "/" + item["source_grey_montage"].rsplit("/", 1)[-1] + SUFFIX))
    for path in destinations:
        require(not eal.does_asset_exist(path), "refusing to overwrite existing asset: " + path)
    sequences, montages = [], []
    for item in ROLLS:
        source = load(item["source_sequence"])
        existing_grey = load(item["source_grey_sequence"])
        montage = load(item["source_grey_montage"])
        require(str(source.get_class().get_name()) == "AnimSequence", "source is not AnimSequence: " + item["source_sequence"])
        require(str(existing_grey.get_class().get_name()) == "AnimSequence", "Grey reference is not AnimSequence: " + item["source_grey_sequence"])
        require(str(montage.get_class().get_name()) == "AnimMontage", "Grey reference is not AnimMontage: " + item["source_grey_montage"])
        require(source.get_editor_property("skeleton") == source_skeleton, "source sequence skeleton mismatch: " + item["source_sequence"])
        require(existing_grey.get_editor_property("skeleton") == target_skeleton, "existing Grey sequence target skeleton mismatch: " + item["source_grey_sequence"])
        require(montage.get_editor_property("skeleton") == target_skeleton, "Grey montage target skeleton mismatch: " + item["source_grey_montage"])
        require(xy_displacement(source, "root") > 0.5, "source has no measurable root XY motion: " + item["source_sequence"])
        sequences.append(source)
        montages.append(montage)
    _, target_root = has_root_chain(target_rig)
    log("PREFLIGHT mode=%s selected_sequences=%d selected_montages=%d source_root=%s target_root=%s (isolated copy will add Root if absent)" %
        ("WRITE" if write else "DRY_RUN", len(sequences), len(montages), source_root,
         target_root if target_root else "absent"))
    for item, source, montage in zip(ROLLS, sequences, montages):
        log("SELECT kind=%s source=%s root_xy_cm=%.3f Grey_sequence=%s Grey_montage=%s" %
            (item["kind"], source.get_path_name(), xy_displacement(source, "root"),
             item["source_grey_sequence"], montage.get_path_name()))
    return source_mesh, target_mesh, source_rig, target_rig, source_root, sequences, montages, source_skeleton, target_skeleton


def ensure_root_chain(rig):
    controller, name = has_root_chain(rig)
    if name:
        return controller, name
    name = str(controller.add_retarget_chain("Root", "root", "root", ""))
    require(name not in ("", "None"), "failed adding Root chain to isolated target rig")
    return controller, name


def main():
    write = write_mode()
    state = preflight(write)
    if not write:
        log("RESULT=PASS dry_run=1 saves=0")
        return
    source_mesh, target_mesh, source_rig, target_rig, source_root, sequences, montages, source_skeleton, target_skeleton = state
    eal = unreal.EditorAssetLibrary
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    for folder in (OUT_ROOT, OUT_ROOT + "/Sequences/quick", OUT_ROOT + "/Sequences/full",
                   OUT_ROOT + "/Montages/quick", OUT_ROOT + "/Montages/full"):
        eal.make_directory(folder)
    require(eal.duplicate_asset(TARGET_RIG, RM_TARGET_RIG) is not None, "could not duplicate target IK rig")
    isolated_target_rig = load(RM_TARGET_RIG)
    target_controller, target_root = ensure_root_chain(isolated_target_rig)
    require(eal.save_loaded_asset(isolated_target_rig), "could not save isolated target IK rig")
    retargeter = tools.create_asset(RETARGETER.rsplit("/", 1)[-1], OUT_ROOT, unreal.IKRetargeter, unreal.IKRetargetFactory())
    require(retargeter is not None, "could not create isolated retargeter")
    rtg = unreal.IKRetargeterController.get_controller(retargeter)
    # UE 5.5.4 exposes these controller setters as void UFUNCTIONs. Python
    # therefore returns None on success; verify state through the paired getters.
    rtg.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, source_rig)
    require(rtg.get_ik_rig(unreal.RetargetSourceOrTarget.SOURCE) == source_rig,
            "source rig readback mismatch")
    rtg.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, isolated_target_rig)
    require(rtg.get_ik_rig(unreal.RetargetSourceOrTarget.TARGET) == isolated_target_rig,
            "target rig readback mismatch")
    rtg.set_preview_mesh(unreal.RetargetSourceOrTarget.SOURCE, source_mesh)
    require(rtg.get_preview_mesh(unreal.RetargetSourceOrTarget.SOURCE) == source_mesh,
            "source preview mesh readback mismatch")
    rtg.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET, target_mesh)
    require(rtg.get_preview_mesh(unreal.RetargetSourceOrTarget.TARGET) == target_mesh,
            "target preview mesh readback mismatch")
    rtg.auto_map_chains(unreal.AutoMapChainType.FUZZY, True)
    require(rtg.set_source_chain(source_root, target_root), "could not map Root chain")
    settings = rtg.get_retarget_chain_settings(target_root)
    fk = settings.get_editor_property("fk")
    fk.set_editor_property("translation_mode", unreal.RetargetTranslationMode.GLOBALLY_SCALED)
    fk.set_editor_property("translation_alpha", 1.0)
    settings.set_editor_property("fk", fk)
    require(rtg.set_retarget_chain_settings(target_root, settings), "could not set Root FK mode")
    require(eal.save_loaded_asset(retargeter), "could not save isolated retargeter")

    asset_data = [eal.find_asset_data(sequence.get_path_name()) for sequence in sequences]
    require(all(data.is_valid() for data in asset_data), "source sequence asset-data lookup failed")
    results = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
        asset_data, source_mesh, target_mesh, retargeter, "", "", "", SUFFIX, False)
    require(len(results) == len(sequences), "batch output count mismatch; inspect newly-created assets before retry")
    by_name = {str(row.asset_name): row for row in results}
    manifest_rows = []
    wrapper_library = getattr(unreal, "RPGMontageWrapperLibrary", None)
    require(wrapper_library is not None, "editor montage wrapper library unavailable")
    for item, source, source_montage in zip(ROLLS, sequences, montages):
        sequence_name = source.get_name() + SUFFIX
        require(sequence_name in by_name, "retarget result missing: " + sequence_name)
        sequence_path = OUT_ROOT + "/Sequences/" + item["kind"] + "/" + sequence_name
        result_path = str(by_name[sequence_name].package_name)
        if result_path != sequence_path:
            require(eal.rename_asset(result_path, sequence_path), "could not move new sequence to isolated output: " + sequence_name)
        target_sequence = load(sequence_path)
        require(target_sequence.get_editor_property("skeleton") == target_skeleton, "retargeted sequence skeleton mismatch")
        source_root_xy = xy_displacement(source, "root")
        output_root_xy = xy_displacement(target_sequence, "root")
        require(output_root_xy > 0.5 * source_root_xy, "root XY did not survive retarget: " + sequence_path)
        require(bool(target_sequence.get_editor_property("enable_root_motion")), "retargeted sequence root motion disabled: " + sequence_path)
        require(eal.save_loaded_asset(target_sequence), "could not save new sequence: " + sequence_path)
        montage_path = OUT_ROOT + "/Montages/" + item["kind"] + "/" + source_montage.get_name() + SUFFIX
        wrapper_result = wrapper_library.create_retarget_wrapper(source_montage, target_sequence, target_skeleton, montage_path)
        require(isinstance(wrapper_result, tuple) and len(wrapper_result) >= 2 and wrapper_result[0] is not None,
                "C++ montage wrapper creation failed: " + repr(wrapper_result))
        wrapper = wrapper_result[0]
        require(not str(wrapper_result[1]), "C++ montage wrapper error: " + str(wrapper_result[1]))
        require(eal.save_loaded_asset(wrapper), "could not save new wrapper: " + montage_path)
        manifest_rows.append({
            "kind": item["kind"], "source_sequence": source.get_path_name(), "output_sequence": target_sequence.get_path_name(),
            "source_root_xy_cm": source_root_xy, "output_root_xy_cm": output_root_xy,
            "root_xy_ratio": output_root_xy / source_root_xy, "root_motion_enabled": True,
            "source_montage": source_montage.get_path_name(), "output_montage": wrapper.get_path_name(),
            "segment_rows": list(wrapper_library.describe_montage_notifies(wrapper)),
        })
        log("OUTPUT kind=%s sequence=%s root_xy_cm=%.3f ratio=%.5f montage=%s" %
            (item["kind"], target_sequence.get_path_name(), output_root_xy, output_root_xy / source_root_xy, wrapper.get_path_name()))
    manifest_path = os.path.join(unreal.Paths.project_saved_dir(), "GreystonePackRollRM_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
    with open(manifest_path, "w", encoding="utf-8") as handle:
        json.dump({"schema_version": 1, "retargeter": RETARGETER, "root_chain": target_root,
                   "fk_translation_mode": "GLOBALLY_SCALED", "clips": manifest_rows}, handle, indent=2)
    log("MANIFEST " + manifest_path)
    log("RESULT=PASS outputs=%d saves=isolated_only" % (len(manifest_rows) * 2))


try:
    main()
except Exception as error:
    log("RESULT=FAIL error=" + repr(error) + "; no existing asset was intentionally modified or deleted; inspect any new partial outputs before retry")
    traceback.print_exc()
finally:
    try:
        unreal.SystemLibrary.execute_console_command(None, "Quit")
    except Exception:
        pass
