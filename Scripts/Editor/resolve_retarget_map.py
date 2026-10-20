"""Matches duplicates that the batch renamed (name_Grey1, _Grey2) to their source assets by class and play length, then moves them
to the mirrored folder and completes Saved/greystone_retarget_map.json."""
import json
import re
import unreal

DEST = "/Game/OneBossFight/GreystonePack"
PACK = "/Game/AdvancedARPGCombat"
log = lambda m: unreal.log("[GreyMap] " + m)
survey = json.load(open(unreal.Paths.project_saved_dir() + "pack_anim_survey.json"))
mapping = json.load(open(unreal.Paths.project_saved_dir() + "greystone_retarget_map.json"))
unmapped = [r for r in survey if r["path"] not in mapping and "SK_CombatMannequin" in r["skeleton"] and r["class"] in ("AnimSequence", "AnimMontage", "BlendSpace", "BlendSpace1D", "AimOffsetBlendSpace")]
log("%d sources without a duplicate yet" % len(unmapped))
extras = {}
for path in unreal.EditorAssetLibrary.list_assets(DEST + "/Extra", recursive=False, include_folder=False):
    name = path.split("/")[-1].split(".")[0]
    extras[name] = path.split(".")[0]
log("%d extras" % len(extras))


def length(path):
    a = unreal.load_asset(path)
    try:
        return round(a.get_play_length(), 3)
    except Exception:
        try:
            return round(a.get_editor_property("sequence_length"), 3)
        except Exception:
            return None


by_base = {}
for name, path in extras.items():
    base = re.sub(r"_Grey\d*$", "", name)
    by_base.setdefault(base, []).append((name, path))
resolved = 0
ambiguous = []
for r in unmapped:
    cands = list(by_base.get(r["name"], []))
    if not cands:
        ambiguous.append((r["name"], "no candidate"))
        continue
    src_len = length(r["path"])
    pick = [c for c in cands if src_len is not None and length(c[1]) == src_len]
    if len(pick) == 1 or (len(pick) > 1 and False):
        name, path = pick[0]
    elif len(cands) == 1:
        name, path = cands[0]
    else:
        ambiguous.append((r["name"], "%d candidates, %d by length" % (len(cands), len(pick))))
        continue
    sub = r["path"][len(PACK):].rsplit("/", 1)[0]
    target = "%s%s/%s_Grey" % (DEST, sub, r["name"])
    if unreal.EditorAssetLibrary.does_asset_exist(target):
        ambiguous.append((r["name"], "target exists"))
        continue
    if unreal.EditorAssetLibrary.rename_asset(path, target):
        mapping[r["path"]] = target
        by_base[r["name"]] = [c for c in by_base[r["name"]] if c[1] != path]
        resolved += 1
log("resolved %d, ambiguous %d" % (resolved, len(ambiguous)))
for a in ambiguous[:40]:
    log("  ? %s: %s" % a)
json.dump(mapping, open(unreal.Paths.project_saved_dir() + "greystone_retarget_map.json", "w"))
unreal.EditorAssetLibrary.save_directory(DEST)
log("mapping now has %d entries" % len(mapping))
