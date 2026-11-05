# PARRY reaction (lead, Claude): NEW profile = a duplicate of DA_Sevarog_PostureProof_F8 with parry_posture_amount 100 (= posture_max: one parry breaks the posture, proof value), attack_count raised to 4 (more contacts to parry), and NEW map = a duplicate of L_SevarogFrameworkProofF8 whose fixture points at the new profile. Nothing existing is edited.
import unreal
DIR = '/Game/OneBossFight/FrameworkProof'
P_SRC, P_DST = DIR + '/DA_Sevarog_PostureProof_F8', DIR + '/DA_Sevarog_ParryReaction_PARRY'
L_SRC, L_DST = DIR + '/L_SevarogFrameworkProofF8', DIR + '/L_SevarogFrameworkProofPARRY'
for d in (P_DST, L_DST):
    if unreal.EditorAssetLibrary.does_asset_exist(d):
        raise SystemExit('exists ' + d)
assert unreal.EditorAssetLibrary.duplicate_asset(P_SRC, P_DST)
p = unreal.load_asset(P_DST)
unreal.log('[PARRY_RX] source posture_max=%s attack_count=%s hit=%s' % (p.get_editor_property('posture_max'), p.get_editor_property('attack_count'), p.get_editor_property('player_posture_hit_amount')))
p.set_editor_property('parry_posture_amount', float(p.get_editor_property('posture_max')))
p.set_editor_property('attack_count', 4)
assert float(p.get_editor_property('parry_posture_amount')) == float(p.get_editor_property('posture_max')) > 0.0
assert unreal.EditorAssetLibrary.save_loaded_asset(p)
assert unreal.EditorAssetLibrary.duplicate_asset(L_SRC, L_DST)
unreal.EditorLevelLibrary.load_level(L_DST)
fx = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_class().get_name() == 'RPGFrameworkProofFixture']
assert len(fx) == 1
fx[0].set_editor_property('profile', p)
assert fx[0].get_editor_property('profile').get_path_name() == p.get_path_name()
assert unreal.EditorLevelLibrary.save_current_level()
unreal.log('[PARRY_RX] created %s and %s parry_posture_amount=%s' % (P_DST, L_DST, p.get_editor_property('parry_posture_amount')))
