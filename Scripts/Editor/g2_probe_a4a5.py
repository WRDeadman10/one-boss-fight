"""Probe for the A4 and A5 stand-ins (log prefix [ProbeA45]): lengths of the A4 and A5 clips. Read only."""
import unreal

log = lambda m: unreal.log("[ProbeA45] " + m)
for clip in ("AN_Boss01_A4_LowSweep", "AN_Boss01_A5_JavelinThrow"):
    a = unreal.load_asset("/Game/OneBossFight/Boss01/Animations/" + clip)
    try:
        log("%s length %.3f root motion %s skeleton %s" % (clip, a.get_editor_property("sequence_length"), a.get_editor_property("enable_root_motion"), a.get_editor_property("skeleton").get_name()))
    except Exception as e:
        log("%s ERR %s" % (clip, e))
        log("%s" % [p for p in dir(a) if "length" in p or "root" in p])
