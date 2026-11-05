"""Create an arena-edge neutral-strafe proof; no spawned geometry or cage."""
import unreal

DIR = "/Game/OneBossFight/FrameworkProof"
PROFILE_SRC = DIR + "/DA_Sevarog_NeutralStrafe_SEL008"
PROFILE_DST = DIR + "/DA_Sevarog_StrafeStuck_R3c"
LEVEL_SRC = DIR + "/L_SevarogFrameworkProofSEL008"
LEVEL_DST = DIR + "/L_SevarogFrameworkProofStrafeEdgeR3c"

# SEL008's 40x40 scaled floor is centered at (250, 0), giving an approximate
# Y edge at +2000 cm. Keep the boss 100 cm inside that edge and the target close
# on the boss's -X facing line; tangent strafe then has one direction toward the
# floor/nav boundary. The runtime result must still be verified by Claude.
BOSS_X, BOSS_Y = 500.0, 1900.0
PLAYER_X, PLAYER_Y = 653.5, 1900.0

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
fixture = fixtures[0]
fixture.set_editor_property("profile", profile)
fixture.set_editor_property("boss_spawn_transform", unreal.Transform(
    location=[BOSS_X, BOSS_Y, 170.0],
    rotation=unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0),
    scale=[1.0, 1.0, 1.0]))
target = fixture.get_editor_property("target_start")
if target is None:
    raise RuntimeError("proof fixture has no target_start")
target.set_actor_location(unreal.Vector(PLAYER_X, PLAYER_Y, 100.0), False, False)
if abs(float(target.get_actor_location().y) - PLAYER_Y) > 1.0:
    raise RuntimeError("target location readback mismatch")
assert fixture.get_editor_property("profile").get_path_name() == profile.get_path_name()
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert unreal.EditorLoadingAndSavingUtils.save_map(world, LEVEL_DST), "save_map under the new name failed"
unreal.log("[CODEX_STRAFE_EDGE_R3C] created profile/map; no cage; boss at Y=1900 near approximate +2000 floor edge")
