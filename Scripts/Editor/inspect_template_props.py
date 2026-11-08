import unreal

def inspect_montage_tracks_and_notifies(path):
    m = unreal.EditorAssetLibrary.load_asset(path)
    if not m:
        unreal.log_error(f"Cannot load {path}")
        return
    unreal.log(f"==================== {m.get_name()} ====================")
    unreal.log(f"PlayLength: {m.get_play_length()}")
    
    # Notify tracks
    tracks = unreal.AnimationLibrary.get_animation_notify_track_names(m)
    unreal.log(f"Notify Tracks ({len(tracks)}): {tracks}")
    
    # Notify events
    events = unreal.AnimationLibrary.get_animation_notify_events(m)
    unreal.log(f"Notify Events count: {len(events)}")
    for ev in events:
        try:
            t = unreal.AnimationLibrary.get_anim_notify_event_trigger_time(ev)
            d = unreal.AnimationLibrary.get_anim_notify_event_duration(ev)
        except Exception as e:
            t, d = -1.0, -1.0
            
        track = ev.get_editor_property("track_index")
        notify_name = str(ev.get_editor_property("notify_name"))
        notify_obj = ev.get_editor_property("notify")
        state_obj = ev.get_editor_property("notify_state_class")
        
        info = f"Track {track} | t={t:.4f} d={d:.4f} name={notify_name}"
        if notify_obj:
            info += f" | NOTIFY: {notify_obj.get_class().get_name()} ({notify_obj.get_class().get_path_name()})"
            try:
                for p in dir(notify_obj):
                    if not p.startswith("_"):
                        try:
                            val = notify_obj.get_editor_property(p)
                            info += f" | {p}={val}"
                        except Exception:
                            pass
            except Exception:
                pass
        if state_obj:
            info += f" | STATE: {state_obj.get_class().get_name()} ({state_obj.get_class().get_path_name()})"
            for prop in ["Collision Target Tag", "CollisionTargetTag", "EventTag", "Desired Rotation Type", "DesiredRotationType", "RotationInterpSpeed"]:
                try:
                    val = state_obj.get_editor_property(prop)
                    info += f" | {prop}={val}"
                except Exception:
                    pass
        unreal.log(info)

templates = [
    "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryA_Montage",
    "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage",
    "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Ability_E_Anim_Montage",
    "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/HitReactions/HitReact_Back_Montage"
]

for p in templates:
    inspect_montage_tracks_and_notifies(p)
