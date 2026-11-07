import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)

# 1. Import animated armature
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\Player\Animations_FBX_Export\Attack_PrimaryA_Anim.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
arm.name = "root"

# 2. Import mesh from SKM_CombatMannequin_Simple
cur_objs = set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\ThirdParty\Reference\SKM_CombatMannequin_Simple.fbx")
new_objs = set(bpy.data.objects) - cur_objs

# Find LOD0 mesh
mesh = [o for o in new_objs if o.type == 'MESH' and 'LOD0' in o.name][0]

# Remove other imported objects from SKM
for o in new_objs:
    if o != mesh:
        bpy.data.objects.remove(o, do_unlink=True)

# Reparent mesh to the animated armature
mesh.parent = arm
for mod in mesh.modifiers:
    if mod.type == 'ARMATURE':
        mod.object = arm

# Check mesh vertex position at frame 1 vs frame 25
scene = bpy.context.scene
scene.frame_set(1)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
mesh_eval1 = mesh.evaluated_get(dg)
v1 = mesh_eval1.to_mesh().vertices[0].co.copy()

scene.frame_set(25)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
mesh_eval25 = mesh.evaluated_get(dg)
v25 = mesh_eval25.to_mesh().vertices[0].co.copy()

diff = (v25 - v1).length
print(f"Mesh vertex 0 at F1: {v1}, at F25: {v25}, diff: {diff:.4f}")
print(f"Is mesh deforming? {diff > 0.001}")
