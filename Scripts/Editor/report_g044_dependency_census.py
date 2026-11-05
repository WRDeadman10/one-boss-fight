"""Read-only H2 Asset Registry dependency census for G044 selection + drafts.

Reports direct hard/soft dependencies and the transitive combined package
closure, then matches /Game packages against configured DirectoriesToAlwaysCook
roots. It does not save assets, maps, manifests, or reports to disk. Log prefix
[H2_G044_COOK_CENSUS]. Lead must compare the output with the Shipping cook
manifest; this source-side registry view is not itself proof of cooking.
"""
import json
import re
from pathlib import Path
import unreal

PREFIX = "[H2_G044_COOK_CENSUS] "
ROOTS = (
    "/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter",
    "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Boss_EmberWarden_Draft",
    "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Player_Hero_Draft_V3",
)


def package_name(value):
    text = str(value)
    return text.split(".")[0] if text.startswith("/") else text


def dependencies(registry, package, options):
    return sorted({package_name(item) for item in (registry.get_dependencies(package, options) or [])})


def parse_always_cook():
    config_root = Path(unreal.Paths.project_dir()) / "Config"
    rows = []
    pattern = re.compile(r"(?:\+|\.)DirectoriesToAlwaysCook\s*=\s*\(\s*Path\s*=\s*\"([^\"]+)\"", re.I)
    for path in sorted(config_root.rglob("*.ini")):
        try:
            for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                match = pattern.search(line)
                if match:
                    rows.append({"file": path.relative_to(config_root).as_posix(),
                                 "line": number, "path": match.group(1).rstrip("/")})
        except OSError:
            continue
    return rows


registry = unreal.AssetRegistryHelpers.get_asset_registry()
registry.search_all_assets(True)
hard = unreal.AssetRegistryDependencyOptions(include_soft_package_references=False,
    include_hard_package_references=True, include_searchable_names=False,
    include_soft_management_references=False, include_hard_management_references=False)
soft = unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,
    include_hard_package_references=False, include_searchable_names=False,
    include_soft_management_references=False, include_hard_management_references=False)
both = unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,
    include_hard_package_references=True, include_searchable_names=False,
    include_soft_management_references=False, include_hard_management_references=False)
cook_roots = parse_always_cook()
closure_rows, missing_roots = [], []

for root in ROOTS:
    root_assets = registry.get_assets_by_package_name(root) or []
    if not root_assets:
        missing_roots.append(root)
    direct_hard = dependencies(registry, root, hard)
    direct_soft = dependencies(registry, root, soft)
    seen, todo, external = {root}, [root], set()
    while todo:
        current = todo.pop()
        for dep in dependencies(registry, current, both):
            is_content_mount = dep.startswith("/Game/") or (dep.startswith("/") and
                not dep.startswith("/Engine/") and not dep.startswith("/Script/"))
            if is_content_mount:
                if dep not in seen:
                    seen.add(dep)
                    todo.append(dep)
            else:
                external.add(dep)
    cooked_dir_matches = sorted(pkg for pkg in seen if pkg.startswith("/Game/") and any(
        pkg == row["path"] or pkg.startswith(row["path"] + "/") for row in cook_roots))
    closure_rows.append({"root": root,
        "root_asset_present": bool(root_assets),
        "direct_hard": direct_hard, "direct_soft": direct_soft,
        "combined_closure": sorted(seen),
        "non_game_content_packages": sorted(pkg for pkg in seen
            if pkg.startswith("/") and not pkg.startswith("/Game/")
            and not pkg.startswith("/Engine/") and not pkg.startswith("/Script/")),
        "external_dependencies": sorted(external),
        "game_packages_outside_explicit_always_cook": sorted(pkg for pkg in seen
            if pkg.startswith("/Game/") and pkg not in cooked_dir_matches),
        "always_cook_matches": cooked_dir_matches})

report = {"schema": "onebossfight.g044-cook-census/v1", "roots": closure_rows,
          "always_cook_config": cook_roots, "missing_roots": missing_roots,
          "read_only": True,
          "scope_note": "Asset Registry closure is not a cooked-file manifest; validate every dependency against the actual Shipping cook manifest and packaging rules."}
unreal.log(PREFIX + json.dumps(report, sort_keys=True, separators=(",", ":")))
unreal.log(PREFIX + "SUMMARY roots=%d missing=%d always_cook_entries=%d" %
           (len(ROOTS), len(missing_roots), len(cook_roots)))
