"""BQ-57/58 (Queue BQ batch 12; B11 KI-045, B9 KI-035): read-only inventories for the Greystone retarget set.

Part A (KI-045): lists every AnimMontage under /Game/OneBossFight/GreystonePack whose package dependencies include a
root-level /Game/<name> package that does not exist (the "eight retargeted enemy montages"), plus who still references
/Game/RMB_Cast_Grey1 (the keep-alive copy). It repairs nothing: rebuilding unused enemy montages or deleting the copy is an
asset decision for the Lead (KI-045 says they are not used by Greystone).

Part B (KI-035): dumps the weapon sockets of the mannequin skeleton and the Greystone skeleton side by side (bone,
relative location/rotation/scale) and flags sockets that are byte-identical copies, i.e. never adjusted for Greystone's
larger body. The visual check per weapon stays ENG/owner; this only tells the reviewer where to look.

Never sets, saves, creates or deletes anything. Run in the full Editor under C-1155 (ENG).
"""
import traceback

PREFIX = "[GreyInventory] "
GP = "/Game/OneBossFight/GreystonePack"
KEEPALIVE = "/Game/RMB_Cast_Grey1"
MANNEQUIN_SKELETON = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin"
GREYSTONE_SKELETON = "/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone_Skeleton"


def is_root_level(package):
    """Pure: '/Game/Name' (exactly one level below /Game) is root-level; '/Game/A/B' is not."""
    text = str(package)
    return text.startswith("/Game/") and "/" not in text[len("/Game/"):]


def same_transform(a, b, tolerance=1.0e-3):
    """Pure: two (loc, rot, scale) triples of 3-tuples are equal within tolerance (an unadjusted copy)."""
    return all(abs(x - y) <= tolerance for pa, pb in zip(a, b) for x, y in zip(pa, pb))


def socket_rows(unreal, skeleton_path):
    skeleton = unreal.load_asset(skeleton_path)
    if skeleton is None:
        return None
    rows = {}
    for socket in skeleton.get_editor_property("sockets"):
        loc, rot, scale = (socket.get_editor_property(n) for n in ("relative_location", "relative_rotation", "relative_scale"))
        rows[str(socket.get_editor_property("socket_name"))] = (
            str(socket.get_editor_property("bone_name")),
            ((loc.x, loc.y, loc.z), (rot.roll, rot.pitch, rot.yaw), (scale.x, scale.y, scale.z)))
    return rows


def main():
    import unreal  # Editor only
    log = lambda m: unreal.log(PREFIX + m)
    eal = unreal.EditorAssetLibrary
    registry = unreal.AssetRegistryHelpers.get_asset_registry()

    broken = 0
    options = unreal.AssetRegistryDependencyOptions(include_soft_package_references=True, include_hard_package_references=True)
    for data in registry.get_assets_by_path(GP, recursive=True):
        if str(data.asset_class_path.asset_name) != "AnimMontage":
            continue
        deps = [str(d) for d in (registry.get_dependencies(data.package_name, options) or [])]
        missing = [d for d in deps if is_root_level(d) and not eal.does_asset_exist(d)]
        if missing:
            broken += 1
            log("BROKEN_MONTAGE package=%s missing=%s" % (data.package_name, missing))
    keepalive_refs = [str(r) for r in eal.find_package_referencers_for_asset(KEEPALIVE, False)] if eal.does_asset_exist(KEEPALIVE) else []
    log("KEEPALIVE path=%s exists=%d referencers=%s" % (KEEPALIVE, int(eal.does_asset_exist(KEEPALIVE)), keepalive_refs))
    log("PART_A broken_montages=%d (KI-045 expects 8)" % broken)

    mannequin, greystone = socket_rows(unreal, MANNEQUIN_SKELETON), socket_rows(unreal, GREYSTONE_SKELETON)
    if mannequin is None or greystone is None:
        log("PART_B skipped: skeleton missing mannequin=%s greystone=%s" % (mannequin is not None, greystone is not None))
    else:
        copied = 0
        for name in sorted(greystone):
            bone, transform = greystone[name]
            twin = mannequin.get(name)
            identical = twin is not None and twin[0] == bone and same_transform(twin[1], transform)
            copied += int(identical)
            log("SOCKET name=%s bone=%s greystone=%s mannequin=%s unadjusted_copy=%d" %
                (name, bone, transform, twin[1] if twin else None, int(identical)))
        log("PART_B greystone_sockets=%d unadjusted_copies=%d" % (len(greystone), copied))
    log("RESULT=DONE saves=0")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        import unreal
        unreal.log_error(PREFIX + "RESULT=FAIL " + str(error))
        unreal.log_error(traceback.format_exc())
