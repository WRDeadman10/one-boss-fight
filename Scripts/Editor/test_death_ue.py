import unreal

POSE = unreal.AnimPoseExtensions
WORLD = unreal.AnimPoseSpaces.WORLD

body = unreal.load_asset("/Game/OneBossFight/Boss01/Body/SK_Boss01_Body")
tools = unreal.AssetToolsHelpers.get_asset_tools()
t = unreal.AssetImportTask()
t.filename = "C:/UnrealProject/OneBossFight/Import/Boss01/Animations/AN_Boss01_DeathLegend.fbx"
t.destination_path = "/Game/OneBossFight/_Review12"
t.destination_name = "AN_Boss01_DeathLegend"
t.automated = True
t.save = False
t.replace_existing = True
o = unreal.FbxImportUI()
o.set_editor_property("import_mesh", False)
o.set_editor_property("import_as_skeletal", False)
o.set_editor_property("import_animations", True)
o.set_editor_property("skeleton", body.get_editor_property("skeleton"))
o.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_ANIMATION)
t.options = o
tools.import_asset_tasks([t])
anim = unreal.load_asset("/Game/OneBossFight/_Review12/AN_Boss01_DeathLegend")

opts = unreal.AnimPoseEvaluationOptions()
opts.set_editor_property("should_retarget", False)
opts.set_editor_property("extract_root_motion", False)

socket = body.find_socket("HeavySwordSocket_R")
bone = str(socket.get_editor_property("bone_name"))
loc = socket.get_editor_property("relative_location")
rot = socket.get_editor_property("relative_rotation")
scale = socket.get_editor_property("relative_scale")
rel = unreal.Transform(loc, rot, scale)
sword = unreal.load_asset("/Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword")
box = sword.get_bounding_box()
tip_local = unreal.Vector(0, 0, box.max.z)

lo_ank, lo_ball, hi_knee = 1e9, 1e9, -1e9
for t_sec in [1.4 + 0.1 * i for i in range(22)]:
    p = POSE.get_anim_pose_at_time(anim, min(t_sec, 3.5), opts)
    fl = POSE.get_bone_pose(p, "foot_l", WORLD).translation.z
    fr = POSE.get_bone_pose(p, "foot_r", WORLD).translation.z
    bl = POSE.get_bone_pose(p, "ball_l", WORLD).translation.z
    br = POSE.get_bone_pose(p, "ball_r", WORLD).translation.z
    kl = POSE.get_bone_pose(p, "calf_l", WORLD).translation.z
    kr = POSE.get_bone_pose(p, "calf_r", WORLD).translation.z
    lo_ank = min(lo_ank, fl, fr)
    lo_ball = min(lo_ball, bl, br)
    hi_knee = max(hi_knee, kl, kr)

unreal.log("[DeathReview] Kneeling frames (1.4-3.5s): lowest ankle=%.2f (want >=3), lowest ball=%.2f (want >= -1), highest knee=%.2f" % (lo_ank, lo_ball, hi_knee))

p25 = POSE.get_anim_pose_at_time(anim, 2.5, opts)
bx = POSE.get_bone_pose(p25, bone, WORLD)
comp = unreal.MathLibrary.compose_transforms(rel, bx)
grip = comp.translation
tip = unreal.MathLibrary.transform_location(comp, tip_local)
unreal.log("[DeathReview] at 2.5s: grip %s, tip %s, tip Z=%.2f (want >= 0)" % (grip, tip, tip.z))

# Slump check: head minus pelvis Y >= 30, head z <= 90
hp25 = POSE.get_bone_pose(p25, "head", WORLD).translation - POSE.get_bone_pose(p25, "pelvis", WORLD).translation
head_z = POSE.get_bone_pose(p25, "head", WORLD).translation.z
unreal.log("[DeathReview] head minus pelvis: %s (y=%.1f, want >=30), head z=%.1f (want <=90)" % (hp25, hp25.y, head_z))
