import unreal

templates = [
    ("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryA_Montage", "Attack_PrimaryA_Montage (GuardCounter / AirLight template)"),
    ("/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage", "Dodge_Small_Forward_Roll_Montage (Backstep template)"),
    ("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Ability_E_Anim_Montage", "Ability_E_Anim_Montage (AirHeavyPlunge template)"),
    ("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/HitReactions/HitReact_Back_Montage", "HitReact_Back_Montage (ParryRecoil template)")
]

unreal.log("=== TEMPLATE MONTAGE NOTIFIES INSPECTION ===")
for path, desc in templates:
    m = unreal.EditorAssetLibrary.load_asset(path)
    if not m:
        unreal.log_error(f"FAILED TO LOAD: {path}")
        continue
    unreal.log(f"--- {desc} [{path}] ---")
    lines = unreal.RPGMontageUtils.describe_notifies(m)
    for line in lines:
        unreal.log(f"  {line}")

unreal.log("=== END INSPECTION ===")
