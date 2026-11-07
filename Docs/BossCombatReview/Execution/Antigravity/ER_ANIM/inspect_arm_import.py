import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\Player\Animations_FBX_Export\Attack_PrimaryA_Anim.fbx")
arm1 = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
print("Arm1:", arm1.name, "Action:", arm1.animation_data.action.name if arm1.animation_data else None)

bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\ThirdParty\Reference\SKM_CombatMannequin_Simple.fbx")
arms = [o for o in bpy.data.objects if o.type == 'ARMATURE']
print("Arms after second import:", [a.name for a in arms])
for a in arms:
    act = a.animation_data.action if a.animation_data else None
    print(f"  {a.name}: action={act.name if act else 'None'}")
