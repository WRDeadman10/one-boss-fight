"""
L_SevarogArena: the boss is the pack's own great-sword boss (mannequin), placed at the arena centre facing the player start.
The pack boss BP defaults EnemyInfoRef to the sword mob's info (sword mob montages, 100 HP), so the placed instance gets the great-sword boss info.
Open L_SevarogArena first (loading a map from a script crashes the editor); the script saves the level.
"""
import unreal

D = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/"
BOSS = D + "BP_ExampleGreatSwordBoss.BP_ExampleGreatSwordBoss_C"
INFO = D + "ExampleGreatSwordBoss"
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_name() == "L_SevarogArena", "open L_SevarogArena first: " + world.get_name()

for a in eas.get_all_level_actors():
    if a.get_class().get_name() in ("BP_SevarogBossPack_C", "BP_ExampleGreatSwordBoss_C"):
        eas.destroy_actor(a)

cls = unreal.load_class(None, BOSS)
half = unreal.get_default_object(cls).get_editor_property("capsule_component").get_scaled_capsule_half_height()
boss = eas.spawn_actor_from_class(cls, unreal.Vector(0, 0, half + 5), unreal.Rotator(0, 0, 180))
boss.set_actor_label("GreatswordBoss")
info = unreal.load_asset(INFO)
boss.set_editor_property("EnemyInfoRef", info)
print("boss info ->", boss.get_editor_property("EnemyInfoRef").get_name())
# The pack boss is born with Status.HitStunImmune, which would stop any stagger: Scripts/Editor/boss_poise_armor.py removes it from the Blueprint default (run it first).
print("boss gameplay tags ->", boss.get_editor_property("GameplayTags").export_text())
print("saved:", unreal.EditorLoadingAndSavingUtils.save_map(world, "/Game/OneBossFight/Levels/L_SevarogArena"))
