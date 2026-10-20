"""Brief 02 reference export (log prefix [Export2]): the pack's GS_ChargedAttack animation (FBX), Paragon body candidates (skeletal mesh FBX plus their textures as PNG), and the Kwang sword textures as the
quality target. Output goes to Import/ThirdParty/Reference/ (git ignored). Run with Scripts/run_in_editor.py."""
import os
import unreal

log = lambda m: unreal.log("[Export2] " + m)
ar = unreal.AssetRegistryHelpers.get_asset_registry()
out_dir = os.path.abspath(os.path.join(unreal.SystemLibrary.get_project_directory(), "Import", "ThirdParty", "Reference"))
os.makedirs(out_dir, exist_ok=True)


def export(obj, fname, fbx=False):
    task = unreal.AssetExportTask()
    task.object = obj
    task.filename = os.path.join(out_dir, fname)
    task.automated = True
    task.prompt = False
    task.replace_identical = True
    if fbx:
        opt = unreal.FbxExportOption()
        opt.ascii = False
        opt.vertex_color = False
        opt.collision = False
        opt.level_of_detail = False
        task.options = opt
    ok = unreal.Exporter.run_asset_export_task(task)
    log("%s ok=%s exists=%s" % (fname, ok, os.path.exists(task.filename)))


# 1. The animation sequences behind the pack boss montages
for mname in ("GS_ChargedAttack_Montage", "GS_Attack01_Montage", "GS_LeapAttack_Montage"):
    for ad in ar.get_assets_by_path("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI", recursive=True):
        if str(ad.asset_name) == mname:
            m = ad.get_asset()
            try:
                seq = m.get_editor_property("slot_anim_tracks")[0].get_editor_property("anim_track").get_editor_property("anim_segments")[0].get_editor_property("anim_reference")
                log("%s -> sequence %s (len %.2f)" % (mname, seq.get_path_name(), seq.get_editor_property("sequence_length")))
                export(seq, "REF_%s.fbx" % seq.get_name(), True)
            except Exception as e:
                log("%s sequence ERR %s" % (mname, e))

# 2. Paragon body candidates
for folder, tag in (("/Game/ParagonSevarog", "Sevarog"), ("/Game/ParagonGrux", "Grux")):
    meshes, texs = [], []
    for ad in ar.get_assets_by_path(folder, recursive=True):
        k = str(ad.asset_class_path.asset_name)
        n = str(ad.asset_name)
        if k == "SkeletalMesh":
            meshes.append(ad)
        elif k == "Texture2D":
            texs.append(ad)
    log("%s: %d skeletal meshes, %d textures" % (tag, len(meshes), len(texs)))
    for ad in meshes:
        log("  mesh %s" % ad.package_name)
    for ad in meshes:
        if "Mesh" in str(ad.package_path) or True:
            export(ad.get_asset(), "REF_%s_%s.fbx" % (tag, ad.asset_name), True)
    for ad in texs:
        n = str(ad.asset_name)
        if any(n.endswith(s) for s in ("_D", "_N", "_ORM", "_E", "_M", "_R", "_O", "_BC", "_Color")) or "Cape" in n or True:
            try:
                export(ad.get_asset(), "REF_%s_%s.png" % (tag, n))
            except Exception as e:
                log("  tex %s ERR %s" % (n, e))

# 3. Quality target: the Kwang sword materials' textures
for ad in ar.get_assets_by_path("/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets", recursive=True):
    n = str(ad.asset_name)
    if str(ad.asset_class_path.asset_name) == "Texture2D" and "kwang" in n.lower():
        export(ad.get_asset(), "REF_Kwang_%s.png" % n)
log("done")
