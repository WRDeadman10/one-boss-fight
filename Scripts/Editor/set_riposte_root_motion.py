"""Switches root motion on for the player's riposte clip AN_Riposte_Player_Front (log prefix [RootMotion]): the clip travels the player 90 cm along the facing (0 to 0.7 s, then holds), and the
dynamic montage that plays it only moves the character when the sequence has bEnableRootMotion. Idempotent, saves the asset. The boss clips stay in place (no root motion). Run with Scripts/run_in_editor.py."""
import unreal

log = lambda m: unreal.log("[RootMotion] " + m)
PATH = "/Game/OneBossFight/Boss01/Animations/AN_Riposte_Player_Front"
clip = unreal.load_asset(PATH)
if clip is None:
    log("FAIL %s does not exist (run import_boss01_clips_r12.py first)" % PATH)
else:
    before = clip.get_editor_property("enable_root_motion")
    if not before:
        clip.set_editor_property("enable_root_motion", True)
        unreal.EditorAssetLibrary.save_loaded_asset(clip)
    log("PASS %s root motion %s -> %s, length %.4f s" % (clip.get_name(), before, clip.get_editor_property("enable_root_motion"), clip.get_editor_property("sequence_length")))
