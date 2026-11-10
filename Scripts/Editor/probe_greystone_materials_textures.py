"""Read-only guarded probe for the Greystone materials and textures used by BP_GreystoneERPlayer.

Lead-run Editor script (`BB-A15`). Strictly read-only: never modifies, creates, saves,
or deletes any asset. Falls back gracefully with clear refusal/status messages if run
outside UE or if `BP_GreystoneERPlayer` has not been authored yet.
"""

from __future__ import annotations

import json
from pathlib import Path

try:
    import unreal
except ImportError:
    unreal = None

PREFIX = "[GreystoneMatProbe] "
CHILD_BP_PATH = "/Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer"
PARENT_BP_PATH = "/Game/OneBossFight/GreystonePack/BP_GreystonePlayer"
EXPECTED_DEFAULT_MESH_PATH = "/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone"
MINIMAL_TEXTURE_ALLOWLIST_PREFIX = "/Game/ParagonGreystone/Characters/Heroes/Greystone/"
REPORT_REL_PATH = Path("Saved") / "BossCombatReview" / "bb_a15_greystone_materials_probe.json"


def _log(msg: str) -> None:
    if unreal is not None:
        unreal.log(PREFIX + msg)
    else:
        print(PREFIX + msg)


def _object_path(obj) -> str | None:
    if obj is None:
        return None
    try:
        return str(obj.get_path_name())
    except Exception:
        return str(obj)


def _package_name(obj_path: str | None) -> str | None:
    if not obj_path:
        return None
    return obj_path.split(".", 1)[0]


def _collect_mesh_materials(mesh_obj) -> list[dict]:
    slots = []
    if mesh_obj is None:
        return slots
    try:
        mat_slots = mesh_obj.get_editor_property("materials")
    except Exception:
        mat_slots = []
    for index, entry in enumerate(mat_slots or []):
        try:
            slot_name = str(entry.get_editor_property("material_slot_name"))
            mat_if = entry.get_editor_property("material_interface")
        except Exception:
            slot_name = f"slot_{index}"
            mat_if = None
        slots.append({
            "index": index,
            "slot_name": slot_name,
            "material_path": _object_path(mat_if),
        })
    return slots


def _collect_used_textures(mat_obj) -> list[str]:
    if mat_obj is None or unreal is None:
        return []
    if not hasattr(unreal, "MaterialEditingLibrary") or not hasattr(unreal.MaterialEditingLibrary, "get_used_textures"):
        return []
    try:
        textures = unreal.MaterialEditingLibrary.get_used_textures(mat_obj) or []
    except Exception as exc:
        _log(f"WARN get_used_textures failed for {_object_path(mat_obj)}: {exc}")
        return []
    return sorted({p for p in (_object_path(t) for t in textures) if p})


def _collect_package_dependencies(package_path: str) -> dict[str, list[str]]:
    if unreal is None or not package_path:
        return {"hard": [], "soft": []}
    try:
        registry = unreal.AssetRegistryHelpers.get_asset_registry()
        opts_hard = unreal.AssetRegistryDependencyOptions(
            include_soft_package_references=False,
            include_hard_package_references=True,
            include_searchable_names=False,
            include_soft_management_references=False,
            include_hard_management_references=False,
        )
        opts_soft = unreal.AssetRegistryDependencyOptions(
            include_soft_package_references=True,
            include_hard_package_references=False,
            include_searchable_names=False,
            include_soft_management_references=False,
            include_hard_management_references=False,
        )
        hard = sorted(str(x) for x in (registry.get_dependencies(package_path, opts_hard) or []))
        soft = sorted(str(x) for x in (registry.get_dependencies(package_path, opts_soft) or []))
        return {"hard": hard, "soft": soft}
    except Exception as exc:
        _log(f"WARN dependency lookup failed for {package_path}: {exc}")
        return {"hard": [], "soft": []}


def inspect_blueprint_materials(bp_path: str) -> dict:
    """Read-only inspection of Blueprint skeletal/static mesh materials & used textures."""
    result = {
        "blueprint_path": bp_path,
        "exists": False,
        "cdo_mesh_path": None,
        "override_materials": [],
        "mesh_slots": [],
        "unique_materials": [],
        "unique_textures": [],
        "non_greystone_textures": [],
        "blueprint_dependencies": {"hard": [], "soft": []},
    }
    if unreal is None:
        return result
    if not unreal.EditorAssetLibrary.does_asset_exist(bp_path):
        _log(f"MISSING Blueprint asset (read-only skip): {bp_path}")
        return result

    bp = unreal.load_asset(bp_path)
    if bp is None or not hasattr(bp, "generated_class"):
        _log(f"WARN failed to load Blueprint generated_class for {bp_path}")
        return result

    result["exists"] = True
    cdo = unreal.get_default_object(bp.generated_class())
    mesh_comp = cdo.get_editor_property("mesh") if cdo is not None else None
    skel_mesh = mesh_comp.get_editor_property("skeletal_mesh_asset") if mesh_comp is not None and hasattr(mesh_comp, "get_editor_property") else None
    if skel_mesh is None and mesh_comp is not None:
        try:
            skel_mesh = mesh_comp.get_editor_property("skeletal_mesh")
        except Exception:
            skel_mesh = None

    overrides = []
    if mesh_comp is not None:
        try:
            overrides = [_object_path(x) for x in (mesh_comp.get_editor_property("override_materials") or [])]
        except Exception:
            overrides = []

    result["cdo_mesh_path"] = _object_path(skel_mesh)
    result["override_materials"] = overrides
    mesh_slots = _collect_mesh_materials(skel_mesh)
    result["mesh_slots"] = mesh_slots

    effective_mat_paths = []
    for idx, slot in enumerate(mesh_slots):
        override_path = overrides[idx] if idx < len(overrides) and overrides[idx] else None
        effective_mat_paths.append(override_path or slot["material_path"])
    for extra in overrides[len(mesh_slots):]:
        if extra:
            effective_mat_paths.append(extra)

    unique_mats = sorted({p for p in effective_mat_paths if p})
    result["unique_materials"] = unique_mats

    all_textures = set()
    for mat_path in unique_mats:
        mat_obj = unreal.load_asset(_package_name(mat_path))
        for tex_path in _collect_used_textures(mat_obj):
            all_textures.add(tex_path)
    result["unique_textures"] = sorted(all_textures)
    result["non_greystone_textures"] = sorted(
        t for t in all_textures if not t.startswith(MINIMAL_TEXTURE_ALLOWLIST_PREFIX)
    )
    result["blueprint_dependencies"] = _collect_package_dependencies(_package_name(bp_path))
    return result


def run_probe(write_report: bool = True) -> dict:
    """Execute read-only material/texture probe on child and parent Greystone Blueprints."""
    if unreal is None:
        raise RuntimeError("Run inside UE 5.5 Editor Python environment (-nosound / Editor CLI).")

    child_info = inspect_blueprint_materials(CHILD_BP_PATH)
    parent_info = inspect_blueprint_materials(PARENT_BP_PATH)
    payload = {
        "child_bp": child_info,
        "parent_bp": parent_info,
        "expected_default_mesh_path": EXPECTED_DEFAULT_MESH_PATH,
        "read_only": True,
    }
    _log(
        f"child_exists={child_info['exists']} child_mats={len(child_info['unique_materials'])} "
        f"child_textures={len(child_info['unique_textures'])} parent_exists={parent_info['exists']} "
        f"parent_mats={len(parent_info['unique_materials'])} parent_textures={len(parent_info['unique_textures'])}"
    )

    if write_report:
        proj_dir = Path(unreal.Paths.project_dir()).resolve()
        out_path = proj_dir / REPORT_REL_PATH
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        _log(f"wrote report: {out_path}")
    return payload


if __name__ == "__main__":
    if unreal is not None:
        run_probe(write_report=True)
    else:
        _log("SKIP: not running inside UE Python interpreter (read-only offline import ok).")
