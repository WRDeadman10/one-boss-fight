# MOV-001 (lead, Claude): Framework.Nav.NoFullPath: the boss spawned exactly at the middle of its band (no path to walk). Each NEW map's boss spawn moves 80 cm back (x 500 -> 580) so it walks 80 cm to the band middle and decides there.
import unreal
DIR = '/Game/OneBossFight/FrameworkProof'
for n in ('R150', 'R300', 'R700'):
    unreal.EditorLevelLibrary.load_level(DIR + '/L_SevarogFrameworkProofMOV001_' + n)
    fx = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_class().get_name() == 'RPGFrameworkProofFixture']
    assert len(fx) == 1
    t = fx[0].get_editor_property('boss_spawn_transform')
    loc = t.translation
    t.translation = unreal.Vector(580.0, loc.y, loc.z)
    fx[0].set_editor_property('boss_spawn_transform', t)
    assert abs(fx[0].get_editor_property('boss_spawn_transform').translation.x - 580.0) < 1e-3
    assert unreal.EditorLevelLibrary.save_current_level()
    unreal.log('[MOV001_SPAWN] %s boss spawn x=580' % n)
