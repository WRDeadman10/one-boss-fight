"""Boss Visual Effects and Material Transitions Audit (AB-A31..AB-A35).
Runs in UnrealEditor-Cmd under ENGINE_LOCK. Read-only inspection.
"""
import unreal
import json
import os

OUT_LOG_PATH = r"c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\VFX\VFX_AUDIT_LOG.txt"
OUT_JSON_PATH = r"c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\VFX\VFX_AUDIT_DATA.json"

log_lines = []
def log(m):
    msg = "[VFXAudit] " + m
    unreal.log(msg)
    log_lines.append(msg)

output_data = {}

# 1. Audit Sevarog Scythe Trail / Mesh Emitters
trail_ps_path = "/Game/ParagonSevarog/FX/Particles/Abilities/Primary/FX/P_SevarogTrails"
trail_ps = unreal.load_asset(trail_ps_path)
trail_mesh_path = "/Game/ParagonSevarog/FX/Meshes/Smoke/SM_Sevarog_WeaponEnergy"
trail_mesh = unreal.load_asset(trail_mesh_path)
trail_data = {
    "particle_system_found": bool(trail_ps),
    "mesh_found": bool(trail_mesh)
}
log("Trail PS: %s, Mesh: %s" % (bool(trail_ps), bool(trail_mesh)))
output_data["scythe_trail"] = trail_data

# 2. Audit NS_Boss_PhaseTwoAura
aura_path = "/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura"
aura = unreal.load_asset(aura_path)
aura_data = {"found": bool(aura)}
if aura:
    aura_data["path"] = aura_path
    aura_data["class"] = aura.get_class().get_name()
    log("NS_Boss_PhaseTwoAura found")
else:
    log("NS_Boss_PhaseTwoAura MISSING")
output_data["phase_two_aura"] = aura_data

# 3. Audit Boss Remains Dissolve Material
mat_path = "/Game/OneBossFight/Boss01/Remains/M_Boss01_Remains"
mat = unreal.load_asset(mat_path)
dissolve_tex_path = "/Game/OneBossFight/Boss01/Remains/T_Boss01_DissolveNoise"
dissolve_tex = unreal.load_asset(dissolve_tex_path)
remains_data = {
    "material_found": bool(mat),
    "noise_texture_found": bool(dissolve_tex)
}
log("M_Boss01_Remains: %s, T_Boss01_DissolveNoise: %s" % (bool(mat), bool(dissolve_tex)))
output_data["dissolve_remains"] = remains_data

# 4. Audit Stagger Down Animations
stagger_down_path = "/Game/OneBossFight/Boss01/Animations/AN_Boss01_StaggerDown"
stagger_down = unreal.load_asset(stagger_down_path)
stagger_fall_path = "/Game/OneBossFight/Boss01/Animations/AN_Boss01_StaggerFall"
stagger_fall = unreal.load_asset(stagger_fall_path)
stagger_data = {
    "stagger_down_found": bool(stagger_down),
    "stagger_down_length": round(float(stagger_down.get_play_length()), 4) if stagger_down else 0.0,
    "stagger_fall_found": bool(stagger_fall),
    "stagger_fall_length": round(float(stagger_fall.get_play_length()), 4) if stagger_fall else 0.0
}
log("StaggerDown: len=%.4f, StaggerFall: len=%.4f" % (stagger_data["stagger_down_length"], stagger_data["stagger_fall_length"]))
output_data["stagger"] = stagger_data

os.makedirs(os.path.dirname(OUT_JSON_PATH), exist_ok=True)
with open(OUT_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2)

with open(OUT_LOG_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines) + "\n")

log("Audit written to %s and %s" % (OUT_JSON_PATH, OUT_LOG_PATH))
unreal.SystemLibrary.quit_editor()
