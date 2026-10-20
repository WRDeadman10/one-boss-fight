"""
M7: wires the imported audio, Niagara effects and roll animations into the existing data assets and blueprints.

Boss attack effects are wired in setup_m4_content.py (it builds the montages). Run AFTER setup_m4_content.py / setup_m5_content.py (those rebuild the montages and data assets from scratch and
would drop this wiring). Idempotent.

  UnrealEditor-Cmd.exe OneBossFight.uproject -run=pythonscript -script=Scripts/Editor/setup_m7_content.py -unattended -nullrhi

Prerequisite: setup_m7_roll.py (needs a real editor) has created the retargeted roll sequences.
"""

import os
import sys

import unreal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rpg_content_lib as lib  # noqa: E402

GAME = "/Game/OneBossFight/"
SWORD_FX = "/Game/RealisticSwordSoundEffects/Cues/"
ARPG_SFX = "/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/"
ROLL_DIR = GAME + "Characters/Greystone/Roll/"
GREY_DIR = GAME + "Characters/Greystone"

NS_SPARKS = "/Game/Free_Spells/VFX_Niagara/NS_Free_Spells_Explosion"  # orange sparks: the block / parry flash


def log(msg):
    unreal.log("[M7Content] " + msg)


def load(path, required=True):
    asset = unreal.load_asset(path)
    if asset is None and required:
        raise RuntimeError("Missing asset: " + path)
    return asset


def cues(folder, names):
    return [load(SWORD_FX + folder + "/" + n) for n in names]


def save(asset):
    unreal.EditorAssetLibrary.save_loaded_asset(asset, False)


# ---------------------------------------------------------------------------------------------
# Weapons: layered swing and impact sounds plus a Niagara impact
# ---------------------------------------------------------------------------------------------

def wire_weapons():
    great_impacts = [load(ARPG_SFX + "Combat/SwordImpacts/SwordImpactLarge%d" % i) for i in range(1, 6)]
    plan = {
        # asset: (swing variants, impact variants, hit stop untouched)
        "DA_Weapon_GreystoneSword": (
            cues("Sword_Swoosh", ["Swoosh_1_Cue", "Swoosh_2_Cue", "Swoosh_3_Cue"]),
            cues("Sword_Attack", ["Sword_Attack_%d_Cue" % i for i in range(1, 7)])),
        "DA_Weapon_GreystoneQuick": (
            cues("Sword_Swoosh", ["Swoosh_4_Cue", "Swoosh_5_Cue", "Swoosh_6_Cue"]),
            cues("Sword_Attack", ["Sword_Attack_Short_1_Cue", "Sword_Attack_Short_2_Cue", "Sword_Attack_7_Cue", "Sword_Attack_8_Cue"])),
        "DA_Weapon_GreystoneGreat": (
            [load(ARPG_SFX + "A_Sword_Swing_Cue")],
            great_impacts),
        "DA_Weapon_SevarogScythe": (
            [load(ARPG_SFX + "A_Hammer_Swing_Cue")],
            [load(ARPG_SFX + "Combat/SwordImpacts/SwordImpactLarge3"), load(ARPG_SFX + "A_Guardian_ImpactL_Cue")]),
    }
    # The Blood VFX pack (NS_Slash_Med, NS_BulletHit_Med) spawns nothing visible in UE 5.5 (its _Commons materials are
    # missing from the download), so weapons keep their Cascade impact effect and ImpactNiagara stays empty.
    for name, (swings, impacts) in plan.items():
        weapon = load(GAME + "Weapons/" + name)
        weapon.set_editor_property("swing_sound_variants", swings)
        weapon.set_editor_property("impact_sound_variants", impacts)
        weapon.set_editor_property("impact_niagara", None)
        save(weapon)
        log("%s: %d swing variants, %d impact variants" % (name, len(swings), len(impacts)))


# ---------------------------------------------------------------------------------------------
# Feedback: shield block and parry
# ---------------------------------------------------------------------------------------------

def wire_feedback():
    shield = load(ARPG_SFX + "Combat/ShieldImpacts/ShieldImpacts_Cue")
    feedback = load(GAME + "Feedback/DA_Feedback_Greystone")
    feedback.set_editor_property("block_sound", shield)
    feedback.set_editor_property("parry_sound", shield)
    feedback.set_editor_property("block_niagara", load(NS_SPARKS))
    feedback.set_editor_property("parry_niagara", load(NS_SPARKS))
    save(feedback)
    log("DA_Feedback_Greystone: shield block and parry sounds, spark Niagara")


# ---------------------------------------------------------------------------------------------
# Roll montages
# ---------------------------------------------------------------------------------------------

def make_roll_montage(name, sequence_name):
    sequence = load(ROLL_DIR + sequence_name)
    # fix_roll_root_motion.py has moved the roll's travel into the root bone and enabled root motion: the capsule travels
    # with the animation (run that script after setup_m7_roll.py).
    if not sequence.get_editor_property("enable_root_motion"):
        raise RuntimeError(name + ": run fix_roll_root_motion.py first (roll travel is still in the pelvis)")
    factory = unreal.AnimMontageFactory()
    factory.set_editor_property("source_animation", sequence)
    montage = lib.recreate(GREY_DIR + "/" + name, unreal.AnimMontage, factory)
    unreal.RPGMontageUtils.set_montage_slot(montage, "UpperBody")
    # Short blends: the dodge state ends when the montage starts blending out, so a long blend-out would end the roll
    # at about half of its travel.
    for slot, seconds in (("blend_in", 0.05), ("blend_out", 0.08)):
        blend = montage.get_editor_property(slot)
        blend.set_editor_property("blend_time", seconds)
        montage.set_editor_property(slot, blend)
    save(montage)
    log("%s: %.2fs" % (name, montage.get_play_length()))
    return montage


def wire_dodge():
    forward = make_roll_montage("AM_Greystone_Dodge", "AS_Roll_Combat_F_0_Seq_Greystone")
    back = make_roll_montage("AM_Greystone_DodgeBack", "AS_Roll_Combat_B_180_Seq_Greystone")
    bp = load(GAME + "Characters/BP_PlayerCharacter")
    cdo = unreal.get_default_object(bp.generated_class())
    cdo.set_editor_property("dodge_montage", forward)
    cdo.set_editor_property("dodge_back_montage", back)
    save(bp)
    log("BP_PlayerCharacter: dodge montages assigned")


def main():
    wire_weapons()
    wire_feedback()
    wire_dodge()


main()
