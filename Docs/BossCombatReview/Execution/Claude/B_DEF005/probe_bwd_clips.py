# DEF-005 probe (lead, Claude): READ-ONLY. Length, rate and root motion of the Sevarog backward clips (candidates for the backstep card).
import unreal
D = '/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/'
for n in ('Jog_Bwd', 'Run_Bwd', 'Sprint_Bwd', 'Knock_back_bwd', 'Jog_Bwd_Pivot_180', 'Speedburst'):
    a = unreal.load_asset(D + n)
    if a is None:
        unreal.log('[DEF005_PROBE] %s: missing' % n)
        continue
    try:
        root = bool(a.get_editor_property('enable_root_motion'))
    except Exception:
        root = 'n/a'
    unreal.log('[DEF005_PROBE] %s class=%s length=%.4f rate_scale=%s root_motion=%s' % (n, a.get_class().get_name(), a.get_play_length(), a.get_editor_property('rate_scale'), root))
