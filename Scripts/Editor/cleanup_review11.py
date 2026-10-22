"""Deletes the scratch assets of review_report11.py in /Game/OneBossFight/_Review11 (nothing references them; an unsaved scratch asset would be saved to disk by the editor's Save Content on a rebuild). Deletes asset by asset, then the folder. Log prefix [Review11]."""
import unreal

path = "/Game/OneBossFight/_Review11"
eal = unreal.EditorAssetLibrary
if eal.does_directory_exist(path):
    for asset in eal.list_assets(path, recursive=True, include_folder=False):
        eal.delete_asset(asset)
    eal.delete_directory(path)
left = eal.list_assets(path, recursive=True, include_folder=False) if eal.does_directory_exist(path) else []
unreal.log("[Review11] scratch assets left: %d, folder still there: %s" % (len(left), eal.does_directory_exist(path)))
