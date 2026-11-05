"""Build one fresh SEL-008 blocker/control map; never edits existing assets."""
import os
import unreal

DIR = "/Game/OneBossFight/FrameworkProof"
PROFILE_PATH = DIR + "/DA_Sevarog_NeutralStrafe_SEL008"
ENGINE_CUBE_PATH = "/Engine/BasicShapes/Cube.Cube"
MODE = os.environ.get("SEL008_STRAFE_MODE", "blocker").strip().lower()
if MODE not in ("blocker", "control"):
    raise RuntimeError("SEL008_STRAFE_MODE must be 'blocker' or 'control'")

BLOCKER = MODE == "blocker"
# lead 2026-11-04: "b" suffix; the first blocker attempt left an unsaved-content L_...StrafeBlockerSEL008 (owner cleanup list)
LEVEL_NAME = ("L_SevarogFrameworkProofStrafeBlockerSEL008c" if BLOCKER
              else "L_SevarogFrameworkProofStrafeNoWallSEL008c")
LEVEL_PATH = DIR + "/" + LEVEL_NAME

# Match the existing SEL008 F5 fixture positions. The fixture's startup walk
# approaches the 110..140 cm band from 350 cm away; the wall leaves a measured
# capsule-radius-plus-15 cm gap to the Y=0 approach lane, then catches the first
# seeded +Y tangent within the 0.3 s stuck-observation interval.
BOSS_START = unreal.Vector(500.0, 0.0, 167.15)
PLAYER_START = unreal.Vector(850.0, 0.0, 100.0)
BOSS_YAW = 180.0
FLOOR_CENTER = unreal.Vector(250.0, 0.0, -50.0)
FLOOR_SCALE = unreal.Vector(40.0, 40.0, 1.0)
NAV_CENTER = unreal.Vector(250.0, 0.0, 100.0)
NAV_SCALE = unreal.Vector(20.0, 20.0, 5.0)
WALL_FACE_Y = 75.0
WALL_THICKNESS_CM = 20.0
WALL_CENTER_Z = 150.0
WALL_WIDTH_X_CM = 160.0
WALL_SCALE = unreal.Vector(WALL_WIDTH_X_CM / 2.0, WALL_THICKNESS_CM / 100.0, 3.0)  # 160 x 20 x 300 cm
NAV_AGENT_RADIUS_CM = 35.0  # RecastNavMesh radius recorded in the failed live pair's editor log.
WALK_CLEARANCE_CM = 15.0
STUCK_OBSERVATION_SECONDS = 0.3

lib = unreal.EditorAssetLibrary
if lib.does_asset_exist(LEVEL_PATH):
    raise RuntimeError("destination map exists; refusing to overwrite: " + LEVEL_PATH)

# Preflight references and exact source-profile contract before creating/saving
# any project asset. Lesson: never use load_asset on a map.
profile = unreal.load_asset(PROFILE_PATH)
if profile is None:
    raise RuntimeError("SEL008 profile is missing: " + PROFILE_PATH)
if profile.get_path_name().split(".")[0] != PROFILE_PATH:
    raise RuntimeError("SEL008 profile resolved to an unexpected package")
band_min = float(profile.get_editor_property("band_min_cm"))
band_max = float(profile.get_editor_property("band_max_cm"))
walk_speed = float(profile.get_editor_property("walk_speed_cm_per_second"))
strafe_seconds = float(profile.get_editor_property("neutral_strafe_seconds"))
cone_hysteresis = float(profile.get_editor_property("cone_hysteresis_degrees"))
capsule_radius = float(profile.get_editor_property("capsule_radius_cm"))
start_range = abs(float(PLAYER_START.x - BOSS_START.x))
if not (band_min == 110.0 and band_max == 140.0):
    raise RuntimeError("profile band changed; review spawn proof geometry before use")
if not (walk_speed > 0.0 and strafe_seconds > 0.3 and cone_hysteresis == 0.0):
    raise RuntimeError("profile does not match the SEL008 strafe proof contract")
if capsule_radius != 60.0:
    raise RuntimeError("profile capsule radius changed; remeasure wall clearance before use")
if start_range < band_max + 80.0:
    raise RuntimeError("boss start is less than 80 cm beyond the profile band")
wall_near_face = WALL_FACE_Y
walk_capsule_clearance = wall_near_face - capsule_radius
walk_nav_clearance = wall_near_face - NAV_AGENT_RADIUS_CM
strafe_contact_travel = walk_capsule_clearance
if walk_capsule_clearance < WALK_CLEARANCE_CM:
    raise RuntimeError("blocker face is less than capsule radius + 15 cm from the walk-in lane")
if walk_nav_clearance < WALK_CLEARANCE_CM:
    raise RuntimeError("blocker face is less than nav agent radius + 15 cm from the walk-in lane")
if strafe_contact_travel > walk_speed * STUCK_OBSERVATION_SECONDS:
    raise RuntimeError("blocker contact falls outside the first 0.3 s stuck-observation window")
cube = unreal.load_asset(ENGINE_CUBE_PATH)
if cube is None:
    raise RuntimeError("engine cube mesh unavailable: " + ENGINE_CUBE_PATH)
for type_name in ("RPGFrameworkProofFixture", "RPGFrameworkProofGameMode",
                  "PlayerStart", "StaticMeshActor", "NavMeshBoundsVolume",
                  "DirectionalLight"):
    if not hasattr(unreal, type_name):
        raise RuntimeError("required Unreal Python class is unavailable: " + type_name)

subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if subsystem is None or not subsystem.new_level(LEVEL_PATH):
    raise RuntimeError("new_level failed: " + LEVEL_PATH)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if world is None:
    raise RuntimeError("new level has no editor world")

world_settings = world.get_world_settings()
world_settings.set_editor_property("default_game_mode", unreal.RPGFrameworkProofGameMode)
game_mode = world_settings.get_editor_property("default_game_mode")
if game_mode is None or game_mode.get_name() != "RPGFrameworkProofGameMode":
    raise RuntimeError("default game mode readback mismatch")

spawn = unreal.EditorLevelLibrary.spawn_actor_from_class
floor = spawn(unreal.StaticMeshActor, FLOOR_CENTER)
start = spawn(unreal.PlayerStart, PLAYER_START)
fixture = spawn(unreal.RPGFrameworkProofFixture, unreal.Vector(0.0, 0.0, 0.0))
nav = spawn(unreal.NavMeshBoundsVolume, NAV_CENTER)
sun = spawn(unreal.DirectionalLight, unreal.Vector(0.0, 0.0, 500.0),
            unreal.Rotator(roll=0.0, pitch=-50.0, yaw=30.0))
if any(actor is None for actor in (floor, start, fixture, nav, sun)):
    raise RuntimeError("failed to create floor, player start, fixture, nav bounds, or light")

floor.set_actor_label("SEL008_ProofFloor")
floor.set_actor_scale3d(FLOOR_SCALE)
floor.static_mesh_component.set_static_mesh(cube)
floor.static_mesh_component.set_collision_profile_name("BlockAll")
floor.static_mesh_component.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
nav.set_actor_label("SEL008_ProofNavBounds")
nav.set_actor_scale3d(NAV_SCALE)
sun.set_actor_label("SEL008_ProofSun")
start.set_actor_label("SEL008_ProofPlayerStart")
fixture.set_actor_label("SEL008_ProofFixture")
fixture.set_editor_property("profile", profile)
fixture.set_editor_property("target_start", start)
fixture.set_editor_property("boss_spawn_transform", unreal.Transform(
    location=[BOSS_START.x, BOSS_START.y, BOSS_START.z],
    rotation=unreal.Rotator(roll=0.0, pitch=0.0, yaw=BOSS_YAW),
    scale=[1.0, 1.0, 1.0]))
fixture.set_editor_property("encounter_id", 1)
fixture.set_editor_property("generation", 1)

wall = None
if BLOCKER:
    # The copied source run logs dir=-1 at elapsed 0. With the boss to the
    # target's left, that rule travels toward +Y. At a 60 cm capsule radius,
    # this face yields 15 cm walk-lane clearance and contact after 15 cm of
    # tangent travel (<= 54 cm in the first 0.3 s). The 160 cm X span blocks
    # lateral escape while keeping the wall localized to the band arrival.
    band_center = (band_min + band_max) * 0.5
    wall_x = float(PLAYER_START.x) - band_center
    wall_y = WALL_FACE_Y + WALL_THICKNESS_CM / 2.0
    wall = spawn(unreal.StaticMeshActor,
                 unreal.Vector(wall_x, wall_y, WALL_CENTER_Z),
                 unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0))
    if wall is None:
        raise RuntimeError("failed to create the authored static blocker")
    wall.set_actor_label("SEL008_StaticBlocker_PositiveY")
    wall.set_actor_scale3d(WALL_SCALE)
    wall.static_mesh_component.set_static_mesh(cube)
    wall.static_mesh_component.set_collision_profile_name("BlockAll")
    wall.static_mesh_component.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
    wall_component = wall.static_mesh_component
    if wall_component.get_editor_property("mobility") != unreal.ComponentMobility.STATIC:
        raise RuntimeError("blocker mobility is not Static")
    if wall_component.get_collision_profile_name() != "BlockAll":
        raise RuntimeError("blocker collision profile is not BlockAll")
    if wall_component.get_editor_property("static_mesh").get_path_name() != ENGINE_CUBE_PATH:   # lead fix: constant is the full object path
        raise RuntimeError("blocker mesh readback mismatch")

# All content and reference checks precede the first explicit save. The
# class-valued GameMode readback uses get_name(); object paths use package part.
if fixture.get_editor_property("profile").get_path_name().split(".")[0] != PROFILE_PATH:
    raise RuntimeError("fixture profile reference readback mismatch")
if fixture.get_editor_property("target_start") != start:
    raise RuntimeError("fixture target-start reference readback mismatch")
actual_range = abs(float(start.get_actor_location().x - BOSS_START.x))
if abs(actual_range - start_range) > 1.0:
    raise RuntimeError("authored start range readback mismatch")
if floor.static_mesh_component.get_collision_profile_name() != "BlockAll":
    raise RuntimeError("proof floor collision profile is not BlockAll")
if floor.static_mesh_component.get_editor_property("mobility") != unreal.ComponentMobility.STATIC:
    raise RuntimeError("proof floor mobility is not Static")

save_ok = unreal.EditorLoadingAndSavingUtils.save_map(world, LEVEL_PATH)
if not save_ok:
    raise RuntimeError("save_map failed: " + LEVEL_PATH)
unreal.log("[CODEX_SEL008_STATIC_BLOCKER] map=%s mode=%s startRange=%g band=%g..%g capsuleRadius=%g navAgentRadius=%g wallFaceY=%g walkCapsuleClearance=%g walkNavClearance=%g strafeContactTravel=%g wallXWidth=%g wall=%s"
           % (LEVEL_PATH, MODE, start_range, band_min, band_max, capsule_radius,
              NAV_AGENT_RADIUS_CM, wall_near_face, walk_capsule_clearance,
              walk_nav_clearance, strafe_contact_travel, WALL_WIDTH_X_CM,
              "Static/BlockAll" if BLOCKER else "absent"))
