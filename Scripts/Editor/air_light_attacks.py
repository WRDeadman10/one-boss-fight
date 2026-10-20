"""
Jump light attack for every weapon. The pack picks Ability.Melee.FallingAttack when the player is airborne and the weapon has FallingAttackMontages
(dual swords, twinblades and polearm have an air clip; sword, claymore and unarmed had none, so a jump attack did nothing special).
For those three the weapon's own first light attack is copied into FallingAttackMontages (struct copied whole: montage, play rate, timings).
Run in the open editor (run_in_editor.py). Idempotent: skips weapons that already have a falling montage.
"""
import unreal

W = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/"
log = lambda m: unreal.log("[AirLight] " + m)

for path in ("Sword/GA_Sword_Melee", "Claymore/GA_Claymore_Melee", "Unarmed/GA_Unarmed_Melee"):
    bp = unreal.load_asset(W + path)
    cdo = unreal.get_default_object(bp.generated_class())
    falling = list(cdo.get_editor_property("FallingAttackMontages"))
    light = list(cdo.get_editor_property("AttackMontages"))
    if falling:
        log("%s already has %d falling montage(s)" % (path, len(falling)))
        continue
    bp.modify()  # CDO edits are not saved without this
    cdo.set_editor_property("FallingAttackMontages", [light[0]])
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_loaded_asset(bp, False)
    log("%s: FallingAttackMontages = first light attack" % path)
