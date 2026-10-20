"""Greystone repair, step 3: blend spaces saved with stale animation references (name-collision duplicates at /Game root). For every blend space in
GreystonePack whose samples have lost their animation, copy the animation from the pack's original blend space sample through the retarget map
(Saved/greystone_retarget_map.json) and save."""
import json
import unreal

log = lambda m: unreal.log("[GreyBS] " + m)
mapping = json.load(open(unreal.Paths.project_saved_dir() + "greystone_retarget_map.json"))
reverse = {v: k for k, v in mapping.items()}
reg = unreal.AssetRegistryHelpers.get_asset_registry()
fixed = broken = 0
for a in reg.get_assets_by_path("/Game/OneBossFight/GreystonePack", recursive=True):
    if str(a.asset_class_path.asset_name) not in ("BlendSpace", "BlendSpace1D", "AimOffsetBlendSpace", "AimOffsetBlendSpace1D"):
        continue
    path = str(a.package_name)
    bs = a.get_asset()
    samples = list(bs.get_editor_property("sample_data"))
    missing = [i for i, s in enumerate(samples) if s.get_editor_property("animation") is None]
    if not missing:
        continue
    orig_path = reverse.get(path)
    orig = unreal.load_asset(orig_path) if orig_path else None
    if orig is None:
        log("%s: %d samples without animation, original unknown" % (a.asset_name, len(missing)))
        broken += 1
        continue
    orig_samples = list(orig.get_editor_property("sample_data"))
    changed = 0
    for i in missing:
        anim = orig_samples[i].get_editor_property("animation")
        if anim is None:
            continue
        target = mapping.get(anim.get_path_name().split(".")[0])
        asset = unreal.load_asset(target) if target else None
        if asset is None:
            log("  %s sample %d: no retargeted animation for %s" % (a.asset_name, i, anim.get_name()))
            continue
        samples[i].set_editor_property("animation", asset)
        changed += 1
    bs.set_editor_property("sample_data", samples)
    unreal.EditorAssetLibrary.save_loaded_asset(bs)
    log("%s: %d of %d missing samples restored" % (a.asset_name, changed, len(missing)))
    fixed += 1
log("blend spaces fixed: %d, unresolved: %d" % (fixed, broken))
