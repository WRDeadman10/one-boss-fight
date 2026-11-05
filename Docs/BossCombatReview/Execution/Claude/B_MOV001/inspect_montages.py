# MOV-001 (lead, Claude): READ-ONLY. Dumps length, rate, skeleton, sections and every notify (name, trigger time, duration, state class) of the candidate Medium / Gap-Closer montages (AnimationLibrary calls, as Scripts/Editor/g0_pack_boss.py).
import unreal
PATHS = ['/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_LeapAttack_Montage',
         '/Game/OneBossFight/SevarogPack/Montages/AM_SevPack_Charge',
         '/Game/OneBossFight/SevarogPack/Montages/AM_SevPack_Lunge',
         '/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_ChargedAttack_Montage']
for p in PATHS:
    n = p.split('/')[-1]
    m = unreal.load_asset(p)
    if m is None:
        unreal.log('[MOV001_MONTAGE] missing ' + p)
        continue
    sk = m.get_editor_property('skeleton')
    try:
        secs = [str(x) for x in unreal.AnimationLibrary.get_montage_section_names(m)]
    except Exception as e:  # noqa
        secs = 'ERR %s' % e
    unreal.log('[MOV001_MONTAGE] %s len=%.3f rate=%.3f skeleton=%s sections=%s' % (n, m.get_play_length(), m.get_editor_property('rate_scale'), sk.get_name() if sk else None, secs))
    try:
        for ev in unreal.AnimationLibrary.get_animation_notify_events(m):
            def prop(q):
                try:
                    return ev.get_editor_property(q)
                except Exception:
                    return '?'
            nsc, nfy = prop('notify_state_class'), prop('notify')
            t = unreal.AnimationLibrary.get_anim_notify_event_trigger_time(ev)
            d = unreal.AnimationLibrary.get_anim_notify_event_duration(ev)
            unreal.log('[MOV001_NOTIFY] %s name=%s t=%.3f dur=%.3f state=%s notify=%s' % (n, prop('notify_name'), t, d, nsc.get_class().get_name() if nsc not in (None, '?') else nsc, nfy.get_class().get_name() if nfy not in (None, '?') else nfy))
    except Exception as e:  # noqa
        unreal.log('[MOV001_NOTIFY] %s ERR %s' % (n, e))
