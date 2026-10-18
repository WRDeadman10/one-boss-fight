"""
M1 content setup for One Boss Fight. Idempotent: safe to re-run.

Run headless from the project root:
  UnrealEditor-Cmd.exe OneBossFight.uproject -run=pythonscript -script=Scripts/Editor/setup_m1_content.py -unattended -nullrhi

Creates / configures:
  - BP_PlayerCharacter  (input assets, placeholder mesh)
  - BP_RPGGameMode      (default pawn = BP_PlayerCharacter)
  - L_Greybox           (arena, lights, player start)
  - L_Benchmark         (arena, lights, benchmark runner)
"""

import unreal

INPUT_DIR = "/Game/OneBossFight/Input/"
CHARACTER_DIR = "/Game/OneBossFight/Characters"
CORE_DIR = "/Game/OneBossFight/Core"
LEVEL_DIR = "/Game/OneBossFight/Levels/"

PLAYER_BP = CHARACTER_DIR + "/BP_PlayerCharacter"
GAMEMODE_BP = CORE_DIR + "/BP_RPGGameMode"

# Engine-provided placeholder (UE4 mannequin). Replaced when the real player asset is chosen.
PLACEHOLDER_MESH = "/Engine/Tutorial/SubEditors/TutorialAssets/Character/TutorialTPP"
PLACEHOLDER_ANIM = "/Engine/Tutorial/SubEditors/TutorialAssets/Character/TutorialTPP_AnimBlueprint"


def log(msg):
    unreal.log("[M1Setup] " + msg)


def load(path):
    asset = unreal.load_asset(path)
    if asset is None:
        raise RuntimeError("Missing asset: " + path)
    return asset


def set_prop(obj, name, value):
    obj.set_editor_property(name, value)


def configure_player_blueprint():
    bp = load(PLAYER_BP)
    cdo = unreal.get_default_object(bp.generated_class())

    set_prop(cdo, "default_mapping_context", load(INPUT_DIR + "IMC_Default"))
    set_prop(cdo, "move_action", load(INPUT_DIR + "IA_Move"))
    set_prop(cdo, "look_action", load(INPUT_DIR + "IA_Look"))
    set_prop(cdo, "jump_action", load(INPUT_DIR + "IA_Jump"))
    set_prop(cdo, "sprint_action", load(INPUT_DIR + "IA_Sprint"))

    # Placeholder visuals: feet at the capsule bottom (half height 88), facing +X.
    mesh_component = cdo.get_editor_property("mesh")
    mesh_asset = unreal.load_asset(PLACEHOLDER_MESH)
    if mesh_asset is not None:
        try:
            mesh_component.set_editor_property("skeletal_mesh_asset", mesh_asset)
        except Exception:
            mesh_component.set_editor_property("skinned_asset", mesh_asset)
        mesh_component.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -88.0))
        mesh_component.set_editor_property("relative_rotation", unreal.Rotator(roll=0.0, pitch=0.0, yaw=-90.0))
        anim = unreal.load_asset(PLACEHOLDER_ANIM)
        if anim is not None:
            mesh_component.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
            mesh_component.set_editor_property("anim_class", anim.generated_class())
        log("Placeholder mesh assigned.")
    else:
        log("Placeholder mesh not found; the player will be invisible.")

    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_loaded_asset(bp)
    log("BP_PlayerCharacter configured.")
    return bp


def ensure_game_mode_blueprint(player_bp):
    if unreal.EditorAssetLibrary.does_asset_exist(GAMEMODE_BP):
        gm_bp = load(GAMEMODE_BP)
    else:
        factory = unreal.BlueprintFactory()
        factory.set_editor_property("parent_class", unreal.load_class(None, "/Script/OneBossFight.RPGGameMode"))
        tools = unreal.AssetToolsHelpers.get_asset_tools()
        gm_bp = tools.create_asset("BP_RPGGameMode", CORE_DIR, unreal.Blueprint, factory)
        log("Created BP_RPGGameMode.")

    cdo = unreal.get_default_object(gm_bp.generated_class())
    set_prop(cdo, "default_pawn_class", player_bp.generated_class())
    unreal.BlueprintEditorLibrary.compile_blueprint(gm_bp)
    unreal.EditorAssetLibrary.save_loaded_asset(gm_bp)
    return gm_bp


def spawn(actor_class, location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0)):
    # rotation tuple is (pitch, yaw, roll)
    return unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class,
        unreal.Vector(*location),
        unreal.Rotator(roll=rotation[2], pitch=rotation[0], yaw=rotation[1]),
    )


def build_level(name, game_mode_bp, with_benchmark):
    path = LEVEL_DIR + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)

    unreal.EditorLevelLibrary.new_level(path)

    arena = spawn(unreal.load_class(None, "/Script/OneBossFight.RPGGreyboxArena"))
    arena.set_actor_label("GreyboxArena")

    sun = spawn(unreal.DirectionalLight, (0.0, 0.0, 1000.0), (-50.0, -30.0, 0.0))
    sun.set_actor_label("Sun")
    spawn(unreal.SkyAtmosphere).set_actor_label("SkyAtmosphere")
    sky_light = spawn(unreal.SkyLight, (0.0, 0.0, 800.0))
    sky_light.set_actor_label("SkyLight")
    try:
        sky_light.get_editor_property("light_component").set_editor_property("real_time_capture", True)
    except Exception as exc:  # property name differs across versions; non-fatal
        log("SkyLight real-time capture not set: %s" % exc)

    # Player spawns at the arena edge facing the center, where the boss will stand.
    start = spawn(unreal.PlayerStart, (-1800.0, 0.0, 100.0), (0.0, 0.0, 0.0))
    start.set_actor_label("PlayerStart")

    if with_benchmark:
        runner = spawn(unreal.load_class(None, "/Script/OneBossFight.RPGBenchmarkRunner"), (0.0, 0.0, 150.0))
        runner.set_actor_label("BenchmarkRunner")
        set_prop(runner, "run_label", "greybox")

    world = unreal.EditorLevelLibrary.get_editor_world()
    settings = world.get_world_settings()
    set_prop(settings, "default_game_mode", game_mode_bp.generated_class())

    unreal.EditorLevelLibrary.save_current_level()
    log("Level saved: " + path)


def main():
    unreal.EditorAssetLibrary.make_directory(CORE_DIR)
    unreal.EditorAssetLibrary.make_directory(LEVEL_DIR.rstrip("/"))

    player_bp = configure_player_blueprint()
    game_mode_bp = ensure_game_mode_blueprint(player_bp)
    build_level("L_Greybox", game_mode_bp, with_benchmark=False)
    build_level("L_Benchmark", game_mode_bp, with_benchmark=True)
    log("M1 content setup complete.")


main()
