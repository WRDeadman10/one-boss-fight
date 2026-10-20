import unreal

def inspect_pillar_mi(name):
    path = f"/Game/Deadly_Ruins/Materials/Instances/{name}"
    mi = unreal.load_asset(path)
    if not mi:
        print("Missing:", path)
        return
    print(f"=== {name} ===")
    print("Parent:", mi.get_editor_property("parent").get_path_name())
    for sp in mi.scalar_parameter_values:
        print(f"  Scalar: {sp.parameter_info.name} = {sp.parameter_value}")
    for tp in mi.texture_parameter_values:
        tex = tp.parameter_value
        print(f"  Texture: {tp.parameter_info.name} = {tex.get_path_name() if tex else 'None'}")

for i in range(1, 6):
    inspect_pillar_mi(f"MI_DR_Pillar_{i}")
