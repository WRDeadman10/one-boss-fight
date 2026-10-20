"""Finds the animation sequences behind the pack boss montages through asset dependencies and exports them as FBX (log prefix [Export3]). Output: Import/ThirdParty/Reference/."""
import os
import unreal

log = lambda m: unreal.log("[Export3] " + m)
ar = unreal.AssetRegistryHelpers.get_asset_registry()
out_dir = os.path.abspath(os.path.join(unreal.SystemLibrary.get_project_directory(), "Import", "ThirdParty", "Reference"))
base = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/"
for mname in ("GS_ChargedAttack_Montage", "GS_Attack01_Montage", "GS_Attack04_Montage", "GS_LeapAttack_Montage"):
    pkg = base + mname
    opts = unreal.AssetRegistryDependencyOptions()
    deps = ar.get_dependencies(pkg, opts) or []
    found = False
    for d in deps:
        for ad in ar.get_assets_by_package_name(d):
            if str(ad.asset_class_path.asset_name) == "AnimSequence":
                seq = ad.get_asset()
                log("%s -> %s len %.2f s" % (mname, ad.package_name, seq.get_editor_property("sequence_length")))
                task = unreal.AssetExportTask()
                task.object = seq
                task.filename = os.path.join(out_dir, "REF_%s__%s.fbx" % (mname.replace("_Montage", ""), ad.asset_name))
                task.automated = True
                task.prompt = False
                task.replace_identical = True
                opt = unreal.FbxExportOption()
                opt.ascii = False
                task.options = opt
                log("  export ok=%s %s" % (unreal.Exporter.run_asset_export_task(task), task.filename))
                found = True
    if not found:
        log("%s: no sequence dependency found (%s)" % (mname, [str(x) for x in deps][:8]))
log("done")
