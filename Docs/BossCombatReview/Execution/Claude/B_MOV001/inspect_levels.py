# MOV-001 (lead, Claude): READ-ONLY. Where are the PlayerStart and the boss spawn in each MOV001 map?
import unreal
for n in ('R150', 'R300', 'R700'):
    unreal.EditorLevelLibrary.load_level('/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofMOV001_' + n)
    ps = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_class().get_name() == 'PlayerStart']
    fx = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_class().get_name() == 'RPGFrameworkProofFixture']
    unreal.log('[MOV001_LEVEL] %s playerstarts=%s fixture_target_start=%s boss_spawn=%s' % (n, [str(p.get_actor_location()) for p in ps], [str(f.get_editor_property('target_start').get_actor_location()) if f.get_editor_property('target_start') else None for f in fx], [str(f.get_editor_property('boss_spawn_transform').translation) for f in fx]))
