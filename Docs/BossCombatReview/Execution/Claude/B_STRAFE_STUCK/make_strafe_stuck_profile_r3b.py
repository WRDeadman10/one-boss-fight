"""Create a fresh-map neutral-strafe cage proof; never edits or loads SEL008."""
import unreal

DIR = "/Game/OneBossFight/FrameworkProof"
PROFILE_SRC = DIR + "/DA_Sevarog_NeutralStrafe_SEL008"
PROFILE_DST = DIR + "/DA_Sevarog_StrafeStuck_R3b"
LEVEL_DST = DIR + "/L_SevarogFrameworkProofStrafeStuckR3b"
ENGINE_CUBE = "/Engine/BasicShapes/Cube.Cube"
BOSS_X, BOSS_Y = 500.0, 0.0
PLAYER_X = 653.5

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

subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not subsystem.new_level(LEVEL_DST):
    raise RuntimeError("new_level failed: " + LEVEL_DST)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
world.get_world_settings().set_editor_property("default_game_mode", unreal.RPGFrameworkProofGameMode)
spawn = unreal.EditorLevelLibrary.spawn_actor_from_class
cube = unreal.load_asset(ENGINE_CUBE)
if cube is None:
    raise RuntimeError("engine cube mesh unavailable: " + ENGINE_CUBE)

floor = spawn(unreal.StaticMeshActor, unreal.Vector(250.0, 0.0, -50.0))
if floor is None:
    raise RuntimeError("failed to spawn proof floor")
floor.set_actor_label("ProofFloor")
floor.set_actor_scale3d(unreal.Vector(40.0, 40.0, 1.0))
floor.static_mesh_component.set_static_mesh(cube)

start = spawn(unreal.PlayerStart, unreal.Vector(PLAYER_X, 0.0, 100.0))
fixture = spawn(unreal.RPGFrameworkProofFixture, unreal.Vector(0.0, 0.0, 0.0))
if start is None or fixture is None:
    raise RuntimeError("failed to spawn proof PlayerStart or fixture")
start.set_actor_label("ProofPlayerStart")
fixture.set_actor_label("ProofFixture")
fixture.set_editor_property("profile", profile)
fixture.set_editor_property("target_start", start)
fixture.set_editor_property("boss_spawn_transform", unreal.Transform(
    location=[BOSS_X, BOSS_Y, 170.0],
    rotation=unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0),
    scale=[1.0, 1.0, 1.0]))
fixture.set_editor_property("encounter_id", 1)
fixture.set_editor_property("generation", 1)

walls = [
    ("Codex_StrafeCage_N", (BOSS_X, BOSS_Y + 90.0, 140.0), (1.8, 0.2, 3.0)),
    ("Codex_StrafeCage_S", (BOSS_X, BOSS_Y - 90.0, 140.0), (1.8, 0.2, 3.0)),
    ("Codex_StrafeCage_E", (BOSS_X + 90.0, BOSS_Y, 140.0), (0.2, 1.8, 3.0)),
    ("Codex_StrafeCage_W", (BOSS_X - 90.0, BOSS_Y, 140.0), (0.2, 1.8, 3.0)),
]
for label, location, scale in walls:
    actor = spawn(unreal.StaticMeshActor, unreal.Vector(*location), unreal.Rotator(0.0, 0.0, 0.0))
    if actor is None:
        raise RuntimeError("failed to spawn " + label)
    actor.set_actor_label(label)
    actor.static_mesh_component.set_static_mesh(cube)
    # lead: set_collision_profile_name crashed the editor (INT_DIVIDE_BY_ZERO); a StaticMeshActor with the engine Cube already blocks all
    actor.set_actor_scale3d(unreal.Vector(*scale))

nav = spawn(unreal.NavMeshBoundsVolume, unreal.Vector(250.0, 0.0, 100.0))
nav.set_actor_label("ProofNavBounds")
nav.set_actor_scale3d(unreal.Vector(20.0, 20.0, 5.0))
light = spawn(unreal.DirectionalLight, unreal.Vector(0.0, 0.0, 500.0),
              unreal.Rotator(roll=0.0, pitch=-50.0, yaw=30.0))
light.set_actor_label("ProofSun")
assert unreal.EditorLoadingAndSavingUtils.save_map(world, LEVEL_DST), "save_map failed"
unreal.log("[CODEX_STRAFE_STUCK_R3B] created fresh map, fixture, floor, nav bounds, and four BlockAll cage walls")
