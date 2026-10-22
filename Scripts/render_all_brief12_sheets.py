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
crown_path = os.path.abspath("Import/Boss01/SK_Boss01_Crown.fbx")
mantle_path = os.path.abspath("Import/Boss01/SK_Boss01_Mantle.fbx")
sword_path = os.path.abspath("Import/Boss01/Weapons/SM_Boss01_Greatsword.fbx")

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = 30
scene.render.fps_base = 1.0
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.01
scene.render.engine = 'BLENDER_EEVEE'

# 1. World setup
world = bpy.data.worlds.new("World_Studio")
scene.world = world
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs['Color'].default_value = (0.24, 0.25, 0.28, 1.0)
bg.inputs['Strength'].default_value = 0.9

# 2. Floor plane at Z = 0
mesh_floor = bpy.data.meshes.new("FloorLine")
o_floor = bpy.data.objects.new("FloorLine", mesh_floor)
scene.collection.objects.link(o_floor)
bm_f = bmesh.new()
bmesh.ops.create_grid(bm_f, x_segments=1, y_segments=1, size=6.0) # 6x6 meters
bm_f.to_mesh(mesh_floor)
bm_f.free()
o_floor.location = (0, 0, 0.0)

mat_fl = bpy.data.materials.new("M_Floor")
mat_fl.use_nodes = True
bsdf_fl = next(n for n in mat_fl.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf_fl.inputs['Base Color'].default_value = (0.13, 0.14, 0.16, 1.0)
bsdf_fl.inputs['Roughness'].default_value = 0.85
mesh_floor.materials.append(mat_fl)

# 3. 50 cm Height Ruler (in meters: height 2.0m, marks at 0.50, 1.00, 1.50, 2.00m)
mesh_ruler = bpy.data.meshes.new("HeightRuler")
o_ruler = bpy.data.objects.new("HeightRuler", mesh_ruler)
scene.collection.objects.link(o_ruler)
bm_r = bmesh.new()
bmesh.ops.create_cube(bm_r, size=1.0, matrix=Matrix.Translation(Vector((0.0, -0.65, 1.00))) @ Matrix.Diagonal(Vector((0.03, 0.03, 2.00, 1.0))))
for hz in [0.50, 1.00, 1.50, 2.00]:
    bmesh.ops.create_cube(bm_r, size=1.0, matrix=Matrix.Translation(Vector((0.0, -0.65, hz))) @ Matrix.Diagonal(Vector((0.14, 0.02, 0.02, 1.0))))
bm_r.to_mesh(mesh_ruler)
bm_r.free()

mat_rl = bpy.data.materials.new("M_Ruler")
mat_rl.use_nodes = True
bsdf_rl = next(n for n in mat_rl.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf_rl.inputs['Base Color'].default_value = (0.92, 0.78, 0.10, 1.0) # Yellow
mesh_ruler.materials.append(mat_rl)

# 4. Boss Character (Body, Crown, Mantle, Sword)
bpy.ops.import_scene.fbx(filepath=body_path)
arm_boss = next(o for o in scene.objects if o.type == 'ARMATURE')
body_boss = next(o for o in scene.objects if o.type == 'MESH')

bpy.ops.import_scene.fbx(filepath=crown_path)
crown = next(o for o in scene.objects if o.type == 'MESH' and "Crown" in o.name)

bpy.ops.import_scene.fbx(filepath=mantle_path)
mantle = next(o for o in scene.objects if o.type == 'MESH' and "Mantle" in o.name)

bpy.ops.import_scene.fbx(filepath=sword_path)
sword = next(o for o in scene.objects if o.type == 'MESH' and "Greatsword" in o.name)
sword.parent = arm_boss
sword.parent_type = 'BONE'
sword.parent_bone = "hand_r"
sword.location = Vector((0, 0, 0))
sword.rotation_euler = Euler((math.radians(90), 0, math.radians(-90)))

# Character materials
mat_body = bpy.data.materials.new("M_BossBody")
mat_body.use_nodes = True
bsdf_b = next(n for n in mat_body.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf_b.inputs['Base Color'].default_value = (0.70, 0.72, 0.75, 1.0) # Grey-white armour
bsdf_b.inputs['Roughness'].default_value = 0.3
body_boss.data.materials.clear()
body_boss.data.materials.append(mat_body)

# Studio Lights
def make_sun(name, rot_euler, energy, color):
    lamp_data = bpy.data.lights.new(name=name, type='SUN')
    lamp_data.energy = energy
    lamp_data.color = color
    lamp_data.use_shadow = False
    lamp_obj = bpy.data.objects.new(name=name, object_data=lamp_data)
    lamp_obj.rotation_euler = rot_euler
    scene.collection.objects.link(lamp_obj)
    return lamp_obj

make_sun("Key", (math.radians(50), math.radians(20), math.radians(45)), 5.2, (1.0, 0.98, 0.92))
make_sun("Fill", (math.radians(45), math.radians(-25), math.radians(-45)), 3.0, (0.85, 0.92, 1.0))
make_sun("Rim", (math.radians(-65), math.radians(35), math.radians(135)), 6.0, (1.0, 0.75, 0.35))

# Cameras (distances in meters!)
# 1. Side View: 3.4m away (+X looking to -X), height 0.95m
cam_side_data = bpy.data.cameras.new("Cam_Side")
cam_side_data.lens = 42.0
cam_side = bpy.data.objects.new("Cam_Side", cam_side_data)
cam_side.location = (3.40, 0.0, 0.95)
cam_side.rotation_euler = (math.radians(90), 0.0, math.radians(90))
scene.collection.objects.link(cam_side)

# 2. Front View: 3.4m away (-Y looking to +Y), height 0.95m
cam_front_data = bpy.data.cameras.new("Cam_Front")
cam_front_data.lens = 42.0
cam_front = bpy.data.objects.new("Cam_Front", cam_front_data)
cam_front.location = (0.0, -3.40, 0.95)
cam_front.rotation_euler = (math.radians(90), 0.0, 0.0)
scene.collection.objects.link(cam_front)

# 3. Player Riposte Side View: centered at Y = -0.45m (tracking lunge), 3.4m away
cam_player_data = bpy.data.cameras.new("Cam_Player")
cam_player_data.lens = 38.0
cam_player = bpy.data.objects.new("Cam_Player", cam_player_data)
cam_player.location = (3.40, -0.45, 0.95)
cam_player.rotation_euler = (math.radians(90), 0.0, math.radians(90))
scene.collection.objects.link(cam_player)

scene.render.resolution_x = 320
scene.render.resolution_y = 480
scene.render.film_transparent = False

def render_sheet_frames(fbx_name, frames, prefix, views=['side']):
    fbx_p = os.path.join(anim_dir, fbx_name)
    s_temp = bpy.data.scenes.new("TempImport")
    bpy.context.window.scene = s_temp
    bpy.ops.import_scene.fbx(filepath=fbx_p)
    a_temp = next(o for o in s_temp.objects if o.type == 'ARMATURE')
    anim_act = a_temp.animation_data.action
    f_offset = int(round(anim_act.frame_range[0]))
    
    bpy.context.window.scene = scene
    arm_boss.animation_data_create()
    arm_boss.animation_data.action = anim_act
    if anim_act.slots:
        arm_boss.animation_data.action_slot = anim_act.slots[0]
        
    out = {}
    for v in views:
        out[v] = []
        if v == 'side':
            scene.camera = cam_side
        elif v == 'front':
            scene.camera = cam_front
        elif v == 'player':
            scene.camera = cam_player
            
        for f in frames:
            f_eval = f_offset + f
            scene.frame_set(f_eval)
            bpy.context.view_layer.update()
            
            p_out = os.path.join(anim_dir, f"{prefix}_{v}_{f:02d}.png" if len(views) > 1 or v != 'side' else f"{prefix}_{f:02d}.png")
            scene.render.filepath = p_out
            bpy.ops.render.render(write_still=True)
            out[v].append(p_out)
            
    # Cleanup temp
    for o in list(s_temp.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.scenes.remove(s_temp)
    return out

# 1. PhaseRoar (2 views: side, front)
roar_frames = [0, 6, 15, 21, 39, 54]
render_sheet_frames("AN_Boss01_PhaseRoar.fbx", roar_frames, "temp_cs_roar", views=['side', 'front'])

# 2. StaggerFall (2 views: side, front)
fall_frames = [0, 4, 9, 15, 18, 21]
render_sheet_frames("AN_Boss01_StaggerFall.fbx", fall_frames, "temp_cs_fall", views=['side', 'front'])

# 3. Riposte_Player_Front (1 view: tracking side)
player_frames = [0, 6, 14, 21, 24, 48]
render_sheet_frames("AN_Riposte_Player_Front.fbx", player_frames, "temp_cs_riposte_player", views=['player'])

# 4. Riposte_Boss_Reaction (1 view: side)
boss_react_frames = [0, 12, 20, 24, 39, 60]
render_sheet_frames("AN_Riposte_Boss_Reaction.fbx", boss_react_frames, "temp_cs_riposte_boss", views=['side'])

# 5. DeathLegend (1 view: side)
death_frames = [0, 15, 24, 40, 75, 105]
render_sheet_frames("AN_Boss01_DeathLegend.fbx", death_frames, "temp_cs_death", views=['side'])

result = {"status": "frames rendered with meter coordinates"}
"""

res = execute_blender(code)
print(res)
