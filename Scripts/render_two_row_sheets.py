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

# Import body and modular pieces
bpy.ops.import_scene.fbx(filepath=body_path)
arm = next(o for o in scene.objects if o.type == 'ARMATURE')
body = next(o for o in scene.objects if o.type == 'MESH')

bpy.ops.import_scene.fbx(filepath=crown_path)
crown = next(o for o in scene.objects if o.type == 'MESH' and "Crown" in o.name)

bpy.ops.import_scene.fbx(filepath=mantle_path)
mantle = next(o for o in scene.objects if o.type == 'MESH' and "Mantle" in o.name)

bpy.ops.import_scene.fbx(filepath=sword_path)
sword = next(o for o in scene.objects if o.type == 'MESH' and "Greatsword" in o.name)

# Ensure sword is attached to right hand
hand_bone = arm.pose.bones.get("hand_r")
if hand_bone:
    sword.parent = arm
    sword.parent_type = 'BONE'
    sword.parent_bone = "hand_r"
    sword.location = Vector((0, 0, 0))
    sword.rotation_euler = Euler((math.radians(90), 0, math.radians(-90)))

# Floor line at Z = 0
mesh_floor = bpy.data.meshes.new("FloorLine")
o_floor = bpy.data.objects.new("FloorLine", mesh_floor)
scene.collection.objects.link(o_floor)
bm_f = bmesh.new()
bmesh.ops.create_grid(bm_f, x_segments=1, y_segments=1, size=250.0)
bm_f.to_mesh(mesh_floor)
bm_f.free()
o_floor.location = (0, 0, 0.0)

mat_fl = bpy.data.materials.new("M_Floor")
mat_fl.use_nodes = True
bsdf_fl = next(n for n in mat_fl.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf_fl.inputs['Base Color'].default_value = (0.15, 0.16, 0.18, 1.0)
mesh_floor.materials.append(mat_fl)

# 50 cm Height Ruler
mesh_ruler = bpy.data.meshes.new("HeightRuler")
o_ruler = bpy.data.objects.new("HeightRuler", mesh_ruler)
scene.collection.objects.link(o_ruler)
bm_r = bmesh.new()
bmesh.ops.create_cube(bm_r, size=1.0, matrix=Matrix.Translation(Vector((0.0, -65.0, 100.0))) @ Matrix.Diagonal(Vector((3.0, 3.0, 200.0, 1.0))))
for hz in [50.0, 100.0, 150.0, 200.0]:
    bmesh.ops.create_cube(bm_r, size=1.0, matrix=Matrix.Translation(Vector((0.0, -65.0, hz))) @ Matrix.Diagonal(Vector((12.0, 2.0, 2.0, 1.0))))
bm_r.to_mesh(mesh_ruler)
bm_r.free()

mat_rl = bpy.data.materials.new("M_Ruler")
mat_rl.use_nodes = True
bsdf_rl = next(n for n in mat_rl.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf_rl.inputs['Base Color'].default_value = (0.85, 0.70, 0.10, 1.0)
mesh_ruler.materials.append(mat_rl)

# Lights
def make_sun(name, rot_euler, energy, color):
    lamp_data = bpy.data.lights.new(name=name, type='SUN')
    lamp_data.energy = energy
    lamp_data.color = color
    lamp_obj = bpy.data.objects.new(name=name, object_data=lamp_data)
    lamp_obj.rotation_euler = rot_euler
    scene.collection.objects.link(lamp_obj)
    return lamp_obj

make_sun("CS_Key", (math.radians(50), math.radians(20), math.radians(45)), 4.5, (1.0, 0.98, 0.92))
make_sun("CS_Fill", (math.radians(45), math.radians(-25), math.radians(-45)), 3.0, (0.85, 0.92, 1.0))
make_sun("CS_Rim", (math.radians(-65), math.radians(35), math.radians(135)), 5.5, (1.0, 0.75, 0.35))

# Side View Camera (profile view looking from +X to -X)
cam_side_data = bpy.data.cameras.new("Cam_SideView")
cam_side_data.lens = 42.0
cam_side = bpy.data.objects.new("Cam_SideView", cam_side_data)
cam_side.location = (340.0, 0.0, 95.0)
cam_side.rotation_euler = (math.radians(90), 0.0, math.radians(90))
scene.collection.objects.link(cam_side)

# Front View Camera (front view looking from -Y to +Y)
cam_front_data = bpy.data.cameras.new("Cam_FrontView")
cam_front_data.lens = 42.0
cam_front = bpy.data.objects.new("Cam_FrontView", cam_front_data)
cam_front.location = (0.0, -340.0, 95.0)
cam_front.rotation_euler = (math.radians(90), 0.0, 0.0)
scene.collection.objects.link(cam_front)

scene.render.resolution_x = 320
scene.render.resolution_y = 480
scene.render.film_transparent = False

def render_clip_2views(fbx_name, frames, prefix):
    fbx_p = f"{anim_dir}/{fbx_name}"
    s_temp = bpy.data.scenes.new("TempAnim")
    bpy.context.window.scene = s_temp
    bpy.ops.import_scene.fbx(filepath=fbx_p)
    a_temp = next(o for o in s_temp.objects if o.type == 'ARMATURE')
    anim_act = a_temp.animation_data.action
    
    bpy.context.window.scene = scene
    arm.animation_data_create()
    arm.animation_data.action = anim_act
    
    out_side = []
    out_front = []
    for f in frames:
        scene.frame_set(f)
        bpy.context.view_layer.update()
        
        # 1. Side view
        scene.camera = cam_side
        path_side = f"{anim_dir}/{prefix}_side_{f:02d}.png"
        scene.render.filepath = path_side
        bpy.ops.render.render(write_still=True)
        out_side.append(path_side)
        
        # 2. Front view
        scene.camera = cam_front
        path_front = f"{anim_dir}/{prefix}_front_{f:02d}.png"
        scene.render.filepath = path_front
        bpy.ops.render.render(write_still=True)
        out_front.append(path_front)
        
    for o in list(s_temp.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.scenes.remove(s_temp)
    return {"side": out_side, "front": out_front}

roar_res = render_clip_2views("AN_Boss01_PhaseRoar.fbx", [0, 6, 15, 21, 39, 54], "temp_cs_roar")
fall_res = render_clip_2views("AN_Boss01_StaggerFall.fbx", [0, 4, 9, 15, 18, 21], "temp_cs_fall")

result = {
    "roar": roar_res,
    "fall": fall_res
}
"""

res = execute_blender(code)
print("Render 2-view frames result:", res)
