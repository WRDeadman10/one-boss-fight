"""Reads default properties of the boss leap ability class. Log prefix [LeapGA]."""
import unreal
base = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/"
for n in ("GA_GS_Boss_LeapAttack", "GA_GS_Boss_CloseAttack"):
    cls = unreal.load_class(None, base + n + "." + n + "_C")
    cdo = unreal.get_default_object(cls) if hasattr(unreal, "get_default_object") else cls.get_default_object()
    unreal.log("[LeapGA] %s cdo %s" % (n, cdo.get_class().get_name()))
    for p in ("activation_blocked_tags", "activation_required_tags", "activation_owned_tags", "ability_tags", "cancel_abilities_with_tag", "block_abilities_with_tag", "cooldown_gameplay_effect_class", "ability_input_tag", "input_tag"):
        try:
            unreal.log("[LeapGA]   %s = %s" % (p, cdo.get_editor_property(p)))
        except Exception as e:
            unreal.log("[LeapGA]   %s ERR %s" % (p, str(e)[:70]))
