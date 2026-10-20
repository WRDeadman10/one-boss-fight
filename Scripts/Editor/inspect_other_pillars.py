import unreal

def inspect_mesh_mats(path):
    mesh = unreal.load_asset(path)
    if not mesh:
        print("Missing:", path)
        return
    print("Mesh:", path)
    for i, sm in enumerate(mesh.static_materials):
        mi = sm.material_interface
        print(f"  Slot {i} ({sm.material_slot_name}): {mi.get_path_name() if mi else 'None'}")

inspect_mesh_mats("/Game/Deadly_Ruins/Meshes/Architecture/SM__pillar2")
inspect_mesh_mats("/Game/Deadly_Ruins/Meshes/Architecture/SM__pillar3")
inspect_mesh_mats("/Game/Deadly_Ruins/Meshes/Architecture/SM__pillar4")
inspect_mesh_mats("/Game/Deadly_Ruins/Meshes/Architecture/SM__Pillar5")
