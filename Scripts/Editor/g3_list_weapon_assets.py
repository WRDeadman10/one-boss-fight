"""G3 audit step 1 (log prefix [G3A]): lists the pack's player weapon assets (abilities, attack data, weapon data) so the per-weapon-attack data of Gate 3 can be designed from what exists.
Prints the package path and class of every asset whose name contains one of the weapon words and whose class is a Blueprint or a data asset. Run with Scripts/run_in_editor.py."""
import unreal

log = lambda m: unreal.log("[G3A] " + m)
WORDS = ("claymore", "greatsword", "sword", "dual", "twinblade", "katana", "attackdata", "weapon", "stamina")
ar = unreal.AssetRegistryHelpers.get_asset_registry()
rows = []
for ad in ar.get_assets_by_path("/Game/AdvancedARPGCombat", recursive=True):
    n = str(ad.asset_name).lower()
    k = str(ad.asset_class_path.asset_name)
    if any(w in n for w in WORDS) and k in ("Blueprint", "DataAsset", "PrimaryDataAsset", "DataTable", "GameplayEffect") or (k.endswith("_C") and any(w in n for w in WORDS)):
        rows.append((str(ad.package_name), k))
rows.sort()
log("%d assets" % len(rows))
for p, k in rows:
    log("%s  [%s]" % (p.replace("/Game/AdvancedARPGCombat/", ""), k))
log("done")
