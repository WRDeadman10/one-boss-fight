"""Move the playable arena into Maps using Unreal's asset redirector workflow.

Caller must hold both C-1155 locks. No other map is deleted or changed.
"""
import json
import unreal

OLD = "/Game/OneBossFight/Levels/L_SevarogArena"
NEW = "/Game/OneBossFight/Maps/L_SevarogArena"

def require(condition, message):
    if not condition:
        raise RuntimeError("[MAP_CLEANUP] REFUSED: " + message)

require(unreal.EditorAssetLibrary.does_asset_exist(OLD), "source arena asset is missing")
require(not unreal.EditorAssetLibrary.does_asset_exist(NEW), "destination arena asset already exists")
asset = unreal.EditorAssetLibrary.load_asset(OLD)
require(asset is not None, "source arena asset could not be loaded")
parts = NEW.rsplit("/", 1)
rename_data = unreal.AssetRenameData(asset, parts[0], parts[1])
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
ok = asset_tools.rename_assets([rename_data])
require(ok, "Unreal rename was cancelled or failed")
require(unreal.EditorAssetLibrary.does_asset_exist(NEW), "destination did not read back after rename")
redirector = unreal.EditorAssetLibrary.does_asset_exist(OLD)
unreal.log("[MAP_CLEANUP] " + json.dumps({
    "status": "MOVED",
    "source": OLD,
    "destination": NEW,
    "source_redirector_present": bool(redirector),
    "destination_exists": True,
}))
