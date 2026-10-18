"""
M5 content setup (weapons, audio, effects, presentation data). Idempotent: safe to re-run.

Run headless from the project root (editor closed), after setup_m3_content.py and setup_m4_content.py:
  UnrealEditor-Cmd.exe OneBossFight.uproject -run=pythonscript -script=Scripts/Editor/setup_m5_content.py -unattended -nullrhi

Creates / configures:
  - Three Greystone weapons as data only: Sword, Quick Blade, Greatblade (new montages, windows from sword speed)
  - IA_SwitchWeapon (R / D-pad up) and the player's weapon list
  - DA_Feedback_Greystone and DA_Feedback_Sevarog (pain, death, block, dodge sounds; block effect)
  - Impact effect, swing sound and hit-stop on the weapons
  - Sevarog's scythe feedback
"""

import os
import sys

import unreal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rpg_content_lib as lib  # noqa: E402

PACK = "/Game/ParagonGreystone"
SEV_PACK = "/Game/ParagonSevarog"
GREY_DIR = "/Game/OneBossFight/Characters/Greystone"
WEAPON_DIR = "/Game/OneBossFight/Weapons"
FEEDBACK_DIR = "/Game/OneBossFight/Feedback"
INPUT_DIR = "/Game/OneBossFight/Input/"
PLAYER_BP = "/Game/OneBossFight/Characters/BP_PlayerCharacter"
DUMMY_BP = "/Game/OneBossFight/Characters/BP_TrainingDummy"
BOSS_BP = "/Game/OneBossFight/Characters/BP_SevarogBoss"

SLOT = "UpperBody"  # Greystone's AnimBP slot (see DECISIONS.md)
TIP = "sword_top"
BASE = "sword_bottom"

SWING_CUE = PACK + "/Audio/Cues/Greystone_Effort_Swing"
IMPACT_FX = PACK + "/FX/Particles/Greystone/Abilities/Primary/FX/P_Greystone_Primary_Impact"
BLOCK_FX = PACK + "/FX/Particles/Greystone/Abilities/Primary/FX/P_Greystone_Primary_Sparks"

# Play rate scales the animation (and so the timing of every window): the Quick Blade is fast, the Greatblade slow.
PLAY_RATES = {"DA_Weapon_GreystoneSword": (1.0, 1.0), "DA_Weapon_GreystoneQuick": (1.3, 1.15), "DA_Weapon_GreystoneGreat": (0.8, 0.7)}

# weapon asset, display name, light attacks [(sequence, damage, poise, stamina)], heavy (sequence, damage, poise, stamina), hit-stop
WEAPONS = [
    ("DA_Weapon_GreystoneSword", "Greystone Sword",
     [("Attack_A_Med", 28, 12, 18), ("Attack_B_Med", 28, 12, 18), ("Attack_C_Med", 32, 14, 20), ("Attack_D_Med", 40, 18, 22)],
     ("Attack_C_Slow", 56, 40, 30), 0.06),
    ("DA_Weapon_GreystoneQuick", "Quick Blade",
     [("Attack_A_Fast", 16, 8, 10), ("Attack_B_Fast", 16, 8, 10), ("Attack_C_Fast", 18, 9, 11), ("Attack_D_Fast", 24, 12, 13)],
     ("Attack_D_Med", 34, 24, 22), 0.04),
    ("DA_Weapon_GreystoneGreat", "Greatblade",
     [("Attack_A_Slow", 50, 28, 28), ("Attack_B_Slow", 52, 28, 28), ("Attack_C_Slow", 66, 34, 32)],
     ("Attack_D_Slow", 92, 60, 46), 0.09),
]


def log(msg):
    unreal.log("[M5Setup] " + msg)


def load(path):
    asset = unreal.load_asset(path)
    if asset is None:
        raise RuntimeError("Missing asset: " + path)
    return asset


def load_optional(path):
    asset = unreal.load_asset(path)
    if asset is None:
        log("Missing optional asset (skipped): " + path)
    return asset


def key(name):
    k = unreal.Key()
    k.set_editor_property("key_name", name)
    return k


def setup_input():
    imc = load(INPUT_DIR + "IMC_Default")
    imc.modify()
    path = INPUT_DIR + "IA_SwitchWeapon"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        action = load(path)
    else:
        action = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "IA_SwitchWeapon", INPUT_DIR.rstrip("/"), unreal.InputAction, unreal.InputAction_Factory())
        action.set_editor_property("value_type", unreal.InputActionValueType.BOOLEAN)
        unreal.EditorAssetLibrary.save_loaded_asset(action)
    for k in ("R", "Gamepad_DPad_Up"):
        imc.unmap_key(action, key(k))
        imc.map_key(action, key(k))
    unreal.EditorAssetLibrary.save_loaded_asset(imc, False)
    log("IA_SwitchWeapon mapped to R and D-pad up.")
    return action


def build_weapons():
    unreal.EditorAssetLibrary.make_directory(WEAPON_DIR)
    swing = load_optional(SWING_CUE)
    impact = load_optional(IMPACT_FX)
    assets = []
    for asset_name, display, lights, heavy, hit_stop in WEAPONS:
        short = asset_name.replace("DA_Weapon_Greystone", "")
        light_montages = []
        for index, (sequence, _, _, _) in enumerate(lights):
            light_montages.append(lib.make_attack_montage(
                GREY_DIR, "AM_Greystone_%s_Light%d" % (short, index + 1), PACK, sequence, TIP, SLOT, combo=True))
        heavy_montage = lib.make_attack_montage(
            GREY_DIR, "AM_Greystone_%s_Heavy" % short, PACK, heavy[0], TIP, SLOT, combo=False)

        factory = unreal.DataAssetFactory()
        factory.set_editor_property("data_asset_class", unreal.RPGWeaponData)
        weapon = lib.recreate(WEAPON_DIR + "/" + asset_name, unreal.RPGWeaponData, factory)
        weapon.set_editor_property("display_name", unreal.Text(display))
        weapon.set_editor_property("light_combo", [
            lib.attack_struct(m, lights[i][1], lights[i][2], lights[i][3], play_rate=PLAY_RATES[asset_name][0])
            for i, m in enumerate(light_montages)])
        weapon.set_editor_property("heavy_attack", lib.attack_struct(
            heavy_montage, heavy[1], heavy[2], heavy[3], play_rate=PLAY_RATES[asset_name][1]))
        weapon.set_editor_property("trace_base_socket", BASE)
        weapon.set_editor_property("trace_tip_socket", TIP)
        weapon.set_editor_property("trace_radius", 18.0)
        weapon.set_editor_property("trace_samples", 4)
        weapon.set_editor_property("hit_stop_seconds", hit_stop)
        if swing:
            weapon.set_editor_property("swing_sound", swing)
        if impact:
            weapon.set_editor_property("impact_effect", impact)
        unreal.EditorAssetLibrary.save_loaded_asset(weapon)
        log("%s: %d light attacks + heavy." % (asset_name, len(lights)))
        assets.append(weapon)
    return assets


def build_feedback(asset_name, fields):
    unreal.EditorAssetLibrary.make_directory(FEEDBACK_DIR)
    factory = unreal.DataAssetFactory()
    factory.set_editor_property("data_asset_class", unreal.RPGCombatFeedbackData)
    data = lib.recreate(FEEDBACK_DIR + "/" + asset_name, unreal.RPGCombatFeedbackData, factory)
    for name, path in fields.items():
        asset = load_optional(path)
        if asset:
            data.set_editor_property(name, asset)
    unreal.EditorAssetLibrary.save_loaded_asset(data)
    return data


def configure_blueprints(weapons, switch_action, grey_feedback, sev_feedback):
    # Player: weapon list, switch input, feedback.
    bp = load(PLAYER_BP)
    cdo = unreal.get_default_object(bp.generated_class())
    cdo.set_editor_property("switch_weapon_action", switch_action)
    cdo.set_editor_property("weapons", weapons)
    combat = cdo.get_components_by_class(unreal.RPGCombatComponent)[0]
    combat.set_editor_property("weapon", weapons[0])
    combat.set_editor_property("feedback", grey_feedback)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_loaded_asset(bp, False)

    # Dummy shares Greystone's voice.
    if unreal.EditorAssetLibrary.does_asset_exist(DUMMY_BP):
        dummy = load(DUMMY_BP)
        dcdo = unreal.get_default_object(dummy.generated_class())
        dcdo.get_components_by_class(unreal.RPGCombatComponent)[0].set_editor_property("feedback", grey_feedback)
        unreal.BlueprintEditorLibrary.compile_blueprint(dummy)
        unreal.EditorAssetLibrary.save_loaded_asset(dummy, False)

    # Boss: scythe feedback and Sevarog's voice.
    if unreal.EditorAssetLibrary.does_asset_exist(BOSS_BP):
        boss = load(BOSS_BP)
        bcdo = unreal.get_default_object(boss.generated_class())
        bcombat = bcdo.get_components_by_class(unreal.RPGCombatComponent)[0]
        bcombat.set_editor_property("feedback", sev_feedback)
        scythe = bcombat.get_editor_property("weapon")
        if scythe is not None:
            swing = load_optional(SEV_PACK + "/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_Swing")
            impact = load_optional(SEV_PACK + "/FX/Particles/Abilities/Primary/FX/P_Sevarog_Melee_SucessfulImpact")
            if swing:
                scythe.set_editor_property("swing_sound", swing)
            if impact:
                scythe.set_editor_property("impact_effect", impact)
            unreal.EditorAssetLibrary.save_loaded_asset(scythe, False)
        unreal.BlueprintEditorLibrary.compile_blueprint(boss)
        unreal.EditorAssetLibrary.save_loaded_asset(boss, False)
    log("Blueprints configured.")


def main():
    switch_action = setup_input()
    weapons = build_weapons()

    grey_feedback = build_feedback("DA_Feedback_Greystone", {
        "pain_sound": PACK + "/Audio/Cues/Greystone_Effort_Pain",
        "heavy_pain_sound": PACK + "/Audio/Cues/Greystone_Effort_PainHeavy",
        "block_sound": PACK + "/Audio/Cues/Greystone_Effort_Block",
        "block_effect": BLOCK_FX,
        "dodge_sound": PACK + "/Audio/Cues/Greystone_Effort_Jump",
        "death_sound": PACK + "/Audio/Cues/Greystone_Death",
    })
    sev_cues = SEV_PACK + "/Characters/Heroes/Sevarog/Sounds/SoundCues/"
    sev_feedback = build_feedback("DA_Feedback_Sevarog", {
        "pain_sound": sev_cues + "Sevarog_Effort_Pain",
        "heavy_pain_sound": sev_cues + "Sevarog_Effort_PainHeavy",
        "death_sound": sev_cues + "Sevarog_Death",
    })

    configure_blueprints(weapons, switch_action, grey_feedback, sev_feedback)
    log("M5 content setup complete.")


main()
