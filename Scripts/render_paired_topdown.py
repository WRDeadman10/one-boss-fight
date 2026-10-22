import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blender_exec import execute_blender

code = r"""
import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler, Matrix

anim_dir = os.path.abspath("Import/Boss01/Animations")
body_path = os.path.abspath("Import/Boss01/SK_Boss01_Body.fbx")
sword_path = os.path.abspath("Import/Boss01/Weapons/SM_Boss01_Greatsword.fbx")
player_clip = os.path.join(anim_dir, "AN_Riposte_Player_Front.fbx")
boss_clip = os.path.join(anim_dir, "AN_Riposte_Boss_Reaction.fbx")

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

scene.render.fps = 30
scene.render.fps_base = 1.0
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.01
scene.render.engine = 'BLENDER_EEVEE'

# 1. Import Boss Character (Armature + Body)
bpy.ops.import_scene.fbx(filepath=body_path)
arm_boss = next(o for o in scene.objects if o.type == 'ARMATURE')
arm_boss.name = "Arm_Boss"
body_boss = next(o for o in scene.objects if o.type == 'MESH')
body_boss.name = "Mesh_Boss"

# Import Greatsword for boss
bpy.ops.import_scene.fbx(filepath=sword_path)
sword_boss = next(o for o in scene.objects if o.type == 'MESH' and "Greatsword" in o.name)
sword_boss.name = "Mesh_Boss_Sword"
sword_boss.parent = arm_boss
sword_boss.parent_type = 'BONE'
sword_boss.parent_bone = "hand_r"
sword_boss.location = Vector((0, 0, 0))
sword_boss.rotation_euler = Euler((math.radians(90), 0, math.radians(-90)))

# 2. Import Player Character (copy of body mesh or second mannequin)
bpy.ops.import_scene.fbx(filepath=body_path)
arm_player = next(o for o in scene.objects if o.type == 'ARMATURE' and o != arm_boss)
arm_player.name = "Arm_Player"
body_player = next(o for o in scene.objects if o.type == 'MESH' and o not in [body_boss, sword_boss])
body_player.name = "Mesh_Player"

# Player material (blue tint to clearly differentiate from boss)
mat_player = bpy.data.materials.new("M_Player_Tint")
mat_player.use_nodes = True
bsdf_p = next(n for n in mat_player.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf_p.inputs['Base Color'].default_value = (0.2, 0.45, 0.85, 1.0)
body_player.data.materials.clear()
body_player.data.materials.append(mat_player)

# 3. Load animations
# Load Boss clip
s_b = bpy.data.scenes.new("Scene_LoadBoss")
bpy.context.window.scene = s_b
bpy.ops.import_scene.fbx(filepath=boss_clip)
a_b = next(o for o in s_b.objects if o.type == 'ARMATURE')
act_boss = a_b.animation_data.action

# Load Player clip
s_p = bpy.data.scenes.new("Scene_LoadPlayer")
bpy.context.window.scene = s_p
bpy.ops.import_scene.fbx(filepath=player_clip)
a_p = next(o for o in s_p.objects if o.type == 'ARMATURE')
act_player = a_p.animation_data.action

# Back to main scene
bpy.context.window.scene = scene
arm_boss.animation_data_create()
arm_boss.animation_data.action = act_boss

arm_player.animation_data_create()
arm_player.animation_data.action = act_player

# Floor Grid
mesh_floor = bpy.data.meshes.new("FloorGrid")
o_floor = bpy.data.objects.new("FloorGrid", mesh_floor)
scene.collection.objects.link(o_floor)
bm_f = bmesh.new()
bmesh.ops.create_grid(bm_f, x_segments=10, y_segments=6, size=300.0)
bm_f.to_mesh(mesh_floor)
bm_f.free()
o_floor.location = (75.0, 0.0, 0.0)

mat_fl = bpy.data.materials.new("M_FloorGrid")
mat_fl.use_nodes = True
bsdf_fl = next(n for n in mat_fl.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf_fl.inputs['Base Color'].default_value = (0.16, 0.17, 0.20, 1.0)
bsdf_fl.inputs['Roughness'].default_value = 0.8
mesh_floor.materials.append(mat_fl)

# Overhead Studio Light
lamp_data = bpy.data.lights.new(name="Sun_Top", type='SUN')
lamp_data.energy = 5.0
lamp_data.color = (1.0, 0.98, 0.95)
lamp_obj = bpy.data.objects.new(name="Sun_Top", object_data=lamp_data)
lamp_obj.rotation_euler = (math.radians(15), math.radians(20), math.radians(-30))
scene.collection.objects.link(lamp_obj)

# Top-Down Camera
cam_data = bpy.data.cameras.new("Cam_TopDown")
cam_data.lens = 38.0
cam = bpy.data.objects.new("Cam_TopDown", cam_data)
# Centered between X=0 (Boss) and X=150 (Player)
cam.location = (75.0, 0.0, 320.0)
# Looking straight down (-Z), with +X pointing right and +Y pointing up
cam.rotation_euler = (0.0, 0.0, math.radians(-90))
scene.collection.objects.link(cam)
scene.camera = cam

scene.render.resolution_x = 480
scene.render.resolution_y = 360
scene.render.film_transparent = False

# Render 3 panels:
# Panel 1: F0 (0.00 s)
# Panel 2: F24 (0.80 s - Impact)
# Panel 3: Last Frame (Player F48, Boss F60)
panels = [
    (0, "F00_Start"),
    (24, "F24_Impact"),
    (48, "F_End")
]

out_frames = []
for f, name in panels:
    scene.frame_set(f)
    bpy.context.view_layer.update()
    out_p = os.path.join(anim_dir, f"temp_topdown_{name}.png")
    scene.render.filepath = out_p
    bpy.ops.render.render(write_still=True)
    out_frames.append(out_p)

# Clean up load scenes
for o in list(s_b.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.data.scenes.remove(s_b)

for o in list(s_p.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.data.scenes.remove(s_p)

result = {
    "rendered": out_frames
}
"""

res = execute_blender(code)
print("Render topdown result:", res)
