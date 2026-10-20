import unreal

def main():
    eal = unreal.EditorAssetLibrary
    assets = eal.list_assets("/Game/Deadly_Ruins/Meshes/Architecture", recursive=False)
    for a in sorted(assets):
        if "wall" in a.lower():
            mesh = unreal.load_asset(a)
            if mesh:
                b = mesh.get_bounds()
                e = b.box_extent
                o = b.origin
                mats = [f"{sm.material_slot_name}: {sm.material_interface.get_name() if sm.material_interface else 'None'}" for sm in mesh.static_materials]
                print(f"{mesh.get_name()}: Extent=({e.x:.1f}, {e.y:.1f}, {e.z:.1f}), Origin=({o.x:.1f}, {o.y:.1f}, {o.z:.1f}), Mats={mats}")

main()
