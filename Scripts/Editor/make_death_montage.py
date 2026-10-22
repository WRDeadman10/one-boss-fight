"""Creates the montage AM_Boss01_DeathLegend (log prefix [DeathMontage]) from the clip AN_Boss01_DeathLegend: the pack's death ability (GA_EnemyRagdollDeath) plays montages from its DeathMontages array, and a montage asset is what that array holds.
A new project asset in /Game/OneBossFight/Boss01/Animations; nothing is replaced or deleted (an existing montage is left as it is). Run with Scripts/run_in_editor.py."""
import unreal

log = lambda m: unreal.log("[DeathMontage] " + m)
DEST = "/Game/OneBossFight/Boss01/Animations"
NAME = "AM_Boss01_DeathLegend"
PATH = DEST + "/" + NAME
if unreal.EditorAssetLibrary.does_asset_exist(PATH):
    m = unreal.load_asset(PATH)
    log("PASS %s already exists, length %.4f s" % (PATH, m.get_editor_property("sequence_length")))
else:
    clip = unreal.load_asset(DEST + "/AN_Boss01_DeathLegend")
    factory = unreal.AnimMontageFactory()
    factory.set_editor_property("source_animation", clip)
    m = unreal.AssetToolsHelpers.get_asset_tools().create_asset(NAME, DEST, unreal.AnimMontage, factory)
    if m is None:
        log("FAIL the montage was not created")
    else:
        # The slot of the pack boss's own montages (the factory makes DefaultSlot, which the boss's anim blueprint may not have): read from one of them, as RPGBossClips::SlotName does.
        ref = unreal.load_asset("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_Attack01_Montage")
        slot = unreal.RPGMontageUtils.get_montage_slot(ref) if ref is not None else "DefaultSlot"
        unreal.RPGMontageUtils.set_montage_slot(m, slot)
        m.set_editor_property("enable_auto_blend_out", False)  # the last pose of the clip must stay when the montage ends (the clip holds it for the last second)
        log("slot of the boss montages: %s, set on the new montage" % slot)
        unreal.EditorAssetLibrary.save_loaded_asset(m)
        log("PASS %s created from %s, length %.4f s" % (PATH, clip.get_name(), m.get_editor_property("sequence_length")))
