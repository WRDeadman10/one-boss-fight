"""
Dresses L_SevarogArena with the Megascans ruin kits copied from the Dark Ruins sample: a double ring of ruin walls around the existing arena wall,
the entrance gate, colossal background columns, columns and lanterns inside, rubble, props, floor slabs, decals, fires with flickering lights, and
the floor material. Everything lands in the outliner folder "Dressing" and is removed and rebuilt on every run, so the script can be rerun after tuning.
The greybox arena actor keeps its collision (the player and boss never touch the dressing, except the few solid props flagged below).
Run with Scripts/run_in_editor.py with L_SevarogArena open. Log prefix [Dress].
"""
import math
import random
import re
import unreal

log = lambda m: unreal.log("[Dress] " + m)
FOLDER = "Dressing"
R_ARENA = 3000.0
RNG = random.Random(11)

ar = unreal.AssetRegistryHelpers.get_asset_registry()
CATALOG = {}
for root in ("/Game/MS/3D", "/Game/MS/Decals", "/Game/CustomAssets", "/Game/Materials", "/Game/MS/Surfaces"):
    for ad in ar.get_assets_by_path(root, recursive=True):
        CATALOG[str(ad.asset_name)] = str(ad.package_name)
actors_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def find(pattern):
    """All asset names matching the regex, sorted."""
    rx = re.compile(pattern)
    return sorted(n for n in CATALOG if rx.search(n))


def load(name):
    return unreal.EditorAssetLibrary.load_asset(CATALOG[name])


def meshes(pattern):
    names = find(pattern)
    assert names, "no asset matches " + pattern
    return [load(n) for n in names]


def mesh1(pattern):
    return meshes(pattern)[0]


def rebuild(actor):
    """Run the actor's construction script (OnConstruction) after property changes (C++ Rebuild, Python cannot do it itself)."""
    actor.rebuild()


def place(mesh, x, y, yaw=0.0, z=0.0, pitch=0.0, roll=0.0, scale=1.0):
    """Transform that puts the bottom centre of the mesh bounds at (x, y, z); mesh pivots in this pack are arbitrary."""
    b = mesh.get_bounds()
    o, e = b.origin, b.box_extent
    rot = unreal.Rotator(roll=roll, pitch=pitch, yaw=yaw)
    off = unreal.MathLibrary.greater_greater_vector_rotator(unreal.Vector(o.x * scale, o.y * scale, (o.z - e.z) * scale), rot)
    return unreal.Transform(unreal.Vector(x - off.x, y - off.y, z - off.z), rot, unreal.Vector(scale, scale, scale))


def width(mesh):
    return mesh.get_bounds().box_extent.x * 2.0


SETS = {}  # mesh path -> {"mesh", "instances", "collision", "shadow"}


def add(mesh, tf, collision=False, shadow=True, material=None, sway=0.0, pivot=None):
    key = mesh.get_path_name()
    s = SETS.setdefault(key, {"mesh": mesh, "instances": [], "collision": collision, "shadow": shadow, "material": material, "sway": sway, "pivot": pivot})
    s["instances"].append(tf)


def polar(r, deg):
    a = math.radians(deg)
    return r * math.cos(a), r * math.sin(a)


# ---------------------------------------------------------------- clear the previous run
removed = 0
for a in actors_sub.get_all_level_actors():
    if str(a.get_folder_path()).startswith(FOLDER) or str(a.get_folder_path()) in ("FxTest", "MeshTest"):
        unreal.EditorLevelLibrary.destroy_actor(a)
        removed += 1
log("removed %d actors from the previous run" % removed)

arena = next(a for a in actors_sub.get_all_level_actors() if a.get_class().get_name() == "RPGGreyboxArena")

# ---------------------------------------------------------------- floor material (one tile every ~2 m instead of one tile across the whole disc)
mat_path = "/Game/OneBossFight/Environment/Materials/MI_Arena_RomanFloor"
if not unreal.EditorAssetLibrary.does_asset_exist(mat_path):
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    mi = tools.create_asset("MI_Arena_RomanFloor", "/Game/OneBossFight/Environment/Materials", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
else:
    mi = unreal.EditorAssetLibrary.load_asset(mat_path)
mi.set_editor_property("parent", load("MI_Roman_Stone_Floor_thsjdfxq_1"))
ml = unreal.MaterialEditingLibrary
ml.set_material_instance_scalar_parameter_value(mi, "UVs - Base  Scale", 26.0)
ml.set_material_instance_vector_parameter_value(mi, "Base - Albedo Tint", unreal.LinearColor(0.62, 0.64, 0.66, 1.0))
unreal.EditorAssetLibrary.save_loaded_asset(mi)
arena.set_editor_property("floor_material", mi)

# slabs get the floor stone at one tile per slab (their own kit material turns mirror-like under the moon)
slab_path = "/Game/OneBossFight/Environment/Materials/MI_Arena_Slab"
if not unreal.EditorAssetLibrary.does_asset_exist(slab_path):
    slab_mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset("MI_Arena_Slab", "/Game/OneBossFight/Environment/Materials", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
else:
    slab_mat = unreal.EditorAssetLibrary.load_asset(slab_path)
slab_mat.set_editor_property("parent", mi)
ml.set_material_instance_scalar_parameter_value(slab_mat, "UVs - Base  Scale", 1.0)
ml.set_material_instance_vector_parameter_value(slab_mat, "Base - Albedo Tint", unreal.LinearColor(0.30, 0.30, 0.32, 1.0))
ml.update_material_instance(slab_mat)
unreal.EditorAssetLibrary.save_loaded_asset(slab_mat)

# ---------------------------------------------------------------- wall ring, front layer (inner face meets the old wall) and tall back layer
GAP_DEG, GAP_HALF = 180.0, 17.0  # the gate
front = meshes(r"^SM_Modular_Brick_Ruins_Kit_xjotbhkiy_0[023]|^SM_Modular_Brick_Ruins_Base_Enterance_Kit|^SM_Modular_Brick_Ruins_Base_Kit_M|^SM_Modular_Brick_Ruins_Window_Kit")
tall = meshes(r"^SM_Ruins_Wall_vdcjbgo|^SM_Modular_Brick_Ruins_Window_Kit_xjotbgviy_02")
broken = meshes(r"^SM_Modular_Broken_Brick_Walls_Kit")
r_front = R_ARENA + 95.0
deg = 0.0
count = 0
while deg < 360.0:
    m = RNG.choice(front)
    w = width(m) * 0.97
    step = math.degrees(w / r_front)
    mid = deg + step / 2.0
    if abs(((mid - GAP_DEG) + 180.0) % 360.0 - 180.0) < GAP_HALF:
        deg += step
        continue
    x, y = polar(r_front + RNG.uniform(-12, 12), mid)
    add(m, place(m, x, y, mid + 90.0 + (180.0 if RNG.random() < 0.0 else 0.0), z=RNG.uniform(-6, 0)), collision=False)
    count += 1
    deg += step
log("front wall ring: %d pieces" % count)

r_back = R_ARENA + 330.0
deg = 8.0
count = 0
while deg < 360.0:
    m = RNG.choice(tall)
    w = width(m) * 0.95
    step = math.degrees(w / r_back)
    mid = deg + step / 2.0
    deg += step * (1.0 if RNG.random() < 0.55 else 1.9)  # leave gaps: the sky and distance show through
    if abs(((mid - GAP_DEG) + 180.0) % 360.0 - 180.0) < GAP_HALF + 4.0:
        continue
    x, y = polar(r_back, mid)
    add(m, place(m, x, y, mid + 90.0, z=RNG.uniform(-10, 0)))
    count += 1
log("back wall ring: %d pieces" % count)

# broken wall stubs standing inside the arena edge: clutter and cover without blocking the fight
for i in range(14):
    m = RNG.choice(broken)
    deg = RNG.uniform(0, 360)
    if abs(((deg - GAP_DEG) + 180.0) % 360.0 - 180.0) < 20.0:
        continue
    x, y = polar(RNG.uniform(2560, 2760), deg)
    add(m, place(m, x, y, deg + 90.0 + RNG.uniform(-25, 25)))

# ---------------------------------------------------------------- the gate behind the player start
arch = mesh1(r"^SM_ArchWay_01_N1")
x, y = polar(R_ARENA + 420.0, GAP_DEG)
add(arch, place(arch, x, y, GAP_DEG + 90.0, z=-10))
archtop = mesh1(r"^SM_ArchTop_01_N1")
x, y = polar(R_ARENA + 420.0, GAP_DEG)
vines = mesh1(r"^SM_Vines_01_N1")
x2, y2 = polar(R_ARENA + 200.0, GAP_DEG)
# (the vines mesh reads as a dark thorn column in the doorway: not placed)

# ---------------------------------------------------------------- colossal background: bridge columns and arches far outside
col01 = mesh1(r"^SM_BridgeColumn_01_N1")
col03 = mesh1(r"^SM_BridgeColumn_03_N1")
col02 = mesh1(r"^SM_BridgeColumn_02_Split_N1")
for k in range(7):
    deg = 20.0 + k * (360.0 / 7.0) + RNG.uniform(-6, 6)
    m = col01 if k % 2 == 0 else col03
    x, y = polar(6800.0 + RNG.uniform(-500, 900), deg)
    add(m, place(m, x, y, deg + 90.0 + RNG.uniform(-12, 12), z=-400))
for k in range(5):
    deg = 55.0 + k * 70.0
    x, y = polar(10500.0, deg)
    add(col02, place(col02, x, y, deg + 90.0, z=0))

# ---------------------------------------------------------------- inside: columns with lanterns, fallen columns, rubble, props, floor slabs
col_a = mesh1(r"^SM_Medieval_Church_Ruin_External_Column_02")
col_b = mesh1(r"^SM_Medieval_Church_Ruin_External_Column_01")
roman = meshes(r"^SM_Roman_Column_wj3keakqx_(00|01|Cut_02|Bend_00)_N1")
lantern = mesh1(r"^SM_Lantern_00_N1")
lantern_spots = []
for k in range(6):
    deg = 15.0 + k * 60.0
    x, y = polar(2560.0, deg)
    m = col_a if k % 2 == 0 else col_b
    add(m, place(m, x, y, deg + RNG.uniform(-10, 10)), collision=True)
    top = m.get_bounds().box_extent.z * 2.0
    add(lantern, place(lantern, x + 8.0, y, deg, z=top - 4.0, scale=1.6), shadow=False)
    lantern_spots.append((x, y, top + 40.0))
for k in range(9):  # fallen and broken columns
    m = RNG.choice(roman)
    deg = RNG.uniform(0, 360)
    if abs(((deg - GAP_DEG) + 180.0) % 360.0 - 180.0) < 15.0:
        continue
    x, y = polar(RNG.uniform(2300, 2800), deg)
    add(m, place(m, x, y, RNG.uniform(0, 360), z=18.0, pitch=RNG.choice([82, 86, 0, 0]), scale=RNG.uniform(1.0, 1.5)), collision=True)

rubble = meshes(r"^SM_Concrete_Rubble_Pile_ujriaadga|^SM_Limestone_Rubble|^SM_Limestone_Rocks|^SM_Limestone_Slab|^SM_Cement_Rubble")
flat_piles = [m for m in rubble if "Concrete_Rubble_Pile" in m.get_name()]  # flat sheets: only against the walls (they read as foil in the open floor)
rocks = [m for m in rubble if m not in flat_piles]
for k in range(70):
    inner = RNG.random() < 0.45
    m = RNG.choice(rocks if inner else rubble)
    deg = RNG.uniform(0, 360)
    r = 3000.0 * math.sqrt(RNG.uniform(0.02, 0.97)) if inner else RNG.uniform(2550, 2950)
    x, y = polar(r, deg)
    add(m, place(m, x, y, RNG.uniform(0, 360), scale=RNG.uniform(0.7, 1.5)), shadow=False)

coffin = mesh1(r"^SM_Roman_Stone_Coffin")
for deg in (30.0, 120.0, 250.0, 320.0):
    x, y = polar(2780.0, deg)
    add(coffin, place(coffin, x, y, deg + 90.0 + RNG.uniform(-10, 10)), collision=True)

barrel = mesh1(r"^SM_Wooden_Barrel")
crate = meshes(r"^SM_Old_Wooden_Crate")
table = mesh1(r"^SM_Wooden_Table")
beam = meshes(r"^SM_Worn_Wooden_Beam")
for deg in (75.0, 205.0, 295.0):
    x, y = polar(2820.0, deg)
    for j in range(4):
        add(barrel, place(barrel, x + RNG.uniform(-90, 90), y + RNG.uniform(-90, 90), RNG.uniform(0, 360)), collision=True)
    add(RNG.choice(crate), place(crate[0], x + 140.0, y - 60.0, deg + RNG.uniform(-30, 30)), collision=True)
x, y = polar(2850.0, 340.0)
add(table, place(table, x, y, 340.0 + 90.0 + 15.0), collision=True)
for k in range(10):  # beams leaning on the walls
    m = RNG.choice(beam)
    deg = RNG.uniform(0, 360)
    if abs(((deg - GAP_DEG) + 180.0) % 360.0 - 180.0) < 15.0:
        continue
    x, y = polar(2960.0, deg)
    add(m, place(m, x, y, deg + 180.0, pitch=RNG.uniform(14, 24)), shadow=False)

skull, sword = mesh1(r"^SM_Skull_"), mesh1(r"^SM_Sword_")
chains = meshes(r"^SM_Pile_Of_Chains")
for k in range(16):
    deg = RNG.uniform(0, 360)
    x, y = polar(RNG.uniform(600, 2700), deg)
    add(skull, place(skull, x, y, RNG.uniform(0, 360), scale=RNG.uniform(0.9, 1.1)), shadow=False)
for k in range(7):  # swords stuck in the ground: the fallen
    deg = RNG.uniform(0, 360)
    x, y = polar(RNG.uniform(900, 2600), deg)
    add(sword, place(sword, x, y, RNG.uniform(0, 360), z=-2.0, pitch=RNG.uniform(-14, 14), scale=1.35), shadow=False)
for k in range(5):
    x, y = polar(RNG.uniform(1000, 2700), RNG.uniform(0, 360))
    add(chains[0], place(chains[0], x, y, RNG.uniform(0, 360), scale=1.4), shadow=False)

mush = meshes(r"^SM_White_Button_Mushroom")
for k in range(110):
    deg = RNG.uniform(0, 360)
    x0, y0 = polar(RNG.uniform(2700, 2960), deg)
    for j in range(RNG.randint(2, 5)):
        add(RNG.choice(mush), place(mush[0], x0 + RNG.uniform(-25, 25), y0 + RNG.uniform(-25, 25), RNG.uniform(0, 360), scale=RNG.uniform(1.3, 2.4)), shadow=False)

slabs = meshes(r"^SM_Medieval_(Floor_Slab_Stone|Slab_Stone_Fine_(13|16|10|09))")
for slab in list(slabs) + list(rubble):  # the kit's slab and rubble materials come out mirror-like under a low light: rougher, no extra specular
    for slot in slab.static_materials:
        slab_mi = slot.material_interface
        if isinstance(slab_mi, unreal.MaterialInstanceConstant):
            unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(slab_mi, "Gen - Final Roughness (Offset)", 0.45)
            unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(slab_mi, "Shore Wetness - Additional Spec", 0.0)
            unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(slab_mi, "Specular Max", 0.3)
            unreal.MaterialEditingLibrary.update_material_instance(slab_mi)
            unreal.EditorAssetLibrary.save_loaded_asset(slab_mi)
for k in range(420):  # worn flagstones breaking up the floor
    deg = RNG.uniform(0, 360)
    r = 2950.0 * math.sqrt(RNG.uniform(0.0, 1.0))
    x, y = polar(r, deg)
    m = RNG.choice(slabs)
    add(m, place(m, x, y, RNG.uniform(0, 360), z=0.6 + RNG.uniform(0, 0.8), scale=RNG.uniform(1.0, 1.7)), shadow=False, material=slab_mat)

# outside the walls: dead trees against the sky
trees = meshes(r"^SM_Dead_Tree")
for k in range(7):
    x, y = polar(RNG.uniform(3700, 5200), 10.0 + k * 50.0 + RNG.uniform(-12, 12))
    add(trees[k % len(trees)], place(trees[k % len(trees)], x, y, RNG.uniform(0, 360), z=-30, scale=RNG.uniform(1.4, 2.2)))

# ---------------------------------------------------------------- polish: mist cards, hanging chains, banners
MATS = "/Game/OneBossFight/Environment/Materials/"
mist_mat = unreal.EditorAssetLibrary.load_asset(MATS + "MI_Arena_Mist")
gate_mat = unreal.EditorAssetLibrary.load_asset(MATS + "MI_Arena_FogGate")
banner_mat = unreal.EditorAssetLibrary.load_asset(MATS + "M_Banner")
pillar_mat = unreal.EditorAssetLibrary.load_asset(MATS + "MI_Arena_Pillar")

fogcard = mesh1(r"^SM_FogCard_01_N1$")
for k in range(44):  # low sheets of drifting mist (the card material animates itself)
    x, y = polar(2750.0 * math.sqrt(RNG.uniform(0.0, 1.0)), RNG.uniform(0, 360))
    add(fogcard, place(fogcard, x, y, RNG.uniform(0, 360), z=RNG.uniform(30, 130), scale=RNG.uniform(6.0, 10.0)), shadow=False, material=mist_mat)

# the fog gate: a standing wall of mist across the gap in the wall ring (the doorway of the gate arch), like the fog doors of the genre
# It is an ARPGFogGate actor (C++): thin mist while the boss sleeps, full mist and a blocking box while the fight runs, gone when the boss dies.
gx, gy = polar(R_ARENA + 150.0, GAP_DEG)
gate_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.RPGFogGate, unreal.Vector(gx, gy, 400.0), unreal.Rotator(0, GAP_DEG, 0))
gate_actor.set_actor_label("FogGate")
gate_actor.set_folder_path(FOLDER)
gate_actor.set_editor_property("card_mesh", fogcard)
gate_actor.set_editor_property("card_material", gate_mat)
gate_actor.rebuild()
log("fog gate actor placed at %.0f %.0f" % (gx, gy))

chains = meshes(r"^SM_Rusty_Hanging_Chain_")
for k in range(26):  # chains hanging down the inner face of the walls
    m = RNG.choice(chains)
    deg = RNG.uniform(0, 360)
    if abs(((deg - GAP_DEG) + 180.0) % 360.0 - 180.0) < GAP_HALF:
        continue
    x, y = polar(R_ARENA + 40.0, deg)
    b = m.get_bounds()
    sc = RNG.uniform(1.4, 2.1)
    add(m, place(m, x, y, deg + RNG.uniform(0, 360), z=RNG.uniform(260, 330), scale=sc), shadow=False, sway=3.0, pivot=unreal.Vector(b.origin.x, b.origin.y, b.origin.z + b.box_extent.z))

plane = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Plane")
for i in range(12):  # banners on the pillars, facing the middle of the arena
    deg = i * 30.0
    if abs(((deg - GAP_DEG) + 180.0) % 360.0 - 180.0) < 20.0:
        continue
    x, y = polar(R_ARENA * arena.get_editor_property("pillar_ring_fraction") - 128.0, deg)
    top_z, length, width_cm = 780.0, 330.0, 150.0
    rot = unreal.Rotator(roll=0.0, pitch=90.0, yaw=deg)
    add(plane, unreal.Transform(unreal.Vector(x, y, top_z - length / 2.0), rot, unreal.Vector(length / 100.0, width_cm / 100.0, 1.0)), shadow=True, material=banner_mat, sway=4.5, pivot=unreal.Vector(50.0, 0.0, 0.0))

# the ground beyond the wall: one big dark disc a few cm under the arena floor, so no void shows between the floor edge and the ruins
cyl = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cylinder")
outside_mat = unreal.EditorAssetLibrary.load_asset(MATS + "MI_Arena_Outside")
add(cyl, unreal.Transform(unreal.Vector(0, 0, -15.0), unreal.Rotator(0, 0, 0), unreal.Vector(500.0, 500.0, 0.2)), shadow=False, material=outside_mat)

# stone for the greybox pillars (the arena actor keeps their collision)
arena.set_editor_property("pillar_material", pillar_mat)

# ---------------------------------------------------------------- the dressing actor
dress = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.RPGArenaDressing, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
dress.set_actor_label("ArenaDressing")
dress.set_folder_path(FOLDER)
sets = []
for s in SETS.values():
    st = unreal.RPGDressingSet()
    st.set_editor_property("mesh", s["mesh"])
    st.set_editor_property("instances", s["instances"])
    st.set_editor_property("collision", s["collision"])
    st.set_editor_property("cast_shadow", s["shadow"])
    if s.get("material"):
        st.set_editor_property("material_override", s["material"])
    if s.get("sway"):
        st.set_editor_property("sway_degrees", s["sway"])
        st.set_editor_property("sway_pivot", s["pivot"] or unreal.Vector(0, 0, 0))
    sets.append(st)
dress.set_editor_property("sets", sets)
rebuild(dress)
log("dressing actor: %d sets, %d instances" % (len(sets), dress.get_instance_count()))

# ---------------------------------------------------------------- fires and lights
fire_t = unreal.EditorAssetLibrary.load_asset("/Game/StarterContent/Particles/P_Fire")  # P_Fire_NeverEnding (pack menu fire) is a wide ribbon, not a brazier flame
small_fire_t = unreal.EditorAssetLibrary.load_asset("/Game/StarterContent/Particles/P_Fire")  # lanterns and candles
smoke_t = unreal.EditorAssetLibrary.load_asset("/Game/StarterContent/Particles/P_Smoke")
spark_t = unreal.EditorAssetLibrary.load_asset("/Game/StarterContent/Particles/P_Sparks")
dust_t = unreal.EditorAssetLibrary.load_asset("/Game/StarterContent/Particles/P_Ambient_Dust")
crackle = unreal.EditorAssetLibrary.load_asset("/Game/StarterContent/Audio/Fire01_Cue")
wind = unreal.EditorAssetLibrary.load_asset("/Game/StarterContent/Audio/Starter_Wind05")


def fire(x, y, z, scale=1.0, intensity=60.0, radius=1800.0, particles=True, smoke=True, sparks=False, shadows=False, label="Fire", small=False, sound=False):
    f = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.RPGFireSource, unreal.Vector(x, y, z), unreal.Rotator(0, 0, 0))
    f.set_actor_label(label)
    f.set_folder_path(FOLDER + "/Fires")
    f.set_editor_property("fire_scale", scale)
    f.set_editor_property("base_intensity", intensity)
    f.set_editor_property("attenuation_radius", radius)
    f.set_editor_property("cast_shadows", shadows)
    if particles:
        f.set_editor_property("fire_template", small_fire_t if small else fire_t)
    if smoke:
        f.set_editor_property("smoke_template", smoke_t)
    if sparks:
        f.set_editor_property("spark_template", spark_t)
    if sound:
        f.set_editor_property("crackle_sound", crackle)
    rebuild(f)
    return f


brazier = arena.get_editor_property("brazier")
top = 90.0
if brazier:
    b = brazier.get_bounds()
    top = b.origin.z + b.box_extent.z
flame_bases = []
for i in range(12):
    deg = (i + 0.5) * 30.0
    x, y = polar(R_ARENA * arena.get_editor_property("brazier_ring_fraction"), deg)
    fire(x, y, top - 6.0, scale=2.2, intensity=5000.0, radius=3200.0, shadows=True, label="BrazierFire_%02d" % i, sound=True)
    flame_bases.append(unreal.Vector(x, y, top + 10.0))
for (x, y, z) in lantern_spots:
    fire(x, y, z - 30.0, scale=0.25, intensity=900.0, radius=1800.0, smoke=False, label="LanternFire", small=True)
candles = meshes(r"^SM_Candles_0[123]_N1")
for deg in (30.0, 120.0, 250.0, 320.0):  # candles on the coffins
    x, y = polar(2780.0, deg)
    for j in range(3):
        cx, cy = x + RNG.uniform(-60, 60), y + RNG.uniform(-18, 18)
        c = RNG.choice(candles)
        ca = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(cx, cy, 63.0), unreal.Rotator(0, RNG.uniform(0, 360), 0))
        ca.static_mesh_component.set_static_mesh(c)
        ca.set_actor_label("Candles")
        ca.set_folder_path(FOLDER + "/Fires")
    fire(x, y, 90.0, scale=0.12, intensity=40.0, radius=500.0, smoke=False, label="CandleFire", small=True)

# embers rising from the braziers and ash drifting in the open
for a in actors_sub.get_all_level_actors():
    if a.get_class().get_name() == "RPGEmberField":
        unreal.EditorLevelLibrary.destroy_actor(a)
ef = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.RPGEmberField, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
ef.set_actor_label("EmberField")
ef.set_folder_path(FOLDER + "/Ambient")
ef.set_editor_property("mesh", unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere"))
ef.set_editor_property("material", unreal.EditorAssetLibrary.load_asset(MATS + "M_Ember"))
ef.set_editor_property("fire_sources", flame_bases)
ef.set_editor_property("count", 380)
ef.set_editor_property("size_min", 3.0)
ef.set_editor_property("size_max", 8.0)
rebuild(ef)
log("ember field: %d embers" % ef.get_alive_count())

# wind bed (game only)
for a in actors_sub.get_all_level_actors():
    if a.get_class().get_name() == "RPGArenaAmbience":
        unreal.EditorLevelLibrary.destroy_actor(a)
amb = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.RPGArenaAmbience, unreal.Vector(0, 0, 300), unreal.Rotator(0, 0, 0))
amb.set_actor_label("ArenaAmbience")
amb.set_folder_path(FOLDER + "/Ambient")
amb.set_editor_property("wind", wind)

# ambient dust drifting through the light
for deg in range(0, 360, 60):
    x, y = polar(1500.0, deg + 20.0)
    d = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.Emitter, unreal.Vector(x, y, 250.0), unreal.Rotator(0, 0, 0))
    d.set_actor_label("AmbientDust")
    d.set_folder_path(FOLDER + "/Ambient")
    d.get_editor_property("particle_system_component").set_template(dust_t)

# ---------------------------------------------------------------- hide the old greybox wall and arch visuals (collision stays)
hidden = 0
for c in arena.get_components_by_class(unreal.StaticMeshComponent):
    if c.get_name() in ("Walls", "WallsDamaged", "Arch"):
        c.set_editor_property("hidden_in_game", True)
        c.set_editor_property("visible", False)
        hidden += 1
log("greybox wall visuals hidden: %d components" % hidden)
rebuild(arena)
unreal.EditorLevelLibrary.save_current_level()
log("done and saved")
