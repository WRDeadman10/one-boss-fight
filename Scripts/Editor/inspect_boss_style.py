"""Prints the ability set entries of the pack great-sword boss combat style and the Anim Layer behaviour."""
import unreal

log = lambda m: unreal.log("[BossStyle] " + m)
P = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/"
cs = unreal.load_asset(P + "ExampleGreatSwordBossCombatStyle")
v = cs.get_editor_property("AbilitiesSet")
log("n=%d" % len(v))
for e in v:
    log(e.export_text()[:900])
log("granted effects: %s" % [str(x) for x in cs.get_editor_property("Granted Gameplay Effects")])
