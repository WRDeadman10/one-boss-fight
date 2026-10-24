"""Second part of the engine review of Antigravity's deliveries (log prefix [Review13b]): the boss's in-game scale, the path of the sword tip through the active window of the close clips and the A2 slam (does the blade reach the height of a 190 cm player or the floor?) and the foot heights of the accepted combat idle for comparison.
Needs review_report13.py to have run first (the scratch folder /Game/OneBossFight/_Review13). Run with Scripts/run_in_editor.py."""
import unreal

log = lambda m: unreal.log("[Review13b] " + m)
POSE = unreal.AnimPoseExtensions
WORLD = unreal.AnimPoseSpaces.WORLD
DEST = "/Game/OneBossFight/_Review13/"
body = unreal.load_asset("/Game/OneBossFight/Boss01/Body/SK_Boss01_Body")
socket = body.find_socket("HeavySwordSocket_R")
rel = unreal.Transform(socket.get_editor_property("relative_location"), socket.get_editor_property("relative_rotation"), socket.get_editor_property("relative_scale"))
bone = str(socket.get_editor_property("bone_name"))
tip_local = unreal.Vector(0, 0, unreal.load_asset("/Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword").get_bounding_box().max.z)

# the boss actor of the level: scale of the actor and of its mesh
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character):
    if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C":
        mc = a.get_components_by_class(unreal.SkeletalMeshComponent)[0]
        log("boss actor scale %s, mesh world scale %s, mesh relative scale %s, capsule half height %.1f" % (a.get_actor_scale3d(), mc.get_world_scale(), mc.get_editor_property("relative_scale3d"), a.get_components_by_class(unreal.CapsuleComponent)[0].get_scaled_capsule_half_height()))


def tipat(anim, t):
    opts = unreal.AnimPoseEvaluationOptions()
    opts.set_editor_property("should_retarget", False)
    opts.set_editor_property("extract_root_motion", False)
    p = POSE.get_anim_pose_at_time(anim, min(t, anim.get_editor_property("sequence_length") - 0.0001), opts)
    comp = unreal.MathLibrary.compose_transforms(rel, POSE.get_bone_pose(p, bone, WORLD))
    return comp.translation, unreal.MathLibrary.transform_location(comp, tip_local)


def path(name, t0, t1, step=0.03):
    anim = unreal.load_asset(DEST + name)
    out = []
    t = t0
    lowest = 9999.0
    while t <= t1 + 1e-6:
        g, tp = tipat(anim, t)
        lowest = min(lowest, tp.z)
        out.append("%.2f:(%.0f,%.0f,%.0f)" % (t, tp.x, tp.y, tp.z))
        t += step
    log("%s tip path %s | lowest tip z %.0f" % (name, " ".join(out), lowest))


path("AN_Boss01_A1_QuickSlash", 0.30, 0.55)
path("AN_Boss01_A3a_Combo1", 0.35, 0.65)
path("AN_Boss01_A3b_Combo2", 0.10, 0.45)
path("AN_Boss01_A2_Slam", 0.0, 0.6, 0.05)
# feet of the accepted combat idle (PhaseRoar frame 0) and of the accepted Report 12 clips, for comparison
for name, path_ in (("PhaseRoar", "/Game/OneBossFight/Boss01/Animations/AN_Boss01_PhaseRoar"), ("StaggerDown", "/Game/OneBossFight/Boss01/Animations/AN_Boss01_StaggerDown")):
    anim = unreal.load_asset(path_)
    low_a, low_b = 9999.0, 9999.0
    for i in range(13):
        opts = unreal.AnimPoseEvaluationOptions()
        opts.set_editor_property("should_retarget", False)
        opts.set_editor_property("extract_root_motion", False)
        p = POSE.get_anim_pose_at_time(anim, anim.get_editor_property("sequence_length") * i / 12.0 - (0.0001 if i == 12 else 0.0), opts)
        for b in ("foot_l", "foot_r"):
            low_a = min(low_a, POSE.get_bone_pose(p, b, WORLD).translation.z)
        for b in ("ball_l", "ball_r"):
            low_b = min(low_b, POSE.get_bone_pose(p, b, WORLD).translation.z)
    log("accepted clip %s: lowest ankle %.1f cm, lowest ball %.1f cm" % (name, low_a, low_b))
log("DONE")
