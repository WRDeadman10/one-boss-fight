import unreal
import json
import os

print("[Tier2FeedbackAudit] Starting Tier 2 Combat Feedback audit...")
audit_results = {}

# 1. PPM_ParryDistortion
ppm_path = "/Game/OneBossFight/Effects/PPM_ParryDistortion"
ppm_asset = unreal.load_asset(ppm_path)
if ppm_asset:
    audit_results["PPM_ParryDistortion"] = {
        "loaded": True,
        "class": ppm_asset.get_class().get_name()
    }
else:
    audit_results["PPM_ParryDistortion"] = {"loaded": False}

# 2. MPC_CombatFeedback
mpc_path = "/Game/OneBossFight/Data/MPC_CombatFeedback"
mpc_asset = unreal.load_asset(mpc_path)
if mpc_asset:
    scalars_info = []
    try:
        scalars = mpc_asset.get_editor_property("scalar_parameters")
        for s in scalars:
            s_name = str(s.get_editor_property("parameter_name"))
            s_val = float(s.get_editor_property("default_value"))
            scalars_info.append({"name": s_name, "default_value": s_val})
    except Exception as e:
        print("[Tier2FeedbackAudit] MPC read error:", e)
        
    audit_results["MPC_CombatFeedback"] = {
        "loaded": True,
        "class": mpc_asset.get_class().get_name(),
        "scalar_parameters": scalars_info
    }
else:
    audit_results["MPC_CombatFeedback"] = {"loaded": False}

# 3. NS_Boss_PhaseTwoAura
ns_path = "/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura"
ns_asset = unreal.load_asset(ns_path)
if ns_asset:
    audit_results["NS_Boss_PhaseTwoAura"] = {
        "loaded": True,
        "class": ns_asset.get_class().get_name()
    }
else:
    audit_results["NS_Boss_PhaseTwoAura"] = {"loaded": False}

# 4. AM_Boss01_ParryRecoil
recoil_path = "/Game/OneBossFight/Boss01/Animations/AM_Boss01_ParryRecoil"
recoil_asset = unreal.load_asset(recoil_path)
if recoil_asset:
    audit_results["AM_Boss01_ParryRecoil"] = {
        "loaded": True,
        "class": recoil_asset.get_class().get_name(),
        "play_length": round(float(recoil_asset.get_play_length()), 4),
        "notifies": list(unreal.RPGMontageUtils.describe_notifies(recoil_asset))
    }
else:
    audit_results["AM_Boss01_ParryRecoil"] = {"loaded": False}

# Save results
out_dir = r"c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\Tier2"
os.makedirs(out_dir, exist_ok=True)
out_file = os.path.join(out_dir, "TIER2_FEEDBACK_AUDIT_DATA.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(audit_results, f, indent=2)

print("[Tier2FeedbackAudit] Completed audit. Saved to:", out_file)
