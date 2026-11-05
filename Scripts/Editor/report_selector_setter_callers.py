"""Read-only Shipping selector caller census. Run in the UE Editor.

Scans standalone Blueprint graphs and level-script Blueprint graphs exposed by
loaded map assets for SetSelectedDefinition K2 call nodes. No assets are saved
or modified. A report is an inventory aid; packaged Shipping behavior is a
separate proof gate. Log prefix [H1_SELECTOR_CALLERS].
"""
import json
from pathlib import Path
import unreal

PREFIX = "[H1_SELECTOR_CALLERS] "
TARGET = "SetSelectedDefinition"


def prop(obj, name, default=None):
    try:
        return obj.get_editor_property(name)
    except Exception:
        return default


def asset_path(data):
    package = str(prop(data, "package_name", ""))
    name = str(prop(data, "asset_name", ""))
    if package and name:
        return package + "." + name
    value = prop(data, "object_path")
    return str(value).split(" ")[0] if value is not None else ""


def graphs(blueprint):
    found = []
    for field in ("ubergraph_pages", "function_graphs", "macro_graphs"):
        value = prop(blueprint, field, []) or []
        found.extend((field, graph) for graph in value)
    return found


registry = unreal.AssetRegistryHelpers.get_asset_registry()
registry.search_all_assets(True)
assets = registry.get_assets_by_path("/Game", recursive=True) or []
hits, scanned, unsupported, errors = [], 0, [], []

for data in assets:
    path = asset_path(data)
    if not path:
        continue
    class_name = str(prop(prop(data, "asset_class_path"), "asset_name", ""))
    if class_name not in ("Blueprint", "WidgetBlueprint", "LevelScriptBlueprint", "World"):
        continue
    try:
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if asset is None:
            errors.append({"asset": path, "error": "load returned None"})
            continue
        blueprints = []
        if class_name == "World":
            level = prop(asset, "persistent_level")
            level_bp = prop(level, "level_script_blueprint") if level else None
            if level_bp:
                blueprints.append(("level_script", level_bp))
            else:
                unsupported.append(path + " (level script Blueprint not exposed by loaded World/Level API)")
        else:
            blueprints.append(("asset_blueprint", asset))

        for bp_kind, blueprint in blueprints:
            graph_rows = graphs(blueprint)
            if not graph_rows:
                unsupported.append(path + " (no graph properties exposed)")
            for graph_kind, graph in graph_rows:
                nodes = prop(graph, "nodes", []) or []
                scanned += 1
                for node in nodes:
                    if "K2Node_CallFunction" not in node.get_class().get_name():
                        continue
                    ref = prop(node, "function_reference")
                    member = str(prop(ref, "member_name", "")) if ref else ""
                    if member != TARGET:
                        continue
                    parent = prop(ref, "member_parent") if ref else None
                    hits.append({"asset": path, "blueprint_kind": bp_kind,
                                 "graph_kind": graph_kind, "graph": graph.get_name(),
                                 "node": node.get_name(), "member": member,
                                 "member_parent": str(parent) if parent else ""})
    except Exception as error:
        errors.append({"asset": path, "error": repr(error)})

# Unreal 5.5 Python does not expose Blueprint graph nodes in this project
# session. Keep the Asset Registry graph scan as the primary mode, and always
# run a separate read-only serialized-package byte search as a fallback. A
# byte-search hit is a candidate reference (manual verify); zero hits are not
# represented as a successful graph scan.
content_root = Path(unreal.Paths.project_dir()) / "Content"
patterns = {"utf8": TARGET.encode("utf-8"),
            "utf16_le": TARGET.encode("utf-16-le"),
            "utf16_be": TARGET.encode("utf-16-be")}
byte_hits, files_checked, byte_errors = [], 0, []
if content_root.is_dir():
    for package_file in sorted(content_root.rglob("*")):
        if package_file.suffix.lower() not in (".uasset", ".umap"):
            continue
        try:
            contents = package_file.read_bytes()
            files_checked += 1
            encodings = [name for name, needle in patterns.items() if needle in contents]
            if encodings:
                byte_hits.append({"asset": package_file.relative_to(content_root).as_posix(),
                                  "encodings": encodings})
        except OSError as error:
            byte_errors.append({"asset": str(package_file), "error": repr(error)})
else:
    byte_errors.append({"asset": str(content_root), "error": "Content directory missing"})

graph_complete = scanned > 0 and not unsupported and not errors
graph_verdict = ("CALLERS_FOUND" if hits else "COMPLETE_NO_CALLERS") if graph_complete else "INCONCLUSIVE"
byte_verdict = "CANDIDATE_REFERENCES_FOUND" if byte_hits else ("NO_MATCHES" if not byte_errors else "INCONCLUSIVE")
if hits or byte_hits:
    overall_verdict = "CANDIDATE_REFERENCES_FOUND_REVIEW"
elif graph_verdict == "COMPLETE_NO_CALLERS":
    overall_verdict = "NO_CALLERS_FOUND"
else:
    overall_verdict = "INCONCLUSIVE"

report = {"schema": "onebossfight.shipping-selector-callers/v1",
          "target_function": TARGET, "registry_assets": len(assets),
          "graphs_scanned": scanned, "callers": hits,
          "unsupported": unsupported, "errors": errors,
          "graph_verdict": graph_verdict,
          "byte_search": {"files_checked": files_checked, "hits": byte_hits,
                          "errors": byte_errors, "verdict": byte_verdict},
          "overall_verdict": overall_verdict,
          "read_only": True,
          "scope_note": "No asset writes. Graph scan is complete only when graphs_scanned > 0 and unsupported/errors are empty. Byte search checks serialized .uasset/.umap bytes in UTF-8/UTF-16 and requires manual review for hits."}
unreal.log(PREFIX + json.dumps(report, sort_keys=True, separators=(",", ":")))
unreal.log(PREFIX + "SUMMARY overall=%s graph=%s graph_hits=%d graphs_scanned=%d unsupported=%d errors=%d byte_search=%s byte_files=%d byte_hits=%d byte_errors=%d" %
           (overall_verdict, graph_verdict, len(hits), scanned, len(unsupported), len(errors),
            byte_verdict, files_checked, len(byte_hits), len(byte_errors)))
