"""Sevarog on the pack, step 5b: GA_Sev_Death and the combat style entries (step 5 stopped before them: deleting assets that other assets reference makes the
editor raise a modal ensure and hang, so this part never deletes). Run in the open editor."""
import re
import unreal

HEAD = open(r"C:/Users/winss/Documents/Unreal Projects/OneBossFight/Scripts/Editor/sevarog_pack_02_montages_abilities.py", encoding="utf-8").read()
exec(HEAD[:HEAD.index("ONLY_TOGGLE = globals()")])  # helper functions and constants of step 2

log = lambda m: unreal.log("[SevPack5] " + m)
OUT = "/Game/OneBossFight/SevarogPack"
STYLE = OUT + "/SevarogCombatStyle"
AN_SEND = A + "AdvancedCombatFramework/AbilitySystem/AnimNotifes/AN_SendEventToAbility.AN_SendEventToAbility_C"
NS_SHOCKWAVE = "/Game/Free_Spells/VFX_Niagara/NS_Free_Spells_Shockwave"
SHOCK_SOUND = "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_Ability_Ultimate"
CAST_SOUND = "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_Ability_Q"
COMET = "/Game/ParagonSevarog/FX/Particles/Abilities/Primary/FX/P_SevarogComet"
tools = unreal.AssetToolsHelpers.get_asset_tools()
lib = unreal.AnimationLibrary


def delete_if_loaded(path):
    if unreal.load_asset(path) is not None:
        unreal.EditorAssetLibrary.delete_asset(path)


def dup_unused(src, folder, name):
    delete_if_loaded(folder + "/" + name)
    asset = tools.duplicate_asset(name, folder, unreal.load_asset(src))
    if asset is None:
        raise RuntimeError("duplicate failed " + src)
    return asset


def new_montage(name, sequence_name):
    delete_if_loaded(MONT + "/" + name)
    sequence = find_pack_asset("AnimSequence", sequence_name)
    factory = unreal.AnimMontageFactory()
    factory.set_editor_property("source_animation", sequence)
    montage = tools.create_asset(name, MONT, unreal.AnimMontage, factory)
    unreal.RPGMontageUtils.set_montage_slot(montage, SLOT)
    lib.add_animation_notify_track(montage, "PackCombat")
    return montage, sequence



death = unreal.load_asset(MONT + "/AM_SevPack_Death")
if unreal.load_asset(ABIL + "/GA_Sev_Death") is None:
    tools.duplicate_asset("GA_Sev_Death", ABIL, unreal.load_asset(A + "MeleeCombatSystem/Blueprints/Abilities/AI/GA_EnemyDeath"))
sev_death = unreal.load_asset(ABIL + "/GA_Sev_Death")
cdo = unreal.get_default_object(sev_death.generated_class())
# The pack's death ability has no montage entry to copy, so borrow an F_AbilityMontage struct from the enter-combat ability.
enter_cdo = unreal.get_default_object(unreal.load_asset(ABIL + "/GA_Sev_EnterCombat").generated_class())
template = enter_cdo.get_editor_property("Enter Combat Montage")
cdo.set_editor_property("DeathMontages", [ability_montage(template, death)])
unreal.BlueprintEditorLibrary.compile_blueprint(sev_death)
unreal.EditorAssetLibrary.save_loaded_asset(sev_death)
log("GA_Sev_Death ready")

# ---- Combat style: new abilities, death replaced ------------------------------------------------------------------------------------
style = unreal.load_asset(STYLE)
entry = style.get_editor_property("AbilitiesSet")[0]
text = entry.export_text()


def cls(name):
    return '"/Script/Engine.BlueprintGeneratedClass\'%s/%s.%s_C\'"' % (ABIL, name, name)


text = re.sub(r'"[^"]*GA_EnemyRagdollDeath[^"]*"', cls("GA_Sev_Death"), text)
for name in ("GA_Sev_Lightning", "GA_Sev_PhaseRoar"):
    if name not in text:
        text = re.sub(r"(Abilities_\d+_[0-9A-F]+=\()", lambda m: m.group(1) + cls(name) + ",", text, count=1)
entry.import_text(text)
style.set_editor_property("AbilitiesSet", [entry])
unreal.EditorAssetLibrary.save_loaded_asset(style)
log("style abilities: %s" % re.findall(r"GA_\w+?\.", text))
