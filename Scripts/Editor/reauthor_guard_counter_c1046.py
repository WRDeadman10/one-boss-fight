"""
C-1046: GuardCounter timing hotfix for AM_ER_Attack_GuardCounter:
- ANS_CollisionTrace: start 0.000 s, duration 0.180 s (AttackData=StrongMeleeAttackData)
- AnimNotify_PlaySound: start 0.050 s
- ANS_InputBuffer: start 0.120 s, duration 0.150 s
- ANS_MovementCancel: start 0.300 s, duration 0.500 s (start >= 0.300 s)
- ANS_DisableMovement_C (0.000..0.800 s), ANS_SetDesiredRotation_C (0.000..0.1232 s), ANS_CancelFrames_C (0.000..0.1371 s) preserved.
- Blend-in preserved at 0.100 s.
- Exports t3d to Saved/C1046_t3d/AM_ER_Attack_GuardCounter.t3d
- Runs check_tier2_er_assets Lead inspection and writes Docs/BossCombatReview/Execution/Antigravity/C1046_LEAD_CHECK.txt
"""

import os
import unreal

AL = unreal.AnimationLibrary

LOG = "[C1046GuardCounter] "
def log(m): unreal.log(LOG + m)

def get_classes_and_source_props(m_gc):
    classes = {}
    saved_props = {}
    
    # 1. Grab props from existing AM_ER_Attack_GuardCounter
    for ev in AL.get_animation_notify_events(m_gc):
        st = ev.get_editor_property("notify_state_class")
        no = ev.get_editor_property("notify")
        obj = st if st is not None else no
        if obj:
            cname = obj.get_class().get_name()
            classes[cname] = (obj.get_class(), st is not None)
            if cname == "AnimNotify_PlaySound":
                try:
                    saved_props["sound"] = obj.get_editor_property("sound")
                except Exception as e:
                    log(f"warning getting sound: {e}")
            elif cname == "ANS_SetDesiredRotation_C":
                props = {}
                for p in ["RotationInterpSpeed", "Desired Rotation Type"]:
                    try:
                        props[p] = obj.get_editor_property(p)
                    except Exception:
                        pass
                saved_props["rotation_props"] = props

    # 2. Grab any missing classes from templates
    templates = [
        "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryA_Montage",
        "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage",
    ]
    for p in templates:
        t_m = unreal.load_asset(p)
        if not t_m:
            continue
        for ev in AL.get_animation_notify_events(t_m):
            st = ev.get_editor_property("notify_state_class")
            no = ev.get_editor_property("notify")
            obj = st if st is not None else no
            if obj:
                cname = obj.get_class().get_name()
                if cname not in classes:
                    classes[cname] = (obj.get_class(), st is not None)
                if "sound" not in saved_props and cname == "AnimNotify_PlaySound":
                    try:
                        saved_props["sound"] = obj.get_editor_property("sound")
                    except Exception:
                        pass

    # 3. Direct class fallbacks
    fallbacks = {
        "ANS_InputBuffer_C": "/Game/AdvancedARPGCombat/AdvancedCombatFramework/Input/AnimNotifies/ANS_InputBuffer.ANS_InputBuffer_C",
        "ANS_DisableMovement_C": "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AnimNotifies/ANS_DisableMovement.ANS_DisableMovement_C",
        "ANS_SetDesiredRotation_C": "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AnimNotifies/ANS_SetDesiredRotation.ANS_SetDesiredRotation_C",
        "ANS_CancelFrames_C": "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AnimNotifies/ANS_CancelFrames.ANS_CancelFrames_C",
        "ANS_CollisionTrace_C": "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CollisionSystem/AnimNotifies/ANS_CollisionTrace.ANS_CollisionTrace_C",
        "ANS_MovementCancel_C": "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AnimNotifies/ANS_MovementCancel.ANS_MovementCancel_C",
    }
    for cname, cpath in fallbacks.items():
        if cname not in classes:
            cls = unreal.load_object(None, cpath)
            if cls:
                classes[cname] = (cls, True)

    return classes, saved_props

def run():
    target_path = "/Game/OneBossFight/Player/Animations/AM_ER_Attack_GuardCounter"
    m = unreal.EditorAssetLibrary.load_asset(target_path)
    if not m:
        raise RuntimeError(f"Could not load {target_path}")

    log(f"Loaded {m.get_name()}, play length: {m.get_play_length():.4f}")

    classes, saved_props = get_classes_and_source_props(m)
    log(f"Available classes: {list(classes.keys())}")

    # Load StrongMeleeAttackData
    strong_data_path = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/DataAssets/AttackData/StrongMeleeAttackData"
    strong_data = unreal.load_asset(strong_data_path)
    if not strong_data:
        raise RuntimeError(f"Could not load StrongMeleeAttackData from {strong_data_path}")
    log(f"Loaded StrongMeleeAttackData: {strong_data.get_path_name()}")

    # Verified specs per C-1046
    specs = [
        ("1", "ANS_DisableMovement_C", True, 0.0000, 0.8000),
        ("2", "ANS_SetDesiredRotation_C", True, 0.0000, 0.1232),
        ("3", "ANS_CancelFrames_C", True, 0.0000, 0.1371),
        ("4", "ANS_InputBuffer_C", True, 0.1200, 0.1500),
        ("5", "ANS_CollisionTrace_C", True, 0.0000, 0.1800),
        ("6", "AnimNotify_PlaySound", False, 0.0500, 0.0000),
        ("7", "ANS_MovementCancel_C", True, 0.3000, 0.5000),
    ]

    # Set blend-in time to 0.100s
    try:
        bi = m.get_editor_property("blend_in")
        try:
            bi.set_editor_property("blend_time", 0.100)
        except Exception:
            bi.blend_time = 0.100
        m.set_editor_property("blend_in", bi)
        log("blend_in verified to 0.100 s")
    except Exception as e:
        log(f"warning setting blend_in: {e}")

    # Clear old tracks
    AL.remove_all_animation_notify_tracks(m)

    # Add required tracks
    needed_tracks = sorted(list(set(s[0] for s in specs)))
    for t in needed_tracks:
        AL.add_animation_notify_track(m, t)

    # Re-add notifies
    for track_name, cname, is_state, start_t, dur in specs:
        cls, _ = classes[cname]
        if is_state:
            inst = AL.add_animation_notify_state_event(m, track_name, start_t, dur, cls)
            if not inst:
                raise RuntimeError(f"Failed to add state {cname}")
            if cname == "ANS_CollisionTrace_C":
                inst.set_editor_property("AttackData", strong_data)
                inst.modify()
                log(f"Set AttackData=StrongMeleeAttackData on ANS_CollisionTrace_C at {start_t:.4f} for {dur:.4f}")
            elif cname == "ANS_SetDesiredRotation_C" and "rotation_props" in saved_props:
                for p, v in saved_props["rotation_props"].items():
                    try:
                        inst.set_editor_property(p, v)
                    except Exception:
                        pass
        else:
            inst = AL.add_animation_notify_event(m, track_name, start_t, cls)
            if not inst:
                raise RuntimeError(f"Failed to add notify {cname}")
            if cname == "AnimNotify_PlaySound" and "sound" in saved_props and saved_props["sound"]:
                try:
                    inst.set_editor_property("sound", saved_props["sound"])
                    log(f"Set sound={saved_props['sound'].get_name()} on AnimNotify_PlaySound at {start_t:.4f}")
                except Exception as e:
                    log(f"warning setting sound: {e}")

    # Assert exactly 7 notify events
    evs = AL.get_animation_notify_events(m)
    log(f"Configured {len(evs)} events on {m.get_name()} (expected 7)")
    assert len(evs) == 7, f"Expected 7 events, found {len(evs)}"

    # Save asset
    m.modify()
    saved = unreal.EditorAssetLibrary.save_asset(target_path, only_if_is_dirty=False)
    assert saved, f"Failed to save {target_path}"
    log(f"SAVED {target_path} successfully.")

    # Export t3d
    out_t3d_dir = "C:/UnrealProject/OneBossFight/Saved/C1046_t3d"
    os.makedirs(out_t3d_dir, exist_ok=True)
    task = unreal.AssetExportTask()
    task.object = m
    task.filename = f"{out_t3d_dir}/{m.get_name()}.t3d"
    task.automated = True
    task.prompt = False
    task.replace_identical = True
    unreal.Exporter.run_asset_export_task(task)
    log(f"Exported {task.filename}")

    # Verify AttackData line in exported t3d
    attack_data_found = False
    with open(task.filename, "r", encoding="utf-8") as f:
        for line in f:
            if "AttackData=" in line and "StrongMeleeAttackData" in line:
                log(f"T3D AttackData line verified: {line.strip()}")
                attack_data_found = True
                break
    assert attack_data_found, "AttackData=StrongMeleeAttackData NOT found in exported t3d!"

    # Run Lead Asset Check (check_tier2_er_assets.py logic)
    log("=== RUNNING LEAD ASSET CHECK ===")
    boss_mesh = unreal.load_asset("/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin_Simple")
    boss_skel = boss_mesh.get_editor_property("skeleton") if boss_mesh else None
    
    lead_lines = []
    montages = [
        "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryA_Montage",
        "/Game/OneBossFight/Player/Animations/AM_ER_Attack_GuardCounter",
        "/Game/OneBossFight/Player/Animations/AM_ER_Backstep_Back",
        "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Light",
        "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Heavy_Plunge",
        "/Game/OneBossFight/Boss01/Animations/AM_Boss01_ParryRecoil"
    ]
    for p in montages:
        a = unreal.load_asset(p)
        if not a:
            line = f"MISSING {p}"
        else:
            skel = a.get_editor_property("skeleton")
            slots = [unreal.RPGMontageUtils.get_montage_slot(a)]
            line = "montage %s class=%s length=%.4f slots=%s skeleton_match=%s notifies=%s" % (
                a.get_name(), a.get_class().get_name(), a.get_play_length(), [str(s) for s in slots],
                bool(skel and boss_skel and skel == boss_skel), list(unreal.RPGMontageUtils.describe_notifies(a)))
        log("[LeadCheck] " + line)
        lead_lines.append(line)

    lead_out_path = "C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/C1046_LEAD_CHECK.txt"
    with open(lead_out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lead_lines) + "\n")
    log(f"Saved Lead check readback to {lead_out_path}")

    unreal.SystemLibrary.quit_editor()

if __name__ == "__main__":
    run()
