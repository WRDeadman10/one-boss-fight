"""Read-only CDO snapshot for authored encounter-definition inputs.

Run in the UE Editor. Writes one new timestamped JSON under Saved/G044 and never
loads a level, changes an asset, or saves a package. CDO component values are
evidence about defaults only; the output deliberately labels that scope.
"""
import hashlib
import json
import os
import time

import unreal


ROOTS = {
    "boss": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss",
    "player": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter",
}
OUT_DIR = os.path.join(unreal.Paths.project_saved_dir(), "G044", "source_snapshots")


def require(condition, message):
    if not condition:
        raise RuntimeError("[G044SourceSnapshot] REFUSED: " + message)


def stable_value(value):
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple)):
        return [stable_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): stable_value(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    path = getattr(value, "get_path_name", None)
    if callable(path):
        try:
            return {"object_path": str(path())}
        except Exception:
            pass
    try:
        return str(value)
    except Exception:
        return {"unreadable_type": type(value).__name__}


def read_properties(obj):
    values = {}
    errors = {}
    for name in sorted(set(dir(obj))):
        if name.startswith("_") or name in ("class", "outer"):
            continue
        try:
            value = obj.get_editor_property(name)
        except Exception:
            continue
        if callable(value):
            continue
        values[name] = stable_value(value)
    return values, errors


def blueprint_snapshot(role, package_path):
    blueprint = unreal.EditorAssetLibrary.load_asset(package_path)
    require(blueprint is not None, "missing " + role + " Blueprint: " + package_path)
    generated = blueprint.generated_class()
    require(generated is not None, "generated class missing: " + package_path)
    cdo = unreal.get_default_object(generated)
    require(cdo is not None, "class default object missing: " + package_path)
    components = []
    for component in sorted(cdo.get_components_by_class(unreal.ActorComponent), key=lambda item: item.get_name()):
        values, _ = read_properties(component)
        components.append({
            "name": component.get_name(),
            "class": component.get_class().get_name(),
            "properties": values,
        })
    actor_values, _ = read_properties(cdo)
    return {
        "role": role,
        "blueprint_asset": blueprint.get_path_name(),
        "generated_class": generated.get_path_name(),
        "snapshot_scope": "class_default_object; not runtime-mutated instance state",
        "actor_properties": actor_values,
        "components": components,
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    output = os.path.join(OUT_DIR, "encounter_sources_" + stamp + ".json")
    require(not os.path.exists(output), "snapshot path already exists: " + output)
    payload = {
        "schema": "onebossfight.encounter-source-snapshot/v1",
        "created_utc": stamp,
        "source_note": "Reflected Blueprint CDO values only; not proof of runtime instance values or permission to copy defaults into gameplay data.",
        "sources": {role: blueprint_snapshot(role, path) for role, path in ROOTS.items()},
    }
    raw = (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")
    with open(output, "xb") as stream:
        stream.write(raw)
    digest = hashlib.sha256(raw).hexdigest()
    unreal.log("[G044SourceSnapshot] PASS file=%s sha256=%s" % (output, digest))


main()
