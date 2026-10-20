"""
Moves the editor viewport camera to the pose in Saved/view.txt ("x y z pitch yaw", cm and degrees; default: the player start looking at the arena centre).
Run with Scripts/run_in_editor.py, then Scripts/capture_to_file.py saves the viewport picture to Saved/Screenshots/current_viewport.png.
"""
import os
import unreal

PATH = r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Saved\view.txt"
vals = [-2600.0, 0.0, 260.0, -6.0, 0.0]
if os.path.exists(PATH):
    vals = [float(v) for v in open(PATH).read().split()]
loc = unreal.Vector(vals[0], vals[1], vals[2])
rot = unreal.Rotator(roll=0.0, pitch=vals[3], yaw=vals[4])
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(loc, rot)
unreal.log("[View] camera at %s rot %s" % (loc, rot))
try:
    unreal.EditorLevelLibrary.editor_invalidate_viewports()
except Exception as e:
    unreal.log("[View] invalidate failed %s" % e)
try:
    unreal.EditorLevelLibrary.set_level_viewport_realtime(True) if hasattr(unreal.EditorLevelLibrary, "set_level_viewport_realtime") else None
except Exception:
    pass
