"""Second pass over the pack's great-sword boss: exact EnemyInfo / CombatStyle / AbilitySet values and the montage element type."""
import unreal

log = lambda m: unreal.log("[PackBoss2] " + m)
P = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/"


def val(obj, n, width=900):
    try:
        v = obj.get_editor_property(n)
    except Exception as e:
        return "FAILED " + str(e)[:60]
    if isinstance(v, (list, tuple, unreal.Array)):
        return "[%s]" % ", ".join((x.get_path_name() if hasattr(x, "get_path_name") else str(x))[:200] for x in v)[:width]
    if isinstance(v, (dict, unreal.Map)):
        return str({str(k): str(x)[:60] for k, x in v.items()})[:width]
    return (v.get_path_name() if hasattr(v, "get_path_name") else str(v))[:width]


info = unreal.load_asset(P + "ExampleGreatSwordBoss")
for n in ("AI Pawn Class", "Anim Class", "DefaultCombatStyle", "BehaviorTree", "Behavior Classes", "Default Behavior State", "DefaultHostileTags", "BB Key Names",
          "Enemy Ability Set", "EnemyName", "StateClasses", "DefaultGameplayCues", "Default Target Types"):
    log("info.%s = %s" % (n, val(info, n)))
for k, v in info.get_editor_property("Default Attributes").items():
    log("attr %s => %s" % (k.export_text(), v.export_text()[:300]))

cs = unreal.load_asset(P + "ExampleGreatSwordBossCombatStyle")
for n in ("CombatStyleType", "CombatType", "Camera Mode Class", "Anim Layer Class"):
    log("cs.%s = %s" % (n, val(cs, n)))
# BP_AbilitySet base fields
for n in dir(cs):
    pass
for n in ("Abilities", "Ability Sets", "AbilitySet", "Ability Array", "Gameplay Abilities", "Effects", "Granted Abilities", "Abilities To Grant", "Attribute Sets"):
    r = val(cs, n)
    if not r.startswith("FAILED"):
        log("cs.%s = %s" % (n, r))

for name in ("GA_GS_Boss_CloseAttack", "GA_GS_Boss_MidRangeAttack", "GA_GS_Boss_LeapAttack"):
    a = unreal.load_asset(P + name)
    c = unreal.get_default_object(a.generated_class())
    ms = c.get_editor_property("AttackMontages")
    log("%s AttackMontages n=%d type=%s" % (name, len(ms), type(ms[0]).__name__ if len(ms) else "-"))
    for m in ms:
        log("   %s" % (m.export_text()[:500] if hasattr(m, "export_text") else str(m)))

abp = unreal.load_asset("/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/ABP_HumanoidEnemyCharacter")
log("ABP_HumanoidEnemyCharacter loaded: %s" % abp)

bt = unreal.load_asset("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/BT_ExampleBoss")
log("BT=%s" % bt)
