import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)

# 1. Import animated armature
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\Player\Animations_FBX_Export\Attack_PrimaryA_Anim.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
arm.name = "root"

# 2. Import sword
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\ThirdParty\Reference\SM_KwangSword.fbx")
sword = [o for o in bpy.data.objects if o.type == 'MESH'][0]

print(f"Sword original scale: {sword.scale}, dims: {sword.dimensions}")

# Parent to hand_r
sword.parent = arm
sword.parent_type = 'BONE'
sword.parent_bone = "hand_r"

# Check sword world location at F1 vs F25
scene = bpy.context.scene
scene.frame_set(1)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
s_eval1 = sword.evaluated_get(dg)
loc1 = s_eval1.matrix_world.translation.copy()

scene.frame_set(25)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
s_eval25 = sword.evaluated_get(dg)
loc25 = s_eval25.matrix_world.translation.copy()

print(f"Sword at F1: {loc1}, at F25: {loc25}, diff: {(loc25-loc1).length:.4f}")
