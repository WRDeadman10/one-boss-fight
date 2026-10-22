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

# World
world = bpy.data.worlds.new("World_TopDown")
scene.world = world
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs['Color'].default_value = (0.28, 0.29, 0.32, 1.0)
bg.inputs['Strength'].default_value = 1.0

# 1. Floor with 50 cm Grid lines (in meters: 0.50m spacing!)
mesh_floor = bpy.data.meshes.new("FloorDark")
o_floor = bpy.data.objects.new("FloorDark", mesh_floor)
scene.collection.objects.link(o_floor)
bm_f = bmesh.new()
bmesh.ops.create_grid(bm_f, x_segments=1, y_segments=1, size=5.0) # 5x5 meters
bm_f.to_mesh(mesh_floor)
bm_f.free()
o_floor.location = (0.0, -0.75, 0.0)

mat_fl = bpy.data.materials.new("M_FloorDark")
mat_fl.use_nodes = True
bsdf_fl = next(n for n in mat_fl.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf_fl.inputs['Base Color'].default_value = (0.22, 0.23, 0.26, 1.0)
mesh_floor.materials.append(mat_fl)

# 50 cm Grid marker bars on the floor (Y = 0.0, -0.50, -1.00, -1.50, -2.00 meters)
mesh_grid = bpy.data.meshes.new("GridMarks")
o_grid = bpy.data.objects.new("GridMarks", mesh_grid)
scene.collection.objects.link(o_grid)
bm_g = bmesh.new()
# Horizontal grid lines every 50 cm across Y
for y_m in [0.0, -0.50, -1.00, -1.50, -2.00]:
    bmesh.ops.create_cube(bm_g, size=1.0, matrix=Matrix.Translation(Vector((0.0, y_m, 0.003))) @ Matrix.Diagonal(Vector((1.80, 0.02, 0.004, 1.0))))
# Vertical guide lines at X = -0.50, 0.0, +0.50
for x_m in [-0.50, 0.0, 0.50]:
    bmesh.ops.create_cube(bm_g, size=1.0, matrix=Matrix.Translation(Vector((x_m, -1.00, 0.003))) @ Matrix.Diagonal(Vector((0.02, 2.40, 0.004, 1.0))))
bm_g.to_mesh(mesh_grid)
bm_g.free()

mat_gm = bpy.data.materials.new("M_GridYellow")
mat_gm.use_nodes = True
bsdf_gm = next(n for n in mat_gm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf_gm.inputs['Base Color'].default_value = (0.85, 0.78, 0.20, 1.0) # Yellow-gold grid lines
mesh_grid.materials.append(mat_gm)

# 2. Boss at origin (0, 0, 0)
bpy.ops.import_scene.fbx(filepath=body_path)
arm_boss = next(o for o in scene.objects if o.type == 'ARMATURE')
arm_boss.name = "Arm_Boss"
body_boss = next(o for o in scene.objects if o.type == 'MESH' and o not in [o_floor, o_grid])
body_boss.name = "Mesh_Boss"

# Boss sword
bpy.ops.import_scene.fbx(filepath=sword_path)
sword_boss = next(o for o in scene.objects if o.type == 'MESH' and "Greatsword" in o.name)
sword_boss.name = "Sword_Boss"
sword_boss.parent = arm_boss
sword_boss.parent_type = 'BONE'
sword_boss.parent_bone = "hand_r"
sword_boss.location = Vector((0, 0, 0))
sword_boss.rotation_euler = Euler((math.radians(90), 0, math.radians(-90)))

# Boss material: Grey
mat_boss = bpy.data.materials.new("M_Boss_Grey")
mat_boss.use_nodes = True
bsdf_b = next(n for n in mat_boss.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf_b.inputs['Base Color'].default_value = (0.65, 0.67, 0.70, 1.0) # Light grey
body_boss.data.materials.clear()
body_boss.data.materials.append(mat_boss)

# 3. Player Character at initial 150 cm standoff
bpy.ops.import_scene.fbx(filepath=body_path)
arm_player = next(o for o in scene.objects if o.type == 'ARMATURE' and o != arm_boss)
arm_player.name = "Arm_Player"
body_player = next(o for o in scene.objects if o.type == 'MESH' and o not in [body_boss, sword_boss, o_floor, o_grid])
body_player.name = "Mesh_Player"

# Player material: Blue
mat_player = bpy.data.materials.new("M_Player_Blue")
mat_player.use_nodes = True
bsdf_p = next(n for n in mat_player.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf_p.inputs['Base Color'].default_value = (0.12, 0.45, 0.98, 1.0) # Vivid Electric Blue
body_player.data.materials.clear()
body_player.data.materials.append(mat_player)

# 4. Load Animations
# Boss Reaction
s_b = bpy.data.scenes.new("Scene_LoadBoss")
bpy.context.window.scene = s_b
bpy.ops.import_scene.fbx(filepath=boss_clip)
a_b = next(o for o in s_b.objects if o.type == 'ARMATURE')
act_boss = a_b.animation_data.action

# Player Riposte
s_p = bpy.data.scenes.new("Scene_LoadPlayer")
bpy.context.window.scene = s_p
bpy.ops.import_scene.fbx(filepath=player_clip)
a_p = next(o for o in s_p.objects if o.type == 'ARMATURE')
act_player = a_p.animation_data.action

# Return to main scene
bpy.context.window.scene = scene

arm_boss.animation_data_create()
arm_boss.animation_data.action = act_boss
if act_boss.slots:
    arm_boss.animation_data.action_slot = act_boss.slots[0]

arm_player.animation_data_create()
arm_player.animation_data.action = act_player
if act_player.slots:
    arm_player.animation_data.action_slot = act_player.slots[0]

# Player placement:
# Standoff: Player starts 150 cm in front of boss along UE +Y (Blender -Y: -1.50 m).
# Player faces boss along UE -Y (Blender +Y: 180 deg yaw!).
player_root_pivot = bpy.data.objects.new("Player_Pivot", None)
scene.collection.objects.link(player_root_pivot)
player_root_pivot.location = Vector((0.0, -1.50, 0.0)) # 1.50m standoff in front of boss
player_root_pivot.rotation_euler = Euler((0.0, 0.0, math.radians(180))) # facing boss!
arm_player.parent = player_root_pivot

# Overhead Sunlight
lamp_data = bpy.data.lights.new(name="Sun_Top", type='SUN')
lamp_data.energy = 6.8
lamp_data.color = (1.0, 0.98, 0.95)
lamp_data.use_shadow = False
lamp_obj = bpy.data.objects.new(name="Sun_Top", object_data=lamp_data)
lamp_obj.rotation_euler = (math.radians(15), math.radians(20), math.radians(-30))
scene.collection.objects.link(lamp_obj)

# Top-Down Camera: Looking straight down (-Z)
# Centered at (0.0, -0.75m, 3.20m), looking straight down
cam_data = bpy.data.cameras.new("Cam_TopDown")
cam_data.lens = 38.0
cam = bpy.data.objects.new("Cam_TopDown", cam_data)
cam.location = (0.0, -0.75, 3.20)
cam.rotation_euler = (0.0, 0.0, math.radians(90))
scene.collection.objects.link(cam)
scene.camera = cam

scene.render.resolution_x = 480
scene.render.resolution_y = 360
scene.render.film_transparent = False

panels = [
    (0, "F00_Start"),
    (24, "F24_Impact"),
    (48, "F_End")
]

f_offset_b = int(round(act_boss.frame_range[0]))
f_offset_p = int(round(act_player.frame_range[0]))

out_frames = []
for f, name in panels:
    # Set boss frame
    scene.frame_set(f_offset_b + f)
    # Set player frame
    scene.frame_set(f_offset_p + f)
    bpy.context.view_layer.update()
    
    out_p = os.path.join(anim_dir, f"temp_topdown_{name}.png")
    scene.render.filepath = out_p
    bpy.ops.render.render(write_still=True)
    out_frames.append(out_p)

# Clean temp scenes
for o in list(s_b.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.data.scenes.remove(s_b)

for o in list(s_p.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.data.scenes.remove(s_p)

result = {"rendered": out_frames}
"""

res = execute_blender(code)
print(res)
