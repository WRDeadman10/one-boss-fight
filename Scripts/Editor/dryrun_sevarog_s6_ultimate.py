"""Transient-only C++ validator dry-run for the C-1242 S6 ultimate card candidate."""
from pathlib import Path
import sys

try:
    import unreal
except ImportError:
    unreal = None

EDITOR_DIR = Path(__file__).resolve().parent
if str(EDITOR_DIR) not in sys.path:
    sys.path.insert(0, str(EDITOR_DIR))
import author_sevarog_draft_cards as shared

SEQUENCE = "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Ultimate_Swing_120fps.Ultimate_Swing_120fps"
SKELETON = shared.SKELETON_PATH
MESH = "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog.Sevarog"


def main():
    unreal_module = shared.require_editor_module(unreal)
    f5 = shared.read_f5_cards(Path(unreal_module.Paths.project_dir()))
    row = dict(shared.build_candidate_specs(f5)[2])  # HeavySlam F5 analogue, values stay provisional.
    row.update({
        "asset_name": "DA_Move_Sevarog_Ultimate_Swing_120fps_S6_C1274",
        "move_id": "Move_Sevarog_Ultimate_Swing_120fps_S6",
        "sequence": SEQUENCE,
        "commit_seconds": 0.600,
        "active_start_seconds": 0.667,
        "active_end_seconds": 0.867,
        "recovery_end_seconds": 2.633,
        "warp_start_seconds": 0.0,
        "warp_end_seconds": 0.0,
        "warp_max_distance_cm": 0.0,
        "warp_max_angle_degrees": 0.0,
        "warp_standoff_cm": 0.0,
        "warp_ease_in_out": False,
        "source_analog": "Move_Sevarog_HeavySlam_F5",
        "source_status": "provisional C-1242 visual timing; other values from proposed F5 heavy-slam analogue",
    })
    row["windows"] = [dict(row["windows"][0],
                            window_id="Window_Ultimate_Swing_Six",
                            start_seconds=0.667, end_seconds=0.867)]
    loaded = {}
    for path in (SKELETON, SEQUENCE, MESH):
        asset = unreal_module.EditorAssetLibrary.load_asset(path.split(".", 1)[0])
        shared.require(asset is not None and str(asset.get_path_name()) == path,
                       "read-only dependency did not resolve exactly: " + path)
        loaded["skeleton" if path == SKELETON else "mesh" if path == MESH else path] = asset
    card_class = unreal_module.load_class(None, "/Script/OneBossFight.RPGBossMoveCard")
    shared.require(card_class is not None, "RPGBossMoveCard class unavailable")
    card = unreal_module.new_object(card_class)
    shared.require(card is not None and not str(card.get_path_name()).startswith("/Game/"),
                   "S6 card must remain transient")
    shared.set_property(card, "spec", shared.make_card_spec(unreal_module, row, loaded))
    validate_card, _validate_profile = shared.get_cpp_validation_bridge(unreal_module)
    valid, diagnostics = shared.unpack_validation_result(validate_card(card, loaded["mesh"]), "S6")
    for diagnostic in diagnostics:
        unreal_module.log("[SevarogS6DryRun] VALIDATION " + diagnostic)
    shared.require(valid and not diagnostics, "S6 production C++ validation failed")
    unreal_module.log("[SevarogS6DryRun] PASS move=%s tell=0.000..0.600 active=0.667..0.867 recoveryEnd=2.633 playRate=1.0 range=90..180 damage=55 provisional=1 saved=0" % row["move_id"])


try:
    main()
except Exception as error:
    if unreal is not None:
        unreal.log_error("[SevarogS6DryRun] FAIL " + str(error))
    else:
        raise
