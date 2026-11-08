"""Lead read-only (C-987): describe_notifies for the pack template montages Codex needs (C-986). Saves nothing."""
import unreal
B = "/Game/AdvancedARPGCombat/"
PATHS = [B + "MeleeCombatSystem/Animations/1Handed/Ability_E_Anim_Montage",
         B + "MeleeCombatSystem/Animations/1Handed/Attack_PrimaryB_Montage",
         B + "MeleeCombatSystem/Animations/1Handed/ChargedAttack_Montage",
         B + "Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage",
         B + "MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Montage",
         B + "MeleeCombatSystem/Animations/1Handed/HitReactions/HitReact_Back_Montage",
         B + "MeleeCombatSystem/Animations/1Handed/HitReactions/HitReact_Front_Montage"]
for p in PATHS:
    a = unreal.load_asset(p)
    if not a:
        unreal.log("[Templates] MISSING " + p); continue
    unreal.log("[Templates] == %s" % a.get_name())
    for line in unreal.RPGMontageUtils.describe_notifies(a):
        unreal.log("[Templates]    " + line)
unreal.log("[Templates] finished")
unreal.SystemLibrary.quit_editor()
