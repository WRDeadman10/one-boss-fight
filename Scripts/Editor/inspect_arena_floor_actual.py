import unreal

mi = unreal.load_asset("/Game/OneBossFight/Environment/Materials/MI_Arena_Floor")
print("Parent:", mi.get_editor_property("parent").get_path_name())
for sp in mi.scalar_parameter_values:
    print(f"  Scalar: {sp.parameter_info.name} = {sp.parameter_value}")
for tp in mi.texture_parameter_values:
    tex = tp.parameter_value
    print(f"  Texture: {tp.parameter_info.name} = {tex.get_path_name() if tex else 'None'}")
