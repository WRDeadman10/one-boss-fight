import bpy
import sys
from pathlib import Path

# Clear existing objects in scene
bpy.ops.wm.read_factory_settings(use_empty=True)

fbx_path = Path("Import/ThirdParty/Reference/REF_Sevarog_Sevarog.fbx").resolve()
print(f"Loading FBX: {fbx_path}")
assert fbx_path.is_file(), f"FBX file not found: {fbx_path}"

# Import FBX
bpy.ops.import_scene.fbx(filepath=str(fbx_path))

armatures = [o for o in bpy.data.objects if o.type == 'ARMATURE']
meshes = [o for o in bpy.data.objects if o.type == 'MESH']

print(f"\nArmatures count: {len(armatures)}")
for a in armatures:
    print(f"  Armature: {a.name}, Bones count: {len(a.data.bones)}")
    bone_names = [b.name for b in a.data.bones]
    print(f"  Sample bones: {bone_names[:10]}")
    has_weapon_r = "weapon_r" in bone_names
    has_tip = "root_weapon_end_r" in bone_names
    has_root = "root" in bone_names
    print(f"  Bones check: root={has_root}, weapon_r={has_weapon_r}, root_weapon_end_r={has_tip}")

print(f"\nMeshes count: {len(meshes)}")
for m in meshes:
    print(f"  Mesh: {m.name}, Verts: {len(m.data.vertices)}, Polygons: {len(m.data.polygons)}")

print("\nBLENDER FBX IMPORT SUCCESSFUL")
