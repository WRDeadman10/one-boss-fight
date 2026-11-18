"""Read-only C-1155 diagnostic for Sevarog definition skeleton/animation refs."""
import json
import os
import sys
import traceback
from pathlib import Path

import unreal

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import ue_editor_values

PREFIX = "[SevarogDependencyReadback] "
DEFINITION_PATH = "/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_Draft.DA_Boss_Sevarog_Draft"


def log(message):
    unreal.log(PREFIX + str(message))


def inspect_reference(value):
    raw_path = ue_editor_values.ue_path(value)
    loaded = unreal.load_asset(raw_path) if raw_path else None
    loaded_path = str(loaded.get_path_name()) if loaded is not None else ""
    return raw_path, loaded, loaded_path


def main():
    output = os.environ.get("SEVAROG_DEPENDENCY_READBACK_RECEIPT", "").strip()
    if not output:
        raise RuntimeError("SEVAROG_DEPENDENCY_READBACK_RECEIPT is required")
    definition = unreal.load_asset(DEFINITION_PATH)
    if definition is None:
        raise RuntimeError("saved Sevarog definition did not load: " + DEFINITION_PATH)

    skeleton_ref = definition.get_editor_property("skeleton")
    skeleton_path, skeleton, loaded_skeleton_path = inspect_reference(skeleton_ref)
    animation_refs = list(definition.get_editor_property("animations") or [])
    animations = []
    for index, reference in enumerate(animation_refs):
        path, animation, loaded_path = inspect_reference(reference)
        animation_skeleton = None
        animation_skeleton_path = ""
        matches_definition_skeleton = False
        if animation is not None:
            animation_skeleton = animation.get_editor_property("skeleton")
            animation_skeleton_path = (str(animation_skeleton.get_path_name())
                                       if animation_skeleton is not None else "")
            matches_definition_skeleton = bool(
                loaded_skeleton_path and animation_skeleton_path == loaded_skeleton_path)
        animations.append({
            "index": index,
            "reference_path": path,
            "loaded": animation is not None,
            "loaded_path": loaded_path,
            "animation_skeleton_path": animation_skeleton_path,
            "matches_definition_skeleton": matches_definition_skeleton,
        })

    dependencies_valid = bool(
        skeleton is not None and animations and
        all(row["loaded"] and row["matches_definition_skeleton"] for row in animations))
    receipt = {
        "readback_complete": True,
        "asset": DEFINITION_PATH,
        "skeleton": {
            "reference_path": skeleton_path,
            "loaded": skeleton is not None,
            "loaded_path": loaded_skeleton_path,
        },
        "animation_count": len(animations),
        "animations": animations,
        "dependencies_valid_for_runtime": dependencies_valid,
        "validation_rule": "Skeleton resolves, Animations is non-empty, and every animation resolves with identical skeleton.",
    }
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    log("READBACK_COMPLETE skeleton_loaded=%d animation_count=%d dependencies_valid=%d receipt=%s" %
        (skeleton is not None, len(animations), dependencies_valid, str(target)))


try:
    main()
except Exception as error:
    log("READBACK_FAILED " + repr(error))
    log(traceback.format_exc())
finally:
    try:
        unreal.SystemLibrary.execute_console_command(None, "Quit")
    except Exception as error:
        log("QUIT_REQUEST_FAILED " + repr(error))
