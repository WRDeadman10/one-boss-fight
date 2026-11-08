"""
Re-authors AM_ER_Attack_GuardCounter, AM_ER_Attack_Air_Light, and AM_ER_Attack_Air_Heavy_Plunge
per Lead directive [C-992] and Codex [X-1407]:
1. CollisionTrace instance properties match pack template with AttackData UNSET (None).
2. MovementCancel starts after CollisionTrace ends:
   - AirLight: CollisionTrace 0.200..0.333 s; MovementCancel 0.333..0.567 s (duration 0.234 s).
   - AirHeavy: CollisionTrace 0.367..0.533 s; MovementCancel 0.533..0.867 s (duration 0.334 s).
3. Blend-in set to 0.100 s on ER montages.
4. Exports .t3d to Saved/C992_t3d/ to verify AttackData is absent in exported text.
"""

import os
import unreal

AL = unreal.AnimationLibrary

def log(msg):
    unreal.log(f"[C992Reauthor] {msg}")

def get_classes():
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

def run():
    classes = get_classes()
    log("Loaded classes.")

    targets = [
        # GuardCounter (0.800 s)
        (
            "/Game/OneBossFight/Player/Animations/AM_ER_Attack_GuardCounter",
            0.100,
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
        # Air Light (0.567 s)
        (
            "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Light",
            0.100,
            3,
            [
                ("1", "ANS_DisableMovement_C", True, 0.0000, 0.5667),
                ("2", "ANS_MovementCancel_C", True, 0.3333, 0.2334),
                ("3", "ANS_CollisionTrace_C", True, 0.2000, 0.1333),
            ]
        ),
        # Air Heavy Plunge (0.867 s)
        (
            "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Heavy_Plunge",
            0.100,
            4,
            [
                ("1", "ANS_DisableMovement_C", True, 0.0000, 0.8667),
                ("2", "ANS_InputBuffer_C", True, 0.0000, 0.1640),
                ("3", "ANS_MovementCancel_C", True, 0.5333, 0.3334),
                ("4", "ANS_CollisionTrace_C", True, 0.3670, 0.1663),
            ]
        ),
        # Backstep (0.467 s) - blend-in 0.100 s per C-992 / X-1407 proposal
        (
            "/Game/OneBossFight/Player/Animations/AM_ER_Backstep_Back",
            0.100,
            2,
            [
                ("1", "ANS_iFrames_C", True, 0.0750, 0.2678),
                ("2", "ANS_InputBuffer_C", True, 0.1640, 0.1874),
            ]
        ),
    ]

    out_t3d_dir = "C:/UnrealProject/OneBossFight/Saved/C992_t3d"
    os.makedirs(out_t3d_dir, exist_ok=True)

    for path, blend_time, expected_count, specs in targets:
        m = unreal.EditorAssetLibrary.load_asset(path)
        if not m:
            raise RuntimeError(f"Cannot load {path}")
        m_name = m.get_name()
        log(f"Reauthoring {m_name}...")

        # 1. Set blend-in time
        try:
            bi = m.get_editor_property("blend_in")
            try:
                bi.set_editor_property("blend_time", blend_time)
            except Exception:
                bi.blend_time = blend_time
            m.set_editor_property("blend_in", bi)
            log(f"{m_name}: blend_in set to {blend_time}")
        except Exception as e:
            log(f"{m_name}: warning setting blend_in: {e}")

        # 2. Clear tracks and notifies
        AL.remove_all_animation_notify_tracks(m)

        # 3. Add tracks
        needed_tracks = sorted(list(set(s[0] for s in specs)))
        for t in needed_tracks:
            AL.add_animation_notify_track(m, t)

        # 4. Add notifies
        for track_name, cname, is_state, start_t, dur in specs:
            cls, _, src_obj = classes[cname]
            if is_state:
                inst = AL.add_animation_notify_state_event(m, track_name, start_t, dur, cls)
                if not inst:
                    raise RuntimeError(f"Failed to add state {cname} on {m_name}")
                if cname == "ANS_SetDesiredRotation_C" and src_obj:
                    for prop in ["RotationInterpSpeed", "Desired Rotation Type"]:
                        try:
                            val = src_obj.get_editor_property(prop)
                            inst.set_editor_property(prop, val)
                        except Exception:
                            pass
                elif cname == "ANS_CollisionTrace_C":
                    # CRITICAL C-992 RULE: AttackData must be UNSET (None)
                    try:
                        inst.set_editor_property("AttackData", None)
                    except Exception:
                        pass
            else:
                inst = AL.add_animation_notify_event(m, track_name, start_t, cls)
                if not inst:
                    raise RuntimeError(f"Failed to add notify {cname} on {m_name}")
                if cname == "AnimNotify_PlaySound" and src_obj:
                    try:
                        snd = src_obj.get_editor_property("sound")
                        inst.set_editor_property("sound", snd)
                    except Exception:
                        pass

        # 5. Assert count
        ev_count = len(AL.get_animation_notify_events(m))
        assert ev_count == expected_count, f"{m_name} count {ev_count} != {expected_count}"

        # 6. Save asset
        m.modify()
        saved = unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)
        assert saved, f"Failed to save {m_name}"
        log(f"SAVED {m_name}")

        # 7. Export .t3d
        task = unreal.AssetExportTask()
        task.object = m
        task.filename = f"{out_t3d_dir}/{m_name}.t3d"
        task.automated = True
        task.prompt = False
        task.replace_identical = True
        unreal.Exporter.run_asset_export_task(task)
        log(f"Exported {m_name}.t3d")

        # 8. Describe notifies
        descs = [str(x) for x in unreal.RPGMontageUtils.describe_notifies(m)]
        for d in descs:
            log(f"  {m_name} notify: {d}")

    log("Re-authoring complete.")

if __name__ == "__main__":
    run()
