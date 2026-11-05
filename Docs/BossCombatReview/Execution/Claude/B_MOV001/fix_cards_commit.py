# MOV-001 (lead, Claude): in-place edit of the two NEW band cards. Rule MoveCard.Warp: commit <= warpStart < warpEnd <= activeEnd, so the warp can only start at the commit. The commit moves from 0.4 s to 0.05 s (tracking stops early: the boss commits to the charge direction at once) and the warp runs 0.05 -> 0.533 s: Gap-Closer 880 cm in 0.483 s = 1822 cm/s (below the pack Charge cap 2200), Medium 330 cm = 683 cm/s (design values, proposed).
import unreal
DIR = '/Game/OneBossFight/FrameworkProof'
for name in ('Move_Sevarog_BandMedium_MOV001', 'Move_Sevarog_BandGap_MOV001'):
    c = unreal.load_asset(DIR + '/Cards/' + name)
    spec = c.get_editor_property('spec')
    spec.set_editor_property('commit_seconds', 0.05)
    spec.set_editor_property('warp_start_seconds', 0.05)
    c.set_editor_property('spec', spec)
    b = c.get_editor_property('spec')
    assert abs(float(b.get_editor_property('commit_seconds')) - 0.05) < 1e-6 and abs(float(b.get_editor_property('warp_start_seconds')) - 0.05) < 1e-6
    assert unreal.EditorAssetLibrary.save_loaded_asset(c)
    unreal.log('[MOV001_FIX2] %s commit %.3f active %.3f..%.3f warp %.3f..%.3f max %.0f' % (name, float(b.get_editor_property('commit_seconds')), float(b.get_editor_property('active_start_seconds')), float(b.get_editor_property('active_end_seconds')), float(b.get_editor_property('warp_start_seconds')), float(b.get_editor_property('warp_end_seconds')), float(b.get_editor_property('warp_max_distance_cm'))))
