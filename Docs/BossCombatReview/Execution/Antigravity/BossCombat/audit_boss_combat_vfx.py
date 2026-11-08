import unreal
import json
import os

print("[BossCombatAudit] Starting Ember Warden Combat VFX audit...")
audit_results = {}

boss_anims = [
    ("/Game/OneBossFight/Boss01/Animations/AM_Boss01_A1", "AM_Boss01_A1"),
    ("/Game/OneBossFight/Boss01/Animations/AM_Boss01_A2", "AM_Boss01_A2"),
    ("/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3a", "AM_Boss01_A3a"),
    ("/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3b", "AM_Boss01_A3b"),
    ("/Game/OneBossFight/Boss01/Animations/AN_Boss01_A4_LowSweep", "AN_Boss01_A4_LowSweep"),
    ("/Game/OneBossFight/Boss01/Animations/AN_Boss01_A5_JavelinThrow", "AN_Boss01_A5_JavelinThrow"),
]

anim_info = {}
for path, name in boss_anims:
    asset = unreal.load_asset(path)
    if asset:
        length = float(asset.get_play_length())
        notifies = []
        try:
            notifies = list(unreal.RPGMontageUtils.describe_notifies(asset))
        except Exception:
            pass
        anim_info[name] = {
            "loaded": True,
            "class": asset.get_class().get_name(),
            "play_length": round(length, 4),
            "notifies": notifies
        }
    else:
        anim_info[name] = {"loaded": False}
audit_results["animations"] = anim_info

# Inspect Ember Javelin
javelin_path = "/Game/OneBossFight/Boss01/Weapons/SM_Boss01_EmberJavelin"
javelin_asset = unreal.load_asset(javelin_path)
if javelin_asset:
    bounds = None
    try:
        b = javelin_asset.get_bounds()
        bounds = {
            "box_extent": [round(float(b.box_extent.x), 2), round(float(b.box_extent.y), 2), round(float(b.box_extent.z), 2)],
            "sphere_radius": round(float(b.sphere_radius), 2)
        }
    except Exception:
        pass
    audit_results["SM_Boss01_EmberJavelin"] = {
        "loaded": True,
        "class": javelin_asset.get_class().get_name(),
        "bounds": bounds
    }
else:
    audit_results["SM_Boss01_EmberJavelin"] = {"loaded": False}

# Save results
out_dir = r"c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\BossCombat"
os.makedirs(out_dir, exist_ok=True)
out_file = os.path.join(out_dir, "BOSS_COMBAT_AUDIT_DATA.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(audit_results, f, indent=2)

print("[BossCombatAudit] Completed audit. Saved to:", out_file)
