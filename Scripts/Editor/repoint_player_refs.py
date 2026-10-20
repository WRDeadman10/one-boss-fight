"""
Stage 3: points the player-side abilities and combat styles at the Greystone retargets. For each referencing Blueprint (CDO) or
data asset instance in Saved/grey_player_vars.json, every variable is rewritten recursively: asset and class references found in
Saved/greystone_retarget_map.json are replaced by their Greystone copies. Struct values are rewritten through export_text /
import_text. DRY = True reports the changes only. Enemy and mannequin-only assets are not touched.
"""
import json
import re
import unreal

DRY = False
log = lambda m: unreal.log("[Repoint] " + m)
saved = unreal.Paths.project_saved_dir()
mapping = json.load(open(saved + "greystone_retarget_map.json"))
players = json.load(open(saved + "grey_player_vars.json"))
# object path text -> replacement: "/Game/X/Name.Name" and "/Game/X/Name.Name_C"
text_map = {}
for old, new in mapping.items():
    on, nn = old.split("/")[-1], new.split("/")[-1]
    text_map[old + "." + on] = new + "." + nn
    text_map[old + "." + on + "_C"] = new + "." + nn + "_C"
PATH_RE = re.compile(r"/Game/[A-Za-z0-9_/\-]+\.[A-Za-z0-9_\-]+")
changes = []


def fix_text(text):
    return PATH_RE.sub(lambda m: text_map.get(m.group(0), m.group(0)), text)


def repoint(value):
    """Returns (new value, changed)."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value, False
    if isinstance(value, (list, tuple, unreal.Array)):
        out, ch = [], False
        for v in value:
            nv, c = repoint(v)
            out.append(nv)
            ch = ch or c
        return (out if ch else value), ch
    if isinstance(value, (dict, unreal.Map)):
        out, ch = {}, False
        for k, v in value.items():
            nv, c = repoint(v)
            out[k] = nv
            ch = ch or c
        return (out if ch else value), ch
    if hasattr(value, "export_text") and hasattr(value, "import_text"):  # struct
        text = value.export_text()
        new_text = fix_text(text)
        if new_text == text:
            return value, False
        copy = value.copy()
        copy.import_text(new_text)
        return copy, True
    if isinstance(value, unreal.Class):
        path = value.get_path_name()
        new = text_map.get(path)
        if new:
            return unreal.load_object(None, new), True
        return value, False
    if isinstance(value, unreal.Object):
        path = value.get_path_name()
        new = text_map.get(path)
        if new:
            return unreal.load_object(None, new), True
    return value, False


for pkg, info in sorted(players.items()):
    asset = unreal.load_asset(pkg)
    if asset is None:
        log("MISSING " + pkg)
        continue
    obj = unreal.get_default_object(asset.generated_class()) if info["target"] == "cdo" else asset
    touched = []
    for name in info["vars"]:
        try:
            value = obj.get_editor_property(name)
        except Exception:
            continue
        new, changed = repoint(value)
        if changed:
            touched.append(name)
            if not DRY:
                try:
                    obj.set_editor_property(name, new)
                except Exception as e:
                    log("  set failed %s.%s: %s" % (pkg.split("/")[-1], name, str(e)[:120]))
    if touched:
        changes.append((pkg, touched))
        log("%s: %s" % (pkg.split("/")[-1], touched))
        if not DRY:
            unreal.EditorAssetLibrary.save_loaded_asset(asset, False)
log("%d assets changed (%s)" % (len(changes), "dry run" if DRY else "saved"))
