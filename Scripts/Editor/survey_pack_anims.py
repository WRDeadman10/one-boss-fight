"""Survey of animation assets in the pack: class, skeleton, folder. Run in the editor (execute_script). Writes Saved/pack_anim_survey.json."""
import json
import unreal

reg = unreal.AssetRegistryHelpers.get_asset_registry()
rows = []
for cls_name in ("AnimSequence", "AnimMontage", "BlendSpace", "BlendSpace1D", "AimOffsetBlendSpace", "AimOffsetBlendSpace1D", "AnimBlueprint", "AnimComposite", "PoseAsset", "AnimLayerInterface"):
    flt = unreal.ARFilter(class_paths=[unreal.TopLevelAssetPath("/Script/Engine", cls_name)], package_paths=["/Game/AdvancedARPGCombat"], recursive_paths=True)
    for d in reg.get_assets(flt):
        skel = ""
        for tag in ("Skeleton", "TargetSkeleton"):
            v = d.get_tag_value(tag)
            if v:
                skel = str(v)
        rows.append({"name": str(d.asset_name), "class": cls_name, "path": str(d.package_name), "skeleton": skel})
json.dump(rows, open(unreal.Paths.project_saved_dir() + "pack_anim_survey.json", "w"), indent=0)
unreal.log("[Survey] %d assets" % len(rows))
