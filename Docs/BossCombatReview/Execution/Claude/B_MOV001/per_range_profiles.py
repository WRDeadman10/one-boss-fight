# MOV-001 (lead, Claude): the boss walks to the MIDDLE of the profile band and decides there, so one wide band decides at ~525 cm in every map. Three profiles (duplicates of the NEW DA_Sevarog_RangeBands_MOV001) with a narrow band around each map's range (150 / 300 / 700 cm), and each NEW map's fixture points at its own profile. Only assets made today are touched; nothing is deleted.
import unreal
DIR = '/Game/OneBossFight/FrameworkProof'
BASE = DIR + '/DA_Sevarog_RangeBands_MOV001'
for n, lo, hi in (('R150', 140.0, 160.0), ('R300', 290.0, 310.0), ('R700', 690.0, 710.0)):
    dst = '%s_%s' % (BASE, n)
    if unreal.EditorAssetLibrary.does_asset_exist(dst):
        raise SystemExit('exists ' + dst)
    if not unreal.EditorAssetLibrary.duplicate_asset(BASE, dst):
        raise SystemExit('duplicate failed ' + dst)
    p = unreal.load_asset(dst)
    p.set_editor_property('band_min_cm', lo)
    p.set_editor_property('band_max_cm', hi)
    assert abs(float(p.get_editor_property('band_min_cm')) - lo) < 1e-4 and abs(float(p.get_editor_property('band_max_cm')) - hi) < 1e-4
    assert p.get_editor_property('range_band_partition') is True
    assert unreal.EditorAssetLibrary.save_loaded_asset(p)
    unreal.EditorLevelLibrary.load_level(DIR + '/L_SevarogFrameworkProofMOV001_' + n)
    fx = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_class().get_name() == 'RPGFrameworkProofFixture']
    assert len(fx) == 1
    fx[0].set_editor_property('profile', p)
    assert fx[0].get_editor_property('profile').get_path_name() == p.get_path_name()
    assert unreal.EditorLevelLibrary.save_current_level()
    unreal.log('[MOV001_PROFILE] %s band %.0f..%.0f fixture profile %s' % (n, lo, hi, p.get_name()))
