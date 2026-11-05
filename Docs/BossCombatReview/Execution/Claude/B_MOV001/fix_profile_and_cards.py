# MOV-001 (lead, Claude): edits the NEW MOV001 assets IN PLACE (no delete, no recreate): the profile gets bRangeBandPartition, and both band cards get their warp from the card start (0 s) to the active end, so the gap closes over about 0.53 s (Gap-Closer 880 cm = 1650 cm/s, below the pack Charge cap of 2200) instead of 0.133 s (6600 cm/s).
import unreal
DIR = '/Game/OneBossFight/FrameworkProof'
prof = unreal.load_asset(DIR + '/DA_Sevarog_RangeBands_MOV001')
prof.set_editor_property('range_band_partition', True)
assert prof.get_editor_property('range_band_partition') is True
assert unreal.EditorAssetLibrary.save_loaded_asset(prof)
unreal.log('[MOV001_FIX] profile range_band_partition=True')
for name in ('Move_Sevarog_BandMedium_MOV001', 'Move_Sevarog_BandGap_MOV001'):
    c = unreal.load_asset(DIR + '/Cards/' + name)
    spec = c.get_editor_property('spec')
    spec.set_editor_property('warp_start_seconds', 0.0)
    c.set_editor_property('spec', spec)
    back = c.get_editor_property('spec')
    assert abs(float(back.get_editor_property('warp_start_seconds'))) < 1e-6
    assert unreal.EditorAssetLibrary.save_loaded_asset(c)
    unreal.log('[MOV001_FIX] %s warp %.3f -> %.3f max %.0f' % (name, float(back.get_editor_property('warp_start_seconds')), float(back.get_editor_property('warp_end_seconds')), float(back.get_editor_property('warp_max_distance_cm'))))
