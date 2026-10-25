"""P0 read-only probe: for each listed montage/animation logs length, rate scale, sections, blend times and every notify (time, duration, name, state class).
Log prefix [P0Notify]. Loads assets, changes and saves nothing."""
import unreal

A = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/"
P = "/Game/OneBossFight/Boss01/Animations/"
PATHS = [A + "GreatswordBoss/GS_Attack0%d_Montage" % i for i in (1, 2, 3, 4)] + [
    A + "GreatswordBoss/GS_ChargedAttack_Montage", A + "GreatswordBoss/GS_LeapAttack_Montage",
    A + "GreatswordBoss/GS_SprintAttackFollowUp_Montage", A + "ExampleSwordMob/Mid01_Anim_Montage",
    A + "ExampleSwordMob/RetaliationAttack_Montage",
    P + "AM_Boss01_A1", P + "AM_Boss01_A3a", P + "AM_Boss01_A3b",
    P + "AN_Boss01_A4_LowSweep", P + "AN_Boss01_A5_JavelinThrow"]
EXTRA = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/"


def log(m):
    unreal.log("[P0Notify] " + m)


for path in PATHS:
    asset = unreal.load_asset(path)
    if asset is None:
        log("%s: NOT FOUND" % path)
        continue
    try:
        length = asset.get_editor_property("sequence_length") if isinstance(asset, unreal.AnimSequenceBase) else asset.get_editor_property("sequence_length")
    except Exception:
        length = asset.get_play_length() if hasattr(asset, "get_play_length") else "?"
    rate = None
    try:
        rate = asset.get_editor_property("rate_scale")
    except Exception:
        pass
    log("== %s (%s) length=%s rate_scale=%s" % (asset.get_name(), asset.get_class().get_name(), length, rate))
    if isinstance(asset, unreal.AnimMontage):
        # Existing C++ helper (Combat/RPGMontageUtils): lists sections, slot segments and notifies of a montage. Python cannot read the protected notify array directly.
        for line in unreal.RPGMontageUtils.describe_notifies(asset):
            log("   " + str(line))
    else:
        log("   (AnimSequence: notifies are not readable from Python; see the authored sidecar and the montage wrappers AM_Boss01_*)")
log("done")
