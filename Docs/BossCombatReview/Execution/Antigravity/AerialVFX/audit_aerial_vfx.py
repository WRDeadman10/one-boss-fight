import unreal
import json
import os

print("[AerialVFXAudit] Starting Aerial Attack VFX and Ribbon audit...")
audit_results = {}

# 1. Inspect AM_ER_Attack_Air_Light
light_path = "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Light"
light_asset = unreal.load_asset(light_path)
if light_asset:
    audit_results["AM_ER_Attack_Air_Light"] = {
        "loaded": True,
        "play_length": round(float(light_asset.get_play_length()), 4),
        "notifies": list(unreal.RPGMontageUtils.describe_notifies(light_asset))
    }
else:
    audit_results["AM_ER_Attack_Air_Light"] = {"loaded": False}

# 2. Inspect AM_ER_Attack_Air_Heavy_Plunge
heavy_path = "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Heavy_Plunge"
heavy_asset = unreal.load_asset(heavy_path)
if heavy_asset:
    audit_results["AM_ER_Attack_Air_Heavy_Plunge"] = {
        "loaded": True,
        "play_length": round(float(heavy_asset.get_play_length()), 4),
        "notifies": list(unreal.RPGMontageUtils.describe_notifies(heavy_asset))
    }
else:
    audit_results["AM_ER_Attack_Air_Heavy_Plunge"] = {"loaded": False}

# 3. Inspect Weapon Trail and Impact Particle Assets
fx_assets = [
    "/Game/ParagonGreystone/FX/Particles/Novaborn/P_Greystone_Novaborn_Primary_Impact",
    "/Game/ParagonGrux/FX/Particles/Abilities/Primary/FX/P_Grux_Melee_ShockwaveImpact",
    "/Game/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/FengMaoFX/Particles/Ultimate/P_FengMao_Ult_Impact_02"
]
audit_results["particle_assets"] = {}
for p_path in fx_assets:
    p = unreal.load_asset(p_path)
    if p:
        audit_results["particle_assets"][p_path] = {
            "loaded": True,
            "class": p.get_class().get_name()
        }
    else:
        audit_results["particle_assets"][p_path] = {"loaded": False}

# Save results
out_dir = r"c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\AerialVFX"
os.makedirs(out_dir, exist_ok=True)
out_file = os.path.join(out_dir, "AERIAL_VFX_AUDIT_DATA.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(audit_results, f, indent=2)

print("[AerialVFXAudit] Completed audit. Saved to:", out_file)
