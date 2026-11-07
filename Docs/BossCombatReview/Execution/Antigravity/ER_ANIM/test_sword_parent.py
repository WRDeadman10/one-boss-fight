import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\Player\Animations_FBX_Export\Attack_PrimaryA_Anim.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]

# Import sword
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\ThirdParty\Reference\SM_KwangSword.fbx")
sword = [o for o in bpy.data.objects if o.type == 'MESH' and o != arm][0]
print(f"Sword object: {sword.name}, dims: {sword.dimensions}")

# Parent sword to hand_r bone
sword.parent = arm
sword.parent_type = 'BONE'
sword.parent_bone = "hand_r"
print("Successfully parented sword to hand_r!")
