import bpy
from math import radians

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# Import animated armature
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\Player\Animations_FBX_Export\Attack_PrimaryA_Anim.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
arm.name = "root"

# Import mannequin mesh
cur_objs = set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\ThirdParty\Reference\SKM_CombatMannequin_Simple.fbx")
new_objs = set(bpy.data.objects) - cur_objs
mesh = [o for o in new_objs if o.type == 'MESH' and 'LOD0' in o.name][0]
for o in new_objs:
    if o != mesh:
        bpy.data.objects.remove(o, do_unlink=True)

mesh.parent = arm
for mod in mesh.modifiers:
    if mod.type == 'ARMATURE':
        mod.object = arm

# Import sword
cur_objs = set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=r"c:\UnrealProject\OneBossFight\Import\ThirdParty\Reference\SM_KwangSword.fbx")
sword = [o for o in set(bpy.data.objects) - cur_objs if o.type == 'MESH'][0]
sword.parent = arm
sword.parent_type = 'BONE'
sword.parent_bone = "hand_r"
# In cm space, sword scale is 1.0 (since it was exported from UE in cm)
sword.scale = (1.0, 1.0, 1.0)
sword.location = (0.0, 5.0, 0.0)
sword.rotation_euler = (0, radians(90), 0)

# Studio world & lights (in cm space: lights placed at 500-1000 cm)
world = bpy.data.worlds.new("StudioWorld")
scene.world = world
world.color = (0.28, 0.28, 0.30)

def add_sun(name, loc, rot, energy, color):
    ld = bpy.data.lights.new(name=name, type='SUN')
    ld.energy = energy
    ld.color = color
    lo = bpy.data.objects.new(name=name, object_data=ld)
    scene.collection.objects.link(lo)
    lo.location = loc
    lo.rotation_euler = rot

add_sun("KeySun", (500.0, -500.0, 1000.0), (radians(45), radians(15), radians(-45)), 3.0, (1.0, 0.98, 0.95))
add_sun("FillSun", (-600.0, -400.0, 600.0), (radians(60), radians(-20), radians(120)), 1.2, (0.75, 0.85, 1.0))
add_sun("RimSun", (0.0, 700.0, 600.0), (radians(-45), 0, radians(180)), 2.5, (1.0, 1.0, 1.0))

cam_data = bpy.data.cameras.new("ReviewCam")
cam_data.lens = 45.0
cam = bpy.data.objects.new("ReviewCam", object_data=cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

# Side view in cm space: camera at X=350 cm, Z=90 cm, looking along -X
cam.location = (350.0, 0.0, 95.0)
cam.rotation_euler = (radians(90), 0, radians(90))

# Frame 25 (peak impact)
scene.frame_set(25)
test_png = r"c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\ER_ANIM\test_cm_render.png"
scene.render.filepath = test_png
bpy.ops.render.render(write_still=True)
print(f"Rendered test frame: {test_png}")
