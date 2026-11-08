"""
Re-slices and re-authors AM_ER_Attack_Air_Light and AM_ER_Attack_Air_Heavy_Plunge
per Lead directive [C-995] and Codex updated AA_A08_NOTIFY_FRAMES_TABLE.md:
- AirLight: slice PrimaryB 0.200..0.800 s (length 0.600 s).
  ANS_DisableMovement_C (0.000..0.600 s)
  ANS_CollisionTrace_C (0.150..0.336 s, duration 0.186 s, AttackData UNSET)
  ANS_MovementCancel_C REMOVED
- AirHeavy: slice PrimaryB 0.200..1.067 s (length 0.867 s).
  ANS_DisableMovement_C (0.000..0.867 s)
  ANS_InputBuffer_C (0.150..0.364 s, duration 0.214 s)
  ANS_CollisionTrace_C (0.150..0.336 s, duration 0.186 s, AttackData UNSET)
  ANS_MovementCancel_C REMOVED
- Blend-in set to 0.100 s on both.
- Subobjects cleaned (AttackData unset).
- Export .t3d to Saved/C995_t3d/.
"""

import os
import unreal

AL = unreal.AnimationLibrary

def log(msg):
    unreal.log(f"[C995Reauthor] {msg}")

def run():
    out_t3d_dir = "C:/UnrealProject/OneBossFight/Saved/C995_t3d"
    os.makedirs(out_t3d_dir, exist_ok=True)

    cls_disable = unreal.load_object(None, "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AnimNotifies/ANS_DisableMovement.ANS_DisableMovement_C")
    cls_input = unreal.load_object(None, "/Game/AdvancedARPGCombat/AdvancedCombatFramework/Input/AnimNotifies/ANS_InputBuffer.ANS_InputBuffer_C")
    cls_trace = unreal.load_object(None, "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CollisionSystem/AnimNotifies/ANS_CollisionTrace.ANS_CollisionTrace_C")

    # Target 1: AM_ER_Attack_Air_Light (0.600 s)
    light_path = "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Light"
    m_light = unreal.EditorAssetLibrary.load_asset(light_path)
    assert m_light, f"Failed to load {light_path}"

    log("Re-slicing AM_ER_Attack_Air_Light to 0.200..0.800 s...")
    ok = unreal.RPGMontageUtils.set_montage_segment_range(m_light, 0.200, 0.800)
    assert ok, "Failed to set segment range for Air Light"
    log(f"Air Light new length: {m_light.get_play_length():.4f}s")

    # Set blend in
    try:
        bi = m_light.get_editor_property("blend_in")
        try:
            bi.set_editor_property("blend_time", 0.100)
        except Exception:
            bi.blend_time = 0.100
        m_light.set_editor_property("blend_in", bi)
    except Exception as e:
        log(f"blend_in error: {e}")

    AL.remove_all_animation_notify_tracks(m_light)
    AL.add_animation_notify_track(m_light, "1")
    AL.add_animation_notify_track(m_light, "2")

    ev_dis = AL.add_animation_notify_state_event(m_light, "1", 0.000, 0.600, cls_disable)
    ev_trc = AL.add_animation_notify_state_event(m_light, "2", 0.150, 0.186, cls_trace)
    try:
        ev_trc.set_editor_property("AttackData", None)
        ev_trc.modify()
    except Exception:
        pass

    assert len(AL.get_animation_notify_events(m_light)) == 2

    # Clean subobjects
    for i in range(10):
        sub = unreal.load_object(None, f"{light_path}.AM_ER_Attack_Air_Light:ANS_CollisionTrace_C_{i}")
        if sub:
            try:
                sub.set_editor_property("AttackData", None)
                sub.modify()
            except Exception:
                pass

    m_light.modify()
    saved = unreal.EditorAssetLibrary.save_asset(light_path, only_if_is_dirty=False)
    assert saved, "Failed to save Air Light"
    log("SAVED AM_ER_Attack_Air_Light")

    task = unreal.AssetExportTask()
    task.object = m_light
    task.filename = f"{out_t3d_dir}/AM_ER_Attack_Air_Light.t3d"
    task.automated = True
    task.prompt = False
    task.replace_identical = True
    unreal.Exporter.run_asset_export_task(task)
    log("Exported AM_ER_Attack_Air_Light.t3d")

    # Target 2: AM_ER_Attack_Air_Heavy_Plunge (0.867 s)
    heavy_path = "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Heavy_Plunge"
    m_heavy = unreal.EditorAssetLibrary.load_asset(heavy_path)
    assert m_heavy, f"Failed to load {heavy_path}"

    log("Re-slicing AM_ER_Attack_Air_Heavy_Plunge to 0.200..1.067 s...")
    ok = unreal.RPGMontageUtils.set_montage_segment_range(m_heavy, 0.200, 1.066667)
    assert ok, "Failed to set segment range for Air Heavy"
    log(f"Air Heavy new length: {m_heavy.get_play_length():.4f}s")

    try:
        bi = m_heavy.get_editor_property("blend_in")
        try:
            bi.set_editor_property("blend_time", 0.100)
        except Exception:
            bi.blend_time = 0.100
        m_heavy.set_editor_property("blend_in", bi)
    except Exception as e:
        log(f"blend_in error: {e}")

    AL.remove_all_animation_notify_tracks(m_heavy)
    AL.add_animation_notify_track(m_heavy, "1")
    AL.add_animation_notify_track(m_heavy, "2")
    AL.add_animation_notify_track(m_heavy, "3")

    AL.add_animation_notify_state_event(m_heavy, "1", 0.000, 0.867, cls_disable)
    AL.add_animation_notify_state_event(m_heavy, "2", 0.150, 0.214, cls_input)
    ev_htrc = AL.add_animation_notify_state_event(m_heavy, "3", 0.150, 0.186, cls_trace)
    try:
        ev_htrc.set_editor_property("AttackData", None)
        ev_htrc.modify()
    except Exception:
        pass

    assert len(AL.get_animation_notify_events(m_heavy)) == 3

    for i in range(10):
        sub = unreal.load_object(None, f"{heavy_path}.AM_ER_Attack_Air_Heavy_Plunge:ANS_CollisionTrace_C_{i}")
        if sub:
            try:
                sub.set_editor_property("AttackData", None)
                sub.modify()
            except Exception:
                pass

    m_heavy.modify()
    saved = unreal.EditorAssetLibrary.save_asset(heavy_path, only_if_is_dirty=False)
    assert saved, "Failed to save Air Heavy"
    log("SAVED AM_ER_Attack_Air_Heavy_Plunge")

    task = unreal.AssetExportTask()
    task.object = m_heavy
    task.filename = f"{out_t3d_dir}/AM_ER_Attack_Air_Heavy_Plunge.t3d"
    task.automated = True
    task.prompt = False
    task.replace_identical = True
    unreal.Exporter.run_asset_export_task(task)
    log("Exported AM_ER_Attack_Air_Heavy_Plunge.t3d")

    # Readback
    log("=== READBACK ===")
    for m in [m_light, m_heavy]:
        lines = [str(x) for x in unreal.RPGMontageUtils.describe_notifies(m)]
        for l in lines:
            log(f"  {m.get_name()}: {l}")

if __name__ == "__main__":
    run()
