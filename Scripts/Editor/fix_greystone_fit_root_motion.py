"""C-1285 Lead: give the Greystone ER fit retargets real root-bone motion.

Default = dry-run (read-only): lists both IK rigs' retarget chains and roots, the RTG_ERFit_Greystone
Root chain mapping and FK translation mode, and the root/pelvis xy displacement of the four ER sources.
--write: ensures a Root chain (root -> root) on IK_CombatMannequin and IK_Fit_Greystone, maps Root -> Root
in RTG_ERFit_Greystone with FK TranslationMode = GloballyScaled, saves those project assets, then runs
duplicate_and_retarget for the four ER source sequences into /Game/OneBossFight/Player/FitTest/Greystone/
as *_Fit_GreystoneRM, measures root/pelvis xy on every output, saves them, and writes Saved/ERFitRM_<stamp>.json.
Never touches pack content; on failure deletes only the outputs it created this run.
Log prefix [GreystoneRootFix]; ends with "[GreystoneRootFix] RESULT=PASS|FAIL".
"""
import json
import os
import time
import traceback

import unreal

PREFIX = "[GreystoneRootFix] "
SOURCE_MESH = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin"
SOURCE_RIG = "/Game/OneBossFight/GreystonePack/IK_CombatMannequin"
TARGET_MESH = "/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone"
TARGET_RIG = "/Game/OneBossFight/Player/FitTest/Greystone/IK_Fit_Greystone"
RETARGETER = "/Game/OneBossFight/Player/FitTest/Greystone/RTG_ERFit_Greystone"
OUT_ROOT = "/Game/OneBossFight/Player/FitTest/Greystone"
SUFFIX = "_Fit_GreystoneRM"
SOURCES = [
    "/Game/OneBossFight/Player/Animations/AN_ER_Backstep_Mixamo_V2",
    "/Game/OneBossFight/Player/Animations/AN_ER_Attack_Air_Light",
    "/Game/OneBossFight/Player/Animations/AN_ER_Attack_Air_Heavy_Plunge",
    "/Game/OneBossFight/Player/Animations/AN_ER_Attack_GuardCounter",
]
CREATED = []


def log(m):
    unreal.log(PREFIX + str(m))


def write_mode():
    return "--write" in unreal.SystemLibrary.get_command_line().split()


def require(cond, msg):
    if not cond:
        raise RuntimeError(msg)


def load(path, what):
    asset = unreal.load_asset(path)
    require(asset is not None, "%s missing: %s" % (what, path))
    return asset


def chain_rows(rig):
    controller = unreal.IKRigController.get_controller(rig)
    rows = []
    for chain in controller.get_retarget_chains():
        name = str(chain.get_editor_property("chain_name"))
        start = str(chain.get_editor_property("start_bone").get_editor_property("bone_name"))
        end = str(chain.get_editor_property("end_bone").get_editor_property("bone_name"))
        rows.append((name, start, end))
    return controller, rows


def displacement(seq, bone):
    length = seq.get_play_length()
    a = unreal.AnimationLibrary.get_bone_pose_for_time(seq, bone, 0.0, False).translation
    b = unreal.AnimationLibrary.get_bone_pose_for_time(seq, bone, length, False).translation
    return ((b.x - a.x) ** 2 + (b.y - a.y) ** 2) ** 0.5


def describe_sequence(tag, seq):
    root = displacement(seq, "root")
    pelvis = displacement(seq, "pelvis")
    log("%s %s skeleton=%s enable_root_motion=%s root_xy_cm=%.2f pelvis_xy_cm=%.2f length=%.4f" %
        (tag, seq.get_name(), seq.get_editor_property("skeleton").get_name(),
         seq.get_editor_property("enable_root_motion"), root, pelvis, seq.get_play_length()))
    return root, pelvis


def ensure_root_chain(rig, label, write):
    controller, rows = chain_rows(rig)
    log("RIG %s retarget_root=%s chains=%s" % (label, controller.get_retarget_root(), rows))
    root_chain = next((r for r in rows if r[1] == "root" and r[2] == "root"), None)
    if root_chain:
        log("RIG %s root chain present: %s" % (label, root_chain[0]))
        return controller, root_chain[0], False
    if not write:
        log("RIG %s has NO root->root chain (dry-run: would add Root)" % label)
        return controller, None, False
    name = str(controller.add_retarget_chain("Root", "root", "root", ""))
    require(name not in ("", "None"), "add_retarget_chain failed on " + label)
    log("RIG %s added chain %s root->root" % (label, name))
    return controller, name, True


def fk_mode(rc, chain_name):
    settings = rc.get_retarget_chain_settings(chain_name)
    return settings, settings.get_editor_property("fk").get_editor_property("translation_mode")


def main():
    write = write_mode()
    log("MODE=%s" % ("WRITE" if write else "DRY_RUN"))
    source_mesh = load(SOURCE_MESH, "source mesh")
    target_mesh = load(TARGET_MESH, "target mesh")
    source_rig = load(SOURCE_RIG, "source IK rig")
    target_rig = load(TARGET_RIG, "target IK rig")
    retargeter = load(RETARGETER, "retargeter")
    sources = [load(p, "source sequence") for p in SOURCES]
    for seq in sources:
        describe_sequence("SOURCE", seq)

    _, source_chain, source_changed = ensure_root_chain(source_rig, "IK_CombatMannequin", write)
    _, target_chain, target_changed = ensure_root_chain(target_rig, "IK_Fit_Greystone", write)

    rc = unreal.IKRetargeterController.get_controller(retargeter)
    probe_chain = target_chain or "Root"
    try:
        mapped = str(rc.get_source_chain(probe_chain))
    except Exception as exc:
        mapped = "ERR(%r)" % exc
    try:
        _, mode = fk_mode(rc, probe_chain)
    except Exception as exc:
        mode = "ERR(%r)" % exc
    log("RETARGETER Root target_chain=%s source_chain=%s fk_translation_mode=%s" % (probe_chain, mapped, mode))

    if not write:
        log("RESULT=PASS dry_run=1 saves=0")
        return

    require(source_chain and target_chain, "root chains missing after write step")
    eal = unreal.EditorAssetLibrary
    if source_changed:
        require(eal.save_loaded_asset(source_rig), "failed to save source rig")
        log("SAVED " + SOURCE_RIG)
    if target_changed:
        require(eal.save_loaded_asset(target_rig), "failed to save target rig")
        log("SAVED " + TARGET_RIG)
    if mapped != source_chain:
        require(rc.set_source_chain(source_chain, target_chain),
                "set_source_chain(%s,%s) failed" % (source_chain, target_chain))
        log("RETARGETER mapped %s -> %s" % (source_chain, target_chain))
    settings, _ = fk_mode(rc, target_chain)
    fk = settings.get_editor_property("fk")
    fk.set_editor_property("translation_mode", unreal.RetargetTranslationMode.GLOBALLY_SCALED)
    fk.set_editor_property("translation_alpha", 1.0)
    settings.set_editor_property("fk", fk)
    require(rc.set_retarget_chain_settings(target_chain, settings), "set_retarget_chain_settings failed")
    _, check = fk_mode(rc, target_chain)
    log("RETARGETER Root fk_translation_mode now %s" % check)
    require(eal.save_loaded_asset(retargeter), "failed to save retargeter")
    log("SAVED " + RETARGETER)

    outputs = []
    for seq in sources:
        out_path = OUT_ROOT + "/" + str(seq.get_name()) + SUFFIX
        require(not eal.does_asset_exist(out_path), "refusing overwrite: " + out_path)
        outputs.append(out_path)
    data = [eal.find_asset_data(p) for p in SOURCES]
    require(all(d.is_valid() for d in data), "asset data lookup failed")
    results = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
        data, source_mesh, target_mesh, retargeter, "", "", "", SUFFIX, False)
    require(len(results) == len(sources), "batch returned %d results for %d sources" % (len(results), len(sources)))
    by_name = {str(r.asset_name): r for r in results}
    for seq, out_path in zip(sources, outputs):
        name = str(seq.get_name()) + SUFFIX
        require(name in by_name, "batch result missing: " + name)
        src_pkg = str(by_name[name].package_name)
        if src_pkg != out_path:
            require(eal.rename_asset(src_pkg, out_path), "rename into FitTest failed: " + name)
        CREATED.append(out_path)
    rows = []
    for seq, out_path in zip(sources, outputs):
        out = load(out_path, "retarget output")
        s_root, s_pelvis = describe_sequence("SOURCE", seq)
        o_root, o_pelvis = describe_sequence("OUTPUT", out)
        ratio = (o_root / s_root) if s_root > 1.0 else None
        rows.append({"source": seq.get_path_name(), "output": out.get_path_name(),
                     "source_root_xy_cm": s_root, "source_pelvis_xy_cm": s_pelvis,
                     "output_root_xy_cm": o_root, "output_pelvis_xy_cm": o_pelvis, "root_ratio": ratio,
                     "enable_root_motion": bool(out.get_editor_property("enable_root_motion"))})
        log("ROOTMOTION %s source_root=%.2f output_root=%.2f output_pelvis=%.2f ratio=%s" %
            (out.get_name(), s_root, o_root, o_pelvis, ("%.3f" % ratio) if ratio else "n/a"))
    backstep = rows[0]
    require(backstep["output_root_xy_cm"] > 0.5 * backstep["source_root_xy_cm"],
            "backstep output root motion still missing (%.2f cm)" % backstep["output_root_xy_cm"])
    for out_path in outputs:
        require(eal.save_loaded_asset(unreal.load_asset(out_path)), "failed to save " + out_path)
        log("SAVED " + out_path)
    manifest = os.path.join(unreal.Paths.project_saved_dir(), "ERFitRM_%s.json" % time.strftime("%Y%m%d_%H%M%S"))
    with open(manifest, "w", encoding="utf-8") as handle:
        json.dump({"schema_version": 1, "retargeter": RETARGETER, "root_chain": target_chain,
                   "fk_translation_mode": str(check), "clips": rows}, handle, indent=2)
    log("MANIFEST " + manifest)
    log("RESULT=PASS outputs=%d rig_saves=%d" % (len(outputs), int(source_changed) + int(target_changed)))


def quit_editor():
    # The batch retarget needs the full editor (Slate); when launched with UnrealEditor.exe -ExecCmds="py ..." the
    # script must end the session itself. Harmless under the commandlet.
    try:
        unreal.SystemLibrary.execute_console_command(None, "Quit")
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log("ERROR " + repr(exc))
        traceback.print_exc()
        for path in reversed(CREATED):
            try:
                if unreal.EditorAssetLibrary.does_asset_exist(path) and unreal.EditorAssetLibrary.delete_asset(path):
                    log("ROLLBACK_DELETED=" + path)
            except Exception as rb:
                log("ROLLBACK_ERROR path=%s error=%r" % (path, rb))
        log("RESULT=FAIL")
    quit_editor()
