"""Create an isolated, non-destructive six-clip player-fit candidate set.

Run once per candidate in the Unreal Editor UI (the batch retarget operation
uses Slate):
  -ExecutePythonScript=.../Scripts/Editor/retarget_er_fit_candidate.py
  -ERFitCandidate=Steel -nosound

Only new fit assets below /Game/OneBossFight/Player/FitTest/<Candidate> are
created. Batch results are renamed into the candidate root before they are
saved. Existing project assets are never replaced, deleted, or assigned to
gameplay.
Four clips are owner-approved ER imports; quick roll and block loop are clearly
labelled pack control clips because the corresponding ER clips are not imported.
"""

import json
import re

try:
    import unreal
except ImportError:  # Allows offline contract inspection outside the Editor.
    unreal = None


CANDIDATES = {
    "Steel": {
        "mesh": "/Game/ParagonSteel/Characters/Heroes/Steel/Meshes/Steel",
    },
    "Greystone": {
        "mesh": "/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone",
    },
    "Grux": {
        "mesh": "/Game/ParagonGrux/Characters/Heroes/Grux/Meshes/Grux",
    },
}
BLIND_IDS = {"Candidate_A", "Candidate_B", "Candidate_C"}

SOURCE_MESH = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin"
SOURCE_IK_RIG = "/Game/OneBossFight/GreystonePack/IK_CombatMannequin"
DEST_ROOT = "/Game/OneBossFight/Player/FitTest"
CLIPS = [
    {
        "id": "ER-A1",
        "name": "Backstep_Mixamo_V2",
        "path": "/Game/OneBossFight/Player/Animations/AN_ER_Backstep_Mixamo_V2",
        "kind": "owner-approved ER animation",
        "root_distance_cm": [84, 98],
    },
    {
        "id": "ER-A2",
        "name": "Attack_Air_Light",
        "path": "/Game/OneBossFight/Player/Animations/AN_ER_Attack_Air_Light",
        "kind": "owner-approved ER animation",
    },
    {
        "id": "ER-A3",
        "name": "Attack_Air_Heavy_Plunge",
        "path": "/Game/OneBossFight/Player/Animations/AN_ER_Attack_Air_Heavy_Plunge",
        "kind": "owner-approved ER animation",
    },
    {
        "id": "ER-A4",
        "name": "Attack_GuardCounter",
        "path": "/Game/OneBossFight/Player/Animations/AN_ER_Attack_GuardCounter",
        "kind": "owner-approved ER animation",
    },
    {
        "id": "PACK-ROLL",
        "name": "Dodge_Small_Forward_Roll",
        "path": "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll",
        "kind": "pack control; ER roll source is not imported",
        "root_distance_cm": [215, 290],
    },
    {
        "id": "PACK-BLOCK",
        "name": "BlockLoop",
        "path": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Defend/BlockLoop",
        "kind": "pack control; ER block/parry source is not imported",
    },
]


def candidate_from_command_line(command_line):
    match = re.search(r"(?:^|\s)-ERFitCandidate=([A-Za-z]+)(?:\s|$)", command_line)
    if not match or match.group(1) not in CANDIDATES:
        raise ValueError("pass exactly one -ERFitCandidate=Steel|Greystone|Grux")
    return match.group(1)


def blind_id_from_command_line(command_line):
    match = re.search(r"(?:^|\s)-ERFitBlindId=(Candidate_[ABC])(?:\s|$)", command_line)
    if not match:
        raise ValueError("pass exactly one -ERFitBlindId=Candidate_A|Candidate_B|Candidate_C")
    return match.group(1)


def root_displacement_cm(sequence):
    """Measure the source/retarget root endpoints in component space, without root extraction."""
    length = float(sequence.get_play_length())
    start = unreal.AnimationLibrary.get_bone_pose_for_time(sequence, "root", 0.0, False).translation
    end = unreal.AnimationLibrary.get_bone_pose_for_time(sequence, "root", length, False).translation
    return float((end - start).length())


def root_distance_match(source_cm, output_cm):
    """Compare distance within 10%; use a 0.1 cm absolute floor for in-place clips."""
    if source_cm is None or output_cm is None:
        return None, None
    tolerance = max(0.1, abs(source_cm) * 0.10)
    error = abs(output_cm - source_cm)
    percent = None if abs(source_cm) < 0.1 else (error / abs(source_cm)) * 100.0
    return error <= tolerance, percent


def require_asset(path, label):
    asset = unreal.load_asset(path)
    if not asset:
        raise RuntimeError("missing %s asset: %s" % (label, path))
    return asset


def require_new(path):
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        raise RuntimeError("refusing to overwrite existing fit-test asset: " + path)


def expected_output_name(source_asset_name, candidate):
    if not re.fullmatch(r"[A-Za-z0-9_]+", source_asset_name):
        raise ValueError("source animation has an unexpected asset name")
    return source_asset_name + "_Fit_" + candidate


def require_package_under(package_name, root):
    package_name = str(package_name).replace("\\", "/")
    root = root.rstrip("/") + "/"
    if not package_name.startswith(root):
        raise RuntimeError("batch retarget escaped fit-test destination: " + package_name)


def existing_asset_pair_state(rig_exists, retargeter_exists):
    if rig_exists != retargeter_exists:
        raise RuntimeError("fit rig/retargeter pair is partial; preserve it and ask Lead to resolve")
    return bool(rig_exists)


def main():
    command_line = unreal.SystemLibrary.get_command_line()
    candidate = candidate_from_command_line(command_line)
    blind_id = blind_id_from_command_line(command_line)
    root = DEST_ROOT + "/" + candidate
    candidate_mesh = require_asset(CANDIDATES[candidate]["mesh"], "candidate mesh")
    source_mesh = require_asset(SOURCE_MESH, "source mesh")
    source_rig = require_asset(SOURCE_IK_RIG, "source IK rig")
    sources = []
    for clip in CLIPS:
        sequence = require_asset(clip["path"], clip["id"])
        if not isinstance(sequence, unreal.AnimSequence):
            raise RuntimeError("source is not an AnimSequence: " + clip["path"])
        sources.append((clip, sequence))

    # Preflight every destination before creating anything.
    rig_path = root + "/IK_Fit_" + candidate
    retargeter_path = root + "/RTG_ERFit_" + candidate
    manifest_path = root + "/FitManifest_" + blind_id
    if unreal.EditorAssetLibrary.does_asset_exist(manifest_path):
        raise RuntimeError("refusing to overwrite existing fit manifest: " + manifest_path)
    rig_exists = unreal.EditorAssetLibrary.does_asset_exist(rig_path)
    retargeter_exists = unreal.EditorAssetLibrary.does_asset_exist(retargeter_path)
    reuse_pair = existing_asset_pair_state(rig_exists, retargeter_exists)

    tools = unreal.AssetToolsHelpers.get_asset_tools()
    if reuse_pair:
        target_rig = require_asset(rig_path, "existing candidate IK rig")
        retargeter = require_asset(retargeter_path, "existing candidate IK retargeter")
        target_controller = unreal.IKRigController.get_controller(target_rig)
        if target_controller.get_skeletal_mesh().get_path_name() != candidate_mesh.get_path_name():
            raise RuntimeError("existing candidate IK rig mesh mismatch; refusing to mutate")
        controller = unreal.IKRetargeterController.get_controller(retargeter)
        expected_rigs = ((unreal.RetargetSourceOrTarget.SOURCE, source_rig),
                         (unreal.RetargetSourceOrTarget.TARGET, target_rig))
        expected_meshes = ((unreal.RetargetSourceOrTarget.SOURCE, source_mesh),
                           (unreal.RetargetSourceOrTarget.TARGET, candidate_mesh))
        if any(controller.get_ik_rig(side).get_path_name() != rig.get_path_name()
               for side, rig in expected_rigs):
            raise RuntimeError("existing retargeter rig mapping mismatch; refusing to mutate")
        if any(controller.get_preview_mesh(side).get_path_name() != mesh.get_path_name()
               for side, mesh in expected_meshes):
            raise RuntimeError("existing retargeter preview mesh mismatch; refusing to mutate")
    else:
        target_rig = tools.create_asset("IK_Fit_" + candidate, root,
                                        unreal.IKRigDefinition,
                                        unreal.IKRigDefinitionFactory())
        if not target_rig:
            raise RuntimeError("failed to create candidate IK rig")
        target_controller = unreal.IKRigController.get_controller(target_rig)
        target_controller.set_skeletal_mesh(candidate_mesh)
        if not target_controller.apply_auto_generated_retarget_definition():
            raise RuntimeError("failed to generate IK chains for " + candidate)
        unreal.EditorAssetLibrary.save_loaded_asset(target_rig)

        retargeter = tools.create_asset("RTG_ERFit_" + candidate, root,
                                        unreal.IKRetargeter,
                                        unreal.IKRetargetFactory())
        if not retargeter:
            raise RuntimeError("failed to create candidate IK retargeter")
        controller = unreal.IKRetargeterController.get_controller(retargeter)
        controller.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, source_rig)
        controller.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, target_rig)
        controller.set_preview_mesh(unreal.RetargetSourceOrTarget.SOURCE, source_mesh)
        controller.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET, candidate_mesh)
        controller.auto_map_chains(unreal.AutoMapChainType.FUZZY, True)
        unreal.EditorAssetLibrary.save_loaded_asset(retargeter)

    # UE 5.5's exposed duplicate_and_retarget API emits beside its inputs.
    # Its result packages are transient until saved, so move them into the
    # approved candidate root before any output save.
    data = [unreal.EditorAssetLibrary.find_asset_data(clip["path"])
            for clip, _ in sources]
    if any(not item.is_valid() for item in data):
        raise RuntimeError("AssetRegistry lookup failed during source preflight")
    output_names = []
    output_paths = []
    for clip, source in sources:
        source_name = str(source.get_name())
        output_name = expected_output_name(source_name, candidate)
        output_path = root + "/" + output_name
        require_new(output_path)
        output_names.append(output_name)
        output_paths.append(output_path)

    results = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
        data, source_mesh, candidate_mesh, retargeter,
        "", "", "", "_Fit_" + candidate, False)
    if len(results) != len(sources):
        raise RuntimeError("batch returned %d results for %d sources" %
                           (len(results), len(sources)))

    # Batch results may initially be in /Game. Match by source-derived asset
    # name and rename into FitTest; do not save any result until all paths pass.
    by_name = {}
    for item in results:
        asset_name = str(item.asset_name)
        if asset_name in by_name:
            raise RuntimeError("batch returned a duplicate output name: " + asset_name)
        by_name[asset_name] = item
    if set(by_name) != set(output_names):
        raise RuntimeError("batch output names differ from source-derived fit names")
    for output_name, output_path in zip(output_names, output_paths):
        result = by_name[output_name]
        result_source_path = str(result.package_name)
        if not unreal.EditorAssetLibrary.rename_asset(result_source_path, output_path):
            raise RuntimeError("failed to move unsaved batch result into FitTest: " + output_name)

    rows = []
    output_assets = []
    for (clip, source), output_name, output_path in zip(sources, output_names, output_paths):
        output = require_asset(output_path, "retarget output after move")
        require_package_under(output.get_path_name(), root)
        if str(output.get_name()) != output_name:
            raise RuntimeError("renamed output asset name mismatch: " + output_name)
        output_assets.append(output)
        try:
            mannequin_root_cm = root_displacement_cm(source)
            retarget_root_cm = root_displacement_cm(output)
            within_ten_percent, root_error_percent = root_distance_match(
                mannequin_root_cm, retarget_root_cm)
        except Exception as exc:
            mannequin_root_cm = retarget_root_cm = root_error_percent = None
            within_ten_percent = None
            unreal.log_warning("[ERFit] root-distance measurement unavailable for %s: %s" %
                               (clip["id"], str(exc)))
        rows.append({
            "id": clip["id"],
            "name": clip["name"],
            "kind": clip["kind"],
            "source": clip["path"],
            "output": output_path,
            "duration_seconds": float(source.get_play_length()),
            "output_duration_seconds": float(output.get_play_length()),
            "mannequin_root_displacement_cm": mannequin_root_cm,
            "retarget_root_displacement_cm": retarget_root_cm,
            "root_distance_error_percent": root_error_percent,
            "root_distance_within_10_percent": within_ten_percent,
            "visual_scores_0_to_2": {key: None for key in
                                     ("weapon_in_hand", "no_foot_sliding", "no_armour_or_weapon_clipping", "er_knight_silhouette_stance")},
        })
    for output in output_assets:
        unreal.EditorAssetLibrary.save_loaded_asset(output)
    manifest = {
        "schema_version": 1,
        "candidate": candidate,
        "blind_id": blind_id,
        "target_mesh": CANDIDATES[candidate]["mesh"],
        "source_mesh": SOURCE_MESH,
        "retargeter": retargeter_path,
        "scope": "retarget-only; not assigned to gameplay; visual review required",
        "clips": rows,
    }
    filename = unreal.Paths.project_saved_dir() + "ERFit_" + blind_id + ".json"
    with open(filename, "x", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
    unreal.log("[ERFit] CANDIDATE_READY=%s CLIPS=%d MANIFEST=%s" %
               (candidate, len(rows), filename))


if __name__ == "__main__":
    if unreal is None:
        raise RuntimeError("run this script inside the Unreal Editor Python environment")
    main()
