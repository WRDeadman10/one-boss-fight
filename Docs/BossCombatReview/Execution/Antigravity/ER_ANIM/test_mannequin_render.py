import bpy
from math import radians

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# 1. Import SKM_CombatMannequin_Simple (has mesh + armature)
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\ThirdParty\Reference\SKM_CombatMannequin_Simple.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]
print(f"Loaded armature: {arm.name}, mesh: {mesh.name}")

# Remove LOD1, LOD2, etc., keep LOD0
for o in list(bpy.data.objects):
    if o.type == 'MESH' and o.name != 'SKM_CombatMannequin_Simple_LOD0':
        bpy.data.objects.remove(o, do_unlink=True)

# 2. Import sword
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\ThirdParty\Reference\SM_KwangSword.fbx")
sword = [o for o in bpy.data.objects if o.type == 'MESH' and o.name != 'SKM_CombatMannequin_Simple_LOD0'][0]
sword.parent = arm
sword.parent_type = 'BONE'
sword.parent_bone = "hand_r"
sword.location = (0.0, 0.05, 0.0)
sword.rotation_euler = (0, radians(90), 0)

# Set studio lighting & camera
world = bpy.data.worlds.new("StudioWorld")
scene.world = world
world.color = (0.28, 0.28, 0.30)

def add_sun(name, loc, rot, energy, color):
    light_data = bpy.data.lights.new(name=name, type='SUN')
    light_data.energy = energy
    light_data.color = color
    light_obj = bpy.data.objects.new(name=name, object_data=light_data)
    scene.collection.objects.link(light_obj)
    light_obj.location = loc
    light_obj.rotation_euler = rot

add_sun("KeySun", (5.0, -5.0, 10.0), (radians(45), radians(15), radians(-45)), 3.0, (1.0, 0.98, 0.95))
add_sun("FillSun", (-6.0, -4.0, 6.0), (radians(60), radians(-20), radians(120)), 1.2, (0.75, 0.85, 1.0))
add_sun("RimSun", (0.0, 7.0, 6.0), (radians(-45), 0, radians(180)), 2.5, (1.0, 1.0, 1.0))

cam_data = bpy.data.cameras.new("ReviewCam")
cam_data.lens = 45.0
cam = bpy.data.objects.new("ReviewCam", object_data=cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

cam.location = (4.8, 0.0, 0.90)
cam.rotation_euler = (radians(90), 0, radians(90))

test_png = r"c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\ER_ANIM\test_render_mannequin.png"
scene.render.filepath = test_png
bpy.ops.render.render(write_still=True)
print(f"Rendered test frame: {test_png}")
