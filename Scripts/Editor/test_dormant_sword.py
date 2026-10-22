import unreal

POSE = unreal.AnimPoseExtensions
WORLD = unreal.AnimPoseSpaces.WORLD

body = unreal.load_asset("/Game/OneBossFight/Boss01/Body/SK_Boss01_Body")
socket = body.find_socket("HeavySwordSocket_R")
bone = str(socket.get_editor_property("bone_name"))
loc = socket.get_editor_property("relative_location")
rot = socket.get_editor_property("relative_rotation")
scale = socket.get_editor_property("relative_scale")
rel = unreal.Transform(loc, rot, scale)
sword = unreal.load_asset("/Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword")
box = sword.get_bounding_box()
tip_local = unreal.Vector(0, 0, box.max.z)

anim = unreal.load_asset("/Game/OneBossFight/_Review12/AN_Boss01_DormantIdle")
opts = unreal.AnimPoseEvaluationOptions()
opts.set_editor_property("should_retarget", False)
opts.set_editor_property("extract_root_motion", False)
p = POSE.get_anim_pose_at_time(anim, 0.0, opts)
bx = POSE.get_bone_pose(p, bone, WORLD)

# Test different Rotators for bx (hand_r in component space)
# We want: tip.z ~ 1.0 cm, tip.y > grip.y (pointing forward), tip.x ~ grip.x (centered)
best_diff = 9999.0
best_rot = None
best_tip = None
best_grip = None

# Let's search over pitch, yaw, roll for hand_r
# bx translation is at (-62.7, 24.1, 73.5)
grip_loc = bx.translation
for pitch in range(-90, 91, 10):
    for yaw in range(-180, 181, 15):
        for roll in range(-180, 181, 15):
            r = unreal.Rotator(pitch=float(pitch), yaw=float(yaw), roll=float(roll))
            test_bx = unreal.Transform(grip_loc, r, unreal.Vector(1, 1, 1))
            comp = unreal.MathLibrary.compose_transforms(rel, test_bx)
            g = comp.translation
            t = unreal.MathLibrary.transform_location(comp, tip_local)
            # Conditions:
            # t.z between 0.5 and 1.5 cm
            # t.y > g.y + 40 (pointing forward along +Y)
            # abs(t.x - g.x) < 40 (not pointing sideways)
            if 0.0 <= t.z <= 2.0 and t.y > g.y + 60.0 and abs(t.x - g.x) < 50.0:
                cost = abs(t.z - 1.0) + abs(t.x - g.x) * 0.1
                if cost < best_diff:
                    best_diff = cost
                    best_rot = (pitch, yaw, roll)
                    best_tip = t
                    best_grip = g

unreal.log("[SocketSolver] Best hand_r rot: %s, grip: %s, tip: %s" % (best_rot, best_grip, best_tip))
