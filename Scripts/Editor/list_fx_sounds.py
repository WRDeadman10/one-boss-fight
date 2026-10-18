"""Lists SoundCue and ParticleSystem asset names in the Greystone and Sevarog packs (for choosing combat audio/VFX)."""
import unreal

registry = unreal.AssetRegistryHelpers.get_asset_registry()
for root in ("/Game/ParagonGreystone", "/Game/ParagonSevarog"):
    registry.scan_paths_synchronous([root], True)
    cues, fx = [], []
    for a in registry.get_assets_by_path(root, recursive=True):
        cls = str(a.asset_class_path.asset_name)
        if cls == "SoundCue":
            cues.append(str(a.package_name).replace(root, ""))
        elif cls == "ParticleSystem":
            fx.append(str(a.package_name).replace(root, ""))
    unreal.log("[FxList] %s SoundCues: %s" % (root, sorted(cues)))
    unreal.log("[FxList] %s ParticleSystems: %s" % (root, sorted(fx)))
