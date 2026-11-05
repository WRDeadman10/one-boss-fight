"""Create a neutral-strafe proof copy with a collision cage; refuses existing assets."""
import unreal

DIR = "/Game/OneBossFight/FrameworkProof"
PROFILE_SRC = DIR + "/DA_Sevarog_NeutralStrafe_SEL008"
PROFILE_DST = DIR + "/DA_Sevarog_StrafeStuck_R3"
LEVEL_SRC = DIR + "/L_SevarogFrameworkProofSEL008"
LEVEL_DST = DIR + "/L_SevarogFrameworkProofStrafeStuckR3"
ENGINE_CUBE = "/Engine/BasicShapes/Cube.Cube"
BOSS_X, BOSS_Y = 500.0, 0.0

lib = unreal.EditorAssetLibrary
for path in (PROFILE_DST, LEVEL_DST):
    if lib.does_asset_exist(path):
        raise RuntimeError("destination exists; refusing to overwrite: " + path)
assert lib.duplicate_asset(PROFILE_SRC, PROFILE_DST), "profile duplicate failed"
profile = unreal.load_asset(PROFILE_DST)
if float(profile.get_editor_property("neutral_strafe_seconds")) <= 0.0:
    raise RuntimeError("source profile must have neutral strafe enabled")
profile.set_editor_property("cone_hysteresis_degrees", 0.0)
assert float(profile.get_editor_property("cone_hysteresis_degrees")) == 0.0
assert lib.save_loaded_asset(profile)

assert unreal.EditorLevelLibrary.load_level(LEVEL_SRC), "source proof map load failed"
fixtures = [a for a in unreal.EditorLevelLibrary.get_all_level_actors()
            if a.get_class().get_name() == "RPGFrameworkProofFixture"]
if len(fixtures) != 1:
    raise RuntimeError("expected one framework proof fixture, got %d" % len(fixtures))
fixtures[0].set_editor_property("profile", profile)
assert fixtures[0].get_editor_property("profile").get_path_name() == profile.get_path_name()

cube = unreal.load_asset(ENGINE_CUBE)
if cube is None:
    raise RuntimeError("engine cube mesh unavailable: " + ENGINE_CUBE)
# Four short, solid walls leave the boss a small start area but block the tangent
# movement in either strafe direction. Center is the SEL008 boss spawn (500,0,170).
walls = [
    ("Codex_StrafeCage_N", (BOSS_X, BOSS_Y + 90.0, 140.0), (1.8, 0.2, 3.0)),
    ("Codex_StrafeCage_S", (BOSS_X, BOSS_Y - 90.0, 140.0), (1.8, 0.2, 3.0)),
    ("Codex_StrafeCage_E", (BOSS_X + 90.0, BOSS_Y, 140.0), (0.2, 1.8, 3.0)),
    ("Codex_StrafeCage_W", (BOSS_X - 90.0, BOSS_Y, 140.0), (0.2, 1.8, 3.0)),
]
for label, loc, scale in walls:
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor, unreal.Vector(*loc), unreal.Rotator(0.0, 0.0, 0.0))
    if actor is None:
        raise RuntimeError("failed to spawn " + label)
    actor.set_actor_label(label)
    component = actor.get_editor_property("static_mesh_component")
    component.set_static_mesh(cube)
    component.set_collision_profile_name("BlockAll")
    actor.set_actor_scale3d(unreal.Vector(*scale))

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert unreal.EditorLoadingAndSavingUtils.save_map(world, LEVEL_DST), "save_map under the new name failed"
unreal.log("[CODEX_STRAFE_STUCK_R3] created profile/map and four BlockAll walls; neutral_str safely enabled, cone hysteresis off")
