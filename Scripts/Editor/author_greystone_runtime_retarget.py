"""Author Greystone's runtime retarget visual. Dry-run by default; run only through its reviewed C-1155 runner."""
import sys
import traceback

import unreal

PREFIX = "[GreystoneRuntimeRetarget] "
PLAYER_PATH = "/Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer"
ANIM_BP_PATH = "/Game/OneBossFight/Player/Greystone/ABP_Greystone_RuntimeRetarget"
GREYSTONE_MESH_PATH = "/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone"
RETARGETER_PATH = "/Game/OneBossFight/GreystonePack/RTG_CombatMannequin_To_Greystone"
VISIBLE_COMPONENT = "GreystoneRuntimeVisual"
WRITE = "--write" in sys.argv


def require(ok, message):
    if not ok:
        raise RuntimeError(PREFIX + "REFUSED: " + message)


def log(message):
    unreal.log(PREFIX + message)


def unpack_result(result, count, operation):
    """UE 5.5 Python maps 'bool F(..., Out1, ..., OutError)': False -> None (outputs dropped), True -> tuple of the
    out parameters only (no bool). count is the C++ arity including the bool, so a success tuple has count-1 items."""
    require(result is not None, "%s failed: the C++ helper returned false (see the [GreystoneRetarget] error token in this log)" % operation)
    require(isinstance(result, tuple) and len(result) == count - 1, "%s returned unexpected Python binding result: %r" % (operation, result))
    require(not str(result[-1]), "%s reported an error despite success: %s" % (operation, result[-1]))
    return result[:-1]


def load(path, cls=None):
    asset = unreal.EditorAssetLibrary.load_asset(path)
    require(asset is not None, "asset unavailable: " + path)
    if cls is not None:
        require(isinstance(asset, cls), "wrong asset type: " + path)
    return asset


def component_inventory(bp, library):
    encoded_rows = unpack_result(
        library.get_greystone_player_component_inventory(bp), 3,
        "SCS and inherited component inventory")
    rows = []
    for encoded in encoded_rows[0]:
        fields = str(encoded).split("|", 5)
        require(len(fields) == 6, "C++ component inventory row has wrong field count: %r" % encoded)
        name, class_path, parent, socket, mesh_path, anim_class_path = fields
        rows.append({"name": name, "class": class_path.rsplit(".", 1)[-1],
                     "class_path": class_path, "parent": parent, "socket": socket,
                     "mesh_path": mesh_path, "anim_class_path": anim_class_path,
                     "path": name})
    return rows


def audit(bp, library):
    rows = component_inventory(bp, library)
    log("COMPONENT_AUDIT count=%d" % len(rows))
    for row in rows:
        log("ATTACH_AUDIT name=%s class=%s parent=%s socket=%s" %
            (row["name"], row["class_path"], row["parent"], row["socket"]))
    attached = [row for row in rows if row["parent"] in ("Mesh", "CharacterMesh0") and row["name"] != VISIBLE_COMPONENT]
    log("SOURCE_ATTACHED_COMPONENTS=%d; preserve and visually verify weapon/equipment sockets before PIE" % len(attached))
    return rows


def main():
    bp = load(PLAYER_PATH, unreal.Blueprint)
    mesh = load(GREYSTONE_MESH_PATH, unreal.SkeletalMesh)
    retargeter = load(RETARGETER_PATH, unreal.IKRetargeter)
    library = getattr(unreal, "RPGGreystoneRuntimeRetargetLibrary", None)
    require(library is not None, "editor C++ RPGGreystoneRuntimeRetargetLibrary is not loaded; build is required")
    require(bp.get_path_name() == PLAYER_PATH + ".BP_GreystoneERPlayer", "player BP package path mismatch")
    log("TARGETS player=%s mesh=%s retargeter=%s write=%s" %
        (bp.get_path_name(), mesh.get_path_name(), retargeter.get_path_name(), int(WRITE)))
    rows = audit(bp, library)
    planned = unpack_result(library.plan_greystone_runtime_retarget(), 3, "read-only AnimBP preflight")
    log("PLAN=" + str(planned[0]))
    require(not any(row["name"] == VISIBLE_COMPONENT for row in rows) or WRITE,
            "visual component already exists; explicit --write required for idempotent configuration")
    if not WRITE:
        log("RESULT=DRY_RUN assets_saved=0 components_changed=0 map_saved=0")
        return

    created = unpack_result(library.create_greystone_runtime_retarget_anim_blueprint(), 3, "AnimBP authoring")
    anim_bp = load(ANIM_BP_PATH, unreal.AnimBlueprint)
    require(anim_bp.get_path_name() == created[0], "AnimBP helper returned unexpected path")
    require(unreal.EditorAssetLibrary.save_loaded_asset(anim_bp), "failed to save runtime retarget AnimBP")
    configured = unpack_result(library.configure_greystone_player_blueprint(bp), 3, "player component setup")
    log("SETUP=" + str(configured[0]))
    require(unreal.EditorAssetLibrary.save_loaded_asset(bp), "failed to save BP_GreystoneERPlayer")

    # Validate the authored templates after compile/save without opening a map or PIE.
    bp = load(PLAYER_PATH, unreal.Blueprint)
    verify_rows = component_inventory(bp, library)
    player_cdo = unreal.get_default_object(bp.generated_class())
    source_template = player_cdo.get_editor_property("mesh")
    source_mesh = source_template.get_editor_property("skeletal_mesh_asset")
    source_anim = source_template.get_editor_property("anim_class")
    require(source_mesh is not None and source_mesh.get_name().startswith("SKM_CombatMannequin"),
            "hidden CharacterMesh0 mannequin readback mismatch")
    require(source_anim is not None and source_anim.get_name() == "ABP_CombatCharacter_C",
            "hidden CharacterMesh0 canonical pack AnimBP readback mismatch")
    require(not source_template.get_editor_property("visible") and source_template.get_editor_property("hidden_in_game"),
            "canonical source mesh is not hidden")
    tick_option = str(source_template.get_editor_property("visibility_based_anim_tick_option"))
    log("SOURCE_TICK_OPTION=" + tick_option)
    # Python renders the enum as e.g. 'VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES'; compare normalised.
    require("ALWAYSTICKPOSEANDREFRESHBONES" in tick_option.upper().replace("_", ""),
            "canonical source mesh tick option readback mismatch: " + tick_option)
    visual = next((row for row in verify_rows if row["name"] == VISIBLE_COMPONENT), None)
    require(visual is not None and visual["class"] == "SkeletalMeshComponent", "visible Greystone component readback missing")
    require(visual["mesh_path"] == mesh.get_path_name(),
            "visible component mesh readback mismatch")
    require(visual["anim_class_path"] == ANIM_BP_PATH + ".ABP_Greystone_RuntimeRetarget_C",
            "visible component AnimBP readback mismatch")
    log("READBACK source_mesh=%s source_anim=%s hidden=1 source_tick=AlwaysTickPoseAndRefreshBones visible=%s parent=%s anim_bp=%s map_saved=0" %
        (source_mesh.get_path_name(), source_anim.get_path_name(), visual["name"], visual["parent"],
         visual["anim_class_path"]))
    log("RESULT=PASS saved=2 map_saved=0 pie=0 attachments_audited=%d" % len(verify_rows))


RUN_RESULT = "NOT_RUN"
try:
    main()
except Exception as exc:
    RUN_RESULT = "FAIL"
    log("RESULT=FAIL " + repr(exc))
    traceback.print_exc()
else:
    RUN_RESULT = "PASS"
finally:
    try:
        unreal.SystemLibrary.execute_console_command(None, "Quit")
    except Exception:
        pass
