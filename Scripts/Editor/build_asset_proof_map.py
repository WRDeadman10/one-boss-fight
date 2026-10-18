"""
Builds /Game/OneBossFight/Levels/L_AssetProof: a visual proof that the chosen player (Greystone)
and boss (Sevarog) packs play their core animations, each on its own skeleton.

Every animation is played in a loop by its own SkeletalMeshActor with a text label, in two rows.
Open the map in the editor (realtime viewport) to watch them.

Run headless:
  UnrealEditor-Cmd.exe OneBossFight.uproject -run=pythonscript ^
      -script=Scripts/Editor/build_asset_proof_map.py -unattended -nullrhi
"""

import unreal

LEVEL_PATH = "/Game/OneBossFight/Levels/L_AssetProof"

PLAYER_ROOT = "/Game/ParagonGreystone"
BOSS_ROOT = "/Game/ParagonSevarog"

PLAYER_MESH = "Greystone"
BOSS_MESH = "Sevarog"

# (label, animation asset name)
PLAYER_ANIMS = [
    ("Idle", "Idle"),
    ("Jog Fwd", "Jog_Fwd"),
    ("Light A", "Attack_A_Med"),
    ("Light B", "Attack_B_Med"),
    ("Light C", "Attack_C_Med"),
    ("Light D", "Attack_D_Med"),
    ("Heavy RMB", "Attack_RMB"),
    ("Deflect (parry)", "Deflect_InPlace"),
    ("Hit Front", "HitReact_Front"),
    ("Stun", "Stun_Start"),
    ("Death", "Death"),
    ("Jump Melee", "Jump_Melee"),
]

BOSS_ANIMS = [
    ("Idle", "Idle"),
    ("Jog Fwd", "Jog_Fwd"),
    ("Swing 1", "Swing1_Medium"),
    ("Swing 2", "Swing2_Medium"),
    ("Swing 3", "Swing3_Medium"),
    ("Ultimate Swing", "Ultimate_Swing_120fps"),
    ("Swing In Air", "Swing_In_Air"),
    ("Cast (special)", "Cast"),
    ("Hit Front", "Hitreact_Front"),
    ("Stun Loop", "Stun_Loop"),
    ("Death", "Death_front"),
    ("Level Start (intro)", "LevelStart"),
]

PLAYER_SPACING = 300.0
BOSS_SPACING = 520.0
PLAYER_X = 0.0
BOSS_X = 1700.0


def log(message):
    unreal.log("[AssetProof] " + message)


def index_assets(root):
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    registry.scan_paths_synchronous([root], True)
    index = {}
    for data in registry.get_assets_by_path(root, recursive=True):
        key = (str(data.asset_class_path.asset_name), str(data.asset_name))
        index.setdefault(key, data)
    return index


def find(index, class_name, name):
    data = index.get((class_name, name))
    if data is None:
        raise RuntimeError("Missing %s '%s'" % (class_name, name))
    return data.get_asset()


def spawn(actor_class, location, yaw=0.0):
    return unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class, unreal.Vector(*location), unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw))


def add_label(text, location):
    # Text faces the camera at -X.
    label = spawn(unreal.TextRenderActor, location, yaw=180.0)
    comp = label.text_render
    try:
        comp.set_text(text)
    except Exception:
        comp.set_editor_property("text", text)
    comp.set_editor_property("world_size", 28.0)
    try:
        # The engine enum is spelled "HorizTextAligment".
        comp.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
    except Exception as exc:
        log("Label alignment not set: %s" % exc)
    label.set_actor_label("Label_" + text.replace(" ", "_"))
    return label


def place_row(index, mesh_name, anims, x, spacing, label_height):
    mesh = find(index, "SkeletalMesh", mesh_name)
    start_y = -spacing * (len(anims) - 1) / 2.0
    missing = []
    for i, (label, anim_name) in enumerate(anims):
        y = start_y + i * spacing
        try:
            anim = find(index, "AnimSequence", anim_name)
        except RuntimeError as exc:
            missing.append(anim_name)
            log(str(exc))
            continue

        # Paragon meshes face +Y natively; yaw 90 turns them to face the camera at -X.
        actor = spawn(unreal.SkeletalMeshActor, (x, y, 0.0), yaw=90.0)
        actor.set_actor_label("%s_%s" % (mesh_name, anim_name))
        comp = actor.skeletal_mesh_component
        try:
            comp.set_skeletal_mesh_asset(mesh)
        except Exception:
            comp.set_editor_property("skeletal_mesh_asset", mesh)
        try:
            comp.set_update_animation_in_editor(True)
        except Exception as exc:
            log("Could not enable editor animation: %s" % exc)
        comp.set_editor_property(
            "visibility_based_anim_tick_option",
            unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
        comp.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        # Write the animation into the saved single-node data so it persists in the level
        # (play_animation only changes runtime state and is not saved).
        anim_data = comp.get_editor_property("animation_data")
        anim_data.set_editor_property("anim_to_play", anim)
        anim_data.set_editor_property("saved_looping", True)
        anim_data.set_editor_property("saved_playing", True)
        comp.set_editor_property("animation_data", anim_data)

        add_label("%s\n(%s)" % (label, anim_name), (x - 120.0, y, label_height))
    return missing


def main():
    # new_level will not overwrite an existing map, so remove a previous one first.
    if unreal.EditorAssetLibrary.does_asset_exist(LEVEL_PATH):
        unreal.EditorAssetLibrary.delete_asset(LEVEL_PATH)
    if not unreal.EditorLevelLibrary.new_level(LEVEL_PATH):
        raise RuntimeError("Could not create level " + LEVEL_PATH)

    player_index = index_assets(PLAYER_ROOT)
    boss_index = index_assets(BOSS_ROOT)

    # Ground: a large flat box from the engine basic shapes (100 uu cube scaled).
    floor = spawn(unreal.StaticMeshActor, (900.0, 0.0, -25.0))
    floor.set_actor_label("Floor")
    floor.static_mesh_component.set_static_mesh(unreal.load_asset("/Engine/BasicShapes/Cube.Cube"))
    floor.set_actor_scale3d(unreal.Vector(60.0, 80.0, 0.5))

    sun = spawn(unreal.DirectionalLight, (0.0, 0.0, 1000.0))
    sun.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=-40.0, yaw=60.0), False)
    sun.set_actor_label("Sun")
    spawn(unreal.SkyAtmosphere, (0.0, 0.0, 0.0)).set_actor_label("SkyAtmosphere")
    sky = spawn(unreal.SkyLight, (0.0, 0.0, 800.0))
    sky.set_actor_label("SkyLight")

    missing = []
    missing += place_row(player_index, PLAYER_MESH, PLAYER_ANIMS, PLAYER_X, PLAYER_SPACING, 260.0)
    missing += place_row(boss_index, BOSS_MESH, BOSS_ANIMS, BOSS_X, BOSS_SPACING, 400.0)

    unreal.EditorLevelLibrary.save_current_level()
    log("Saved %s. Missing animations: %s" % (LEVEL_PATH, missing if missing else "none"))


main()
