import unreal
log = lambda m: unreal.log("[ProbeBS] " + m)
bs = unreal.load_asset("/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Unarmed/Locomotion/BaseUnarmedLocomotion_BS_Grey")
log("class %s" % bs.get_class().get_name())
log(str([n for n in dir(bs) if "sample" in n.lower() or "blend" in n.lower()][:40]))
for n in ("sample_data", "blend_samples", "SampleData"):
    try:
        v = bs.get_editor_property(n)
        log("%s -> %s" % (n, v))
    except Exception as e:
        log("%s failed %s" % (n, str(e)[:80]))
try:
    log("get_blend_samples: %s" % bs.get_blend_samples())
except Exception as e:
    log("get_blend_samples failed %s" % str(e)[:80])
