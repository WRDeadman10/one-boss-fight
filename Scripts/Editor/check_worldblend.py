import unreal

def main():
    m = unreal.load_asset("/Game/Deadly_Ruins/Materials/MasterMaterial/MM_Prop_WorldBlend")
    print("MM_Prop_WorldBlend loaded:", m is not None)
    mf = unreal.load_asset("/Game/Deadly_Ruins/Materials/MaterialFunction/MF_Worldspace_Blend_Material")
    print("MF_Worldspace_Blend_Material loaded:", mf is not None)

main()
