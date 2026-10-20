import unreal

def inspect_mi(path):
    mi = unreal.load_asset(path)
    if not mi:
        print("Missing:", path)
        return
    print(f"=== {path} ===")
    print("Parent:", mi.get_editor_property("parent").get_path_name())
    for sp in mi.scalar_parameter_values:
        print(f"  Scalar: {sp.parameter_info.name} = {sp.parameter_value}")
    for tp in mi.texture_parameter_values:
        tex = tp.parameter_value
        print(f"  Texture: {tp.parameter_info.name} = {tex.get_path_name() if tex else 'None'}")

inspect_mi("/Game/Deadly_Ruins/Materials/Instances/MI_Floor_Relief")
inspect_mi("/Game/Deadly_Ruins/Materials/Instances/MI_TIling_Brick_floor")
inspect_mi("/Game/Deadly_Ruins/Materials/Instances/MI_Brick_Debris")
