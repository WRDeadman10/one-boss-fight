"""Dumps the pack's great-sword boss: Blueprint CDO values, EnemyInfo data asset, combat style and ability CDOs. Run in the open editor."""
import unreal

log = lambda m: unreal.log("[PackBoss] " + m)
P = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/"


def show(label, obj, names):
    for n in names:
        try:
            v = obj.get_editor_property(n)
            text = v.export_text() if hasattr(v, "export_text") else str(v)
            log("%s.%s = %s" % (label, n, text[:700]))
        except Exception as e:
            log("%s.%s failed: %s" % (label, n, str(e)[:80]))


bp = unreal.load_asset(P + "BP_ExampleGreatSwordBoss")
cdo = unreal.get_default_object(bp.generated_class())
for n in ("Player Info", "PlayerInfo", "Enemy Info", "EnemyInfo", "Info", "Behavior Tree", "BehaviorTree", "Boss HUD"):
    show("bpCDO", cdo, [n])
mesh = cdo.get_editor_property("mesh")
log("mesh=%s anim_class=%s" % (mesh.get_editor_property("skeletal_mesh_asset"), mesh.get_editor_property("anim_class")))
log("capsule r=%s hh=%s" % (cdo.get_editor_property("capsule_component").get_editor_property("capsule_radius"), cdo.get_editor_property("capsule_component").get_editor_property("capsule_half_height")))
log("ai controller=%s auto_possess=%s" % (cdo.get_editor_property("ai_controller_class"), cdo.get_editor_property("auto_possess_ai")))
log("components=%s" % [c.get_name() for c in cdo.get_components_by_class(unreal.ActorComponent)])
info = unreal.load_asset(P + "ExampleGreatSwordBoss")
log("info class=%s" % info.get_class().get_name())
for n in ("Default Attributes", "ExtendedAttributes", "Ability Sets", "AbilitySets", "Combat Style", "CombatStyle", "Behavior Tree", "BehaviorTree", "Mesh", "Skeletal Mesh",
          "Anim Class", "Animation Blueprint", "Display Name", "Boss Name", "Name", "Level", "Souls", "Drops", "Loot", "Cues", "Target Types"):
    show("info", info, [n])
cs = unreal.load_asset(P + "ExampleGreatSwordBossCombatStyle")
log("combatstyle class=%s" % cs.get_class().get_name())
show("cs", cs, ["Abilities", "Ability Sets", "AbilitySets", "Combat Style Tag", "Style Tag", "Layer Class", "Anim Layer", "Linked Layer"])
for name in ("GA_GS_Boss_CloseAttack", "GA_GS_Boss_CloseRare", "GA_GS_Boss_MidRangeAttack", "GA_GS_Boss_LeapAttack", "GA_GS_Boss_SprintAttack",
             "GA_GS_Boss_RetaliationAttack", "GA_GS_Boss_EnterCombat", "GA_GS_Boss_HitStun", "GA_GS_Boss_TurnInPlace"):
    a = unreal.load_asset(P + name)
    c = unreal.get_default_object(a.generated_class())
    log("== %s" % name)
    for n in ("Attack Montages", "AttackMontages", "Montage", "Montages", "Montage To Play", "Attack Data", "AttackData", "Ability Tags", "Ability Tag",
              "Cooldown", "Ability Input Tag", "Activation Required Tags", "Activation Owned Tags", "Combo Montages", "Min Range", "Max Range"):
        try:
            v = c.get_editor_property(n)
            text = v.export_text() if hasattr(v, "export_text") else str(v)
            log("  %s = %s" % (n, text[:500]))
        except Exception:
            pass
