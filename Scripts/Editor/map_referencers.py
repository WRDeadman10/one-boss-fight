"""Which assets reference the original pack animations that were retargeted? Writes Saved/grey_referencers.json
(referencer package -> list of original packages it references)."""
import json
import unreal

log = lambda m: unreal.log("[GreyRefs] " + m)
mapping = json.load(open(unreal.Paths.project_saved_dir() + "greystone_retarget_map.json"))
reg = unreal.AssetRegistryHelpers.get_asset_registry()
opts = unreal.AssetRegistryDependencyOptions(include_soft_package_references=False, include_hard_package_references=True)
refs = {}
newset = set(mapping.values())
for old in mapping:
    for r in reg.get_referencers(old, opts):
        r = str(r)
        if r in newset or r == old or r.startswith("/Game/OneBossFight/GreystonePack"):
            continue
        refs.setdefault(r, []).append(old)
json.dump(refs, open(unreal.Paths.project_saved_dir() + "grey_referencers.json", "w"))
log("%d referencing assets" % len(refs))
