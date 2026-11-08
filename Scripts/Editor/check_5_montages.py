import unreal

montages = [
    "/Game/OneBossFight/Player/Animations/AM_ER_Attack_GuardCounter",
    "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Light",
    "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Heavy_Plunge",
    "/Game/OneBossFight/Player/Animations/AM_ER_Backstep_Back",
    "/Game/OneBossFight/Boss01/Animations/AM_Boss01_ParryRecoil"
]

for p in montages:
    m = unreal.load_asset(p)
    if not m:
        unreal.log_error(f"Missing {p}")
        continue
    tracks = unreal.AnimationLibrary.get_animation_notify_track_names(m)
    events = unreal.AnimationLibrary.get_animation_notify_events(m)
    unreal.log(f"Montage {m.get_name()}: length={m.get_play_length():.4f}, tracks={tracks}, events={len(events)}")
