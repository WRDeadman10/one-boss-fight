"""Deletes the scratch assets of review_report12.py in /Game/OneBossFight/_Review12 (nothing references them; an unsaved scratch asset would be written to disk by the editor's Save Content on the next rebuild).
Deletes asset by asset, then the folder; if the editor still holds an asset in use the leftover is listed and must be removed from disk after the next rebuild. Log prefix [Review12]."""
import unreal

path = "/Game/OneBossFight/_Review12"
eal = unreal.EditorAssetLibrary
if eal.does_directory_exist(path):
    for asset in eal.list_assets(path, recursive=True, include_folder=False):
        eal.delete_asset(asset)
    eal.delete_directory(path)
left = eal.list_assets(path, recursive=True, include_folder=False) if eal.does_directory_exist(path) else []
unreal.log("[Review12] scratch assets left: %d %s, folder still there: %s" % (len(left), left, eal.does_directory_exist(path)))
