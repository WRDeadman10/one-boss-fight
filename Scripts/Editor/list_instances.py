import unreal

def main():
    eal = unreal.EditorAssetLibrary
    assets = eal.list_assets("/Game/Deadly_Ruins/Materials/Instances", recursive=False)
    for a in assets:
        mi = unreal.load_asset(a)
        if isinstance(mi, unreal.MaterialInstanceConstant):
            parent = mi.get_editor_property("parent")
            parent_name = parent.get_name() if parent else "None"
            print(f"{mi.get_name()} -> Parent: {parent_name}")

main()
