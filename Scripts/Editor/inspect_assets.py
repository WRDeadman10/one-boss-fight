"""
Asset pipeline inspection for One Boss Fight (milestone M2).

Reads an asset folder and reports what a character pack actually contains, so we know
whether it can drive the player or the boss BEFORE any gameplay is built on it.

Run headless from the project root:
  UnrealEditor-Cmd.exe OneBossFight.uproject -run=pythonscript ^
      -script=Scripts/Editor/inspect_assets.py -InspectPath=/Game/ParagonGreystone ^
      -unattended -nullrhi

Output:
  Saved/AssetReports/<folder name>.json   full details
  Log lines prefixed [Inspect]            summary and core-animation coverage

Read-only: it loads assets and never modifies or saves them.
"""

import json
import os
import re

import unreal

# Core animations the gameplay needs, matched against animation asset names (case-insensitive).
CORE_BUCKETS = {
    "idle": r"idle|stand",
    "locomotion": r"walk|run|jog|sprint|locomotion|move",
    "dodge": r"dodge|roll|evade|dash|sidestep|backstep",
    "attack": r"attack|combo|slash|swing|strike|slam|smash|sweep|lunge|punch|melee|primary|cleave|swipe",
    "ranged_or_special": r"ability|ult|cast|spell|projectile|shockwave|aoe|leap|charge|rage|summon|beam",
    "hit_react": r"hit|react|flinch|stagger|stun|impact|knock",
    "death": r"death|die|dead|defeat",
    "block": r"block|guard|parry|shield",
    "intro_or_transition": r"intro|spawn|emote|taunt|roar|enter|transform|transition",
}


def log(message):
    unreal.log("[Inspect] " + message)


def get_inspect_path():
    command_line = unreal.SystemLibrary.get_command_line()
    match = re.search(r"-InspectPath=(\S+)", command_line)
    if not match:
        raise RuntimeError("Pass -InspectPath=/Game/SomeFolder on the command line.")
    return match.group(1).strip('"')


def safe_get(obj, name, default=None):
    try:
        return obj.get_editor_property(name)
    except Exception:
        return default


def class_name_of(asset_data):
    try:
        return str(asset_data.asset_class_path.asset_name)
    except Exception:
        return str(asset_data.asset_class)


def describe_anim_sequence(asset):
    info = {
        "name": asset.get_name(),
        "length_s": round(float(asset.get_play_length()), 3),
        "root_motion": bool(safe_get(asset, "enable_root_motion", False)),
        "rate_scale": float(safe_get(asset, "rate_scale", 1.0) or 1.0),
        "additive": str(safe_get(asset, "additive_anim_type", "")),
    }
    try:
        info["notifies"] = sorted({str(n.get_editor_property("notify_name")) for n in asset.get_editor_property("notifies")})
    except Exception:
        info["notifies"] = []
    return info


def describe_montage(asset):
    info = {
        "name": asset.get_name(),
        "length_s": round(float(asset.get_play_length()), 3),
        "sections": [],
        "slots": [],
        "root_motion": bool(safe_get(asset, "enable_root_motion", False)),
    }
    try:
        info["sections"] = [str(s.get_editor_property("section_name")) for s in asset.get_editor_property("composite_sections")]
    except Exception:
        pass
    try:
        info["slots"] = [str(t.get_editor_property("slot_name")) for t in asset.get_editor_property("slot_anim_tracks")]
    except Exception:
        pass
    try:
        info["notifies"] = sorted({str(n.get_editor_property("notify_name")) for n in asset.get_editor_property("notifies")})
    except Exception:
        info["notifies"] = []
    return info


def describe_skeletal_mesh(asset):
    info = {"name": asset.get_name()}
    try:
        bounds = asset.get_bounds()
        extent = bounds.box_extent
        info["size_cm"] = [round(extent.x * 2), round(extent.y * 2), round(extent.z * 2)]
    except Exception:
        pass
    skeleton = safe_get(asset, "skeleton")
    info["skeleton"] = skeleton.get_path_name() if skeleton else None
    try:
        info["bone_count"] = len(skeleton.get_editor_property("bone_tree")) if skeleton else None
    except Exception:
        pass
    try:
        info["lod_count"] = asset.get_num_lods()
    except Exception:
        pass
    try:
        info["material_slots"] = len(asset.get_editor_property("materials"))
    except Exception:
        pass
    return info


def bucket_names(names):
    """Maps each core bucket to the animation names matching it."""
    coverage = {}
    for bucket, pattern in CORE_BUCKETS.items():
        regex = re.compile(pattern, re.IGNORECASE)
        coverage[bucket] = sorted(n for n in names if regex.search(n))
    return coverage


def main():
    root = get_inspect_path()
    log("Inspecting " + root)

    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    registry.scan_paths_synchronous([root], True)
    assets = registry.get_assets_by_path(root, recursive=True)
    log("%d assets found." % len(assets))
    if not assets:
        raise RuntimeError("No assets under " + root + ". Is the pack added to the project?")

    counts = {}
    by_class = {}
    for data in assets:
        cls = class_name_of(data)
        counts[cls] = counts.get(cls, 0) + 1
        by_class.setdefault(cls, []).append(data)

    report = {"root": root, "asset_counts": counts}

    meshes = []
    for data in by_class.get("SkeletalMesh", []):
        meshes.append(describe_skeletal_mesh(data.get_asset()))
    report["skeletal_meshes"] = meshes

    skeletons = sorted({m["skeleton"] for m in meshes if m.get("skeleton")})
    report["skeletons"] = skeletons

    sequences = []
    for data in by_class.get("AnimSequence", []):
        sequences.append(describe_anim_sequence(data.get_asset()))
    report["anim_sequences"] = sequences

    montages = []
    for data in by_class.get("AnimMontage", []):
        montages.append(describe_montage(data.get_asset()))
    report["anim_montages"] = montages

    report["blendspaces"] = sorted(d.get_asset().get_name() for cls in ("BlendSpace", "BlendSpace1D") for d in by_class.get(cls, []))
    report["anim_blueprints"] = sorted(d.get_asset().get_name() for d in by_class.get("AnimBlueprint", []))
    report["niagara_systems"] = sorted(d.asset_name.__str__() for d in by_class.get("NiagaraSystem", []))
    report["sounds"] = counts.get("SoundWave", 0) + counts.get("SoundCue", 0)

    animation_names = [s["name"] for s in sequences] + [m["name"] for m in montages]
    report["core_coverage"] = bucket_names(animation_names)

    root_motion_anims = [s["name"] for s in sequences if s["root_motion"]]
    report["root_motion_sequences"] = root_motion_anims

    out_dir = os.path.join(unreal.SystemLibrary.get_project_saved_directory(), "AssetReports")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, root.strip("/").replace("/", "_") + ".json")
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    log("Asset counts: %s" % counts)
    for mesh in meshes:
        log("Mesh %s size_cm=%s bones=%s lods=%s skeleton=%s" % (
            mesh["name"], mesh.get("size_cm"), mesh.get("bone_count"), mesh.get("lod_count"), mesh.get("skeleton")))
    log("Anim sequences: %d (root motion on %d), montages: %d, blendspaces: %d, anim BPs: %s" % (
        len(sequences), len(root_motion_anims), len(montages), len(report["blendspaces"]), report["anim_blueprints"]))
    for bucket, names in report["core_coverage"].items():
        log("  %-20s %d  %s" % (bucket, len(names), ", ".join(names[:8]) + (" ..." if len(names) > 8 else "")))
    log("Report: " + out_path)


main()
