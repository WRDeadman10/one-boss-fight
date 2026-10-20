"""Finds the boss weapon mesh (Kwang sword) and prints its sockets. Log prefix [G0W]. Run with Scripts/run_in_editor.py."""
import unreal

log = lambda m: unreal.log("[G0W] " + m)
ar = unreal.AssetRegistryHelpers.get_asset_registry()
for ad in ar.get_assets_by_path("/Game/AdvancedARPGCombat", recursive=True):
    n = str(ad.asset_name)
    k = str(ad.asset_class_path.asset_name)
    if "kwang" in n.lower() and k in ("StaticMesh", "SkeletalMesh"):
        m = ad.get_asset()
        b = m.get_bounds()
        log("%s %s size %.0f x %.0f x %.0f" % (k, ad.package_name, b.box_extent.x * 2, b.box_extent.y * 2, b.box_extent.z * 2))
        if k == "SkeletalMesh":
            log("  sockets: %s" % ",".join("%s@%s" % (m.get_socket_by_index(i).get_editor_property("socket_name"), m.get_socket_by_index(i).get_editor_property("bone_name")) for i in range(m.num_sockets())))
        else:
            try:
                ss = m.get_sockets_by_tag("")
                log("  sockets by empty tag: %s" % [str(s.get_editor_property("socket_name")) for s in ss])
            except Exception as e:
                log("  get_sockets_by_tag ERR %s" % e)
            for cand in ("Socket_0", "Socket_1", "TraceStart", "TraceEnd", "Start", "End", "Tip", "Base", "Trail_Start", "Trail_End", "Trace_0", "Trace_1", "WeaponTip", "WeaponBase", "TrailStart", "TrailEnd"):
                try:
                    s = m.find_socket(cand)
                    if s:
                        log("  found socket %s at %s" % (cand, s.get_editor_property("relative_location")))
                except Exception:
                    pass
log("done")
