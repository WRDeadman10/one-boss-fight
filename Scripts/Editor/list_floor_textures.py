import unreal

eal = unreal.EditorAssetLibrary
assets = eal.list_assets("/Game/Deadly_Ruins/Textures/TilingEnvironment", recursive=False)
for a in sorted(assets):
    t = unreal.load_asset(a)
    if isinstance(t, unreal.Texture2D):
        print(f"Texture: {t.get_name()}, size={t.blueprint_get_size_x()}x{t.blueprint_get_size_y()}")
