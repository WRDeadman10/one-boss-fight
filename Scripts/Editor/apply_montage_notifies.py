"""
Applies verified pack notifies to the 5 newly trimmed montages per Lead directives [C-986] and [C-987],
strictly conforming to Codex's finalized AA_A08_NOTIFY_FRAMES_TABLE.md.
Uses remove_all_animation_notify_tracks to clean previous state,
asserts notifies before saving, forces save with only_if_is_dirty=False,
and logs full describe_notifies readback for verification.
"""

import unreal

AL = unreal.AnimationLibrary

def log(msg):
    unreal.log(f"[ApplyNotifies] {msg}")

def get_all_classes():
    classes = {}
    templates = [
        "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryA_Montage",
        "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage",
        "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Ability_E_Anim_Montage",
        "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/HitReactions/HitReact_Back_Montage"
    ]
    for p in templates:
        m = unreal.load_asset(p)
        if not m:
            continue
        for ev in AL.get_animation_notify_events(m):
            st = ev.get_editor_property("notify_state_class")
            no = ev.get_editor_property("notify")
            obj = st if st is not None else no
            if obj:
                cname = obj.get_class().get_name()
                classes[cname] = (obj.get_class(), st is not None, obj)
                
    # Direct class fallbacks
    fallbacks = {
        "ANS_InputBuffer_C": "/Game/AdvancedARPGCombat/AdvancedCombatFramework/Input/AnimNotifies/ANS_InputBuffer.ANS_InputBuffer_C",
        "ANS_DisableMovement_C": "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AnimNotifies/ANS_DisableMovement.ANS_DisableMovement_C",
        "ANS_SetDesiredRotation_C": "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AnimNotifies/ANS_SetDesiredRotation.ANS_SetDesiredRotation_C",
        "ANS_CancelFrames_C": "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AnimNotifies/ANS_CancelFrames.ANS_CancelFrames_C",
        "ANS_CollisionTrace_C": "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CollisionSystem/AnimNotifies/ANS_CollisionTrace.ANS_CollisionTrace_C",
        "ANS_MovementCancel_C": "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AnimNotifies/ANS_MovementCancel.ANS_MovementCancel_C",
        "ANS_iFrames_C": "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AnimNotifies/ANS_iFrames.ANS_iFrames_C",
    }
    for cname, cpath in fallbacks.items():
        if cname not in classes:
            cls = unreal.load_object(None, cpath)
            if cls:
                classes[cname] = (cls, True, None)

    return classes

def apply_notifies():
    log("Starting clean montage notifies application per C-987 finalized table...")
    classes = get_all_classes()
    log(f"Loaded {len(classes)} available notify classes: {sorted(classes.keys())}")
    
    # Target configurations per Codex AA_A08_NOTIFY_FRAMES_TABLE.md:
    targets = [
        # AM_ER_Attack_GuardCounter (0.8000 s)
        (
            "/Game/OneBossFight/Player/Animations/AM_ER_Attack_GuardCounter",
            7,
            [
                ("1", "ANS_DisableMovement_C", True, 0.0000, 0.8000),
                ("2", "ANS_SetDesiredRotation_C", True, 0.0000, 0.1232),
                ("3", "ANS_CancelFrames_C", True, 0.0000, 0.1371),
                ("4", "ANS_InputBuffer_C", True, 0.1510, 0.1200),
                ("5", "ANS_CollisionTrace_C", True, 0.1682, 0.0894),
                ("6", "AnimNotify_PlaySound", False, 0.1684, 0.0),
                ("7", "ANS_MovementCancel_C", True, 0.3507, 0.4493),
            ]
        ),
        # AM_ER_Attack_Air_Light (0.5667 s)
        (
            "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Light",
            3,
            [
                ("1", "ANS_DisableMovement_C", True, 0.0000, 0.5667),
                ("2", "ANS_MovementCancel_C", True, 0.0930, 0.4737),
                ("3", "ANS_CollisionTrace_C", True, 0.2000, 0.1333),
            ]
        ),
        # AM_ER_Attack_Air_Heavy_Plunge (0.8667 s)
        (
            "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Heavy_Plunge",
            4,
            [
                ("1", "ANS_DisableMovement_C", True, 0.0000, 0.8667),
                ("2", "ANS_InputBuffer_C", True, 0.0000, 0.1640),
                ("3", "ANS_MovementCancel_C", True, 0.2930, 0.5737),
                ("4", "ANS_CollisionTrace_C", True, 0.3670, 0.1663),
            ]
        ),
        # AM_ER_Backstep_Back (0.4667 s - NO ANS_SetDesiredRotation per C-987)
        (
            "/Game/OneBossFight/Player/Animations/AM_ER_Backstep_Back",
            2,
            [
                ("1", "ANS_iFrames_C", True, 0.0750, 0.2678),
                ("2", "ANS_InputBuffer_C", True, 0.1640, 0.1874),
            ]
        ),
        # AM_Boss01_ParryRecoil (0.6000 s)
        (
            "/Game/OneBossFight/Boss01/Animations/AM_Boss01_ParryRecoil",
            1,
            [
                ("1", "ANS_InputBuffer_C", True, 0.0000, 0.2962),
            ]
        ),
    ]
    
    results = {}
    
    for path, expected_count, specs in targets:
        m = unreal.EditorAssetLibrary.load_asset(path)
        if not m:
            raise RuntimeError(f"Cannot load target montage {path}")
        
        m_name = m.get_name()
        log(f"Configuring {m_name} (length {m.get_play_length():.4f}s)...")
        
        # 1. Clean all existing notify tracks and events completely
        AL.remove_all_animation_notify_tracks(m)
        
        # 2. Add required tracks
        needed_tracks = sorted(list(set(s[0] for s in specs)))
        for t in needed_tracks:
            AL.add_animation_notify_track(m, t)
        
        # 3. Add notifies
        for track_name, cname, is_state, start_t, dur in specs:
            if cname not in classes:
                raise RuntimeError(f"Class {cname} missing from class cache for {m_name}")
            cls, _, src_obj = classes[cname]
            
            if is_state:
                inst = AL.add_animation_notify_state_event(m, track_name, start_t, dur, cls)
                if not inst:
                    raise RuntimeError(f"Failed to add state {cname} on {m_name}")
                if src_obj:
                    if cname == "ANS_SetDesiredRotation_C":
                        for prop in ["RotationInterpSpeed", "Desired Rotation Type"]:
                            try:
                                val = src_obj.get_editor_property(prop)
                                inst.set_editor_property(prop, val)
                            except Exception:
                                pass
                    elif cname == "ANS_CollisionTrace_C":
                        for prop in ["AttackData", "Collision Target Tag", "EventTag"]:
                            try:
                                val = src_obj.get_editor_property(prop)
                                inst.set_editor_property(prop, val)
                            except Exception:
                                pass
            else:
                inst = AL.add_animation_notify_event(m, track_name, start_t, cls)
                if not inst:
                    raise RuntimeError(f"Failed to add notify {cname} on {m_name}")
                if src_obj and cname == "AnimNotify_PlaySound":
                    try:
                        snd = src_obj.get_editor_property("sound")
                        inst.set_editor_property("sound", snd)
                    except Exception:
                        pass
        
        # 4. Assert exact count
        events = AL.get_animation_notify_events(m)
        ev_count = len(events)
        log(f"{m_name}: total {ev_count} notifies (expected {expected_count})")
        assert ev_count == expected_count, f"{m_name} notify count {ev_count} != expected {expected_count}"
        
        # 5. Force save asset
        m.modify()
        saved = unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)
        assert saved, f"Failed to save {m_name}"
        log(f"SAVED {m_name} successfully.")
        
        # 6. Read back with describe_notifies
        desc_lines = [str(line) for line in unreal.RPGMontageUtils.describe_notifies(m)]
        results[m_name] = desc_lines
    
    log("================ CLEAN AUTHORITATIVE NOTIFY READBACK ================")
    for m_name, lines in results.items():
        log(f"--- {m_name} ---")
        for line in lines:
            log(f"  {line}")
    log("================ END SUMMARY ================")

if __name__ == "__main__":
    apply_notifies()
