import unreal

MESH_DIR = "/Game/OneBossFight/Environment/Meshes/"

def main():
    meshes = [
        "SM_Pillar_Intact",
        "SM_Pillar_Cracked",
        "SM_Pillar_Broken",
        "SM_Wall_Curved_Intact",
        "SM_Wall_Curved_Damaged",
        "SM_Entrance_Arch",
        "SM_Arena_Brazier",
        "SM_Arena_Rubble_Cluster"
    ]
    sm = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    for name in meshes:
        mesh = unreal.load_asset(MESH_DIR + name)
        if not mesh:
            print(f"Missing {name}")
            continue
        uvs = sm.get_num_uv_channels(mesh, 0)
        mats = [m.material_slot_name for m in mesh.static_materials]
        print(f"{name}: UV channels = {uvs}, Materials = {mats}")

main()
