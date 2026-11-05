"""Read-only preflight for Claude-authorized saved G044 definition drafts.

Loads the exact boss/player Data Assets, verifies their reflected class and every
field consumed by the encounter pipeline, prints stable field readbacks, and
pins package/evidence bytes. It never writes or saves assets or files.
"""
import hashlib
import json
import sys
from pathlib import Path

import unreal

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import ue_editor_values


ASSETS = {
    "boss": "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Boss_EmberWarden_Draft",
    "player": "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Player_Hero_Draft_V3",
}
EXPECTED_CLASS = "/Script/OneBossFight.RPGBossDefinition"
FIELDS = (
    "schema", "definition_id", "presentation_id", "stats", "encounter_policy",
    "stagger_policy", "phase_flow", "fireball", "phase_dependencies", "stagger_profile",
    "dormant_wake", "bleed", "low_sweep", "shockwave", "heal_punish", "look",
    "close_clip_swap", "death", "attack_tracker", "phases", "skeleton", "animations", "fields",
)
DD27J_EVIDENCE = Path("Docs/BossCombatReview/Execution/Claude/F3a/full2_raw.log")
ERRORS = []


def stable_value(value, where):
    return ue_editor_values.stable_value(value, unreal, where)


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def package_file(project_root, package_path):
    if not package_path.startswith("/Game/"):
        raise ValueError("asset package is outside /Game: " + package_path)
    path = (project_root / "Content" / (package_path[len("/Game/"):] + ".uasset")).resolve(strict=True)
    path.relative_to(project_root.resolve())
    return path


def inspect(role, package_path, expected_class, project_root):
    asset = unreal.EditorAssetLibrary.load_asset(package_path)
    if asset is None:
        ERRORS.append(role + " asset failed to load: " + package_path)
        unreal.log_error("[G044DraftPreflight] FAIL role=%s asset=%s" % (role, package_path))
        return None
    actual_class = str(asset.get_class().get_path_name())
    unreal.log("[G044DraftPreflight] CLASS role=%s expected=%s actual=%s" %
               (role, EXPECTED_CLASS, actual_class))
    # Lead fix: unreal.load_class returns a UClass object, not a Python type, so isinstance() cannot take it.
    if actual_class != str(expected_class.get_path_name()) and not asset.get_class().is_child_of(expected_class):
        ERRORS.append(role + " has incompatible class " + actual_class)
    if str(asset.get_path_name()) != package_path + "." + package_path.rsplit("/", 1)[-1]:
        ERRORS.append(role + " loaded object path does not match requested package")
    values = {}
    for field in FIELDS:
        try:
            values[field] = stable_value(asset.get_editor_property(field), role + "." + field)
            unreal.log("[G044DraftPreflight] FIELD role=%s name=%s value=%s" %
                       (role, field, json.dumps(values[field], ensure_ascii=False, sort_keys=True, allow_nan=False)))
        except Exception as exc:
            ERRORS.append(role + " missing/unreadable field " + field + ": " + str(exc))
            unreal.log_error("[G044DraftPreflight] FIELD role=%s name=%s MISSING error=%s" %
                             (role, field, str(exc)))
    for field in ("definition_id", "presentation_id", "phases", "skeleton", "animations", "fields"):
        if field in values and values[field] in (None, "", []):
            ERRORS.append(role + " required field is empty: " + field)
    if role == "boss" and "phases" in values:
        phase_ids = []
        try:
            for phase in asset.get_editor_property("phases"):
                phase_ids.append(str(phase.get_editor_property("phase_id")))
        except Exception as exc:
            ERRORS.append("boss phase IDs unreadable: " + str(exc))
        unreal.log("[G044DraftPreflight] PHASES role=boss ids=%s" % json.dumps(phase_ids))
        if not phase_ids or any(not phase_id for phase_id in phase_ids):
            ERRORS.append("boss draft phase list must contain nonempty phase IDs")
    try:
        file_path = package_file(project_root, package_path)
        unreal.log("[G044DraftPreflight] PACKAGE role=%s path=%s sha256=%s" %
                   (role, str(file_path), sha256(file_path)))
    except Exception as exc:
        ERRORS.append(role + " package bytes unavailable: " + str(exc))
    return asset


def main():
    project_root = Path(unreal.Paths.project_dir()).resolve()
    expected_class = unreal.load_class(None, EXPECTED_CLASS)
    if expected_class is None:
        ERRORS.append("encounter-required class unavailable: " + EXPECTED_CLASS)
    else:
        inspect("boss", ASSETS["boss"], expected_class, project_root)
        inspect("player", ASSETS["player"], expected_class, project_root)
    try:
        evidence_path = (project_root / DD27J_EVIDENCE).resolve(strict=True)
        evidence_path.relative_to(project_root)
        unreal.log("[G044DraftPreflight] DD27J_EVIDENCE path=%s sha256=%s" %
                   (str(DD27J_EVIDENCE).replace("\\", "/"), sha256(evidence_path)))
    except Exception as exc:
        ERRORS.append("DD27j compile evidence unavailable: " + str(exc))
    if ERRORS:
        for error in ERRORS:
            unreal.log_error("[G044DraftPreflight] REFUSED reason=" + error)
        raise RuntimeError("[G044DraftPreflight] REFUSED with %d error(s); no assets/files were written" % len(ERRORS))
    unreal.log("[G044DraftPreflight] PASS roles=2 fields_per_role=%d writes=0" % len(FIELDS))


main()
