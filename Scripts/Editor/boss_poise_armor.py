"""
Poise is the pack boss's armor (Elden Ring): BP_ExampleGreatSwordBoss is born with GameplayTags = (Enemy.Character, Status.HitStunImmune). Its hit stun ability lists
Status.HitStunImmune as an activation blocker, so the boss could never stagger however much poise it lost. This removes the permanent immunity from the Blueprint's
default (the variable is not editable per instance): hits are absorbed while poise lasts (the GA_BaseHitReaction poise gate) and a poise break staggers.
Pack asset edited in place (git-ignored): run again after a pack re-import. Run in the open editor (Scripts/run_in_editor.py), then respawn the arena boss with
Scripts/Editor/arena_use_pack_boss.py. Idempotent.
"""
import unreal

PATH = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss"
bp = unreal.load_asset(PATH)
cdo = unreal.get_default_object(bp.generated_class())
before = cdo.get_editor_property("GameplayTags").export_text()
tags = unreal.GameplayTagContainer()
tags.import_text('(GameplayTags=((TagName="Enemy.Character")))')
bp.modify()  # CDO edits are not saved without this
cdo.set_editor_property("GameplayTags", tags)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_loaded_asset(bp, False)
print("[BossArmor] GameplayTags: %s -> %s" % (before, unreal.get_default_object(bp.generated_class()).get_editor_property("GameplayTags").export_text()))
