"""
Lists the animation assets of the Advanced ARPG Combat pack by folder, so the asset request only asks for what the pack lacks.
Names only, no asset is loaded. Log prefix [PackAnims]. Run with Scripts/run_in_editor.py.
"""
import unreal, collections

log = lambda m: unreal.log("[PackAnims] " + m)
ar = unreal.AssetRegistryHelpers.get_asset_registry()
roots = ["/Game/AdvancedARPGCombat"]
kinds = ("AnimMontage", "AnimSequence", "BlendSpace", "BlendSpace1D", "AimOffsetBlendSpace")
by_folder = collections.defaultdict(list)
total = collections.Counter()
for root in roots:
    for ad in ar.get_assets_by_path(root, recursive=True):
        k = str(ad.asset_class_path.asset_name)
        if k not in kinds:
            continue
        total[k] += 1
        folder = str(ad.package_path).replace(root + "/", "")
        by_folder[folder].append("%s(%s)" % (str(ad.asset_name), k.replace("AnimMontage", "M").replace("AnimSequence", "S").replace("BlendSpace", "BS")))
log("TOTAL %s" % dict(total))
for f in sorted(by_folder):
    log("FOLDER %s (%d)" % (f, len(by_folder[f])))
    for n in sorted(by_folder[f]):
        log("   %s" % n)
