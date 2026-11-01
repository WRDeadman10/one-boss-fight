# PAC-003 probe (lead, Claude): READ-ONLY. Which attributes does a montage notify event expose to Python?
import unreal
m = unreal.load_asset('/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/Attack_PrimaryA_Montage.Attack_PrimaryA_Montage')
evs = unreal.AnimationLibrary.get_animation_notify_events(m)
unreal.log('[PAC003_PROBE] count=%d' % len(evs))
ev = evs[0]
unreal.log('[PAC003_PROBE] attrs=%s' % [a for a in dir(ev) if not a.startswith('_')])
for e in evs:
    row = {}
    for a in ('notify_name', 'display_time', 'trigger_time_offset', 'link', 'duration', 'end_link', 'notify_state_class', 'notify', 'notify_trigger_chance', 'trigger_weight_threshold'):
        try:
            row[a] = str(e.get_editor_property(a))
        except Exception as ex:
            row[a] = 'ERR'
    unreal.log('[PAC003_PROBE] ev=%s' % row)
