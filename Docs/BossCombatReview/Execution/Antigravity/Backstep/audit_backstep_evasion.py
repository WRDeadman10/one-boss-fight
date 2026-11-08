import unreal
import json
import os

print("[BackstepAudit] Starting Backstep Evasion visual audit...")
audit_results = {}

bs_path = "/Game/OneBossFight/Player/Animations/AM_ER_Backstep_Back"
bs_asset = unreal.load_asset(bs_path)
if bs_asset:
    audit_results["AM_ER_Backstep_Back"] = {
        "loaded": True,
        "play_length": round(float(bs_asset.get_play_length()), 4),
        "notifies": list(unreal.RPGMontageUtils.describe_notifies(bs_asset))
    }
else:
    audit_results["AM_ER_Backstep_Back"] = {"loaded": False}

# Check footstep dust particle assets
dust_assets = [
    "/Game/ParagonGreystone/FX/Textures/Smoke/T_ImpactDust_01",
    "/Game/ParagonGrux/FX/Textures/Smoke/T_ImpactDust_01"
]
audit_results["dust_textures"] = {}
for d_path in dust_assets:
    d = unreal.load_asset(d_path)
    audit_results["dust_textures"][d_path] = {
        "loaded": d is not None,
        "class": d.get_class().get_name() if d else None
    }

# Save results
out_dir = r"c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\Backstep"
os.makedirs(out_dir, exist_ok=True)
out_file = os.path.join(out_dir, "BACKSTEP_EVASION_AUDIT_DATA.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(audit_results, f, indent=2)

print("[BackstepAudit] Completed audit. Saved to:", out_file)
