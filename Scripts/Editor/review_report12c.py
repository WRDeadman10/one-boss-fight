"""Third part of the Report 12 engine review (log prefix [Review12c]): how the boss's sword sits in the hand in the engine, and what that does to the dormant and wake poses.
Reads the socket HeavySwordSocket_R of SK_Boss01_Body (bone, relative transform), then evaluates the clips of the scratch folder /Game/OneBossFight/_Review12 and the accepted combat idle (PhaseRoar frame 0) in component space:
the sword's grip position, the tip position and the blade direction (the sword's local +Z is the blade, origin at the grip, tip at z 163.3 cm), and the distance between the two hands. Needs review_report12.py's scratch clips."""
import unreal

log = lambda m: unreal.log("[Review12c] " + m)
POSE = unreal.AnimPoseExtensions
WORLD = unreal.AnimPoseSpaces.WORLD
DEST = "/Game/OneBossFight/_Review12/"
body = unreal.load_asset("/Game/OneBossFight/Boss01/Body/SK_Boss01_Body")
skel = body.get_editor_property("skeleton")
log("body %s, skeleton %s" % (body.get_name(), skel.get_name() if skel else None))
socket = None
for i in range(body.num_sockets()):
    smesh = body.get_socket_by_index(i)
    log("mesh socket %s on bone %s: location %s rotation %s scale %s" % (smesh.get_editor_property("socket_name"), smesh.get_editor_property("bone_name"), smesh.get_editor_property("relative_location"), smesh.get_editor_property("relative_rotation"), smesh.get_editor_property("relative_scale")))
for owner, label in ((body, "mesh"), (skel, "skeleton")):
    try:
        found = owner.find_socket("HeavySwordSocket_R")
    except Exception as e:
        found = None
        log("%s find_socket failed: %s" % (label, str(e)[:100]))
    if found:
        log("%s socket HeavySwordSocket_R: bone %s location %s rotation %s scale %s" % (label, found.get_editor_property("bone_name"), found.get_editor_property("relative_location"), found.get_editor_property("relative_rotation"), found.get_editor_property("relative_scale")))
        if socket is None:
            socket = found
if socket is None:
    log("no HeavySwordSocket_R found")
else:
    bone = str(socket.get_editor_property("bone_name"))
    rel = unreal.Transform(socket.get_editor_property("relative_location"), socket.get_editor_property("relative_rotation"), socket.get_editor_property("relative_scale"))
    sword = unreal.load_asset("/Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword")
    box = sword.get_bounding_box()
    tip_local = unreal.Vector(0, 0, box.max.z)
    pommel_local = unreal.Vector(0, 0, box.min.z)
    log("sword local z from %.1f (pommel) to %.1f (tip)" % (box.min.z, box.max.z))

    def pose_at(anim, t):
        opts = unreal.AnimPoseEvaluationOptions()
        opts.set_editor_property("should_retarget", False)
        opts.set_editor_property("extract_root_motion", False)
        return POSE.get_anim_pose_at_time(anim, t, opts)

    def report(label, anim, t):
        p = pose_at(anim, t)
        bx = POSE.get_bone_pose(p, bone, WORLD)  # the hand bone in component space
        sx = rel.transform_to_world if False else None
        # socket in component space = relative * bone transform
        comp = unreal.MathLibrary.compose_transforms(rel, bx)
        grip = comp.translation
        tip = unreal.MathLibrary.transform_location(comp, tip_local)
        pom = unreal.MathLibrary.transform_location(comp, pommel_local)
        d = (tip - grip)
        d = d / d.length() if d.length() > 0 else d
        hl = POSE.get_bone_pose(p, "hand_l", WORLD).translation
        hr = POSE.get_bone_pose(p, "hand_r", WORLD).translation
        log("%-28s grip (%.0f %.0f %.0f) tip (%.0f %.0f %.0f) pommel (%.0f %.0f %.0f) blade dir (%.2f %.2f %.2f); hands %.0f cm apart (hand_r (%.0f %.0f %.0f), hand_l (%.0f %.0f %.0f))" % (
            label, grip.x, grip.y, grip.z, tip.x, tip.y, tip.z, pom.x, pom.y, pom.z, d.x, d.y, d.z, (hl - hr).length(), hr.x, hr.y, hr.z, hl.x, hl.y, hl.z))

    for name, times in (("AN_Boss01_PhaseRoar", (0.0, 0.7)), ("AN_Boss01_DormantIdle", (0.0, 1.25)), ("AN_Boss01_Wake", (0.0, 1.0, 1.5, 2.0, 2.5, 3.5)), ("AN_Boss01_StaggerDown", (0.0,)), ("AN_Boss01_DeathLegend", (0.0, 2.5))):
        anim = unreal.load_asset(DEST + name)
        for t in times:
            report("%s %.2f s" % (name.replace("AN_Boss01_", ""), t), anim, t)
    # an earlier accepted combat clip in the project
    a1 = unreal.load_asset("/Game/OneBossFight/Boss01/Animations/AN_Boss01_A1_QuickSlash")
    if a1:
        for t in (0.0, 0.3, 0.6):
            report("A1_QuickSlash %.2f s" % t, a1, t)
log("done")
