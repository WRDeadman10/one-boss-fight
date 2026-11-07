import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)

# 1. Import BlockLoop
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\Player\Animations_FBX_Export\BlockLoop.fbx")
arm_block = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
act_block = arm_block.animation_data.action
act_block.name = "act_block"

# 2. Import Attack_PrimaryA
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\Player\Animations_FBX_Export\Attack_PrimaryA_Anim.fbx")
arm_attack = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != arm_block][0]
act_attack = arm_attack.animation_data.action
act_attack.name = "act_attack"

bpy.data.objects.remove(arm_attack, do_unlink=True)
arm = arm_block

# Test snapshot
def snapshot(action, frame):
    arm.animation_data.action = action
    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()
    pb = arm.pose.bones["hand_r"]
    return pb.location.copy(), pb.rotation_quaternion.copy()

loc_block, quat_block = snapshot(act_block, 1)
loc_att, quat_att = snapshot(act_attack, 25)

print("Block hand_r loc:", loc_block, "quat:", quat_block)
print("Attack hand_r loc:", loc_att, "quat:", quat_att)
