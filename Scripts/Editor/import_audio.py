"""Imports the two boss music tracks from Import/Audio into /Game/OneBossFight/Audio (log prefix [ImportAudio]): MX_Boss01_Phase1 (the battle theme) and MX_Boss01_Phase2 (the choral climax).
OGG first (about 10 MB of source in the asset instead of about 85 MB of PCM for the WAV), the WAV when the OGG import returns nothing. Looping on, sound group Music, saved at once (an unsaved import is lost on an editor restart).
Idempotent: a second run replaces the asset in place; it never deletes an asset (other assets may reference it). Import/Audio is git-ignored, the imported assets under Content/OneBossFight/Audio are tracked.
Run with Scripts/run_in_editor.py. The credits of both tracks are in Import/Audio/SOURCES.txt and Documentation/ASSET_LICENSES.md."""
import os
import unreal

log = lambda m: unreal.log("[ImportAudio] " + m)
proj = unreal.SystemLibrary.get_project_directory()
tools = unreal.AssetToolsHelpers.get_asset_tools()
DEST = "/Game/OneBossFight/Audio"
NAMES = ("MX_Boss01_Phase1", "MX_Boss01_Phase2")


def import_one(name, ext):
    t = unreal.AssetImportTask()
    t.filename = os.path.join(proj, "Import", "Audio", name + "." + ext).replace("/", os.sep)
    t.destination_path = DEST
    t.destination_name = name
    t.automated = True
    t.save = False
    t.replace_existing = True
    t.replace_existing_settings = True
    tools.import_asset_tasks([t])
    return [str(p) for p in t.imported_object_paths]


def read(asset, prop):
    try:
        return asset.get_editor_property(prop)
    except Exception as e:
        return "? (%s)" % e


for name in NAMES:
    used, paths = None, []
    for ext in ("ogg", "wav"):
        source = os.path.join(proj, "Import", "Audio", name + "." + ext)
        if not os.path.exists(source):
            log("%s.%s is not there" % (name, ext))
            continue
        try:
            paths = import_one(name, ext)
        except Exception as e:
            log("%s.%s import raised %s" % (name, ext, e))
            paths = []
        if paths:
            used = ext
            break
        log("%s.%s import returned nothing, trying the next format" % (name, ext))
    asset = unreal.load_asset("%s/%s" % (DEST, name)) if used else None
    if asset is None:
        log("FAILED %s: nothing imported" % name)
        continue
    for prop, value in (("looping", True), ("sound_group", unreal.SoundGroup.SOUNDGROUP_MUSIC)):
        try:
            asset.set_editor_property(prop, value)
        except Exception as e:
            log("could not set %s on %s: %s" % (prop, name, e))
    saved = unreal.EditorAssetLibrary.save_loaded_asset(asset)
    disk = os.path.join(proj, "Content", "OneBossFight", "Audio", name + ".uasset")
    size = os.path.getsize(disk) if os.path.exists(disk) else -1
    log("%s from .%s: duration %s s, channels %s, sample rate %s, looping %s, sound group %s, saved %s, %.1f MB on disk" % (name, used, read(asset, "duration"), read(asset, "num_channels"), read(asset, "sample_rate"),
        read(asset, "looping"), read(asset, "sound_group"), saved, size / 1048576.0))
log("done")
