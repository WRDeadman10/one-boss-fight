"""Audio Cue and Montage Audio Notify Audit (AB-A16..AB-A20).
Runs in UnrealEditor-Cmd under ENGINE_LOCK. Read-only inspection.
"""
import unreal
import json
import os

OUT_LOG_PATH = r"c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\Audio\AUDIO_AUDIT_LOG.txt"
OUT_JSON_PATH = r"c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\Audio\AUDIO_AUDIT_DATA.json"

log_lines = []
def log(m):
    msg = "[AudioAudit] " + m
    unreal.log(msg)
    log_lines.append(msg)

output_data = {}

cues_to_inspect = [
    ("/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue", "A_Guardian_ImpactL_Cue"),
    ("/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/ShieldImpacts/ShieldImpacts_Cue", "ShieldImpacts_Cue"),
    ("/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Sword_Swing_Cue", "A_Sword_Swing_Cue"),
    ("/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/SwordImpacts/SwordImpact_Cue", "SwordImpact_Cue"),
]

cue_results = {}
for path, name in cues_to_inspect:
    cue = unreal.load_asset(path)
    if not cue:
        log("MISSING CUE: %s" % path)
        cue_results[name] = {"found": False, "path": path}
        continue
    
    vol = float(cue.get_editor_property("volume_multiplier"))
    pitch = float(cue.get_editor_property("pitch_multiplier"))
    sound_class = cue.get_editor_property("sound_class_object")
    sc_name = sound_class.get_name() if sound_class else "None"
    attenuation = cue.get_editor_property("attenuation_settings")
    att_name = attenuation.get_name() if attenuation else "None"
    
    first_node = cue.get_editor_property("first_node")
    node_name = first_node.get_class().get_name() if first_node else "None"

    cue_results[name] = {
        "found": True,
        "path": path,
        "volume_multiplier": round(vol, 3),
        "pitch_multiplier": round(pitch, 3),
        "sound_class": sc_name,
        "attenuation": att_name,
        "first_node": node_name
    }
    log("Cue %s: vol=%.2f pitch=%.2f class=%s att=%s node=%s" % (name, vol, pitch, sc_name, att_name, node_name))

output_data["cues"] = cue_results

montages_to_inspect = [
    ("/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Heavy_Plunge", "AM_ER_Attack_Air_Heavy_Plunge"),
    ("/Game/OneBossFight/Player/Animations/AM_ER_Attack_GuardCounter", "AM_ER_Attack_GuardCounter"),
    ("/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Light", "AM_ER_Attack_Air_Light"),
    ("/Game/OneBossFight/Player/Animations/AM_ER_Backstep_Back", "AM_ER_Backstep_Back"),
    ("/Game/OneBossFight/Boss01/Animations/AM_Boss01_ParryRecoil", "AM_Boss01_ParryRecoil"),
]

montage_results = {}
for path, name in montages_to_inspect:
    m = unreal.load_asset(path)
    if not m:
        log("MISSING MONTAGE: %s" % path)
        montage_results[name] = {"found": False, "path": path}
        continue
    
    length = float(m.get_play_length())
    notifies = list(unreal.RPGMontageUtils.describe_notifies(m))
    
    sound_notifies = []
    try:
        raw_notifies = m.get_editor_property("notifies")
        for ne in raw_notifies:
            obj = ne.get_editor_property("notify")
            time = float(ne.get_editor_property("link_value"))
            if obj and obj.get_class().get_name() == "AnimNotify_PlaySound":
                snd = obj.get_editor_property("sound")
                v = float(obj.get_editor_property("volume_multiplier"))
                p = float(obj.get_editor_property("pitch_multiplier"))
                sound_notifies.append({
                    "time": round(time, 4),
                    "sound": snd.get_path_name() if snd else "None",
                    "volume": round(v, 3),
                    "pitch": round(p, 3)
                })
    except Exception as e:
        log("Error reading raw notifies on %s: %s" % (name, str(e)))
    
    montage_results[name] = {
        "found": True,
        "path": path,
        "length": round(length, 4),
        "notifies": notifies,
        "sound_notifies": sound_notifies
    }
    log("Montage %s: len=%.4f sound_notifies=%s" % (name, length, str(sound_notifies)))

output_data["montages"] = montage_results

os.makedirs(os.path.dirname(OUT_JSON_PATH), exist_ok=True)
with open(OUT_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2)

with open(OUT_LOG_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines) + "\n")

log("Audit written to %s and %s" % (OUT_JSON_PATH, OUT_LOG_PATH))
unreal.SystemLibrary.quit_editor()
