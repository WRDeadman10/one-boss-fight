"""Mannequin, Mesh Hygiene and Sockets Audit (AB-A26..AB-A30).
Runs in UnrealEditor-Cmd under ENGINE_LOCK. Read-only inspection.
"""
import unreal
import json
import os

OUT_LOG_PATH = r"c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\Mesh\MESH_AUDIT_LOG.txt"
OUT_JSON_PATH = r"c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\Mesh\MESH_AUDIT_DATA.json"

log_lines = []
def log(m):
    msg = "[MeshAudit] " + m
    unreal.log(msg)
    log_lines.append(msg)

output_data = {}

# 1. Audit SKM_CombatMannequin
mannequin_path = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin"
mannequin = unreal.load_asset(mannequin_path)
mannequin_data = {"found": False}
if mannequin:
    skel = mannequin.get_editor_property("skeleton")
    candidate_sockets = [
        "hand_rSocket", "hand_lSocket", "hand_r", "hand_l",
        "weapon_r", "weapon_l", "Root", "pelvis", "spine_01",
        "Sword_Socket", "Shield_Socket"
    ]
    found_sockets = []
    for s_name in candidate_sockets:
        try:
            sock = mannequin.find_socket(s_name)
            if sock:
                b_name = str(sock.get_editor_property("bone_name"))
                loc = sock.get_editor_property("relative_location")
                rot = sock.get_editor_property("relative_rotation")
                found_sockets.append({
                    "socket_name": s_name,
                    "bone_name": b_name,
                    "location": [round(float(loc.x), 2), round(float(loc.y), 2), round(float(loc.z), 2)],
                    "rotation": [round(float(rot.pitch), 2), round(float(rot.yaw), 2), round(float(rot.roll), 2)]
                })
                log("Found socket %s on bone %s: loc=%s rot=%s" % (s_name, b_name, [loc.x, loc.y, loc.z], [rot.pitch, rot.yaw, rot.roll]))
        except Exception as e:
            log("Error checking socket %s: %s" % (s_name, str(e)))
            
    mannequin_data = {
        "found": True,
        "skeleton": skel.get_path_name() if skel else "None",
        "found_sockets": found_sockets
    }
    log("SKM_CombatMannequin audit complete. Found %d sockets." % len(found_sockets))
else:
    log("SKM_CombatMannequin MISSING")
output_data["mannequin"] = mannequin_data

# 2. Audit Weapon Mesh SM_SteelSword
sword_path = "/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/Meshes/Weapons/Paragon/SM_SteelSword"
sword = unreal.load_asset(sword_path)
sword_data = {"found": False}
if sword:
    candidate_sword_sockets = [
        "SwordTrail1", "SwordTrail2", "Trail1", "Trail2", "Trail_Start", "Trail_End",
        "WeaponSocket", "HandSocket", "Blade_Base", "Blade_Tip", "Socket_Hand"
    ]
    found_sword_sockets = []
    for s_name in candidate_sword_sockets:
        try:
            sock = sword.find_socket(s_name)
            if sock:
                loc = sock.get_editor_property("relative_location")
                rot = sock.get_editor_property("relative_rotation")
                found_sword_sockets.append({
                    "socket_name": s_name,
                    "location": [round(float(loc.x), 2), round(float(loc.y), 2), round(float(loc.z), 2)],
                    "rotation": [round(float(rot.pitch), 2), round(float(rot.yaw), 2), round(float(rot.roll), 2)]
                })
                log("Found sword socket %s: loc=%s rot=%s" % (s_name, [loc.x, loc.y, loc.z], [rot.pitch, rot.yaw, rot.roll]))
        except Exception as e:
            log("Error checking sword socket %s: %s" % (s_name, str(e)))
            
    sword_data = {
        "found": True,
        "found_sockets": found_sword_sockets
    }
    log("SM_SteelSword audit complete. Found %d sockets." % len(found_sword_sockets))
else:
    log("SM_SteelSword MISSING")
output_data["sword"] = sword_data

# 3. Audit Greystone Mesh & Materials
greystone_path = "/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone"
greystone = unreal.load_asset(greystone_path)
greystone_data = {"found": False}
if greystone:
    materials = []
    try:
        for i, m_slot in enumerate(greystone.get_editor_property("materials")):
            mat_interface = m_slot.get_editor_property("material_interface")
            slot_name = str(m_slot.get_editor_property("material_slot_name"))
            mat_name = mat_interface.get_path_name() if mat_interface else "None"
            materials.append({
                "slot_index": i,
                "slot_name": slot_name,
                "material": mat_name
            })
    except Exception as e:
        log("Error reading materials: %s" % str(e))
        
    phys_asset = None
    try:
        phys_asset = greystone.get_editor_property("physics_asset")
    except Exception:
        pass
        
    # Check sockets on Greystone mesh too
    greystone_sockets = []
    for s_name in ["hand_rSocket", "hand_lSocket", "weapon_r", "weapon_l", "FX_Trail_01", "FX_Trail_02", "SwordTrail1", "SwordTrail2"]:
        try:
            sock = greystone.find_socket(s_name)
            if sock:
                b_name = str(sock.get_editor_property("bone_name"))
                loc = sock.get_editor_property("relative_location")
                greystone_sockets.append({
                    "socket_name": s_name,
                    "bone_name": b_name,
                    "location": [round(float(loc.x), 2), round(float(loc.y), 2), round(float(loc.z), 2)]
                })
                log("Found Greystone socket %s on bone %s" % (s_name, b_name))
        except Exception:
            pass
            
    greystone_data = {
        "found": True,
        "material_count": len(materials),
        "materials": materials,
        "physics_asset": phys_asset.get_path_name() if phys_asset else "None",
        "sockets": greystone_sockets
    }
    log("Greystone found: %d materials, phys=%s sockets=%d" % (
        len(materials), phys_asset.get_name() if phys_asset else "None", len(greystone_sockets)))
else:
    log("Greystone MISSING")
output_data["greystone"] = greystone_data

os.makedirs(os.path.dirname(OUT_JSON_PATH), exist_ok=True)
with open(OUT_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2)

with open(OUT_LOG_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines) + "\n")

log("Audit written to %s and %s" % (OUT_JSON_PATH, OUT_LOG_PATH))
unreal.SystemLibrary.quit_editor()
