"""For each pack boss ability: lists the Blueprint variables of the whole parent chain and the values on the boss child's defaults."""
import unreal

log = lambda m: unreal.log("[GADef] " + m)
A = "/Game/AdvancedARPGCombat/"
P = A + "MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/"
AI = A + "MeleeCombatSystem/Blueprints/Abilities/AI/"
CORE = A + "AdvancedCombatFramework/CoreCombatSystem/Abilities/"

CHAINS = {
    "EnterCombat": [P + "GA_GS_Boss_EnterCombat", AI + "GA_EnemyEnterCombat"],
    "ExitCombat": [P + "GA_GS_Boss_ExitCombat", AI + "GA_EnemyExitCombat"],
    "HitStun": [P + "GA_GS_Boss_HitStun", AI + "HitReactions/GA_EnemyHitStun"],
    "TurnInPlace": [P + "GA_GS_Boss_TurnInPlace", AI + "GA_EnemyTurnInPlace"],
    "Leap": [P + "GA_GS_Boss_LeapAttack", AI + "GA_LeapAttack"],
    "Sprint": [P + "GA_GS_Boss_SprintAttack", AI + "GA_EnemySprintAttack"],
    "Close": [P + "GA_GS_Boss_CloseAttack", AI + "GA_EnemyMeleeAttack"],
}


KNOWN = {
    "EnterCombat": ["Enter Combat Montage"], "ExitCombat": ["ExitCombatMontage"],
    "HitStun": ["Hit React Montages", "Hit React Montages (in Air)", "Directional?", "UseInAirMontages?", "UseSwingDirection?", "bCanRecieveKnockback", "KnockbackSpeed",
                "bHitStunImmuneOnMaxHitCount?", "bUsesPoise", "Hit Count Attribute Tag", "RequiredSourceTags", "RequiredAttackTypeTags"],
    "TurnInPlace": ["MinAngle", "MaxAngle", "Turn Left 90", "Turn Right 90", "Turn Left 180", "Turn Right 180"],
    "Leap": ["MinDistance", "MaxAllowedLeapDistance", "LeapSpeed", "LeapMaxHeight", "AttackMontages", "Random Attack Index?", "ResetAttackTime"],
    "Sprint": ["FollowUpRange", "SprintSpeed", "Timelimit", "AttackMontages", "Random Attack Index?", "ResetAttackTime"],
    "Close": ["AttackMontages", "AttackData", "Random Attack Index?", "ResetAttackTime", "BlockGameplayCuesByImpactTags"],
}


def var_names(key):
    return KNOWN[key]


def text(v):
    if isinstance(v, (list, tuple, unreal.Array)):
        return "[" + "; ".join(text(x) for x in v)[:600] + "]"
    if hasattr(v, "export_text"):
        return v.export_text()[:500]
    if hasattr(v, "get_path_name"):
        return v.get_path_name()
    return str(v)[:300]


for key, chain in CHAINS.items():
    child = unreal.load_asset(chain[0])
    cdo = unreal.get_default_object(child.generated_class())
    log("##### " + key)
    names = var_names(key)
    for n in names:
        try:
            log("  %s = %s" % (n, text(cdo.get_editor_property(n))))
        except Exception as e:
            log("  %s = <unreadable>" % n)
