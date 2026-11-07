import bpy
from mathutils import Vector, Quaternion

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

# Delete arm_attack, keep arm_block as main armature
bpy.data.objects.remove(arm_attack, do_unlink=True)
arm = arm_block

print("Successfully imported both actions!")
print("act_block:", act_block.name)
print("act_attack:", act_attack.name)
