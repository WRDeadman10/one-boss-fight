import unreal
import json
import os

print("[GuardCounterAudit] Starting Guard Counter visual polish audit...")
audit_results = {}

gc_path = "/Game/OneBossFight/Player/Animations/AM_ER_Attack_GuardCounter"
gc_asset = unreal.load_asset(gc_path)

if gc_asset:
    length = float(gc_asset.get_play_length())
    notifies = list(unreal.RPGMontageUtils.describe_notifies(gc_asset))
    
    raw_notifies_info = []
    try:
        raw_notifies = gc_asset.get_editor_property("notifies")
        for ne in raw_notifies:
            time = float(ne.get_editor_property("link_value"))
            n_name = str(ne.get_editor_property("notify_name"))
            dur = float(ne.get_editor_property("duration")) if hasattr(ne, "get_editor_property") else 0.0
            raw_notifies_info.append({
                "name": n_name,
                "time": round(time, 4),
                "duration": round(dur, 4)
            })
    except Exception as e:
        print("[GuardCounterAudit] raw notifies read error:", e)

    audit_results["AM_ER_Attack_GuardCounter"] = {
        "loaded": True,
        "class": gc_asset.get_class().get_name(),
        "play_length": round(length, 4),
        "notifies": notifies,
        "raw_notifies": raw_notifies_info
    }
else:
    audit_results["AM_ER_Attack_GuardCounter"] = {"loaded": False}

# Audit camera setup in BP_CombatPlayerCharacter
player_bp_path = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter"
player_asset = unreal.load_asset(player_bp_path)
camera_info = {"loaded": player_asset is not None}
if player_asset:
    gen_class = player_asset.generated_class()
    if gen_class:
        cdo = unreal.get_default_object(gen_class)
        if cdo:
            try:
                # inspect components on cdo
                boom = None
                cam = None
                for prop_name in ["camera_boom", "CameraBoom", "SpringArm", "spring_arm"]:
                    try:
                        boom = cdo.get_editor_property(prop_name)
                        if boom:
                            break
                    except Exception:
                        pass
                
                if boom:
                    arm_len = float(boom.get_editor_property("target_arm_length"))
                    rot = boom.get_editor_property("relative_rotation")
                    offset = boom.get_editor_property("target_offset")
                    sock_offset = boom.get_editor_property("socket_offset")
                    camera_info["spring_arm"] = {
                        "name": boom.get_name(),
                        "target_arm_length": round(arm_len, 2),
                        "relative_rotation": [round(float(rot.pitch), 2), round(float(rot.yaw), 2), round(float(rot.roll), 2)],
                        "target_offset": [round(float(offset.x), 2), round(float(offset.y), 2), round(float(offset.z), 2)],
                        "socket_offset": [round(float(sock_offset.x), 2), round(float(sock_offset.y), 2), round(float(sock_offset.z), 2)],
                        "enable_camera_lag": bool(boom.get_editor_property("b_enable_camera_lag")) if hasattr(boom, "b_enable_camera_lag") else None
                    }
                else:
                    camera_info["spring_arm"] = "Not found directly on CDO property"
            except Exception as e:
                camera_info["error"] = str(e)
audit_results["camera_setup"] = camera_info

# Audit shield deflection particle assets
shield_particles = [
    "/Game/ParagonSteel/FX/Particles/Steel/Abilities/Bash/FX/P_ShieldBashImpact",
    "/Game/ParagonSteel/FX/Particles/Steel/Abilities/AbilityArmor/FX/P_Steel_AbilityArmor_Impact"
]
audit_results["shield_particles"] = {}
for p_path in shield_particles:
    p_asset = unreal.load_asset(p_path)
    if p_asset:
        bounds = None
        try:
            b = p_asset.get_bounds()
            bounds = {
                "box_extent": [round(float(b.box_extent.x), 2), round(float(b.box_extent.y), 2), round(float(b.box_extent.z), 2)],
                "sphere_radius": round(float(b.sphere_radius), 2)
            }
        except Exception:
            pass
        audit_results["shield_particles"][p_path] = {
            "loaded": True,
            "class": p_asset.get_class().get_name(),
            "bounds": bounds
        }
    else:
        audit_results["shield_particles"][p_path] = {"loaded": False}

# Save results
out_dir = r"c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\GuardCounter"
os.makedirs(out_dir, exist_ok=True)
out_file = os.path.join(out_dir, "GUARD_COUNTER_POLISH_DATA.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(audit_results, f, indent=2)

print("[GuardCounterAudit] Completed audit. Saved to:", out_file)
