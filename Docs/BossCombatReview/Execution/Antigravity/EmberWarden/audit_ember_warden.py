import unreal
import json
import os

print("[EmberWardenAudit] Starting detailed Ember Warden presentation audit...")
audit_results = {}

# 1. Inspect BP_ExampleGreatSwordBoss
bp_path = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss"
bp_asset = unreal.EditorAssetLibrary.load_asset(bp_path)
cdo = None
gen_class = None
if bp_asset:
    gen_class = bp_asset.generated_class()
    if gen_class:
        cdo = unreal.get_default_object(gen_class)

audit_results["BP_ExampleGreatSwordBoss"] = {
    "loaded": bp_asset is not None,
    "class_name": gen_class.get_name() if gen_class else None,
}

if cdo:
    mesh_comp = None
    try:
        mesh_comp = cdo.get_editor_property("mesh")
    except Exception as e:
        print("[EmberWardenAudit] Mesh get_editor_property error:", e)
    
    if mesh_comp:
        sk_mesh = None
        try:
            sk_mesh = mesh_comp.get_editor_property("skeletal_mesh_asset")
        except Exception:
            try:
                sk_mesh = mesh_comp.get_editor_property("skeletal_mesh")
            except Exception:
                pass
        
        audit_results["BP_ExampleGreatSwordBoss"]["mesh_component"] = {
            "name": mesh_comp.get_name(),
            "skeletal_mesh": sk_mesh.get_path_name() if sk_mesh else None
        }

# 2. Inspect Mannequin Skeletal Meshes and Sockets
mannequin_path = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin_Simple"
mannequin_asset = unreal.EditorAssetLibrary.load_asset(mannequin_path)
mannequin_info = {"loaded": mannequin_asset is not None}
if mannequin_asset:
    skel = None
    try:
        skel = mannequin_asset.get_editor_property("skeleton")
        mannequin_info["skeleton"] = skel.get_path_name() if skel else None
    except Exception:
        pass
    
    # Check sockets on mannequin
    check_sockets = ["WeaponSocket_R", "WeaponSocket_L", "SwordTrail1", "SwordTrail2", "head", "spine_03"]
    sockets_found = {}
    for s_name in check_sockets:
        try:
            sock = mannequin_asset.find_socket(s_name)
            if sock:
                sockets_found[s_name] = {
                    "bone_name": str(sock.get_editor_property("bone_name")),
                    "relative_location": str(sock.get_editor_property("relative_location")),
                    "relative_rotation": str(sock.get_editor_property("relative_rotation"))
                }
            else:
                sockets_found[s_name] = None
        except Exception as e:
            sockets_found[s_name] = f"error: {e}"
    mannequin_info["sockets"] = sockets_found

audit_results["SKM_CombatMannequin_Simple"] = mannequin_info

# 3. Inspect SM_Boss01_Greatsword
sword_path = "/Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword"
sword_asset = unreal.EditorAssetLibrary.load_asset(sword_path)
if sword_asset:
    sockets_info = []
    try:
        # Check static mesh sockets array
        sockets = sword_asset.get_editor_property("sockets")
        for s in sockets:
            s_name = s.get_editor_property("socket_name")
            s_loc = s.get_editor_property("relative_location")
            s_rot = s.get_editor_property("relative_rotation")
            sockets_info.append({
                "socket_name": str(s_name),
                "location": str(s_loc),
                "rotation": str(s_rot)
            })
    except Exception as e:
        print("[EmberWardenAudit] Sword sockets read error:", e)
        
    mat_slots = []
    try:
        mats = sword_asset.get_editor_property("static_materials")
        for m in mats:
            m_slot = m.get_editor_property("material_slot_name")
            m_interface = m.get_editor_property("material_interface")
            mat_slots.append({
                "slot_name": str(m_slot),
                "material": m_interface.get_path_name() if m_interface else None
            })
    except Exception as e:
        print("[EmberWardenAudit] Sword mats read error:", e)

    bounds = None
    try:
        bounds_box = sword_asset.get_bounds()
        bounds = {
            "box_extent": str(bounds_box.box_extent),
            "sphere_radius": float(bounds_box.sphere_radius)
        }
    except Exception:
        pass

    audit_results["SM_Boss01_Greatsword"] = {
        "loaded": True,
        "sockets": sockets_info,
        "materials": mat_slots,
        "bounds": bounds
    }
else:
    audit_results["SM_Boss01_Greatsword"] = {"loaded": False}

# 4. Inspect Boss01 Materials and Parameters
boss_mats = [
    "/Game/OneBossFight/Boss01/Materials/M_Boss01_Blade_Glow",
    "/Game/OneBossFight/Boss01/Materials/M_Boss01_EmberGlow",
    "/Game/OneBossFight/Boss01/Materials/M_Boss01_BlackPlate",
    "/Game/OneBossFight/Boss01/Materials/M_Boss01_CrimsonCloth",
    "/Game/OneBossFight/Boss01/Materials/M_Boss01_GoldTrim",
    "/Game/OneBossFight/Boss01/Materials/M_Boss01_Master"
]
audit_results["materials"] = {}
for m_path in boss_mats:
    m_asset = unreal.EditorAssetLibrary.load_asset(m_path)
    if m_asset:
        mat_entry = {
            "loaded": True,
            "class": m_asset.get_class().get_name()
        }
        if isinstance(m_asset, unreal.MaterialInstanceConstant):
            try:
                parent = m_asset.get_editor_property("parent")
                mat_entry["parent"] = parent.get_path_name() if parent else None
            except Exception:
                pass
            
            # Inspect scalar parameters
            try:
                scalars = m_asset.get_editor_property("scalar_parameter_values")
                mat_entry["scalar_params"] = [
                    {"name": str(p.parameter_info.name), "value": float(p.parameter_value)}
                    for p in scalars
                ]
            except Exception:
                pass
                
            # Inspect vector parameters
            try:
                vectors = m_asset.get_editor_property("vector_parameter_values")
                mat_entry["vector_params"] = [
                    {
                        "name": str(p.parameter_info.name),
                        "value": [float(p.parameter_value.r), float(p.parameter_value.g), float(p.parameter_value.b), float(p.parameter_value.a)]
                    }
                    for p in vectors
                ]
            except Exception:
                pass

            # Inspect texture parameters
            try:
                textures = m_asset.get_editor_property("texture_parameter_values")
                mat_entry["texture_params"] = [
                    {
                        "name": str(p.parameter_info.name),
                        "texture": p.parameter_value.get_path_name() if p.parameter_value else None
                    }
                    for p in textures
                ]
            except Exception:
                pass

        audit_results["materials"][m_path] = mat_entry
    else:
        audit_results["materials"][m_path] = {"loaded": False}

# 5. Inspect Boss01 Body Skeletal Meshes and Skeletons
body_assets = [
    "/Game/OneBossFight/Boss01/Body/SK_Boss01_Crown",
    "/Game/OneBossFight/Boss01/Body/SK_Boss01_Body",
    "/Game/OneBossFight/Boss01/Body/SK_Boss01_BrazierGauntlet",
    "/Game/OneBossFight/Boss01/Body/SK_Boss01_Mantle"
]
audit_results["body_meshes"] = {}
for b_path in body_assets:
    b_asset = unreal.EditorAssetLibrary.load_asset(b_path)
    if b_asset:
        skel = None
        try:
            skel = b_asset.get_editor_property("skeleton")
        except Exception:
            pass
            
        mats_info = []
        try:
            mats = b_asset.get_editor_property("materials")
            for m in mats:
                m_slot = m.get_editor_property("material_slot_name")
                m_interface = m.get_editor_property("material_interface")
                mats_info.append({
                    "slot_name": str(m_slot),
                    "material": m_interface.get_path_name() if m_interface else None
                })
        except Exception:
            pass

        audit_results["body_meshes"][b_path] = {
            "loaded": True,
            "class": b_asset.get_class().get_name(),
            "skeleton": skel.get_path_name() if skel else None,
            "materials": mats_info
        }
    else:
        audit_results["body_meshes"][b_path] = {"loaded": False}

# Save results
out_dir = r"c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\EmberWarden"
os.makedirs(out_dir, exist_ok=True)
out_file = os.path.join(out_dir, "EMBER_WARDEN_AUDIT_DATA.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(audit_results, f, indent=2)

print("[EmberWardenAudit] Completed detailed audit. Saved to:", out_file)
