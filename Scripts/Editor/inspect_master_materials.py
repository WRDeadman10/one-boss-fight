import unreal

def inspect_master(path):
    m = unreal.load_asset(path)
    if not m:
        print("Missing master:", path)
        return
    print("=== Master Material:", path, "===")
    mel = unreal.MaterialEditingLibrary
    # Let's inspect parameter names
    scalars = mel.get_scalar_parameter_names(m)
    vectors = mel.get_vector_parameter_names(m)
    textures = mel.get_texture_parameter_names(m)
    print("Scalars:", scalars)
    print("Vectors:", vectors)
    print("Textures:", textures)

inspect_master("/Game/Deadly_Ruins/Materials/MasterMaterial/MM_Prop_WorldBlend")
inspect_master("/Game/Deadly_Ruins/Materials/MasterMaterial/MM_Prop_Detail")
