import unreal

DR_MESH = "/Game/Deadly_Ruins/Meshes/"

def main():
    meshes = [
        "Architecture/SM_pillar1",
        "Architecture/SM__pillar2",
        "Architecture/SM__pillar3",
        "Architecture/SM__pillar4",
        "Architecture/SM__Pillar5",
        "Architecture/SM_archway_1",
        "Architecture/SM_archway_B",
        "Architecture/SM_wall1",
        "Architecture/SM_wall2",
        "Architecture/SM_I_Wall1",
        "Prop/SM_brickrubble1",
        "Prop/SM_brickrubble2",
        "Prop/SM_brickrubble3",
        "Prop/SM_rockprop1",
        "Prop/SM_rockprop2",
        "Prop/SM_Brazer",
    ]
    for m in meshes:
        mesh = unreal.load_asset(DR_MESH + m)
        if mesh:
            b = mesh.get_bounds()
            e = b.box_extent
            o = b.origin
            mats = [str(mat.material_slot_name) for mat in mesh.static_materials]
            unreal.log(f"[SurveyDR] {m} -> Extent: ({e.x:.1f}, {e.y:.1f}, {e.z:.1f}), Origin: ({o.x:.1f}, {o.y:.1f}, {o.z:.1f}), Mats: {mats}")
        else:
            unreal.log(f"[SurveyDR] MISSING: {m}")

main()
