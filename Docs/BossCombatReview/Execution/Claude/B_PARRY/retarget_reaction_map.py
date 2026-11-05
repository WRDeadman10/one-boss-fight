# PARRY reaction (lead, Claude): the first content run crashed (world GC leak) right after duplicating the map; only the NEW profile (DA_Sevarog_ParryReaction_PARRY) was saved. This run loads the F8 map, points its fixture at the NEW profile IN MEMORY and saves the world under the NEW name; the F8 map file itself is never saved (same method as B_QA001/create_nav_baked_map.py).
import unreal
DIR = '/Game/OneBossFight/FrameworkProof'
DST = DIR + '/L_SevarogFrameworkProofPARRY'
if unreal.EditorAssetLibrary.does_asset_exist(DST):
    raise SystemExit('exists ' + DST)
p = unreal.load_asset(DIR + '/DA_Sevarog_ParryReaction_PARRY')
assert p is not None and float(p.get_editor_property('parry_posture_amount')) == float(p.get_editor_property('posture_max')) > 0.0 and int(p.get_editor_property('attack_count')) == 4
assert unreal.EditorLevelLibrary.load_level(DIR + '/L_SevarogFrameworkProofF8')
fx = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_class().get_name() == 'RPGFrameworkProofFixture']
assert len(fx) == 1
fx[0].set_editor_property('profile', p)
assert fx[0].get_editor_property('profile').get_path_name() == p.get_path_name()
world = unreal.EditorLevelLibrary.get_editor_world()
ok = unreal.EditorLoadingAndSavingUtils.save_map(world, DST)
unreal.log('[PARRY_RX2] saved=%s dst=%s profile=%s' % (ok, DST, p.get_name()))
