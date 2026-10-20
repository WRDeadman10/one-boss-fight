"""
Runs inside the DarkRuinsMegascansSample project (commandlet: UnrealEditor-Cmd <sample uproject> -run=pythonscript -script=<this file>).
Computes the dependency closure (hard references) of the folders in ROOTS and writes one line per package to OUT: "<package>|<size bytes>|<exists in target>".
Only the asset registry is used: nothing is loaded or built. Soft references (for example material parameters set by name) are followed too, so the copy is complete.
"""
import unreal, os, json

SAMPLE = r"C:\Users\winss\Documents\Unreal Projects\DarkRuinsMegascansSample\Content"
TARGET = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Content"
OUT = r"C:\Users\winss\AppData\Local\Temp\claude\C--Users-winss-Documents-Unreal-Projects-one-boss-fight\a0ecc616-a415-4cf1-90ff-c18bbaa95ed5\scratchpad\sample_closure.json"
ROOTS = json.load(open(OUT.replace("sample_closure.json", "sample_roots.json")))

ar = unreal.AssetRegistryHelpers.get_asset_registry()
ar.search_all_assets(True)
opts = unreal.AssetRegistryDependencyOptions(include_soft_package_references=True, include_hard_package_references=True, include_searchable_names=False, include_soft_management_references=False, include_hard_management_references=False)

todo = []
for root in ROOTS:
    found = [str(ad.package_name) for ad in ar.get_assets_by_path(root, recursive=True)]
    todo.extend(found if found else [root])  # a root that is not a folder is a single package
seen, outside = set(), set()
while todo:
    p = todo.pop()
    if p in seen:
        continue
    seen.add(p)
    for d in ar.get_dependencies(p, opts) or []:
        d = str(d)
        if d.startswith("/Game/"):
            todo.append(d)
        else:
            outside.add(d)
rows = []
for p in sorted(seen):
    rel = p[len("/Game/"):]
    f = os.path.join(SAMPLE, rel.replace("/", os.sep))
    size = 0
    for ext in (".uasset", ".uexp", ".ubulk", ".umap"):
        if os.path.exists(f + ext):
            size += os.path.getsize(f + ext)
    clash = any(os.path.exists(os.path.join(TARGET, rel.replace("/", os.sep)) + e) for e in (".uasset", ".umap"))
    rows.append({"pkg": p, "size": size, "clash": clash})
json.dump({"packages": rows, "outside": sorted(outside)}, open(OUT, "w"))
unreal.log("[Deps] %d packages, %d outside /Game: %s" % (len(rows), len(outside), sorted(outside)[:20]))
