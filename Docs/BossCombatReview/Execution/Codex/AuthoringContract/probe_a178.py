"""Independent targeted probes. Executes Python only, never imports Unreal.

The writer probe uses a tiny recording fake: proof of Python control flow/setter
calls only, NOT Unreal API validity, reflection, asset serialization or gameplay.
"""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import typing
from types import SimpleNamespace
from native_profile_contract import extract_contract

ROOT = Path(__file__).resolve().parents[5]
AG = ROOT / "Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit"


def main():
    spec = importlib.util.spec_from_file_location("a178_pure_core", AG / "authoring_core.py")
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)  # Pure standard-library core, no Unreal import.
    source = (AG / "draft_boss_profiles.py").read_text(encoding="utf-8-sig")
    tree = ast.parse(source)
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                 and node.name in {"validate_boss_profile_data", "execute_draft_apply"}]
    scope = {**vars(typing), **vars(core), "json": json}
    exec(compile(ast.Module(body=functions, type_ignores=[]), "a178_selected_functions", "exec"), scope)
    profiles = json.loads((AG / "examples/boss_draft_profiles.json").read_text())["profiles"]
    evidence = {"scope": __doc__, "inputs": {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in [AG / "authoring_core.py", AG / "draft_boss_profiles.py", AG / "examples/boss_draft_profiles.json"]}}
    validate = scope["validate_boss_profile_data"]
    evidence["baseline_profile"] = validate(copy.deepcopy(profiles[0]), [], [])
    changed = copy.deepcopy(profiles[0])
    changed["phases"][0]["damage_scale"] = float("nan")
    evidence["nan_phase_damage_accepted"] = validate(changed, [], [])[0]
    changed = copy.deepcopy(profiles[0])
    changed["encounter_policy"]["auto_target_player"] = "not-a-bool"
    evidence["invented_policy_invalid_type_accepted"] = validate(changed, [], [])[0]

    # Local UE implementation removes at most ONE leading and ONE trailing quote.
    def native_ascii_normalize(text):
        text = text.strip()
        start = 1 if text.startswith('"') else 0
        end = len(text) - (1 if len(text) > 1 and text.endswith('"') else 0)
        return text[start:end].strip().lower()
    text = '""off""'
    evidence["quote_parity"] = {"input": text, "ue_source_result": native_ascii_normalize(text),
                               "ag_result": core.exact_native_normalize(text)}
    builds = [{"BuildId": name, "Aliases": ["original"]} for name in ["Starter", "Strength", "Dex"]]
    snapshot = core.SourceInventorySnapshot("catalog", 1, [], builds, {"catalog": False})
    builds[0]["Aliases"].append("mutation-after-snapshot")
    after = core.SourceInventorySnapshot("catalog", 1, [], builds, {"catalog": False})
    evidence["nested_source_alias_drift_missed"] = snapshot.compare_with(after)[0]

    # Derive the actual names/style table from current C++ rather than AG constants.
    rules = (ROOT / "Source/OneBossFight/Player/RPGBuildRules.h").read_text()
    rows = re.findall(r'\{ERPGBuild::\w+, TEXT\("([^"]+)"\), TEXT\("([^"]+)"\)', rules)
    builds = [{"BuildId": name, "ConsoleName": name, "DisplayName": name, "UiOrder": i,
               "LegacySlot": i, "WeaponId": name} for i, (name, _) in enumerate(rows)]
    weapons = [{"WeaponId": name, "StyleName": style} for name, style in rows]
    evidence["actual_native_legacy_records"] = {"builds": builds, "weapons": weapons,
        "ag_validation": core.validate_pinned_legacy_contract(builds, weapons)}

    # Real function, recording fake only: enumerate what the current Python writer
    # actually sets and whether it still claims success while omitting typed records.
    class RecordedAsset:
        def __init__(self): self.values = {}
        def set_editor_property(self, key, value): self.values[key] = value
        def get_editor_property(self, key): return self.values[key]
    created = []
    class Tools:
        def create_asset(self, *args):
            value = RecordedAsset()
            created.append(value)
            return value
    tools = Tools()
    fake = SimpleNamespace(
        AssetToolsHelpers=SimpleNamespace(get_asset_tools=lambda: tools),
        load_class=lambda *args: "RecordingFakeClass",
        EditorAssetLibrary=SimpleNamespace(does_asset_exist=lambda _: False),
        DataAssetFactory=RecordedAsset, Name=lambda value: value,
        SoftObjectPath=lambda value: value,
    )
    scope.update(HAS_UNREAL=True, unreal=fake, verify_editor_environment=lambda: (True, ""))
    result = scope["execute_draft_apply"]({"profiles": [copy.deepcopy(profiles[0])]}, False)
    evidence["recording_fake_writer"] = {"returned_success": result,
        "written_fields": sorted(created[0].values),
        "typed_fields_omitted": sorted({"stats", "encounter_policy", "stagger_policy", "phase_flow",
            "fireball", "phase_dependencies", "stagger_profile", "dormant_wake", "phases", "animations", "fields"}
            - created[0].values.keys()), "is_unreal_execution": False}
    contract = extract_contract(ROOT)
    evidence["native_stats_fields"] = list(contract["records"]["FRPGBossStatsConfig"])
    evidence["profile_stats_fields"] = list(profiles[0]["stats"])
    destination = Path(__file__).with_name("a178_probe_results.json")
    destination.write_text(json.dumps(evidence, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2, allow_nan=False))
    return 0  # Probe completed; discovered defects are in the evidence, not passing authoring acceptance.


if __name__ == "__main__":
    raise SystemExit(main())
