import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

body_path = os.path.abspath(r"Import\Boss01\SK_Boss01_Body.fbx")
crown_path = os.path.abspath(r"Import\Boss01\SK_Boss01_Crown.fbx")

code = """
import bpy
s = bpy.data.scenes.new('MeasureCrown')
bpy.context.window.scene = s

bpy.ops.import_scene.fbx(filepath=r'""" + body_path + """')
body = [o for o in s.objects if o.type == 'MESH'][0]

bpy.ops.import_scene.fbx(filepath=r'""" + crown_path + """')
crown = [o for o in s.objects if o.type == 'MESH' and o != body][0]

b_verts = [body.matrix_world @ v.co for v in body.data.vertices]
head_verts = [v for v in b_verts if abs(v.x) <= 20.0 and abs(v.y) <= 20.0 and v.z > 150.0]

highest_head_z = max(v.z for v in head_verts) if head_verts else max(v.z for v in b_verts)
highest_body_z = max(v.z for v in b_verts)

c_verts = [crown.matrix_world @ v.co for v in crown.data.vertices]
lowest_crown_z = min(v.z for v in c_verts)
highest_crown_z = max(v.z for v in c_verts)

z_sorted = sorted(v.z for v in c_verts)
ring_sample = z_sorted[:20]
avg_ring_z = sum(ring_sample) / len(ring_sample)

print(f"Body highest overall Z: {highest_body_z:.2f} cm")
print(f"Body highest head Z: {highest_head_z:.2f} cm")
print(f"Crown lowest Z: {lowest_crown_z:.2f} cm")
print(f"Crown average base ring Z: {avg_ring_z:.2f} cm")
print(f"Crown highest spire Z: {highest_crown_z:.2f} cm")
diff = lowest_crown_z - highest_head_z
print(f"Difference (lowest crown - highest head): {diff:.2f} cm")

for o in list(s.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.data.scenes.remove(s)
"""

res = execute_blender(code)
print(res.get("stdout"))
if res.get("stderr"):
    print("ERR:", res.get("stderr"))
