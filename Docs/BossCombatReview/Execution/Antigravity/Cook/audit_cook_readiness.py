"""Cook and Package Readiness Audit (AB-A41..AB-A45).
Runs in UnrealEditor-Cmd under ENGINE_LOCK. Read-only inspection.
"""
import unreal
import json
import os

OUT_LOG_PATH = r"c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\Cook\COOK_AUDIT_LOG.txt"
OUT_JSON_PATH = r"c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\Cook\COOK_AUDIT_DATA.json"

log_lines = []
def log(m):
    msg = "[CookAudit] " + m
    unreal.log(msg)
    log_lines.append(msg)

output_data = {}

# 1. AB-A41: Audit Player Animations
er_assets = [
    "/Game/OneBossFight/Player/Animations/AM_ER_Attack_GuardCounter",
    "/Game/OneBossFight/Player/Animations/AM_ER_Backstep_Back",
    "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Light",
    "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Heavy_Plunge",
    "/Game/OneBossFight/Player/Animations/AN_ER_Attack_GuardCounter",
    "/Game/OneBossFight/Player/Animations/AN_ER_Backstep_Back",
    "/Game/OneBossFight/Player/Animations/AN_ER_Attack_Air_Light",
    "/Game/OneBossFight/Player/Animations/AN_ER_Attack_Air_Heavy_Plunge",
]
er_results = {}
for path in er_assets:
    a = unreal.load_asset(path)
    if a:
        er_results[path] = {"found": True, "class": a.get_class().get_name()}
        log("ER Asset OK: %s (%s)" % (a.get_name(), a.get_class().get_name()))
    else:
        er_results[path] = {"found": False}
        log("ER Asset MISSING: %s" % path)
output_data["player_animations"] = er_results

# 2. AB-A42: Audit Tier 2 Art Assets
t2_assets = [
    "/Game/OneBossFight/Boss01/Animations/AM_Boss01_ParryRecoil",
    "/Game/OneBossFight/Boss01/Animations/AN_Boss01_ParryRecoil",
    "/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura",
    "/Game/OneBossFight/Effects/PPM_ParryDistortion",
    "/Game/OneBossFight/Data/MPC_CombatFeedback",
]
t2_results = {}
for path in t2_assets:
    a = unreal.load_asset(path)
    if a:
        t2_results[path] = {"found": True, "class": a.get_class().get_name()}
        log("Tier 2 Asset OK: %s (%s)" % (a.get_name(), a.get_class().get_name()))
    else:
        t2_results[path] = {"found": False}
        log("Tier 2 Asset MISSING: %s" % path)
output_data["tier2_assets"] = t2_results

# 3. AB-A43: Audit UI Textures
ui_textures = [
    "/Game/OneBossFight/UI/Art/T_Boss01_FlaskPlate",
    "/Game/OneBossFight/UI/Art/T_Boss01_Flask_Full",
    "/Game/OneBossFight/UI/Art/T_Boss01_Flask_Half",
    "/Game/OneBossFight/UI/Art/T_Boss01_Flask_Empty",
]
ui_results = {}
for path in ui_textures:
    tex = unreal.load_asset(path)
    if tex:
        srgb = True
        try:
            srgb = bool(tex.get_editor_property("srgb"))
        except Exception:
            try:
                srgb = bool(tex.get_editor_property("s_rgb"))
            except Exception:
                pass
        compression = "Default"
        try:
            compression = str(tex.get_editor_property("compression_settings"))
        except Exception:
            pass
        ui_results[path] = {
            "found": True,
            "srgb": srgb,
            "compression": compression
        }
        log("UI Tex %s: sRGB=%s comp=%s" % (tex.get_name(), srgb, compression))
    else:
        ui_results[path] = {"found": False}
        log("UI Tex MISSING: %s" % path)
output_data["ui_textures"] = ui_results

# 4. AB-A44: Audit Arena Meshes
arena_meshes = [
    "/Game/ParagonSevarog/FX/Meshes/Shapes/SM_Sevarog_Comet_v1",
    "/Game/OneBossFight/Boss01/Remains/SM_Boss01_CorpseStatue",
]
mesh_results = {}
for path in arena_meshes:
    m = unreal.load_asset(path)
    if m:
        mesh_results[path] = {"found": True, "class": m.get_class().get_name()}
        log("Mesh OK: %s" % m.get_name())
    else:
        mesh_results[path] = {"found": False}
output_data["arena_meshes"] = mesh_results

os.makedirs(os.path.dirname(OUT_JSON_PATH), exist_ok=True)
with open(OUT_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2)

with open(OUT_LOG_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines) + "\n")

log("Audit written to %s and %s" % (OUT_JSON_PATH, OUT_LOG_PATH))
unreal.SystemLibrary.quit_editor()
