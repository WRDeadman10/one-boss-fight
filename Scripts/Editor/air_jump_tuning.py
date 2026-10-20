"""
Longer jump for the jump heavy: the pack player jumps with JumpZVelocity 600 at gravity scale 1.7 (about 0.72 s in the air, 108 cm apex). The heavy
swing needs air time, so JumpZVelocity goes to 680 (about 0.82 s, 139 cm); gravity stays so the fall keeps its weight.
Pack asset edited in place (BP_CombatPlayerCharacter component defaults). Run in the open editor; verify after a restart.
"""
import unreal

JUMP_Z = 680.0
bp = unreal.load_asset("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter")
cdo = unreal.get_default_object(bp.generated_class())
movement = cdo.get_editor_property("character_movement")
bp.modify()
movement.set_editor_property("jump_z_velocity", JUMP_Z)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_loaded_asset(bp, False)
print("[AirJump] jump_z_velocity =", unreal.get_default_object(bp.generated_class()).get_editor_property("character_movement").get_editor_property("jump_z_velocity"))
