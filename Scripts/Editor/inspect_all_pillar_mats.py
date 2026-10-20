import unreal

for p in ["SM_I_Pillar1", "SM_I_Pillar2", "SM_I_Pillar3", "SM_pillar1", "SM__pillar2", "SM__pillar3", "SM__pillar4", "SM__Pillar5"]:
    mesh = unreal.load_asset("/Game/Deadly_Ruins/Meshes/Architecture/" + p)
    if mesh:
        mats = [f"{sm.material_slot_name}: {sm.material_interface.get_name() if sm.material_interface else 'None'}" for sm in mesh.static_materials]
        print(f"{p}: {mats}")
