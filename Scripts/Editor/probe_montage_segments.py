import unreal
log = lambda m: unreal.log("[ProbeMont] " + m)
m = unreal.load_asset("/Game/OneBossFight/GreystonePack/MagicCombatSystem/Animations/ProjectileMeteor/MeteorProjectile_Cast_Montage_Grey")
for n in ("slot_anim_tracks", "SlotAnimTracks"):
    try:
        t = m.get_editor_property(n)
        log("%s -> %d tracks" % (n, len(t)))
        seg = t[0].get_editor_property("anim_track").get_editor_property("anim_segments")
        log("segments %d first anim=%s" % (len(seg), seg[0].get_editor_property("anim_reference")))
    except Exception as e:
        log("%s failed %s" % (n, str(e)[:100]))
