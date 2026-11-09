"""Create the two NEW typed boss/player definitions needed by G044.

Refuses overwrite. The spec module is produced only after Editor readback and
must explicitly provide every URPGBossDefinition field plus source provenance.
No defaults are promoted, no map is loaded, and no package is saved until both
new assets pass all readback assertions.
"""
import importlib.util
import hashlib
import json
import math
import re
from pathlib import Path

import unreal


PACKAGE_DIR = "/Game/OneBossFight/Data"
SPECS_PATH = Path(unreal.Paths.project_saved_dir()) / "G044" / "typed_definition_specs.py"
TARGETS = {
    "boss": ("DA_Sevarog_G044_BossDefinition", True),
    "player": ("DA_Sevarog_G044_PlayerDefinition", False),
}
TOP_LEVEL_FIELDS = {
    "Schema", "DefinitionId", "PresentationId", "PhaseTwoAuraEffect", "Stats", "EncounterPolicy",
    "StaggerPolicy", "PhaseFlow", "Fireball", "PhaseDependencies",
    "StaggerProfile", "DormantWake", "Bleed", "LowSweep", "Shockwave",
    "HealPunish", "Look", "CloseClipSwap", "Death", "AttackTracker", "Phases", "Skeleton",
    "Animations", "Fields",
}


def require(condition, message):
    if not condition:
        raise RuntimeError("[G044Definitions] REFUSED: " + message)


def property_name(name):
    name = name.replace("SHA256", "Sha256")
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def spec_leaf_paths(value, prefix):
    if isinstance(value, list):
        for index, item in enumerate(value):
            for path in spec_leaf_paths(item, prefix + "[" + str(index) + "]"):
                yield path
        return
    if isinstance(value, dict) and "$struct" in value:
        descriptor = value["$struct"]
        require(isinstance(descriptor, dict), prefix + " struct encoding must be an object")
        fields = descriptor.get("fields")
        require(isinstance(fields, dict), prefix + " struct fields must be an object")
        for name, item in fields.items():
            require(isinstance(name, str) and name, prefix + " struct field names must be nonempty text")
            for path in spec_leaf_paths(item, prefix + "." + name):
                yield path
        return
    yield prefix


def load_specs():
    require(SPECS_PATH.is_file(), "Editor-readback spec module missing: " + str(SPECS_PATH))
    spec = importlib.util.spec_from_file_location("g044_typed_definition_specs", SPECS_PATH)
    require(spec is not None and spec.loader is not None, "could not load the source spec module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    values = {"boss": getattr(module, "BOSS_SPEC", None), "player": getattr(module, "PLAYER_SPEC", None)}
    cited_hashes = set()
    for role, value in values.items():
        require(isinstance(value, dict), role + " spec must be a dict")
        require(isinstance(value.get("source_snapshot_sha256"), str) and
                re.fullmatch(r"[0-9a-f]{64}", value["source_snapshot_sha256"]) is not None,
                role + " spec must cite a lowercase Editor snapshot SHA-256")
        cited_hashes.add(value["source_snapshot_sha256"])
        properties = value.get("properties")
        require(isinstance(properties, dict), role + " properties must be an object")
        require(set(properties) == TOP_LEVEL_FIELDS,
                role + " properties must set every URPGBossDefinition field explicitly")
        expected_sources = set()
        for name, item in properties.items():
            if name not in ("Schema", "Fields"):
                expected_sources.update(spec_leaf_paths(item, name))
        field_sources = value.get("field_sources", {})
        require(isinstance(field_sources, dict), role + " field_sources must be an object")
        require(set(field_sources) == expected_sources,
                role + " source citations must cover every nested value and no extras")
        for path, source in field_sources.items():
            require(isinstance(source, dict) and isinstance(source.get("path"), str) and
                    bool(source["path"].strip()) and type(source.get("line")) is int and source["line"] > 0,
                    role + " has no path/line source citation for " + path)
    require(len(cited_hashes) == 1,
            "boss and player specs must cite the same current source snapshot")
    snapshot_dir = SPECS_PATH.parent / "source_snapshots"
    snapshots = sorted(snapshot_dir.glob("encounter_sources_*.json"))
    require(snapshots, "no Editor source snapshots exist")
    latest = snapshots[-1]
    snapshot_bytes = latest.read_bytes()
    latest_digest = hashlib.sha256(snapshot_bytes).hexdigest()
    require(latest_digest in cited_hashes,
            "spec provenance does not match the newest timestamped source snapshot")
    try:
        snapshot = json.loads(snapshot_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("[G044Definitions] REFUSED: newest source snapshot is invalid JSON: " + str(exc))
    require(isinstance(snapshot, dict), "newest source snapshot root must be an object")
    sources = snapshot.get("sources")
    require(snapshot.get("schema") == "onebossfight.encounter-source-snapshot/v1" and
            isinstance(sources, dict) and set(sources) == {"boss", "player"},
            "newest source snapshot has an unexpected schema or source inventory")
    require(str(values["boss"]["properties"]["DefinitionId"]).strip(), "boss DefinitionId is empty")
    require(str(values["player"]["properties"]["DefinitionId"]).strip(), "player DefinitionId is empty")
    return values


def materialize(value, where):
    if isinstance(value, list):
        return [materialize(item, where + "[]") for item in value]
    if isinstance(value, dict):
        require(len(value) == 1, where + " tagged value must have exactly one type key")
        if "$soft_object" in value:
            path = value["$soft_object"]
            require(isinstance(path, str) and path, where + " soft-object path missing")
            asset = unreal.EditorAssetLibrary.load_asset(path)
            require(asset is not None, where + " soft-object reference does not resolve: " + path)
            return unreal.SoftObjectPath(asset.get_path_name())
        if "$soft_class" in value:
            path = value["$soft_class"]
            require(isinstance(path, str) and path, where + " soft-class path missing")
            loaded = unreal.load_class(None, path)
            require(loaded is not None, where + " soft-class reference does not resolve: " + path)
            return unreal.SoftObjectPath(path)
        if "$struct" in value:
            descriptor = value["$struct"]
            require(isinstance(descriptor, dict) and set(descriptor) == {"type", "fields"},
                    where + " struct encoding requires type and fields")
            require(isinstance(descriptor["type"], str) and descriptor["type"],
                    where + " struct type must be nonempty text")
            require(isinstance(descriptor["fields"], dict), where + " struct fields must be an object")
            struct_type = getattr(unreal, descriptor["type"], None)
            require(struct_type is not None, where + " reflected struct type missing: " + str(descriptor["type"]))
            struct_value = struct_type()
            for name, item in descriptor["fields"].items():
                struct_value.set_editor_property(name, materialize(item, where + "." + name))
            return struct_value
        if "$enum" in value:
            descriptor = value["$enum"]
            require(isinstance(descriptor, dict) and set(descriptor) == {"type", "value"},
                    where + " enum encoding requires type and value")
            require(isinstance(descriptor["type"], str) and descriptor["type"] and
                    isinstance(descriptor["value"], str) and descriptor["value"],
                    where + " enum type and value must be nonempty text")
            enum_type = getattr(unreal, descriptor["type"], None)
            require(enum_type is not None and hasattr(enum_type, descriptor["value"]),
                    where + " reflected enum value missing")
            return getattr(enum_type, descriptor["value"])
        raise RuntimeError("[G044Definitions] REFUSED: unsupported tagged value at " + where)
    if isinstance(value, float):
        require(math.isfinite(value), where + " is non-finite")
    require(value is None or isinstance(value, (str, int, float, bool)),
            where + " must be a JSON-like scalar, list, or explicit Unreal tagged value")
    return value


def preflight(values, definition_class):
    require(definition_class is not None, "URPGBossDefinition class unavailable")
    for role, (asset_name, boss_role) in TARGETS.items():
        asset_path = PACKAGE_DIR + "/" + asset_name
        require(not unreal.EditorAssetLibrary.does_asset_exist(asset_path),
                "target already exists; never overwrite: " + asset_path)
        props = values[role]["properties"]
        require(int(props["Schema"]) == 1, role + " schema must equal 1")
        require(str(props["DefinitionId"]).strip() and str(props["PresentationId"]).strip(),
                role + " IDs must be nonempty")
        require(bool(props["Phases"]), role + " phase array is empty")
        require(isinstance(props["Skeleton"], dict) and bool(props["Skeleton"].get("$soft_object")),
                role + " skeleton is not an explicit soft-object path")
        require(bool(props["Animations"]), role + " animation array is empty")
        require(bool(props["Fields"]), role + " source-field manifest is empty")
        if boss_role:
            phase_ids = [str(entry.get("$struct", {}).get("fields", {}).get("phase_id", ""))
                         for entry in props["Phases"] if isinstance(entry, dict)]
            require("PhaseOne" in phase_ids, "boss must explicitly declare selected PhaseOne")
        for name, item in props.items():
            materialize(item, role + "." + name)  # resolve every reference before creating either asset
        for index, encoded in enumerate(props["Fields"]):
            fields = encoded.get("$struct", {}).get("fields", {}) if isinstance(encoded, dict) else {}
            required_metadata = ("field_path", "type", "source_path", "source_sha256", "source_site",
                                 "origin", "precedence", "destination", "first_read", "witness")
            require(all(fields.get(key) for key in required_metadata),
                    role + " Fields[" + str(index) + "] lacks required provenance")
            require(re.fullmatch(r"[0-9a-fA-F]{64}", str(fields["source_sha256"])) is not None,
                    role + " Fields[" + str(index) + "] source hash is not SHA-256")


def populate(asset, properties):
    for name, encoded in properties.items():
        value = materialize(encoded, "asset." + name)
        asset.set_editor_property(property_name(name), value)
    for name, encoded in properties.items():
        actual = asset.get_editor_property(property_name(name))
        require(equivalent(actual, encoded, "readback." + name),
                "readback differs from authored value for " + name)


def equivalent(actual, encoded, where):
    """Compare reflected property readbacks to the full authored encoding."""
    if actual is None:
        return encoded is None
    if isinstance(encoded, list):
        return isinstance(actual, (list, tuple)) and len(actual) == len(encoded) and all(
            equivalent(actual[index], item, where + "[" + str(index) + "]")
            for index, item in enumerate(encoded))
    if isinstance(encoded, dict):
        if "$struct" in encoded:
            descriptor = encoded["$struct"]
            try:
                return all(equivalent(actual.get_editor_property(name), item,
                                      where + "." + name)
                           for name, item in descriptor["fields"].items())
            except Exception:
                return False
        if "$enum" in encoded:
            descriptor = encoded["$enum"]
            expected = getattr(getattr(unreal, descriptor["type"], None), descriptor["value"], None)
            if expected is None:
                return False
            actual_value = getattr(actual, "value", None)
            expected_value = getattr(expected, "value", None)
            if actual_value is not None and expected_value is not None:
                return actual_value == expected_value
            return actual == expected
        if "$soft_object" in encoded or "$soft_class" in encoded:
            expected = materialize(encoded, where)
            def path_text(value):
                for method_name in ("to_string", "get_path_name"):
                    method = getattr(value, method_name, None)
                    if callable(method):
                        try:
                            return str(method())
                        except Exception:
                            pass
                return str(value)
            return path_text(actual) == path_text(expected)
        return False
    if isinstance(encoded, float):
        try:
            return math.isfinite(float(actual)) and math.isclose(
                float(actual), encoded, rel_tol=1e-7, abs_tol=1e-7)
        except (TypeError, ValueError):
            return False
    if isinstance(encoded, bool):
        return isinstance(actual, bool) and actual is encoded
    if isinstance(encoded, (str, int)):
        return str(actual) == str(encoded)
    return actual == encoded


def main():
    values = load_specs()
    definition_class = unreal.load_class(None, "/Script/OneBossFight.RPGBossDefinition")
    factory_class = unreal.DataAssetFactory
    preflight(values, definition_class)
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    created = {}
    for role, (asset_name, _) in TARGETS.items():
        asset = tools.create_asset(asset_name, PACKAGE_DIR, definition_class, factory_class())
        require(asset is not None and isinstance(asset, definition_class), "asset creation failed for " + role)
        populate(asset, values[role]["properties"])
        created[role] = asset
    require(created["boss"].get_path_name() != created["player"].get_path_name(),
            "boss and player definitions must be separate assets")
    # The two new assets are saved only after both have complete asserted readbacks.
    for role in ("boss", "player"):
        require(unreal.EditorAssetLibrary.save_loaded_asset(created[role]), "save failed for " + role)
        unreal.log("[G044Definitions] PASS role=%s asset=%s source_snapshot_sha256=%s" %
                   (role, created[role].get_path_name(), values[role]["source_snapshot_sha256"]))


main()
