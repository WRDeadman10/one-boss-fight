import unreal

def inspect_uvs(mesh_path):
    mesh = unreal.load_asset(mesh_path)
    if not mesh:
        print("Missing:", mesh_path)
        return
    sm = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    num_uvs = sm.get_num_uv_channels(mesh, 0)
    print(f"{mesh_path}: num UV channels = {num_uvs}")
    # Let's inspect LOD 0 vertex count and bounds
    print(f"  Bounds: {mesh.get_bounds().box_extent}")

inspect_uvs("/Game/OneBossFight/Environment/Meshes/SM_Wall_Curved_Intact")
inspect_uvs("/Game/OneBossFight/Environment/Meshes/SM_Arena_Rubble_Cluster")
