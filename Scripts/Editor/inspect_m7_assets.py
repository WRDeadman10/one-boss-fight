"""Inspect the imported audio, font, Niagara and animation assets before wiring them.

Run: UnrealEditor-Cmd.exe OneBossFight.uproject -run=pythonscript -script=Scripts/Editor/inspect_m7_assets.py -unattended -nullrhi
"""
import unreal


def log(msg):
    unreal.log("[M7Inspect] " + msg)


def load(path):
    asset = unreal.load_asset(path)
    log("%s -> %s" % (path, asset.get_class().get_name() if asset else None))
    return asset


font = load("/Game/AdvancedARPGCombat/MeleeCombatSystem/UI/Fonts/Cinzel/Cinzel")
if font:
    try:
        for typeface in font.get_editor_property("composite_font").get_editor_property("default_typeface").get_editor_property("fonts"):
            log("  typeface: %s" % typeface.get_editor_property("name"))
    except Exception as exc:
        log("  typeface read failed: %s" % exc)

for name in ("NS_Thunder_Beam7", "NS_LightingBeamV3"):
    system = load("/Game/BeamPack/Niagara/LaserBeam/" + name)
    if system:
        try:
            for param in system.get_exposed_parameters() if hasattr(system, "get_exposed_parameters") else []:
                log("  param %s" % param)
        except Exception as exc:
            log("  params failed: %s" % exc)
for path in ("/Game/BloodPack/Slash/Niagara/NS_Slash_Med", "/Game/BloodPack/Hit/Niagara/NS_BulletHit_Med",
             "/Game/Free_Spells/VFX_Niagara/NS_Free_Spells_Shockwave", "/Game/Free_Spells/VFX_Niagara/NS_Free_Spells_Circle",
             "/Game/Free_Spells/VFX_Niagara/NS_Free_Spells_Buff_Lightning"):
    load(path)

root = "/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/"
for name in ("A_Sword_Swing_Cue", "A_Hammer_Swing_Cue", "A_Guardian_ImpactL_Cue", "Combat/ShieldImpacts/ShieldImpacts_Cue",
             "Combat/SwordImpacts/SwordImpact_Cue", "Combat/SwordImpacts/SwordImpactLarge3"):
    cue = load(root + name)
    if cue and hasattr(cue, "duration"):
        log("  duration %.2f" % cue.duration)

sequence = load("/Game/Mage/Animations/Sequence1/07_Roll/02_Roll_Combat/AS_Roll_Combat_F_0_Seq")
if sequence:
    log("  length %.2fs root motion %s skeleton %s" % (sequence.get_play_length(), sequence.get_editor_property("enable_root_motion"),
                                                      sequence.get_editor_property("skeleton").get_name()))
for path in ("/Game/Mage/Animations/Sequence1/07_Roll/02_Roll_Combat/AS_Roll_Combat_B_180_Seq",):
    seq = load(path)
    if seq:
        log("  length %.2fs" % seq.get_play_length())
load("/Game/Mage/Demo/Mannequin_UE4/Rigs/IK_UE4_Mannequin")
greystone = unreal.EditorAssetLibrary.load_asset("/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone_Skeleton")
log("greystone skeleton: %s" % greystone)
if greystone:
    mesh = unreal.EditorAssetLibrary.load_asset("/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone")
    log("greystone mesh: %s" % mesh)
    bones = list(unreal.AnimationLibrary.get_skeleton_bone_names(greystone)) if hasattr(unreal.AnimationLibrary, "get_skeleton_bone_names") else []
    log("greystone bones (%d): %s" % (len(bones), ", ".join(str(b) for b in bones[:80])))
ue4 = unreal.EditorAssetLibrary.load_asset("/Game/Mage/Demo/Mannequin_UE4/Character/Mesh/UE4_Mannequin_Skeleton")
if ue4 and hasattr(unreal.AnimationLibrary, "get_skeleton_bone_names"):
    log("ue4 bones: %s" % ", ".join(str(b) for b in list(unreal.AnimationLibrary.get_skeleton_bone_names(ue4))[:80]))
