import bpy
import os

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\Player\Animations_FBX_Export\Attack_PrimaryA_Anim.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
act = arm.animation_data.action
print("Action type:", type(act))
print("Action attributes:", [a for a in dir(act) if not a.startswith('_')])
print("Action frame range:", act.frame_range)
